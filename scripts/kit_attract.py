#!/usr/bin/env python3
"""kit_attract.py: advisory lookup, which kit parts a job attracts. Read-only; never edits a page.

    python3 scripts/kit_attract.py <backlog row id | free text> [--top N] [--json]
    python3 scripts/kit_attract.py --self-test

Matches the job's text (a backlog row's id, jtbd, status_note and route, or the free text) to the manifest's
part names, subtitles and data_shape (the 13-term vocabulary in kit_pull.SHAPE_WORDS). Prints the nearest
parts, the shapes the job needs, the shapes no near part covers, and, when something is uncovered, the one
new kit file to write (rule O2: write one kit file for the gap, do not fork a page). Stdlib only.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_pull  # noqa: E402

ROOT = kit_pull.ROOT
STOP = set("the a an and or of to for in on with is are be it this that as at by from not no into per".split())


def words(text):
    return {w for w in re.findall(r"[a-z][a-z0-9]{2,}", text.lower()) if w not in STOP}


def job_text(arg):
    """A backlog row id resolves to the row's own text; anything else is free text."""
    for line in kit_pull.read(kit_pull.BACKLOG).splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("id") == arg:
            route = json.dumps(r.get("route", {}))
            return r["id"], " ".join([r["id"].replace("-", " "), r.get("jtbd", ""), r.get("status_note", ""), route])
    return None, arg


def rank(text, manifest, top=5):
    need = set(kit_pull.shape_tags(text))
    tw = words(text)
    rows = []
    for p in manifest["parts"]:
        shapes = set(p.get("data_shape", []))
        hit = need & shapes
        fit = len(hit) / len(need) if need else 0.0
        pw = words(p["name"] + " " + p.get("subtitle", ""))
        lex = len(tw & pw) / len(pw) if pw else 0.0
        score = round(0.6 * fit + 0.4 * lex, 3)
        if score > 0:
            rows.append({"id": p["id"], "name": p["name"], "family": p["family"], "score": score,
                         "shapes_hit": sorted(hit), "words_hit": sorted(tw & pw), "jobs": len(p.get("jobs", [])),
                         "templates": p.get("templates", [])})
    rows.sort(key=lambda r: (-r["score"], r["id"]))
    near = rows[:top]
    covered = set()
    for r in near:
        covered |= set(r["shapes_hit"])
    gap = sorted(need - covered)
    return need, near, gap


def new_file(text, manifest, gap):
    if not gap:
        return None
    nums = [int(p["number"]) for p in manifest["parts"] if p["family"] == "kit" and str(p["number"]).isdigit()]
    n = max(nums) + 1
    slug = "-".join(sorted(words(text))[:3]) or "new-part"
    return {"path": f"src/ui-kit/recoil-report/{n:02d}-{slug}.html", "renders": gap,
            "then": "python3 scripts/kit_pull.py manifest"}


def run(arg, top=5):
    manifest = json.loads(kit_pull.MANIFEST.read_text())
    row, text = job_text(arg)
    need, near, gap = rank(text, manifest, top)
    return {"job": row or "free text", "needs": sorted(need), "nearest": near, "uncovered": gap,
            "new_file": new_file(text, manifest, gap)}


def show(o):
    print(f"job: {o['job']}\nneeds shapes: {', '.join(o['needs']) or '(none inferred)'}")
    for r in o["nearest"]:
        print(f"  {r['score']:.3f}  {r['id']:<34} shapes {','.join(r['shapes_hit']) or '-'}  words {','.join(r['words_hit']) or '-'}  jobs {r['jobs']}")
    if not o["nearest"]:
        print("  no part attracted")
    if not o["needs"]:
        print("no data shape inferred from the job text; matches above are word overlap only. Add what it must render (table, timeline, gauge...) for a real answer.")
    print(f"uncovered shapes: {', '.join(o['uncovered']) or 'none'}")
    nf = o["new_file"]
    print(f"new kit file (rule O2): {nf['path']} renders {', '.join(nf['renders'])}" if nf else "new kit file: none needed")


def self_test():
    m = {"parts": [
        {"id": "01-gauge", "number": "01", "name": "Gauge", "subtitle": "scalar readout", "family": "kit", "data_shape": ["scalar"], "jobs": []},
        {"id": "02-ledger", "number": "02", "name": "Ledger", "subtitle": "table of receipts", "family": "kit", "data_shape": ["table", "evidence"], "jobs": ["x"]}]}
    need, near, gap = rank("a ledger table of receipts", m)
    assert near[0]["id"] == "02-ledger" and not gap, (near, gap)
    need, near, gap = rank("show a timeline scrub", m)
    assert gap == ["timeline"] and new_file("show a timeline scrub", m, gap)["path"].startswith("src/ui-kit/recoil-report/03-")
    need, near, gap = rank("zzz", m)
    assert not near
    o = run("kit-wire-attract")
    assert o["job"] == "kit-wire-attract"
    print("kit_attract self-test ok")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    args = [a for a in argv if not a.startswith("--")]
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 5
    args = [a for a in args if not (a.isdigit() and "--top" in argv)]
    if not args:
        print(__doc__)
        return 2
    o = run(" ".join(args), top)
    print(json.dumps(o, indent=2)) if "--json" in argv else show(o)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
