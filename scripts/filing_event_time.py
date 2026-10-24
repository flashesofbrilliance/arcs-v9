#!/usr/bin/env python3
"""filing_event_time: event-time Monte Carlo over the filing plan graph. Stdlib only.

Imported by scripts/filing_workback.py; runnable alone for its self-test:
  python3 scripts/filing_event_time.py --self-test

Why this exists (Zach, 2026-10-17): the first workback treated time as even integer days in a strict line (chronos).
Real work arrives in bursts and waits, and many constraints are about the right moment, not elapsed days. This module:
  - treats a duration as a distribution (triangular: optimistic, likely, pessimistic), sampled as a FLOAT number of days
  - fires each step when all its preconditions have finished (event time), so dates are distributions, not points
  - reports the chance of meeting the one hard calendar edge, percentile dates, and a criticality index per step
  - compares alternative paths (graph patches) under COMMON RANDOM NUMBERS so a difference is the path, not the dice
  - checks that every one-way door has a declared write-lock step before it

Types it keeps apart: an INSTANT (a sampled finish time, reported as an interval), an ORDER (the needs edges, a partial
order), a DURATION (a distribution), a BRANCH (a path patch). All duration inputs are author estimates unless a node
sets measured:true; the module never claims otherwise.
"""
import argparse
import copy
import datetime as dt
import random


def order(nodes):
    seen, out = set(), []

    def visit(i, stack=()):
        if i in stack:
            raise ValueError("cycle at " + i)
        if i in seen:
            return
        for d in nodes[i]["needs"]:
            if d not in nodes:
                raise ValueError("%s needs unknown %s" % (i, d))
            visit(d, stack + (i,))
        seen.add(i)
        out.append(i)
    for i in nodes:
        visit(i)
    return out


def tri_params(node, sim):
    """(low, mode, high) in days for one node."""
    if node.get("dur"):
        d = node["dur"]
        return float(d["opt"]), float(d["likely"]), float(d["pess"])
    lo, mo, hi = sim.get("spreads", {}).get(node.get("owner"), [0.5, 1.0, 2.0])
    base = float(node.get("days", 0))
    return base * lo, base * mo, base * hi


def apply_patch(nodes, patch):
    """Return a patched deep copy: nodes_add (list of node dicts), needs_set / needs_add (id -> list)."""
    out = copy.deepcopy(nodes)
    for n in patch.get("nodes_add", []):
        n = copy.deepcopy(n)
        n.setdefault("status", "blocked")
        out[n["id"]] = n
    for i, needs in patch.get("needs_set", {}).items():
        out[i]["needs"] = list(needs)
    for i, needs in patch.get("needs_add", {}).items():
        out[i]["needs"] = list(out[i]["needs"]) + [x for x in needs if x not in out[i]["needs"]]
    return out


