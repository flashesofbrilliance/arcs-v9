#!/usr/bin/env python3
"""proposal_rank.py: idempotent ranking of _PROPOSALS/*.json over five axes, with nested decision edges.

Axes (each 0 to 5; 5^5 = 3,125 cells, the decision-geometry grid size):
  recency    MEASURED  days since the proposal's date
  ripple     MEASURED  decisions that transitively depend on this proposal's decisions (edges are curated, so incomplete)
  coherence  PROXY     share of controls that define both a known-bad and a known-good case (test-readiness, not truth)
  potency    JUDGMENT  only if a human supplies it in _PROPOSALS/edges.json "judgments"; otherwise unscored
  relevancy  JUDGMENT  same rule

An unscored axis is shown as "?" and excluded from ranking. Nothing is guessed. Weights are chosen
by the reader (frame dial on the page), never fixed here.

Idempotent: same inputs and the same --as-of date give byte-identical output. No writes outside stdout/return values.

  python3 scripts/proposal_rank.py [--as-of YYYY-MM-DD]
  python3 scripts/proposal_rank.py --self-test
Stdlib only.
"""
import argparse, collections, datetime as dt, glob, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUBRIC_PATH = os.path.join(ROOT, "_PROPOSALS", "rubric.json")


def validate_rubric(r):
    """A rubric is usable only if every dimension has a key, both anchors and a positive integer scale_max."""
    errs = []
    for d in r.get("dims", []):
        for k in ("key", "label", "basis", "anchor0", "anchor_max"):
            if not d.get(k):
                errs.append("dim %s missing %s" % (d.get("key", "?"), k))
        if not isinstance(d.get("scale_max"), int) or d["scale_max"] < 1:
            errs.append("dim %s needs a positive integer scale_max" % d.get("key", "?"))
    if not r.get("dims"):
        errs.append("no dims")
    return errs


def load_rubric(path=RUBRIC_PATH):
    r = json.load(open(path, encoding="utf-8"))
    errs = validate_rubric(r)
    if errs:
        raise ValueError("rubric invalid: " + "; ".join(errs))
    return r


RUBRIC = load_rubric()
AXES = [d["key"] for d in RUBRIC["dims"]]
BASIS = {d["key"]: d["basis"] for d in RUBRIC["dims"]}
ANCHORS = {d["key"]: (d["anchor0"], d["anchor_max"]) for d in RUBRIC["dims"]}
assert AXES == ["recency", "ripple", "coherence", "potency", "relevancy"], "axes changed: update the scorers"


def recency_score(age_days):
    return 5 if age_days <= 1 else 4 if age_days <= 3 else 3 if age_days <= 7 else 2 if age_days <= 14 else 1 if age_days <= 30 else 0


def ripple_score(n):
    return 0 if n == 0 else 1 if n == 1 else 2 if n == 2 else 3 if n <= 4 else 4 if n <= 7 else 5


def coherence_score(controls):
    if not controls:
        return 0
    ok = sum(1 for c in controls if c.get("bad") and c.get("good"))
    return round(5 * ok / len(controls))


def check_edges(edges, known):
    """Return (problems, graph). Cycles and dangling ends are problems, never silently dropped."""
    problems, graph = [], collections.defaultdict(set)
    for e in edges:
        if e["from"] not in known or e["to"] not in known:
            problems.append("dangling edge: %s -> %s" % (e["from"], e["to"]))
            continue
        graph[e["from"]].add(e["to"])
    state = {}

    def visit(n, path):
        if state.get(n) == 2:
            return
        if state.get(n) == 1:
            problems.append("cycle: " + " -> ".join(path + [n]))
            return
        state[n] = 1
        for m in sorted(graph.get(n, ())):
            visit(m, path + [n])
        state[n] = 2

    for n in sorted(graph):
        visit(n, [])
    return problems, graph


def downstream(graph, node):
    """Decisions that depend (transitively) on `node`."""
    rev = collections.defaultdict(set)
    for a, bs in graph.items():
        for b in bs:
            rev[b].add(a)
    seen, stack = set(), [node]
    while stack:
        for m in rev.get(stack.pop(), ()):
            if m not in seen:
                seen.add(m)
                stack.append(m)
    return seen


def load(root=ROOT):
    props = []
    for f in sorted(glob.glob(os.path.join(root, "_PROPOSALS", "*.json"))):
        if os.path.basename(f) == "edges.json":
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(d, dict) and "controls" in d and "decisions" in d:
            d["_stem"] = os.path.splitext(os.path.basename(f))[0]
            props.append(d)
    ep = os.path.join(root, "_PROPOSALS", "edges.json")
    edges = json.load(open(ep, encoding="utf-8")) if os.path.exists(ep) else {"edges": [], "judgments": {}}
    legacy = sorted(os.path.basename(f) for f in glob.glob(os.path.join(root, "_PROPOSALS", "*"))
                    if os.path.isfile(f) and not f.endswith("edges.json") and os.path.splitext(f)[1] in (".md", ".html")
                    and os.path.splitext(os.path.basename(f))[0] not in {p["_stem"] for p in props})
    return props, edges, legacy


