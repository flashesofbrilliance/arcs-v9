#!/usr/bin/env python3
"""
tooltip_link_lint.py - Frustration Gate for the "term-inside-link" tooltip bug class.

Failure mode (banked 2026-09-23): a glossary `.term` (hover/tap tooltip) wrapped in an
`<a>` had its link navigation silently blocked, because the tooltip click handler calls
`e.preventDefault()` on any `.term` click. The term showed its tooltip but the link never
resolved. The fix is a one-line guard: when a `.term` sits inside a link, let the click
navigate instead of toggling the tooltip.

The rule this gate enforces: ANY page that ships the term-tooltip toggle handler
(preventDefault on a `.term` click) MUST carry the link-navigation guard `closest('a')`.
The guard is always-safe (a no-op when no term is ever nested in a link), so requiring it
whenever the handler exists catches the whole class cheaply, with zero false positives on
correct pages.

Usage:  python3 scripts/tooltip_link_lint.py <file.html> [<file.html> ...]
Exit 0 = all clean; exit 1 = at least one FAIL.
"""
import re
import sys

# The term-tooltip toggle handler preventing default on a `.term` click.
# Matches the shipped shape: ...preventDefault();active===t?hide():show(t)...
TOGGLE_RE = re.compile(r"preventDefault\(\)\s*;\s*active\s*===\s*t\s*\?", re.S)
GUARD_RE = re.compile(r"closest\(\s*['\"]a['\"]\s*\)")
HAS_TERMS_RE = re.compile(r'class\s*=\s*"[^"]*\bterm\b|data-def\s*=')


def check(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
    except OSError as exc:
        return ("FAIL", f"cannot read: {exc}")

    has_terms = bool(HAS_TERMS_RE.search(src))
    has_toggle = bool(TOGGLE_RE.search(src))
    has_guard = bool(GUARD_RE.search(src))

    if not (has_terms and has_toggle):
        return ("SKIP", "no term-tooltip toggle handler")
    if not has_guard:
        return ("FAIL",
                "term-tooltip click handler preventDefaults without a closest('a') "
                "guard: a `.term` inside an <a> will block link navigation")
    return ("PASS", "term-tooltip handler carries the link-navigation guard")


def main(argv):
    files = argv[1:]
    if not files:
        print("usage: tooltip_link_lint.py <file.html> [...]", file=sys.stderr)
        return 2
    failed = False
    for path in files:
        status, msg = check(path)
        if status == "FAIL":
            failed = True
            print(f"✗ tooltip-link-lint: {path}  {msg}")
        elif status == "PASS":
            print(f"✓ tooltip-link-lint: {path} clean")
        # SKIP is silent
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
