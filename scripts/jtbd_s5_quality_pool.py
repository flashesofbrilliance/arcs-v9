#!/usr/bin/env python3
"""Prepare the JTBD s5 quality rerun pool and score it (EARLY/INTERIM run, started 2026-11-01).

Rules: _PATTERNS/2026-10-20-jtbd-s5-preregistration.md (Tests, Quality) and amendment 7.
Pass rule is fixed there: graph passes >= 16 of 18 and mean essential recall >= 0.89.

  pool   Build pool-sealed.json, pool-key.json (sealed key) and JUDGE.md from the raw assemblies in
         runtime/specs/jtbd-s5-quality/. Reuses scripts/jtbd_s4_pool.py's resolver, shuffle seed
         (random.Random(20261020 + row) over the sorted union) and leak check.
  score  Read the filled JUDGE.md (E/U/W after each arrow, optional Missing line) plus the key and print
         pass count and mean essential recall per system against the thresholds. Opens the key.
  --self-test  Re-scores the committed s4 marks and must reproduce graph 16/18, recall 0.89, catalog 6/18.
Stdlib only.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jtbd_s4_pool as s4

ROOT = s4.ROOT
D5 = ROOT / "runtime/specs/jtbd-s5-quality"
D4 = ROOT / "runtime/specs/jtbd-s4"
PASS_N, RECALL = 16, 0.89
SYSTEMS = {"graph", "catalog"}
LABEL = "EARLY/INTERIM (day 12 of 28); informs, does not replace the official check dated 2026-11-17"


def judge_md(sealed):
    L = ["# JTBD s5 quality rerun judging sheet (blind)", "",
         "For each item write **E** (essential: the job fails without it), **U** (useful) or **W** (wrong) "
         "after the arrow. Optionally name a missing essential piece on the `Missing:` line. "
         "Item order is random per job.", ""]
    for r in sealed:
        L += [f"## Job {r['row']}: {r['job']}", ""]
        for i, it in enumerate(r["items"], 1):
            d = f": {it['description']}" if it["description"] else ""
            L.append(f"{i}. `{it['name']}`{d}  ->  ")
        L += ["", "Missing: ", ""]
    return "\n".join(L)


def build_source_mapping(raws):
    return [{"row": r["row"], "item": it, "from": r["system"]}
            for raw in raws for r in raw["rows"] for it in r["assembly"]]


def cmd_pool():
    queries = s4.load(D5 / "queries-rows-1-18.json")
    raws = [s4.load(D5 / "graph-raw.json"), s4.load(D5 / "catalog-raw.json")]
    sealed, key = s4.build(queries, raws, s4.resolver())
    md = judge_md(sealed)
    found = s4.leaks(sealed, md, SYSTEMS)
    if found:
        sys.exit("LEAK: " + "; ".join(found))
    (D5 / "source-mapping.json").write_text(json.dumps(
        {"note": f"{LABEL}. Keep out of anything a judge sees.", "map": build_source_mapping(raws)}, indent=1) + "\n")
    (D5 / "pool-sealed.json").write_text(json.dumps(
        {"label": LABEL, "rule": "amendment 7 rule 3", "seed": f"random.Random({s4.SEED} + row) over sorted union",
         "rows": sealed}, indent=1) + "\n")
    (D5 / "pool-key.json").write_text(json.dumps(
        {"label": LABEL, "note": "SEALED KEY: id -> system. Never show to the judge; open only after marks are in.",
         "rows": key}, indent=1) + "\n")
    (D5 / "JUDGE.md").write_text(md)
    print("wrote source-mapping.json, pool-sealed.json, pool-key.json, JUDGE.md;",
          sum(len(r["items"]) for r in sealed), "items, 0 leaks")


def parse_judge(md, sealed):
    """Return {row: ({item_id: mark}, missing_text)} from a filled JUDGE.md."""
    out, cur, idx = {}, None, 0
    by = {r["row"]: r for r in sealed}
    for ln in md.splitlines():
        m = re.match(r"## Job (\d+):", ln)
        if m:
            cur, idx = int(m.group(1)), 0
            out[cur] = ({}, "")
            continue
        m = re.match(r"\d+\. .*->\s*(\S*)\s*$", ln)
        if m and cur:
            mark = m.group(1).upper()
            if mark not in ("E", "U", "W"):
                sys.exit(f"row {cur} item {idx + 1}: mark {m.group(1)!r} is not E, U or W")
            out[cur][0][by[cur]["items"][idx]["id"]] = mark
            idx += 1
        elif ln.startswith("Missing:") and cur:
            out[cur] = (out[cur][0], ln[8:].strip())
    for row, (marks, _) in out.items():
        if len(marks) != len(by[row]["items"]):
            sys.exit(f"row {row}: {len(marks)} marks for {len(by[row]['items'])} items")
    if set(out) != set(by):
        sys.exit("rows missing from JUDGE.md: " + str(sorted(set(by) - set(out))))
    return out


def score(marks_by_row, key_rows):
    res = {s: {"rows": []} for s in sorted(SYSTEMS)}
    missing = 0
    for kr in key_rows:
        marks, miss = marks_by_row[kr["row"]]
        if miss:
            missing += 1
        ess = [i for i, m in marks.items() if m == "E"]
        for s in res:
            mine = [i for i, owners in kr["items"].items() if s in owners]
            e = [i for i in mine if marks[i] == "E"]
            w = [i for i in mine if marks[i] == "W"]
            res[s]["rows"].append({
                "row": kr["row"], "marks": "".join(marks[i] for i in mine),
                "pass": bool(e) and len(w) <= len(mine) // 2,
                "essential_recall": round(len(e) / len(ess), 3) if ess else None})
    for s, v in res.items():
        v["pass"] = sum(r["pass"] for r in v["rows"])
        rec = [r["essential_recall"] for r in v["rows"] if r["essential_recall"] is not None]
        v["mean_essential_recall"] = round(sum(rec) / len(rec), 2) if rec else None
    res["rows_with_missing_essential"] = missing
    return res


def verdict(res):
    g, c = res["graph"], res["catalog"]
    ok = g["pass"] >= PASS_N and (g["mean_essential_recall"] or 0) >= RECALL
    return {"label": LABEL, "thresholds": f"graph pass >= {PASS_N}/18 AND mean essential recall >= {RECALL}",
            "graph": f"{g['pass']}/18, recall {g['mean_essential_recall']}",
            "catalog": f"{c['pass']}/18, recall {c['mean_essential_recall']}",
            "verdict": "HOLDS" if ok else "BELOW THRESHOLD (weights reset to 1.0 and rule revisited by amendment, per prereg; interim run only)"}


def cmd_score(judged_md):
    d = D5
    sealed = s4.load(d / "pool-sealed.json")["rows"]
    key = s4.load(d / "pool-key.json")["rows"]
    marks = parse_judge(Path(judged_md).read_text(), sealed)
    res = score(marks, key)
    res["verdict"] = verdict(res)
    (d / "score.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res["verdict"], indent=1))


def self_test():
    m = s4.load(D4 / "marks.json")
    key = s4.load(D4 / "pool-key.json")["rows"]
    marks = {r["row"]: ({i["id"]: i["mark"] for i in r["items"]}, "") for r in m["rows"]}
    res = score(marks, key)
    g, c = res["graph"], res["catalog"]
    assert (g["pass"], g["mean_essential_recall"], c["pass"]) == (16, 0.89, 6), (g["pass"], g["mean_essential_recall"], c["pass"])
    # Fails on bad: a sheet with a stray mark must be rejected by the parser.
    sealed = s4.load(D4 / "pool-sealed.json")["rows"]
    try:
        parse_judge(judge_md(sealed).replace("->  ", "->  X", 1), sealed)
        raise AssertionError("bad mark not caught")
    except SystemExit:
        pass
    print("self-test OK: s4 marks reproduce graph 16/18 recall 0.89, catalog 6/18; bad mark rejected")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--self-test"]:
        self_test()
    elif a[:1] == ["pool"]:
        cmd_pool()
    elif a[:1] == ["score"] and len(a) == 2:
        cmd_score(a[1])
    else:
        sys.exit(__doc__)
