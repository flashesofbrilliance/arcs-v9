#!/usr/bin/env python3
"""Inline-styles-only gate (ledger LINT-006 / ADR-034).

The rule ("inline styles only in components — no Tailwind, no className, no
CSS modules") was violated at the root layout from the repo's first commit and
sat undetected for seven weeks because no mechanism enforced it. This is the
mechanism.

Fails (exit 1) if `className=` appears in any .tsx/.jsx under src/ outside the
sanctioned allowlist:
  - src/app/layout.tsx        (next/font variable classes — framework mechanism)

Stdlib only. Run from repo root: python3 scripts/style_rule_check.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST = {ROOT / "src" / "app" / "layout.tsx"}
PATTERN = re.compile(r"className\s*=")


def main() -> int:
    violations = []
    for path in (ROOT / "src").rglob("*"):
        if path.suffix not in {".tsx", ".jsx"} or path in ALLOWLIST:
            continue
        for i, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            if PATTERN.search(line):
                violations.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:100]}")

    if violations:
        print("Inline-styles-only rule violated (className outside allowlist):")
        for v in violations:
            print(f"  ✗ {v}")
        print("\nFix: convert to an inline style object, or (rare) extend the")
        print("allowlist in scripts/style_rule_check.py with a comment saying why.")
        return 1
    print("Style rule clean: no className outside the allowlist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