def simulate(nodes, sim, target, today, plan_date, runs=None, seed=None, also=(), stall=None):
    runs = int(runs or sim.get("runs", 20000))
    seed = sim.get("seed", 17) if seed is None else seed
    topo = order(nodes)
    done = {i for i, n in nodes.items() if n.get("status") == "done"}
    if target not in nodes:
        raise ValueError("target %s not in graph" % target)
    deadline = (plan_date - today).days + 1.0  # end of the plan date, in float days from today
    samples = {}
    for i in topo:
        if i in done:
            samples[i] = None
            continue
        lo, mo, hi = tri_params(nodes[i], sim)
        rng = random.Random("%s:%s" % (seed, i))  # one stream per node: common random numbers across paths
        samples[i] = [rng.triangular(lo, hi, mo) if hi > lo else lo for _ in range(runs)]
        sp = (stall or {}).get("p", {}).get(nodes[i].get("owner"), 0.0)
        if sp > 0:  # heavy tail: a stall adds an exponential delay; its own per-node stream keeps common random numbers
            srng = random.Random("%s:%s:stall" % (seed, i))
            mean = max(mo, 0.25) * (stall or {}).get("mean_mult", 2.0)
            for r in range(runs):
                if srng.random() < sp:
                    samples[i][r] += srng.expovariate(1.0 / mean)
    nb = {}
    for i, n in nodes.items():
        w = (n.get("window") or {}).get("not_before")
        if w:
            nb[i] = float((dt.date.fromisoformat(w) - today).days)
    fins, crit = [], {i: 0 for i in topo}
    extra = {a: [] for a in also}
    for r in range(runs):
        fin, pred = {}, {}
        for i in topo:
            if i in done:
                fin[i] = 0.0
                continue
            start, p = 0.0, None
            for d in nodes[i]["needs"]:
                if fin[d] >= start:
                    start, p = fin[d], d
            if i in nb and nb[i] > start:
                start, p = nb[i], None
            fin[i] = start + samples[i][r]
            pred[i] = p
        fins.append(fin[target])
        for a in also:
            extra[a].append(fin[a])
        cur = target
        while cur is not None:
            crit[cur] += 1
            cur = pred.get(cur)
    fs = sorted(fins)

    def pct(q, arr=None):
        arr = fs if arr is None else arr
        return arr[min(len(arr) - 1, int(q * (len(arr) - 1)))]
    effort = 0.0
    for i in topo:
        if i not in done:
            lo, mo, hi = tri_params(nodes[i], sim)
            effort += (lo + mo + hi) / 3.0
    doors = [i for i in topo if nodes[i].get("one_way") and i not in done]
    import bisect
    if_earlier = {k: bisect.bisect_right(fs, deadline - k) / float(runs) for k in (0, 30, 60, 90, 120)}
    res = {"p_if_earlier": if_earlier, "runs": runs, "seed": seed, "target": target, "deadline_days": deadline,
           "p_on_time": sum(1 for x in fins if x <= deadline) / float(runs),
           "pct": {q: pct(q / 100.0) for q in (10, 50, 80, 95)},
           "crit": {i: crit[i] / float(runs) for i in topo if crit[i]},
           "mean_effort_days": effort, "one_way_doors": doors,
           "also": {a: {"p50": pct(0.5, sorted(v)), "p80": pct(0.8, sorted(v))} for a, v in extra.items()}}
    return res


def write_lock_problems(nodes):
    """Every pending one-way node needs a direct write_lock need that carries a declare text;
    a done one-way node needs its write_lock done with done_on."""
    bad = []
    for i, n in nodes.items():
        if not n.get("one_way"):
            continue
        wls = [d for d in n["needs"] if nodes.get(d, {}).get("kind") == "write_lock"]
        if not wls:
            bad.append("%s is a one-way door with no write-lock step before it" % i)
            continue
        for w in wls:
            if not (nodes[w].get("declare") or "").strip():
                bad.append("%s has no declare text" % w)
            if n.get("status") == "done" and not (nodes[w].get("status") == "done" and nodes[w].get("done_on")):
                bad.append("%s is done but its write-lock %s is not declared" % (i, w))
    return bad


