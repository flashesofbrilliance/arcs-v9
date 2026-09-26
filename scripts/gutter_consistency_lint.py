#!/usr/bin/env python3
"""
gutter_consistency_lint.py - Frustration Gate for the "stale gutter" mis-indent bug class.

Failure mode (banked 2026-09-24): in the recoil-report page template, body sections live in a
`.pad` container (e.g. `padding:26px 40px`) while `header` and `footer` carry their own horizontal
padding. When the header/footer gutter drifts from the `.pad` gutter (44px vs 40px), every header
and footer element sits a few px inward of the body text -- a left edge that lies about its lane.
It is invisible to the wrap-lint (nothing overflows) and to a casual read, and it propagated to
six sibling pages from one shared template before anyone measured it.

The rule this gate enforces: in any page that has a `.pad` container with horizontal padding, the
`header` and `footer` rules (when they set their own horizontal padding) MUST use the SAME horizontal
value as `.pad`, so the left edge is true from header to footer. Pages without a `.pad` container
use a different layout and are skipped (zero false positives on them).

Only the FIRST (top-of-file, desktop) rule block for each selector is checked -- media-query
overrides are intentionally separate and not compared here.

Usage:  python3 scripts/gutter_consistency_lint.py <file.html> [<file.html> ...]
Exit 0 = all consistent (or N/A); exit 1 = at least one gutter mismatch.
"""
import re
import sys


def _first_block(src, selector):
    m = re.search(re.escape(selector) + r"\{([^}]*)\}", src)
    return m.group(1) if m else None


def _hpad(block):
    if not block:
        return None
    m = re.search(r"padding:\s*([0-9]+)px\s+([0-9]+)px", block)
    return m.group(2) if m else None


def check(path):
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
    except OSError as exc:
        return ("FAIL", f"cannot read: {exc}")
    pad = _hpad(_first_block(src, ".pad"))
    if pad is None:
        return ("SKIP", "no .pad container")
    bad = []
    for sel in ("header", "footer"):
        v = _hpad(_first_block(src, sel))
        if v is not None and v != pad:
            bad.append(f"{sel}={v}px")
    if bad:
        return ("FAIL", f"gutter mismatch: .pad={pad}px but " + ", ".join(bad))
    return ("OK", f"gutter {pad}px consistent")


def main(argv):
    files = argv[1:]
    if not files:
        print("usage: gutter_consistency_lint.py <file.html> [...]", file=sys.stderr)
        return 2
    failed = False
    for path in files:
        status, msg = check(path)
        if status == "FAIL":
            failed = True
            print(f"✗ gutter-lint: {path} -- {msg}", file=sys.stderr)
        elif status == "OK":
            print(f"✓ gutter-lint: {path} {msg}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
