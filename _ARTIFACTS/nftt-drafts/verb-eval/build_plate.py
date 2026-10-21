"""Build the five-sheet acetate plate for the held NFTT draft.

1. Anchors every claim in the post: <span class="cl" data-claim="Cn" data-n="n">. Facts (sourced or
   unproven) also carry class="claim" data-id data-render, so arcs-verb-eval synthesis runs on the
   post itself rather than on a derived list.
2. Reads the atoms file and the stage prints (p/*.json) and embeds them as PLATE data in the post.
3. Enforces the invariant: a lower sheet can never contradict a higher one. Any failing self-test
   or stopped stage forces the Exec stamp to STOP; unresolved claims or unscored judgment cap it at HOLD.

usage: python3 build_plate.py [--check]   (--check: exit 1 if an anchor is missing or the invariant breaks)
Rerun after build_inputs.py and the verb-eval steps.
"""
import json, re, sys, html
from pathlib import Path

here = Path(__file__).parent
post = here.parent / "blog-nftt-the-lagging-indicator.html"
atoms = json.loads((here.parent / "lagging-indicator.atoms.json").read_text())

ANCHOR = {
    "C1": "if you treat a lagging indicator as a leading one, you steer by the wake.",
    "C2": "The round reports it faithfully, the way closed revenue does.",
    "C3": "When an agent writes two hundred lines in a minute, someone has to know whether those lines are right.",
    "C4": "a few thousand commits",
    "C5": "Merges go through a script that pins the exact commit being merged and refuses if any check is still pending or failing.",
    "C6": "It has refused me twice when a branch moved under me",
    "C7": "a model name typed by hand",
    "C8": "a file moved while something still points to the old path",
    "C9": "a page whose text wraps badly at some screen width",
    "C10": "The ledger refuses edits; a correction is a new row that names the old one.",
    "C11": "What is not yet proven: whether these receipts make my calls better over time.",
    "C12": "Faking both at once is much harder than gaming either one alone.",
    "C13": "Finding them was the test.",
}
ROLE = {"I": "Thesis", "II": "Steelman", "III": "Leading indicators", "IV": "Receipts", "V": "Proposed gate", "VI": "Close"}
STAGES = ["analysis", "assessment", "evaluation", "synthesis"]
STOPS = {"unsourced", "fail", "hold", "blocked"}


def load_prints():
    out = {}
    for s in STAGES:
        f = here / "p" / f"{s}.json"
        out[s] = json.loads(f.read_text()) if f.exists() else None
    return out


def main(argv):
    problems = []
    t = post.read_text()
    prints = load_prints()
    syn_render = {}
    if (here / "synthesis.html").exists():
        syn_render = dict(re.findall(r'data-id="(C\d+)" data-render="(\w+)"', (here / "synthesis.html").read_text()))
    ids = [c["id"] for c in atoms["claims"]]
    for n, c in enumerate(atoms["claims"], 1):
        if f'data-claim="{c["id"]}"' in t:
            continue
        a = ANCHOR[c["id"]]
        if a not in t:
            problems.append(f"{c['id']}: anchor text not found in post")
            continue
        fact = c["type"] in ("sourced", "unproven")
        extra = f' class="cl claim" data-id="{c["id"]}" data-render="{syn_render.get(c["id"], "sharp")}"' if fact else ' class="cl"'
        t = t.replace(a, f'<span{extra} data-claim="{c["id"]}" data-n="{n}" data-type="{c["type"]}">{a}</span>', 1)

    # verdicts and dissent from the prints' inputs
    assess = dict((m[0], (m[1], m[2])) for m in re.findall(
        r'data-id="(C\d+)" data-verdict="(\w+)" data-severity="(\w+)"', (here / "assessment.html").read_text()))
    gaunt = json.loads((here / "evaluation.json").read_text())
    dissent = {}
    for k in gaunt.get("conditions", []):
        dissent.setdefault(k["claim"], []).append(k["text"])
    lenses = gaunt["lenses"]

    claims = []
    for n, c in enumerate(atoms["claims"], 1):
        v = assess.get(c["id"])
        claims.append({k: c.get(k) for k in ("id", "section", "type", "text", "file", "atom", "applied", "excerpt",
                                             "selftest_result", "asset", "liability", "evidence", "measured")}
                      | {"n": n, "verdict": v[0] if v else None, "severity": v[1] if v else None,
                         "render": syn_render.get(c["id"]), "dissent": dissent.get(c["id"], [])})

    fates = {s: (p or {}).get("fate") for s, p in prints.items()}
    judged = sum(1 for p in prints.values() if p for r in p.get("judgment", []) if isinstance(r, dict) and r.get("score") is not None)
    facts = [c for c in claims if c["type"] in ("sourced", "unproven")]
    verified = sum(c["verdict"] == "verified" for c in facts)
    unresolved = sum(c["verdict"] == "unresolved" for c in facts)
    failing = [c["id"] for c in claims if c.get("selftest_result") == "FAIL"]
    if failing or any(f in STOPS or f is None for f in fates.values()):
        stamp, why = "STOP", "a self-test failed or a stage stopped" if failing else "a stage stopped or did not run"
    elif unresolved or not judged or fates.get("evaluation") == "conditional pass":
        stamp, why = "HOLD", f"{unresolved} claims unresolved, conditional pass, human scorecard not filled"
    else:
        stamp, why = "GO", "every stage passed and the scorecard is filled"

    plate = {"exec": {"stamp": stamp, "why": why, "held": verified, "of": len(facts), "unresolved": unresolved,
                      "judged": judged, "status": "Held draft: not indexed, not routed"},
             "stages": [{"step": s, "fate": fates[s]} for s in STAGES] + [{"step": "recapitulation", "fate": "n/a, no note for a held post"}],
             "lenses": lenses, "roles": ROLE, "claims": claims}
    # invariant: exec can never read GO if anything below it says otherwise
    if stamp == "GO" and (failing or unresolved):
        problems.append("invariant broken: Exec says GO over a failing or unresolved claim")
    blob = json.dumps(plate, ensure_ascii=False).replace("</", "<\\/").replace("—", "--")
    block = f'<script type="application/json" id="plate-data">{blob}</script>'
    t = re.sub(r'<script type="application/json" id="plate-data">.*?</script>', lambda m: block, t, flags=re.S) \
        if 'id="plate-data"' in t else t.replace("</html>", block + "\n</html>")
    post.write_text(t)
    print(f"Exec {stamp}: {verified}/{len(facts)} held, {unresolved} unresolved, judged {judged}; stages {fates}")
    for p in problems:
        print("PROBLEM", p)
    return 1 if ("--check" in argv and problems) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
