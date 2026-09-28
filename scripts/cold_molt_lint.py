#!/usr/bin/env python3
"""
cold_molt_lint.py — is this chip prompt FLAWLESS (self-contained for a 100% lossless
translation into a COLD session) or UNCUT (it leaks the parent's RAM)?

Definition (Zach, 2026-09-27): flawless == self-contained for 100% lossless translation for
cold molt. A cold molt is a receiving session with NONE of the parent's RAM: no transcript, no
scratchpad, no "as we discussed". It gets the chip prompt + the committed repo, nothing else.
Lossless is bounded the way the diamond cut is: lossless w.r.t. the invariants (the ridgeline),
lossy by design w.r.t. the occlusion.

Four mechanical checks (all greps; the real test is spawning the chip and watching whether its
first tool call is an ACTION (lossless) or a RE-DERIVATION (it leaked)):
  1. session-relative references  "earlier", "above", "as we said/discussed", "the doc", "this
                                   session", "the other session", "you mentioned", "recall that",
                                   scratchpad or gitignored paths, bare "it"/"that one" openers
  2. Step 3 categories present or DECLARED EMPTY  (fold SKILL.md Step 3): ground truth, SSOT,
                                   routes, gates, corrections, close protocol (timing optional)
     A "## Outputs" section (files the chip will CREATE) is exempt from check 3: a stone may name
     what it is about to make; it may not cite, as existing, a thing that is not on main.
  3. integrity gate --strict       every path / sha / ADR the prompt cites exists on origin/main
  4. altitude canary               every assertive section has a ground return

Exit 0 = FLAWLESS, 1 = UNCUT (reasons printed). Never modifies the prompt.

Usage:
  python3 scripts/cold_molt_lint.py <chip-prompt.md> [...]
  python3 scripts/cold_molt_lint.py --self-test
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RELATIVE = [
    (r"\b(as (we|i|you) (said|discussed|mentioned|agreed|noted))\b", "session-relative: 'as we said/discussed'"),
    (r"\b(earlier (today|tonight|in the session)|earlier,|see above|as above|mentioned above)\b", "session-relative: 'earlier/above'"),
    (r"\b(this|the current|the other|the previous|the parent) session\b", "session-relative: names a session instead of a path"),
    (r"\byou (mentioned|said|asked|told me)\b", "session-relative: 'you mentioned'"),
    (r"\b(recall that|remember (that|when)|like before)\b", "session-relative: appeals to memory"),
    (r"\bthe (doc|document|file|thing|one) (we|i) (made|built|wrote|discussed)\b", "session-relative: 'the doc we made' with no path"),
    (r"/private/tmp/claude-|/tmp/claude|scratchpad/", "leaks a scratchpad path (dies with the session)"),
    (r"_STATE/handoff-progress\.(md|jsonl)", "cites the gitignored progress trail"),
    (r"^\s*(it|that one|those|the same)\b", "opens with a pronoun that has no antecedent in a cold read"),
]
CATEGORIES = {
    "ground truth": r"ground[- ]truth",
    "ssot": r"\bssot",
    "routes": r"\broutes?\b",
    "gates": r"\bgates?\b",
    "corrections": r"\bcorrections?\b",
    "close protocol": r"close[- ]protocol",
}
EMPTY_DECL = r"(none|n/a|empty|\(declared empty\)|nothing)"


def _load(name: str):
    p = ROOT / "scripts" / f"{name}.py"
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def lint(path: Path, run_gate: bool = True) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()
    reasons: list[str] = []
    for pat, why in RELATIVE:
        for m in re.finditer(pat, text, re.I | re.M):
            line = text.count("\n", 0, m.start()) + 1
            reasons.append(f"line {line}: {why} ({m.group(0)!r})")
    for cat, pat in CATEGORIES.items():
        if not re.search(pat, low):
            reasons.append(f"missing category '{cat}' (present it, or declare it empty)")
    if run_gate and (ROOT / "scripts" / "integrity_gate.py").exists():
        # strip the Outputs section (declared-new files) before the strict integrity pass
        import tempfile
        body = re.sub(r"^## Outputs.*?(?=^## |\Z)", "", text, flags=re.M | re.S)
        tf = Path(tempfile.mkdtemp()) / path.name
        tf.write_text(body, encoding="utf-8")
        r = subprocess.run([sys.executable, "scripts/integrity_gate.py", "--strict", str(tf)], capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            bad = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith(("✖", "⚠"))]
            reasons.append("integrity gate --strict: " + ("; ".join(bad[:4]) if bad else "failed"))
    can = _load("altitude_canary")
    if can:
        rep = can.report(path)
        if rep["verdict"] == "NO GROUND RETURN":
            reasons.append("altitude canary: NO GROUND RETURN in " + ", ".join(s["section"] for s in rep["sections"] if s["verdict"] == "NO GROUND RETURN"))
    return {"file": str(path), "verdict": "FLAWLESS" if not reasons else "UNCUT", "reasons": reasons}


def self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    good = tmp / "good.md"
    good.write_text("# Chip: regenerate the lattice\n\n## Ground truth\n- lattice epoch stamped 2026-09-27 (verified 2026-09-27, commit on main)\n\n## SSOT\n- runtime/specs/knowledge-lattice-v1.json\n\n## Routes\n- python3 scripts/lattice_drift_check.py --regenerate (verified 2026-09-27)\n\n## Gates\n- pre-commit integrity gate\n\n## Corrections\n- none\n\n## Close protocol\n- receipt per AGENTS.md\n", encoding="utf-8")
    bad = tmp / "bad.md"
    bad.write_text("# Chip\n\nAs we discussed earlier, finish the doc we made. It is in /private/tmp/claude-501/x/scratchpad/draft.md.\n\n## Gates\n- none\n", encoding="utf-8")
    fails = 0
    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1
    g = lint(good, run_gate=False); b = lint(bad, run_gate=False)
    check("self-contained chip with all categories -> FLAWLESS", g["verdict"] == "FLAWLESS", g["reasons"])
    check("session-relative + scratchpath + missing categories -> UNCUT", b["verdict"] == "UNCUT" and len(b["reasons"]) >= 4, b["reasons"][:3])
    check("reasons name the line", any(r.startswith("line ") for r in b["reasons"]))
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if not argv:
        print(__doc__); return 2
    worst = 0
    for f in argv:
        r = lint(Path(f))
        mark = "✓" if r["verdict"] == "FLAWLESS" else "✖"
        print(f"{mark} {f} — {r['verdict']}")
        for why in r["reasons"]:
            print(f"    {why}")
        worst = max(worst, 0 if r["verdict"] == "FLAWLESS" else 1)
    return worst


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