def self_test():
    today = dt.date(2026, 10, 17)
    pdate = dt.date(2027, 4, 4)
    sim = {"runs": 4000, "seed": 7, "spreads": {"a": [0.5, 1.0, 2.0], "b": [0.5, 1.0, 3.0]}}

    def g(days_a=10, days_b=10):
        return {"x": {"id": "x", "needs": [], "owner": "a", "status": "ready", "days": days_a},
                "y": {"id": "y", "needs": [], "owner": "b", "status": "ready", "days": days_b},
                "t": {"id": "t", "needs": ["x", "y"], "owner": "a", "status": "blocked", "days": 5, "one_way": True},
                "w": {"id": "w", "needs": ["t"], "owner": "a", "status": "blocked", "days": 1}}
    base = simulate(g(), sim, "t", today, pdate)
    again = simulate(g(), sim, "t", today, pdate)
    assert base == again, "same seed must give the same result"
    p = base["pct"]
    assert p[10] <= p[50] <= p[80] <= p[95], "percentiles out of order"
    assert 0 <= base["p_on_time"] <= 1, "probability out of range"
    assert abs(base["crit"]["t"] - 1.0) < 1e-12, "the target is on every critical path"
    assert abs(base["crit"].get("x", 0) + base["crit"].get("y", 0) - 1.0) < 1e-9, "exactly one of the two parallel steps is critical per run"
    twin = {"x": {"id": "x", "needs": [], "owner": "a", "status": "ready", "days": 10},
            "y": {"id": "y", "needs": [], "owner": "a", "status": "ready", "days": 10},
            "t": {"id": "t", "needs": ["x", "y"], "owner": "a", "status": "blocked", "days": 1}}
    cr = simulate(twin, sim, "t", today, pdate)["crit"]
    assert 0.35 < cr["x"] < 0.65 and 0.35 < cr["y"] < 0.65, "identical parallel steps must split criticality about evenly (independent streams): %s" % cr
    slow = simulate(g(days_a=400, days_b=400), sim, "t", today, pdate)
    assert slow["p_on_time"] < base["p_on_time"] and slow["p_on_time"] < 0.5, "a huge slip must collapse the chance (the gate can fail)"
    assert base["p_on_time"] > 0.99, "a comfortable plan must score high (the gate does not cry wolf)"
    upper = sum(tri_params(n, sim)[2] for n in g().values())
    assert max(simulate(g(), sim, "t", today, pdate, runs=500)["pct"].values()) <= upper, "finish beyond the sum of pessimistic durations"
    # common random numbers: a shared node draws identically under a patched graph
    patched = apply_patch(g(), {"needs_set": {"t": ["x"]}})
    r1 = simulate(g(), sim, "x", today, pdate)
    r2 = simulate(patched, sim, "x", today, pdate)
    assert r1["pct"] == r2["pct"], "common random numbers broken: a shared node drew different values"
    assert simulate(patched, sim, "t", today, pdate)["pct"][50] < base["pct"][50], "dropping a precondition must not make the target later"
    # stall scenario: heavier tail, never improves the chance, deterministic, independent of the bounded draws
    st = {"p": {"a": 0.4, "b": 0.4}, "mean_mult": 3.0}
    tight = g(days_a=60, days_b=60)
    b0 = simulate(tight, sim, "t", today, pdate)
    b1 = simulate(tight, sim, "t", today, pdate, stall=st)
    assert b1["pct"][95] > b0["pct"][95], "stalls must lengthen the tail"
    assert b1["p_on_time"] <= b0["p_on_time"], "stalls must not improve the chance"
    assert b1 == simulate(tight, sim, "t", today, pdate, stall=st), "stall scenario is not deterministic"
    pe = b0["p_if_earlier"]
    assert pe[0] == b0["p_on_time"] and pe[0] >= pe[30] >= pe[60] >= pe[90] >= pe[120], "p_if_earlier must start at p_on_time and not increase as the deadline moves earlier"
    # not_before window
    w = g(); w["t"]["window"] = {"not_before": "2027-01-01"}
    assert simulate(w, sim, "t", today, pdate)["pct"][10] >= (dt.date(2027, 1, 1) - today).days, "not_before ignored"
    # cycle and unknown need
    c = g(); c["x"]["needs"] = ["w"]
    for bad in (c, dict(g(), q={"id": "q", "needs": ["nope"], "owner": "a", "status": "ready", "days": 1})):
        try:
            simulate(bad, sim, "t", today, pdate, runs=10)
        except ValueError:
            pass
        else:
            raise AssertionError("cycle or unknown need not caught")
    # write-lock gate
    assert write_lock_problems(g()), "one-way door without a write-lock was accepted"
    ok = g()
    ok["wl"] = {"id": "wl", "needs": ["x", "y"], "kind": "write_lock", "declare": "irreversible", "owner": "a", "status": "ready", "days": 0.5}
    ok["t"]["needs"] = ["x", "y", "wl"]
    assert not write_lock_problems(ok), "a declared write-lock was rejected"
    ok["wl"]["declare"] = ""
    assert write_lock_problems(ok), "an empty declaration was accepted"
    ok["wl"]["declare"] = "irreversible"; ok["t"]["status"] = "done"
    assert write_lock_problems(ok), "a done door with an undeclared write-lock was accepted"
    print("self-test OK: 21 assertion sites behaved (determinism, ordering, independence, collapse and no-false-alarm, bounds, common random numbers, window, cycle, unknown need, write-lock)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        self_test()
