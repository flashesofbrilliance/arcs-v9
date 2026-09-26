#!/usr/bin/env python3
"""no_tailwind_guard.py — hard guard closing ledger finding LINT-006.

Tailwind was removed 2026-07-11 (AGENTS.md: inline styles only; the sole
stylesheet is src/app/globals.css). CI lint is advisory (continue-on-error), so
nothing HARD-blocks Tailwind from creeping back. This guard is that hard gate: it
fails CI when a `className` in src/ carries a Tailwind utility-class signature.

Scope is deliberately narrow to avoid false positives:
  - It only inspects the VALUE of `className=` attributes (string literals and the
    string parts of `{...}` expressions) — never arbitrary identifiers, so a
    styled-object property called `flex` or a variable named `grid` is fine.
  - It flags only unambiguous Tailwind utility tokens (spacing/sizing/layout/
    color/typography scales), not ordinary semantic class names (e.g. `no-print`,
    next/font variable classes).

Deterministic, stdlib-only. Run from repo root: python3 scripts/no_tailwind_guard.py
Exit 0 = clean · 1 = Tailwind signature found.
"""
import re
import sys
import pathlib

SRC = pathlib.Path("src")

# Tailwind utility-token signatures. Each must match a WHOLE space-delimited token
# inside a className value. Kept to scale-based utilities that are unmistakably
# Tailwind, never plain English class names.
TW_TOKEN = re.compile(
    r"^(?:"
    r"(?:sm|md|lg|xl|2xl):.+"                       # responsive prefixes
    r"|(?:hover|focus|active|group-hover|dark):.+"  # state prefixes
    r"|(?:p|m|px|py|pt|pb|pl|pr|mx|my|mt|mb|ml|mr)-\d+"      # spacing scale
    r"|(?:w|h|min-w|min-h|max-w|max-h)-(?:\d+|full|screen|px)"  # sizing scale
    r"|gap-\d+|space-[xy]-\d+"
    r"|text-(?:xs|sm|base|lg|xl|\d?xl|left|center|right)"
    r"|font-(?:thin|light|normal|medium|semibold|bold|extrabold|black)"
    r"|(?:bg|text|border|ring|from|to|via)-(?:[a-z]+)-\d{2,3}"   # color scale
    r"|rounded(?:-(?:sm|md|lg|xl|full|none))?"
    r"|shadow(?:-(?:sm|md|lg|xl|none|inner))?"
    r"|(?:items|justify|self|content|place)-(?:center|start|end|between|around|evenly|stretch|baseline)"
    r"|flex-(?:row|col|wrap|nowrap|1|auto|initial|none)"
    r"|grid-cols-\d+|col-span-\d+|row-span-\d+"
    r"|(?:opacity|z)-\d+"
    r")$"
)

# Pull the value out of className="..." / className='...' / className={`...`} /
# className={"..."}. We collect the literal string content and split on whitespace.
CLASSNAME = re.compile(r"""className\s*=\s*(?:"([^"]*)"|'([^']*)'|\{`([^`]*)`\}|\{"([^"]*)"\}|\{'([^']*)'\})""")


def tokens(value: str):
    # Drop ${...} template interpolations (next/font variables etc.) before tokenizing.
    value = re.sub(r"\$\{[^}]*\}", " ", value)
    for tok in value.split():
        tok = tok.strip()
        if tok:
            yield tok


def main() -> int:
    if not SRC.exists():
        print("no_tailwind_guard: src/ not found — skipping.")
        return 0
    hits = []
    for f in sorted(list(SRC.rglob("*.tsx")) + list(SRC.rglob("*.ts"))):
        text = f.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in CLASSNAME.finditer(line):
                value = next(g for g in m.groups() if g is not None)
                for tok in tokens(value):
                    if TW_TOKEN.match(tok):
                        hits.append(f"{f}:{lineno}: Tailwind-utility class '{tok}' in className")
    if hits:
        print("✘ no-tailwind guard (LINT-006): Tailwind utility classes found in src/:")
        for h in hits:
            print("   -", h)
        print("\n  Tailwind was removed 2026-07-11. Use inline styles (WORLD.md) or a")
        print("  class defined in src/app/globals.css. Do not reintroduce Tailwind utilities.")
        return 1
    print("✔ no-tailwind guard (LINT-006): no Tailwind utility classes in src/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
