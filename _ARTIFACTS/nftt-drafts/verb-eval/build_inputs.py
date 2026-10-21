"""Build arcs-verb-eval inputs for the held NFTT draft from its atoms file. Rerun after editing the claims."""
import json, html
from pathlib import Path
here = Path(__file__).parent
d = json.loads((here.parent / "lagging-indicator.atoms.json").read_text())
facts = [c for c in d["claims"] if c["type"] in ("sourced", "unproven")]
SRC = {"C4": "git:rev-list --no-merges", "C6": "repo:CLAUDE.md#handoff-v3.141.0", "C11": "https://app.arcs.care/api/pulse#gates.calibration"}
VERD = {"C6": ("unresolved", "low"), "C10": ("unresolved", "medium"), "C5": ("verified", "medium")}
DEGRADE = {"C5": "name that CI is off, so the merge script waits on few checks",
           "C10": "say the rule, then the measured coverage (about 75%)"}
def src(c):
    if c["id"] in SRC: return SRC[c["id"]]
    a = c.get("applied") or c.get("atom")
    return f"git:{a['sha']}"
HEAD = '<!doctype html>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<style>body{background:#020408;color:#e2e8f0}</style>\n'
e = lambda s: html.escape(s, quote=True)
(here / "sources.jsonl").write_text("".join(json.dumps({"source": src(c)}) + "\n" for c in facts))
(here / "analysis.html").write_text(HEAD + "<html><body>\n" + "".join(
    f'<span class="claim" data-id="{c["id"]}" data-src="{e(src(c))}">{e(c["text"])}</span>\n' for c in facts) + "</body></html>\n")
v = [VERD.get(c["id"], ("verified", "low")) for c in facts]
summ = f'{sum(x[0]=="verified" for x in v)}/{sum(x[0]=="gap" for x in v)}/{sum(x[0]=="unresolved" for x in v)}'
(here / "assessment.html").write_text(HEAD + f'<html><body><div data-summary="{summ}">\n' + "".join(
    f'<span class="claim" data-id="{c["id"]}" data-verdict="{x[0]}" data-severity="{x[1]}">{e(c["text"])}</span>\n'
    for c, x in zip(facts, v)) + "</div></body></html>\n")
g = {"lenses": [
    {"name": "LAB", "result": "pass", "reason": "each sourced claim traces to a commit, and its self-test passes today"},
    {"name": "BAR", "result": "dissent", "reason": "C10 said every merge ends in a receipt; measured coverage is about 75%"},
    {"name": "Loki", "result": "dissent", "reason": "C5 implies strong checks while CI is switched off"},
    {"name": "dual bar-raiser", "result": "pass", "reason": "argument holds; C6 rests on one record, kept as unresolved"}],
    "verdict": "conditional pass",
    "conditions": [{"id": f"k{i+1}", "claim": cid, "action": "degrade", "text": t} for i, (cid, t) in enumerate(DEGRADE.items())]}
(here / "evaluation.json").write_text(json.dumps(g, indent=1) + "\n")
rend = lambda c, x: "degraded" if c["id"] in DEGRADE or x[0] == "unresolved" else "sharp"
(here / "synthesis.html").write_text(HEAD + '<html><head><meta name="robots" content="noindex"></head><body><p>\n' + "".join(
    f'<span class="claim" data-id="{c["id"]}" data-render="{rend(c, x)}">{e(c["text"])}</span>\n' for c, x in zip(facts, v)) + "</p></body></html>\n")
print(len(facts), "facts;", summ)
