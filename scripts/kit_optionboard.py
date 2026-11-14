#!/usr/bin/env python3
"""kit_optionboard.py: build the internal kit option board from kit_rank.py output. Advisory page; edits nothing else.

    python3 scripts/kit_optionboard.py [-o OUT.html] [--jobs jobs.json] [--thumbs DIR] [--lens lens.json]
    python3 scripts/kit_optionboard.py --self-test

Each job is {id, state, what, shapes, fid}; the default list is DEFAULT_JOBS below, or --jobs FILE. The options,
misses, fidelity gaps, job links and gate pass rates all come from kit_rank.rank, so the board and the CLI never
disagree. --thumbs is a folder of <part-id>.jpg renders (embedded as data URIs; parts without one show no image).
--lens is optional JSON {"imp": {part: findings}, "tok": {part: bool}} for the folksonomy filters; without it the
lens tags read "not measured". Template: scripts/kit_optionboard.tpl.html. Stdlib only.
"""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_pull  # noqa: E402
import kit_rank  # noqa: E402

ROOT = kit_pull.ROOT
TPL = ROOT / "scripts/kit_optionboard.tpl.html"
OUT = ROOT / "_ARTIFACTS/kit-option-board.html"
DEFAULT_JOBS = [
    {"id": "hud-high-signal-field", "state": "OPEN", "what": "A HUD that shows the highest-signal field at altitude",
     "shapes": ["graph", "timeline", "state", "fidelity", "scalar", "sequence"], "fid": ["grain", "moire", "degraded", "sharp"]},
    {"id": "unified-design-system-receipts-reports", "state": "OPEN", "what": "Receipts and reports on one design grammar",
     "shapes": ["table", "evidence", "delta", "label", "note", "state"], "fid": ["sharp", "degraded"]},
    {"id": "arcs-mini-adopt-design-md-motion", "state": "READY", "what": "Adopt the motion tokens in a small instrument",
     "shapes": ["state", "control", "fidelity", "percent"], "fid": ["sharp", "degraded"]},
]


def lens_tags(p, lens):
    t = {}
    t["composer"] = "molecule" if p["group"] == "Molecules" else ("organism" if p["group"] in ("Recoil Report", "Instrument Lab") else "specimen")
    t["conductor"] = "sets order" if set(p["data_shape"]) & {"sequence", "timeline"} else "holds still"
    t["skeptic"] = "shows its basis" if set(p["data_shape"]) & {"evidence", "delta", "fidelity"} else "asserts"
    if lens and p["id"] in lens.get("imp", {}):
        n = lens["imp"][p["id"]]
        t["impeccable"] = "clean" if n == 0 else "%d findings" % n
    else:
        t["impeccable"] = "not measured"
    if lens and p["id"] in lens.get("tok", {}):
        t["brand"] = "token gate pass" if lens["tok"][p["id"]] else "token gate fail"
    else:
        t["brand"] = "not measured"
    return t


def thumb(pid, thumbs):
    f = Path(thumbs) / f"{pid}.jpg" if thumbs else None
    if f and f.is_file():
        return "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
    return ""


def recuts(job, ranked, manifest):
    """Where the best option leaves a shape or fidelity state uncovered, name the donor part and the gap."""
    out = []
    if not ranked:
        return out
    a = ranked[0]
    parts = {p["id"]: p for p in manifest["parts"]}
    kit = [p for p in manifest["parts"] if p["family"] == "kit"]
    for s in a["misses"][:2]:
        near = [p for p in kit if s in p["data_shape"]]
        out.append({"kind": "shape", "shape": s, "near": near[0]["id"] if near else None,
                    "near_n": near[0]["name"] if near else None, "tmpl": a["template"]})
    for fs in a["fidelity_gaps"][:1]:
        lack = [pid for pid in a["parts"] if fs not in parts[pid].get("fidelity", [])]
        if lack:
            out.append({"kind": "fidelity", "state": fs, "part": lack[0], "part_n": parts[lack[0]]["name"], "tmpl": a["template"]})
    return out


def payload(jobs, thumbs=None, lens=None):
    manifest = json.loads(kit_pull.MANIFEST.read_text())
    kit = [p for p in manifest["parts"] if p["family"] == "kit"]
    data = [{"id": p["id"], "n": p["name"], "g": p["group"], "sub": p["subtitle"], "sh": p["data_shape"],
             "fi": p["fidelity"], "tp": p.get("templates", []), "jobs": len(p.get("jobs", [])),
             "img": thumb(p["id"], thumbs), "lens": lens_tags(p, lens)} for p in kit]
    out = []
    for j in jobs:
        r = kit_rank.rank(j["id"] + " " + j["what"], shapes=j["shapes"], fid=j["fid"])
        out.append({**j, "options": r["options"], "recut": recuts(j, r["options"], manifest), "ranker_new_file": r["new_file"]})
    return {"parts": data, "jobs": out, "shapes": manifest["shape_vocabulary"]}


def build(jobs, thumbs=None, lens=None):
    pay = json.dumps(payload(jobs, thumbs, lens), separators=(",", ":"))
    return TPL.read_text().replace("/*__DATA__*/null", pay)


def self_test():
    jobs = [{"id": "t", "state": "OPEN", "what": "x", "shapes": ["table", "timeline"], "fid": ["sharp"]}]
    page = build(jobs)
    assert "/*__DATA__*/" not in page and '"options"' in page
    p = payload(jobs)
    o = p["jobs"][0]["options"]
    assert o and {"template", "covers", "misses", "fidelity_gaps", "job_links", "gate_pass_rate"} <= set(o[0])
    assert all(x["lens"]["impeccable"] == "not measured" for x in p["parts"]), "no lens file means not measured, never clean"
    assert all(x["img"] == "" for x in p["parts"])
    assert "—" not in TPL.read_text(), "em-dash in template"
    print("kit_optionboard self-test ok")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()

    def opt(n):
        return argv[argv.index(n) + 1] if n in argv else None
    jobs = json.loads(Path(opt("--jobs")).read_text()) if opt("--jobs") else DEFAULT_JOBS
    lens = json.loads(Path(opt("--lens")).read_text()) if opt("--lens") else None
    out = Path(opt("-o") or OUT)
    out.write_text(build(jobs, opt("--thumbs"), lens))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