def rank(props, edges, as_of):
    known = {"%s#%s" % (p["id"], d["id"]) for p in props for d in p["decisions"]}
    problems, graph = check_edges(edges.get("edges", []), known)
    judg = edges.get("judgments", {})
    rows = []
    for p in props:
        age = (as_of - dt.date.fromisoformat(p["date"])).days
        down = set()
        for d in p["decisions"]:
            down |= downstream(graph, "%s#%s" % (p["id"], d["id"]))
        own = {"%s#%s" % (p["id"], d["id"]) for d in p["decisions"]}
        down -= own
        j = judg.get(p["id"], {})
        sc = {"recency": recency_score(age), "ripple": ripple_score(len(down)), "coherence": coherence_score(p["controls"]),
              "potency": j.get("potency"), "relevancy": j.get("relevancy")}
        issues = []
        for d in p["decisions"]:
            nid = "%s#%s" % (p["id"], d["id"])
            waits = sorted(graph.get(nid, ()))
            issues.append({"id": nid, "question": d["question"], "waits_on": waits,
                           "blocks": sorted(downstream(graph, nid)), "state": "BLOCKED by undecided" if waits else "READY to decide"})
        rows.append({"id": p["id"], "stem": p["_stem"], "title": p["title"], "date": p["date"], "scores": sc,
                     "cell": "-".join("?" if sc[a] is None else str(sc[a]) for a in AXES), "downstream_decisions": len(down), "issues": issues})
    rows.sort(key=lambda r: (-sum(v for v in r["scores"].values() if v is not None), r["id"]))
    return {"as_of": as_of.isoformat(), "axes": AXES, "basis": BASIS, "problems": problems, "rows": rows}


def self_test():
    p = lambda i, dec, ctl=(): {"id": i, "date": "2026-10-15", "_stem": i, "title": i, "decisions": [{"id": d, "question": "q"} for d in dec], "controls": list(ctl)}
    A, B, C = p("A", ["D1"]), p("B", ["D1"]), p("C", ["D1"])
    asof = dt.date(2026, 10, 15)
    chain = {"edges": [{"from": "B#D1", "to": "A#D1"}, {"from": "C#D1", "to": "B#D1"}], "judgments": {}}
    r = rank([A, B, C], chain, asof)
    top = {x["id"]: x for x in r["rows"]}
    assert top["A"]["downstream_decisions"] == 2 and top["C"]["downstream_decisions"] == 0, "known-good: chain ripple"
    assert top["B"]["issues"][0]["state"] == "BLOCKED by undecided" and top["A"]["issues"][0]["state"] == "READY to decide"
    bad_cycle = rank([A, B], {"edges": [{"from": "A#D1", "to": "B#D1"}, {"from": "B#D1", "to": "A#D1"}]}, asof)
    assert any(x.startswith("cycle") for x in bad_cycle["problems"]), "known-bad: cycle must be reported"
    bad_dangle = rank([A], {"edges": [{"from": "A#D1", "to": "Z#D9"}]}, asof)
    assert any(x.startswith("dangling") for x in bad_dangle["problems"]), "known-bad: dangling edge must be reported"
    assert top["A"]["scores"]["potency"] is None and top["A"]["cell"].endswith("?-?"), "unscored axes must stay unscored"
    one = json.dumps(rank([A, B, C], chain, asof), sort_keys=True)
    two = json.dumps(rank([C, B, A], chain, asof), sort_keys=True)
    assert one == two, "idempotent: input order must not change output"
    good_r = {"dims": [{"key": "a", "label": "A", "basis": "MEASURED", "scale_max": 5, "anchor0": "x", "anchor_max": "y"}]}
    assert validate_rubric(good_r) == [], "known-good rubric must validate"
    assert validate_rubric({"dims": [{"key": "a", "label": "A", "basis": "M", "scale_max": 5, "anchor0": "x"}]}), "known-bad: missing anchor_max must be rejected"
    assert validate_rubric({"dims": [{"key": "a", "label": "A", "basis": "M", "scale_max": 0, "anchor0": "x", "anchor_max": "y"}]}), "known-bad: scale_max 0 must be rejected"
    assert validate_rubric(RUBRIC) == [], "the shipped rubric must validate"
    print("self-test ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
    else:
        props, edges, legacy = load()
        out = rank(props, edges, dt.date.fromisoformat(a.as_of) if a.as_of else dt.date.today())
        out["legacy_unconverted"] = legacy
        print(json.dumps(out, indent=1, sort_keys=True))
