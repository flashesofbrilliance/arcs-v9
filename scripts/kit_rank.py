#!/usr/bin/env python3
"""kit_rank.py: three kit-assembly options for a job, as JSON. Advisory; never edits a page.

    python3 scripts/kit_rank.py <backlog row id | free text> [--shapes a,b] [--fid sharp,grain] [--top 3]
    python3 scripts/kit_rank.py --self-test

For each page template in src/ui-kit/templates.json that has two or more kit parts, pick up to 4 parts by
greedy cover of the shapes the job needs (shapes come from the text via kit_attract, or --shapes). Options
are then ordered by, in this order:
  1. shapes covered (more is better)
  2. fidelity gaps: needed states (--fid) that not every picked part renders (fewer is better)
  3. job links: backlog rows that already name the picked parts (more is better)
  4. gate results: mean static page_gate pass rate of the picked parts, from src/ui-kit/kit-gate-results.json
     (higher is better; parts with no data count as 0.5, so unknown never beats a measured pass)
Each option also lists the shapes and fidelity states it misses, and the one new kit file to write when a shape
is uncovered (rule O2). Stdlib only.
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_attract  # noqa: E402
import kit_pull  # noqa: E402

GATES = kit_pull.ROOT / "src/ui-kit/kit-gate-results.json"
UNKNOWN_RATE = 0.5


def load_gates():
    try:
        return json.loads(GATES.read_text()).get("parts", {})
    except (OSError, ValueError):
        return {}


def part_rate(pid, gates):
    r = gates.get(pid, {}).get("pass_rate")
    return UNKNOWN_RATE if r is None else r


def pick_for(ps, need, gates, limit=4):
    pool = sorted(ps, key=lambda p: (-len(p.get("jobs", [])), len(set(p["data_shape"]) - need), p["id"]))
    cov, pick = set(), []
    while len(pick) < limit and pool:
        def gain(p):
            return (len((set(p["data_shape"]) & need) - cov), -len(set(p["data_shape"]) - need), part_rate(p["id"], gates))
        best = max(pool, key=gain)
        if not (set(best["data_shape"]) & need) - cov:
            break
        pick.append(best)
        cov |= set(best["data_shape"]) & need
        pool.remove(best)
    pick.sort(key=lambda p: p["number"])
    return pick, cov


def options(manifest, need, fid_need, gates, top=3):
    kit = [p for p in manifest["parts"] if p["family"] == "kit"]
    by_t = collections.defaultdict(list)
    for p in kit:
        for t in p.get("templates", []):
            by_t[t].append(p)
    res = []
    for t in sorted(by_t):
        if len(by_t[t]) < 2:
            continue
        pick, cov = pick_for(by_t[t], need, gates)
        if not pick:
            continue
        fid = set.intersection(*[set(p.get("fidelity", [])) for p in pick])
        rates = [part_rate(p["id"], gates) for p in pick]
        res.append({
            "template": t, "parts": [p["id"] for p in pick], "covers": sorted(cov), "misses": sorted(need - cov),
            "fidelity_gaps": sorted(set(fid_need) - fid),
            "job_links": sum(len(p.get("jobs", [])) for p in pick),
            "gate_pass_rate": round(sum(rates) / len(rates), 3),
            "gate_measured": sum(1 for p in pick if gates.get(p["id"], {}).get("pass_rate") is not None),
        })
    res.sort(key=lambda o: (-len(o["covers"]), len(o["fidelity_gaps"]), -o["job_links"], -o["gate_pass_rate"], o["template"]))
    for i, o in enumerate(res[:top]):
        o["option"] = "ABC"[i] if i < 3 else str(i + 1)
    return res[:top]


def rank(arg, shapes=None, fid=None, top=3):
    manifest = json.loads(kit_pull.MANIFEST.read_text())
    row, text = kit_attract.job_text(arg)
    need = set(shapes) if shapes else set(kit_pull.shape_tags(text))
    gates = load_gates()
    opts = options(manifest, need, fid or [], gates, top)
    gap = sorted(need - set().union(*[set(o["covers"]) for o in opts])) if opts else sorted(need)
    return {"job": row or "free text", "needs": sorted(need), "needs_fidelity": sorted(fid or []),
            "options": opts, "uncovered": gap, "new_file": kit_attract.new_file(text, manifest, gap),
            "gate_results": bool(gates)}


def self_test():
    def part(i, shapes, tmpl, fid=("sharp",), jobs=()):
        return {"id": i, "number": i[:2], "family": "kit", "data_shape": list(shapes), "templates": [tmpl],
                "fidelity": list(fid), "jobs": list(jobs)}
    m = {"parts": [part("01-a", ["table"], "t1"), part("02-b", ["timeline"], "t1"),
                   part("03-c", ["table"], "t2"), part("04-d", ["timeline"], "t2"), part("05-e", ["delta"], "t3")]}
    need = {"table", "timeline"}
    # tie on coverage, fidelity and jobs: the better gate record wins
    gates = {"03-c": {"pass_rate": 1.0}, "04-d": {"pass_rate": 1.0}, "01-a": {"pass_rate": 0.0}, "02-b": {"pass_rate": 0.0}}
    o = options(m, need, [], gates)
    assert [x["template"] for x in o] == ["t2", "t1"] and o[0]["option"] == "A", o
    # job links beat gate results
    m["parts"][0]["jobs"] = ["row"]
    assert options(m, need, [], gates)[0]["template"] == "t1"
    # fewer fidelity gaps beat job links
    m["parts"][2]["fidelity"] = ["sharp", "grain"]
    m["parts"][3]["fidelity"] = ["sharp", "grain"]
    assert options(m, need, ["grain"], gates)[0]["template"] == "t2"
    # more coverage beats everything
    m["parts"][4]["data_shape"] = ["table", "timeline"]
    assert options(m, need, [], gates, 3) != [] and len(options(m, need, [], gates)) >= 2
    # unknown gate data never beats a measured pass
    assert part_rate("zz", {}) == UNKNOWN_RATE < 1.0
    # an uncoverable need returns no option, not a fake one
    assert options(m, {"graph"}, [], gates) == []
    print("kit_rank self-test ok")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()

    def opt(name):
        return argv[argv.index(name) + 1] if name in argv else None
    skip = {opt("--shapes"), opt("--fid"), opt("--top")} - {None}
    args = [a for a in argv if not a.startswith("--") and a not in skip]
    if not args:
        print(__doc__)
        return 2
    sh = opt("--shapes")
    fd = opt("--fid")
    out = rank(" ".join(args), sh.split(",") if sh else None, fd.split(",") if fd else None, int(opt("--top") or 3))
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
