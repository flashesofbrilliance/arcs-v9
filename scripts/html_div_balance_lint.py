#!/usr/bin/env python3
"""
html_div_balance_lint.py - Frustration Gate for the "unclosed div" column-collapse bug class.

Failure mode (banked 2026-09-23): a `<div class="row">...</p>` on vico.html was missing its
closing `</div>`, so the NEXT `.row` nested inside it. Because `.row` lays its children out in
columns, the nested bullet rendered as a pinched second column instead of its own full-width
row -- a silent visual regression invisible to the wrap-lint (nothing overflows) and to a
casual read of the source (the line looks complete because it ends in `</p>`).

The rule this gate enforces: in a self-contained page, the count of `<div ...>` opening tags
must equal the count of `</div>` closing tags. `<div>` is never a void element, so a well-formed
page always balances; an inequality means a div is unclosed (or over-closed) somewhere. This is
the cheapest mechanical check that FAILS on the whole class with zero false positives on
correct pages.

Usage:  python3 scripts/html_div_balance_lint.py <file.html> [<file.html> ...]
Exit 0 = all balanced; exit 1 = at least one imbalance.
"""
import re
import sys

OPEN_RE = re.compile(r"<div(?:\s[^>]*)?>", re.I)
CLOSE_RE = re.compile(r"</div\s*>", re.I)


def check(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
    except OSError as exc:
        return ("FAIL", f"cannot read: {exc}")
    # Ignore <script>/<style> bodies: a JS string or template could carry a bare "<div"
    # token that is not real markup and would skew the count.
    stripped = re.sub(r"<(script|style)\b.*?</\1>", "", src, flags=re.I | re.S)
    opens = len(OPEN_RE.findall(stripped))
    closes = len(CLOSE_RE.findall(stripped))
    if opens != closes:
        delta = opens - closes
        which = f"{delta} unclosed <div>" if delta > 0 else f"{-delta} stray </div>"
        return ("FAIL", f"div imbalance: {opens} open vs {closes} close ({which})")
    return ("OK", f"{opens} div pairs balanced")


def main(argv):
    files = argv[1:]
    if not files:
        print("usage: html_div_balance_lint.py <file.html> [...]", file=sys.stderr)
        return 2
    failed = False
    for path in files:
        status, msg = check(path)
        if status == "FAIL":
            failed = True
            print(f"✗ div-balance: {path} -- {msg}", file=sys.stderr)
        else:
            print(f"✓ div-balance: {path} {msg}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
