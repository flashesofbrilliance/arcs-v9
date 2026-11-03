#!/usr/bin/env python3
"""jtbd_edge_weights: outcome-weighted (job, tool) edges for the JTBD graph (row jtbd-graph-s5-feedback). Stdlib, read-only.

Rules are pre-registered in _PATTERNS/2026-10-20-jtbd-s5-preregistration.md; constants live in
runtime/specs/jtbd-s5/config.json. In short:
  use      = a decision_receipt row with tool_id (an edge only when job_id is also set), event_at >= start
  success  = a strictly later receipt with the same job_id exists AND the job's backlog row is DONE now
  failure  = the row is COMPOSTED/SUPERSEDED, or DONE with the latest receipt for the job naming another tool
  pending  = anything else (incl. every non-backlog job); never moves a weight
  weight   = 1.0 until the edge has n_min uses; then EMA w = (1-alpha)*w + alpha*(0.5+s) over resolved outcomes whose
             use is inside [start, start+promote_days), in event_at order. Applied W = max(1.0, w); w < 1.0 is a
             demotion FLAG for Zach, never applied.
No backfill: start null -> nothing counts. Receipts are read from the existing export
(`python3 scripts/universe_receipts_adapter.py --export`, gitignored); this script never writes the database.
Output (gitignored): _STATE/jtbd-graph/weights.json, read by operators/jtbd_query.py rank().

  python3 scripts/jtbd_edge_weights.py              # compute and write weights.json, print a summary
  python3 scripts/jtbd_edge_weights.py --self-test
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CONFIG = "runtime/specs/jtbd-s5/config.json"
EXPORT = "_STATE/job-search/universe/sources/decision-receipts.json"
BACKLOG = "_QUEUE/induced-backlog.jsonl"
OUT = "_STATE/jtbd-graph/weights.json"
CLOSED, ABANDONED = {"DONE"}, {"COMPOSTED", "SUPERSEDED"}


def _ts(s):
    """ISO-8601 -> aware UTC datetime, or None. A bare date is read as midnight UTC."""
    if not s:
        return None
    # Postgres text form ("2026-10-20 16:57:46.010822+00") has an hour-only offset and 6-digit micros; Python 3.9's
    # fromisoformat rejects "+00", which made every exported receipt read as undated (coverage 0, 2026-10-20).
    v = re.sub(r"([+-]\d\d)$", r"\1:00", str(s).strip().replace("Z", "+00:00").replace(" ", "T", 1))
    try:
        t = dt.datetime.fromisoformat(v)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def open_nofollow(path, mode):
    """Open for writing ("w" or "a") without following a symlink at the final component (closes the check-then-open race)."""
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) | (os.O_APPEND if mode == "a" else os.O_TRUNC)
    return os.fdopen(os.open(path, flags, 0o644), mode, encoding="utf-8")


def load_config(root=REPO):
    c = json.load(open(os.path.join(root, CONFIG)))
    for k, ok in (("n_min", lambda v: isinstance(v, int) and v >= 1), ("alpha", lambda v: isinstance(v, (int, float)) and 0 < v < 1),
                  ("promote_days", lambda v: isinstance(v, int) and v >= 0)):
        if not ok(c.get(k)):
            raise ValueError(f"config {k}={c.get(k)!r} invalid")
    if c.get("start") is not None and _ts(c["start"]) is None:
        raise ValueError(f"config start={c['start']!r} is not ISO-8601")
    return c


def backlog_states(root=REPO):
    out = {}
    p = os.path.join(root, BACKLOG)
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                out["job:backlog:" + r["id"]] = r.get("state")
    return out


def eligible(rows, start, now=None):
    """Distinct receipts (by receipt_id) dated in [start, now], oldest first. start None -> none (no backfill).
    A repeated receipt_id counts once; a future-dated receipt is not counted; a receipt that a later row
    names in `supersedes` is not counted (its replacement is)."""
    if start is None:
        return []
    now = now or dt.datetime.now(dt.timezone.utc)
    out, seen = [], set()
    replaced = {str(r.get("supersedes")).strip() for r in rows if r.get("supersedes")}
    for r in rows:
        rid = str(r.get("receipt_id") or "").strip()
        t = _ts(r.get("event_at"))
        if not rid or rid in seen or rid in replaced or t is None or t < start or t > now:
            continue
        seen.add(rid)
        out.append(dict(r, _t=t))
    return sorted(out, key=lambda r: (r["_t"], r.get("receipt_id", "")))


def outcome(use, rows, states):
    """1 success, 0 failure, None pending, for one use against the eligible rows."""
    j, t = use.get("job_id"), use.get("tool_id")
    st = states.get(j)
    if st in ABANDONED:
        return 0
    if st not in CLOSED:
        return None
    later = [r for r in rows if r.get("job_id") == j and r["_t"] > use["_t"]]
    if not later:
        return None
    last_tool = next((r.get("tool_id") for r in reversed(later) if r.get("tool_id")), None)
    if last_tool and last_tool != t:
        return 0
    return 1


def compute(rows, states, cfg, now=None):
    start = _ts(cfg.get("start"))
    now = now or dt.datetime.now(dt.timezone.utc)
    el = eligible(rows, start, now)
    window_end = start + dt.timedelta(days=cfg["promote_days"]) if start else None
    edges = {}
    for r in el:
        if r.get("tool_id") and r.get("job_id"):
            edges.setdefault((r["job_id"], r["tool_id"]), []).append(r)
    weights, flags, detail = {}, [], []
    for (j, t), uses in sorted(edges.items()):
        n = len(uses)
        w, folded = 1.0, 0
        if n >= cfg["n_min"]:
            for u in uses:
                if not (u["_t"] < window_end):
                    continue
                s = outcome(u, el, states)
                if s is None:
                    continue
                w = (1 - cfg["alpha"]) * w + cfg["alpha"] * (0.5 + s)
                folded += 1
        applied = max(1.0, w)
        key = f"{j}|{t}"
        if applied != 1.0:
            weights[key] = round(applied, 6)
        if w < 1.0:
            flags.append({"edge": key, "computed": round(w, 6), "applied": 1.0, "uses": n})
        detail.append({"edge": key, "uses": n, "folded": folded, "computed": round(w, 6), "applied": round(applied, 6)})
    with_both = sum(1 for r in el if r.get("job_id") and r.get("tool_id"))
    return {
        "generator": "scripts/jtbd_edge_weights.py",
        "rule": "_PATTERNS/2026-10-20-jtbd-s5-preregistration.md",
        "start": cfg.get("start"), "computed_at": now.isoformat(timespec="seconds"),
        "constants": {k: cfg[k] for k in ("n_min", "alpha", "promote_days")},
        "weights": weights, "demotion_flags": flags, "edges": detail,
        "coverage": {"receipts_since_start": len(el), "with_job_and_tool": with_both,
                     "share": round(with_both / len(el), 3) if el else None},
    }


def load_export(root=REPO):
    p = os.path.join(root, EXPORT)
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def run(root=REPO, out=None, quiet=False):
    cfg = load_config(root)
    rows = load_export(root)
    note = None
    if rows is None:
        rows, note = [], "no receipt export; run `python3 scripts/universe_receipts_adapter.py --export`"
    res = compute(rows, backlog_states(root), cfg)
    if note:
        res["note"] = note
    path = out or os.path.join(root, OUT)
    if os.path.islink(path) or os.path.realpath(os.path.dirname(path)) != os.path.join(os.path.realpath(root), os.path.dirname(OUT)):
        raise ValueError(f"refusing to write {path}: only a regular file in {os.path.dirname(OUT)}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open_nofollow(path, "w") as f:
        json.dump(res, f, indent=1)
    if not quiet:
        c = res["coverage"]
        print(f"jtbd weights: start {res['start']} · receipts since start {c['receipts_since_start']} "
              f"(job+tool {c['with_job_and_tool']}) · edges {len(res['edges'])} · moved {len(res['weights'])} · "
              f"demotion flags {len(res['demotion_flags'])} -> {os.path.relpath(path, root)}" + (f"\n{note}" if note else ""))
    return res


def load_weights(root=REPO, rows=None, now=None):
    """{(job, tool): W} for jtbd_query.rank, RECOMPUTED from the receipt export with the pre-registered rules.
    weights.json is a report only and is never trusted as input (counter-agent finding: a hand-made file could skip
    the 3-use minimum). Any problem -> {} (every weight 1.0)."""
    try:
        cfg = load_config(root)
        if cfg.get("start") is None:
            return {}
        rows = load_export(root) if rows is None else rows
        res = compute(rows or [], backlog_states(root), cfg, now)
        out = {}
        for k, v in res["weights"].items():
            j, t = k.split("|", 1)
            if 1.0 <= v <= 1.5:
                out[(j, t)] = float(v)
        return out
    except Exception:  # noqa: BLE001  a broken export must never break retrieval
        return {}


def self_test():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    S = "2026-11-01T00:00:00Z"
    cfg = {"start": S, "n_min": 3, "alpha": 0.1, "promote_days": 30}
    J, T, T2 = "job:backlog:x", "tool:script:a.py", "tool:script:b.py"

    def r(i, day, job=J, tool=T):
        return {"receipt_id": f"r{i}", "event_at": f"2026-11-{day:02d}T12:00:00Z", "job_id": job, "tool_id": tool}
    done = {J: "DONE"}
    now = _ts("2026-11-20T00:00:00Z")
    # good: 3 uses + a later close -> first two uses succeed (third has a later receipt? r4 is the close)
    rows = [r(1, 2), r(2, 3), r(3, 4), r(4, 5)]
    res = compute(rows, done, cfg, now)
    w = res["weights"].get(f"{J}|{T}")
    check("good: 4 uses on a DONE job promote the edge above 1.0", w is not None and w > 1.0)
    check("good: the EMA matches the formula (3 successes, last use pending)", w is not None and abs(w - 1.1355) < 1e-9)
    # bad (a): two uses only -> no move
    res = compute(rows[:2] + [r(9, 6, tool=None)], done, cfg, now)
    check("bad(a): fewer than 3 uses never moves a weight", res["weights"] == {})
    # bad (b): failures compute w < 1 but are never applied
    rows_f = [r(1, 2), r(2, 3), r(3, 4), r(4, 5, tool=T2)]
    res = compute(rows_f, done, cfg, now)
    check("bad(b): a computed demotion is flagged, not applied", res["weights"].get(f"{J}|{T}") is None
          and any(f["edge"] == f"{J}|{T}" and f["applied"] == 1.0 for f in res["demotion_flags"]))
    res = compute(rows, {J: "COMPOSTED"}, cfg, now)
    check("bad(b): an abandoned job demotes nothing automatically", res["weights"] == {} and res["demotion_flags"])
    # bad (c): pre-start receipts are never counted
    pre = [{"receipt_id": f"p{i}", "event_at": "2026-10-01T00:00:00Z", "job_id": J, "tool_id": T} for i in range(9)]
    res = compute(pre + rows[:1], done, cfg, now)
    check("bad(c): receipts dated before start are not counted", res["coverage"]["receipts_since_start"] == 1 and res["weights"] == {})
    res = compute(rows, done, dict(cfg, start=None), now)
    check("bad(c): start null counts nothing", res["coverage"]["receipts_since_start"] == 0 and res["weights"] == {})
    # promote window: uses after day 30 do not fold
    late = [dict(x, event_at=x["event_at"].replace("2026-11", "2026-12")) for x in rows]
    res = compute(late, done, cfg, _ts("2026-12-20T00:00:00Z"))
    check("window: uses after start+30d never promote", res["weights"] == {})
    # pending: open job or non-backlog job
    res = compute(rows, {J: "OPEN"}, cfg, now)
    check("pending: an OPEN job moves nothing", res["weights"] == {} and not res["demotion_flags"])
    # bad config fails loudly
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, os.path.dirname(CONFIG)))
        json.dump({"start": "yesterday", "n_min": 3, "alpha": 0.1, "promote_days": 30}, open(os.path.join(d, CONFIG), "w"))
        try:
            load_config(d); raised = False
        except ValueError:
            raised = True
        check("bad config: a non-ISO start raises", raised)
        json.dump({"start": S, "n_min": 3, "alpha": 0.1, "promote_days": 30}, open(os.path.join(d, CONFIG), "w"))
        os.makedirs(os.path.join(d, os.path.dirname(OUT)))
        json.dump({"start": S, "weights": {f"{J}|{T}": 1.5}}, open(os.path.join(d, OUT), "w"))
        check("bad(a): a hand-made weights.json with 0 uses is ignored", load_weights(d, rows=[]) == {})
        os.makedirs(os.path.join(d, "_QUEUE")); open(os.path.join(d, BACKLOG), "w").write(json.dumps({"id": "x", "state": "DONE"}) + "\n")
        lw = load_weights(d, rows=rows, now=now)
        check("good: load_weights recomputes from receipts (4 uses on a DONE job -> 1.1355)", lw == {(J, T): 1.1355})
    ws = [dict(r(i, 2 + i), receipt_id=" " * i) for i in (1, 2, 3)] + [r(9, 9)]
    res = compute(ws, done, cfg, now)
    check("bad(a): whitespace-only receipt ids are not uses", res["weights"] == {})
    dup = dict(r(1, 2), receipt_id="dup")
    res = compute([dup, dup, dup, r(4, 5)], done, cfg, now)
    check("bad(a): one receipt id repeated three times is one use", res["weights"] == {} and res["coverage"]["receipts_since_start"] == 2)
    res = compute(rows[:3] + [dict(r(4, 5), event_at="2099-01-01T00:00:00Z")], done, cfg, now)
    check("future-dated receipts are not counted", res["coverage"]["receipts_since_start"] == 3)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, os.path.dirname(CONFIG))); os.makedirs(os.path.join(d, os.path.dirname(OUT)))
        json.dump(cfg, open(os.path.join(d, CONFIG), "w"))
        os.symlink(os.path.join(d, "outside.txt"), os.path.join(d, OUT))
        try:
            run(d, quiet=True); refused = False
        except ValueError:
            refused = True
        check("bad(d): refuses to write weights.json through a symlink", refused and not os.path.exists(os.path.join(d, "outside.txt")))
    print("self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Outcome-weighted JTBD edges (read-only; writes only _STATE/jtbd-graph/weights.json).")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
