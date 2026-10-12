#!/usr/bin/env python3
"""decision_geometry_ret.py: score the RET take-home DECISIONS.md on the 5x5 decision geometry.

Spec: runtime/specs/decision-geometry-cells-v0.json (aspects D R W C H, levels L0 to L5,
shape_vector_spec collapse to a 5-digit DRWCH code in the 5^5 = 3125 space).

The spec's level rules are written against compass Receipt columns. DECISIONS.md is prose, so
each cell here uses a TEXT ADAPTATION of its rule (listed in ADAPTATION below and on the page).
Rules are mechanical: a regex hit quotes the matching sentence as evidence; no hit means L0
(tilde), never a guess. L5 is never reached from DECISIONS.md alone (no outcome record).

Read-only on the source repo (single writer). Stdlib only.

  python3 scripts/decision_geometry_ret.py [--src PATH] [--check]
Writes _ARTIFACTS/decision-geometry/ret-decisions.json and decision-geometry.html.
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "runtime/specs/decision-geometry-cells-v0.json"
TOKENS = ROOT / "src/ui-kit/recoil-report/_tokens.css"
TEMPLATE = ROOT / "scripts/templates/decision-geometry.template.html"
OUT_DIR = ROOT / "_ARTIFACTS/decision-geometry"
DEFAULT_SRC = Path("/Users/zharris/ret-rfp-intelligence/DECISIONS.md")

FIELD_RE = re.compile(r"\*\*(Decision|Why|Rejected|Revisit when|What changes[^*]*?)\.?\*\*", re.I)


def parse(md):
    """Split DECISIONS.md into records; bold field labels become keys, text before any label is Body."""
    out = []
    for block in re.split(r"^## ", md, flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        did, _, title = head.partition(":")
        pieces = FIELD_RE.split(body)
        fields = {"Body": pieces[0]}
        for name, text in zip(pieces[1::2], pieces[2::2]):
            fields[name.rstrip(".").title()] = text
        fields = {k: re.sub(r"\s+", " ", v).strip() for k, v in fields.items() if v.strip()}
        out.append({"id": did.strip(), "title": title.strip(), "fields": fields})
    return out


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(`])", text) if s.strip()]


def find(fields, keys, pattern, flags=re.I):
    """First sentence in the named fields matching pattern -> 'Field: sentence', else None."""
    rx = re.compile(pattern, flags)
    for k in keys:
        for s in sentences(fields.get(k, "")):
            if rx.search(s):
                return f"{k}: {s}"
    return None


ALL = ["Decision", "Why", "Rejected", "Revisit When", "Body", "What Changes At 600 Pages, In Order Of Risk"]

# (cell id, [(level, fields, regex, rule text)]) evaluated top-down; first hit wins.
ADAPTATION = {
    "D1": [(2, ["Decision"], r".", "a **Decision.** paragraph states the choice"),
           (1, ["Body"], r".", "unstructured record: the choice is inferred from the prose")],
    "D2": [(4, ["Why"], r"\((B|C)\b|[Mm]easured", "Why cites a measured (B) or primary-source (C) grade"),
           (3, ["Why"], r"\([A-E](:|\))|\b[A-E]: ", "Why carries an A-E source grade"),
           (2, ["Why"], r".", "a **Why.** paragraph gives reasons"),
           (1, ["Body"], r"\b(because|so|keeps|stays)\b", "a reason appears in unstructured prose")],
    "D3": [(2, ["Revisit When"], r".", "Rejected alternatives plus a revisit trigger (the meta-question) both present; needs Rejected too"),
           (1, ["Rejected"], r".", "a **Rejected.** paragraph names at least one alternative")],
    "D4": [(2, ALL, r"[Nn]ever for this repo|force|one-way|rewrite|until .*submitted|lossless|backup", "an approver is named AND a reversibility signal is stated; needs approver too"),
           (1, ALL, r"Zach (approved|chose|accepted|'s choice)|\(Zach, 20", "an approver is named (Zach)")],
    "D5": [(2, ALL, r"\b(K\d+|BR\d|BR-P\d|D-[A-Z0-9-]+|H\d|W\d+|Q\d|T\d|S\d)\b", "cites another logged id (mistake K, review BR, decision D, case, hypothesis): thread position stated")],
    "R1": [(2, ALL, r"\$\d|\d+%|\d+(\.\d+)? ?MB|\d+x\b", "a quantified stake ($, %, MB, multiple)"),
           (1, ALL, r"\b(cost|risk|grade|over-built|spend)\b", "stakes named in words only")],
    "R2": [(2, ALL, r"bar-raiser|reviewer|gauntlet|reviewed against|panel", "a named review or court (bar-raiser, reviewer, gauntlet, panel)")],
    "R3": [(2, ["Rejected"], r"\b(but|[Cc]heaper|[Gg]ood for|[Ee]asy to)\b", "Rejected steelmans the alternative before refusing it (the strongest objection stated)"),
           (1, ["Why", "Decision"], r"\brisk\b", "a risk is named with no stated objection")],
    "R4": [(2, ALL, r"[Nn]ever|backup|lossless|stays in|force|cannot drift|no duplicates", "reversibility stated explicitly (backup, lossless, never, idempotent)"),
           (1, ALL, r"\b(cut|remove|ship|rewrite)\b", "reversibility inferred from the action verb")],
    "R5": [(3, ALL, r"\bK\d+\b.*\b(test|seam|case|W\d+)\b|\b(test|seam|case)\b.*\bK\d+\b", "a logged mistake (K) AND the test or case that guards it"),
           (2, ALL, r"\bK\d+\b", "cites a logged mistake (KINTSUGI K id)")],
    "W1": [(2, ALL, r"20\d\d-\d\d-\d\d|Thursday|until submission|before Thursday|after (the dress )?rehearsal", "a dated or deadline-bounded window")],
    "W2": [(2, ["Revisit When"], r".", "a Revisit trigger: the window is CONDITIONAL (CLOSED when it says Never)")],
    "W3": [(2, ["Revisit When"], r"\d|passes|runs|asks|finds|grows|cites", "the Revisit trigger is an observable entry condition")],
    "W4": [(2, ["Rejected"], r".", "two or more headings: the chosen line plus a rejected one"),
           (1, ["Decision", "Body"], r".", "one heading only (no rejected line recorded)")],
    "W5": [(2, ALL, r"grew from|went from|once more|regressed|now |became|had become|before\b", "a change over time is recorded (trajectory)")],
    "C1": [(1, ["Decision"], r".", "clarity inferred: a Decision paragraph exists (no clarity score in the source)")],
    "C2": [(1, ALL, r"\([A-E](:|\)|,)|\b[A-E]: |measured", "conviction inferred from an A-E source grade or measurement")],
    "C3": [(1, ["Why"], r".", "coherence inferred: a Why paragraph exists (no coherence score)")],
    "C4": [(1, ["Rejected"], r"\b(cost|adds?|drops?|removes?|hides?|harder|duplicate)\b", "consequence inferred from tradeoff prose in Rejected")],
    "C5": [(1, ["Revisit When"], r".", "cadence inferred: a revisit timing exists")],
    "H1": [(1, ALL, r"[Nn]ever for this repo|next client|second client|next one", "implied Executive: a one-way, cross-engagement consequence")],
    "H2": [(1, ALL, r"\b(scope|brand|story|panel|grade|positioning|next step)\b", "implied Strategic: scope, story or panel-grade framing")],
    "H3": [(1, ALL, r"\b(rehearsal|plan|release|gate|submission|package|process)\b", "implied Operational: plan, release or gate process")],
    "H4": [(1, ALL, r"\b(SDK|API|GraphQL|SVG|PDF|MCP|Mermaid|LangGraph|Playground|Docling|ZIP)\b", "implied Tactical: a named tool or format choice")],
    "H5": [(1, ALL, r"`[^`]+`|\.py\b|\.jsonl\b|test_", "implied Surgical: a named file, command or test")],
}


def score_cell(cid, fields):
    for level, keys, pat, rule in ADAPTATION[cid]:
        ev = find(fields, keys, pat)
        if not ev:
            continue
        if cid == "D3" and level == 2 and "Rejected" not in fields:
            continue
        if cid == "D4" and level == 2 and not find(fields, ALL, ADAPTATION["D4"][1][2]):
            continue
        if cid == "W2":
            tok = "CLOSED" if re.search(r"^Never", fields["Revisit When"]) else "CONDITIONAL"
            ev = f"[{tok}] {ev}"
        return {"level": level, "evidence": ev, "rule": rule}
    return {"level": 0, "evidence": None, "rule": "no matching text: tilde (unknown), not guessed"}


def collapse(levels):
    """shape_vector_spec: 3+ tilde cells -> 1; else median of non-tilde, lower middle; floor 1."""
    if sum(1 for l in levels if l == 0) >= 3:
        return 1
    nz = sorted(l for l in levels if l > 0)
    return max(1, nz[(len(nz) - 1) // 2])


def build(src):
    spec = json.loads(SPEC.read_text())
    aspects = [{"key": a["key"], "label": a["label"],
                "cells": [{"id": c["id"], "label": c["label"], "spec_rule": c["level_rule"]} for c in a["cells"]]}
               for a in spec["aspects"]]
    rungs = [c["label"].split(" rung")[0] for c in spec["aspects"][4]["cells"]]
    decisions = []
    for d in parse(src.read_text()):
        cells = {c["id"]: score_cell(c["id"], d["fields"]) for a in aspects for c in a["cells"]}
        digits = [collapse([cells[c["id"]]["level"] for c in a["cells"]]) for a in aspects]
        index = sum((v - 1) * 5 ** (4 - i) for i, v in enumerate(digits))
        occupied = [rungs[i] for i in range(5) if cells[f"H{i+1}"]["level"] > 0]
        decisions.append({"id": d["id"], "title": d["title"], "fields": d["fields"], "cells": cells,
                          "shape": "".join(map(str, digits)), "index": index, "rungs": occupied})
    return {"_meta": {"spec": str(SPEC.relative_to(ROOT)), "spec_version": spec["_meta"]["version"],
                      "source": "ret-rfp-intelligence/DECISIONS.md (read-only)",
                      "generator": "scripts/decision_geometry_ret.py",
                      "note": "Text adaptation of the spec's Receipt-column rules; see adaptation. L0 = tilde. No L5 is reachable from DECISIONS.md."},
            "aspects": aspects, "rungs": rungs,
            "adaptation": {k: [{"level": l, "rule": r} for l, _, _, r in v] for k, v in ADAPTATION.items()},
            "decisions": decisions}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--check", action="store_true", help="fail if any non-L0 cell lacks evidence")
    a = ap.parse_args()
    data = build(a.src)
    bad = [(d["id"], c) for d in data["decisions"] for c, v in d["cells"].items() if v["level"] and not v["evidence"]]
    if bad:
        print("FAIL: levels without evidence:", bad); sys.exit(1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(data, indent=1, ensure_ascii=False)
    (OUT_DIR / "ret-decisions.json").write_text(blob + "\n")
    html = TEMPLATE.read_text().replace("/*__TOKENS__*/", TOKENS.read_text()).replace(
        "__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (OUT_DIR / "decision-geometry.html").write_text(html)
    for d in data["decisions"]:
        print(f"{d['shape']}  #{d['index']:>4}  {d['id']:<12} rungs={d['rungs']}")
    if a.check:
        print("check: every non-L0 cell cites evidence")


if __name__ == "__main__":
    main()
