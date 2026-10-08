#!/usr/bin/env python3
"""design_debt_sweep.py: the design-debt burn-down for every page surfaces.arcs.care serves.

DONE GOAL (Zach, 2026-10-08): every served page at 0 design-detector findings except recorded,
reasoned exemptions; 0 em-dashes in visible copy; wrap lint, token gate and template-leak clean.
This script is how that goal is measured and how it is kept from going backwards.

Sources: runtime/specs/surface-catalog.json (the served files) and the repo's own gates:
  detector  Impeccable `detect --json --no-advisory` (honors .impeccable/config.json exemptions)
  emdash    U+2014 in visible text (script, style, code and comments removed)
  wrap      scripts/artifact_wrap_lint.py
  tokens    scripts/token_source_gate.py
  leak      scripts/template_leak_lint.py
Retired color literals are a separate hard rule: RETIRED below may never appear in a served page.

Usage:
  python3 scripts/design_debt_sweep.py --emit           # full sweep -> runtime/specs/design-debt-baseline.json
  python3 scripts/design_debt_sweep.py --report         # burn-down: baseline totals vs a fresh sweep
  python3 scripts/design_debt_sweep.py --check F [F..]  # ratchet: each served page's counts must not rise
The detector is the repo's pinned `impeccable` dev dependency (or the skill launcher); without either
the detector column is skipped cleanly, same as the kintsugi pre-commit gate. Stdlib only.
"""
from __future__ import annotations

import html as H
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "runtime" / "specs" / "surface-catalog.json"
BASELINE = ROOT / "runtime" / "specs" / "design-debt-baseline.json"
# The repo's own dev dependency first (impeccable, pinned in package.json), then the skill launcher.
LAUNCHER = next((p for p in (ROOT / "node_modules/.bin/impeccable", Path.home() / ".claude/skills/impeccable/scripts/impeccable") if p.exists()),
                ROOT / "node_modules/.bin/impeccable")
# Raised 2026-10-04 (DESIGN.md text-dimmed / text-muted): the old values fail WCAG AA on #020408.
RETIRED = {"#64748b": "#8391a7", "#475569": "#7a8699"}
HIDDEN = re.compile(r"<(script|style|template|textarea|code|pre)\b.*?</\1\s*>|<!--.*?-->", re.S | re.I)


def served() -> list[str]:
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))["rows"]
    return sorted({r["file"] for r in rows if (r.get("file") or "").endswith(".html") and (ROOT / r["file"]).exists()})


def emdashes(path: str) -> int:
    src = (ROOT / path).read_text(encoding="utf-8", errors="replace")
    return H.unescape(re.sub(r"<[^>]+>", " ", HIDDEN.sub(" ", src))).count("—")


RETIRED_USE = re.compile(r"(?:[\w-]+\s*:\s*|\bfill\s*=\s*[\"'])(" + "|".join(RETIRED) + r")\b", re.I)


def retired(path: str) -> int:
    """Retired greys used as a color: CSS declarations and SVG fills (text). Strokes and data stay."""
    return len(RETIRED_USE.findall((ROOT / path).read_text(encoding="utf-8", errors="replace")))


def gate(script: str, path: str) -> int | None:
    if not (ROOT / "scripts" / script).exists():
        return None  # gate not on this branch yet: skip, never count it as a failure
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / script), path], capture_output=True, text=True, cwd=ROOT)
    return 0 if p.returncode == 0 else 1


def detector(paths: list[str]) -> dict[str, Counter] | None:
    if not LAUNCHER.exists() or not paths:
        return None
    p = subprocess.run([str(LAUNCHER), "detect", "--json", "--no-advisory", *paths], capture_output=True, text=True, cwd=ROOT)
    try:
        found = json.loads(p.stdout or "[]")
    except json.JSONDecodeError:
        return None
    out: dict[str, Counter] = {f: Counter() for f in paths}
    for x in found:
        f = os.path.relpath(x["file"], ROOT)
        out.setdefault(f, Counter())[x["antipattern"]] += 1
    return out


def sweep(paths: list[str]) -> dict:
    det = detector(paths)
    pages = {}
    for f in paths:
        pages[f] = {
            "detector": sum(det[f].values()) if det is not None else None,
            "rules": dict(sorted(det[f].items())) if det is not None else None,
            "emdash": emdashes(f),
            "wrap": gate("artifact_wrap_lint.py", f),
            "tokens": gate("token_source_gate.py", f),
            "leak": gate("template_leak_lint.py", f),
            "retired_color": retired(f),
        }
    return pages


def totals(pages: dict) -> dict:
    t = Counter()
    for v in pages.values():
        for k in ("detector", "emdash", "wrap", "tokens", "leak", "retired_color"):
            t[k] += v[k] or 0
    t["pages"] = len(pages)
    t["pages_clean"] = sum(1 for v in pages.values() if not any(v[k] for k in ("detector", "emdash", "wrap", "tokens", "leak", "retired_color")))
    return dict(t)


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "--report"
    if mode == "--emit":
        pages = sweep(served())
        BASELINE.write_text(json.dumps({"version": "0.1.0", "goal": "every served page clean except reasoned exemptions",
                                         "totals": totals(pages), "pages": pages}, indent=1) + "\n", encoding="utf-8")
        print("design-debt baseline:", json.dumps(totals(pages)))
        return 0
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    if mode == "--report":
        now = totals(sweep(served()))
        for k in now:
            print(f"  {k:14} {base['totals'].get(k, 0):6} -> {now[k]:6}")
        return 0
    if mode == "--check":
        targets = [f for f in argv[2:] if f in base["pages"]]
        if not targets:
            return 0
        bad = 0
        fresh = sweep(targets)
        for f in targets:
            was, now = base["pages"][f], fresh[f]
            for k in ("detector", "emdash", "wrap", "tokens", "leak", "retired_color"):
                if now[k] is None or was[k] is None:
                    continue
                if now[k] > was[k]:
                    print(f"✖ design-debt {f}: {k} rose {was[k]} -> {now[k]} (the burn-down only goes down)")
                    bad += 1
        return 1 if bad else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
