#!/usr/bin/env python3
"""template_leak_lint.py: fail any static HTML page whose VISIBLE text carries unevaluated template code.

WHY: the ARCS OS design system's Instrument Panel card (src/instrument/card.html in Claude Design)
shipped `${Array.from({length:20},...).join('')}` and `${[['QUICKMOVE',...]].map(...)}` as
on-screen text: JavaScript template literals written into plain HTML, where nothing evaluates them.
Every design built from that card would print code instead of a segment bar and a distribution.
The class is "template syntax that only a JS runtime would expand, sitting in static markup", so
the guard reads what a browser would SHOW (script, style, comments and tags removed) and fails on
`${` or a dangling `).join(`. Kintsugi seam: _PATTERNS/kintsugi-visual-grammar-seams.md, 2026-10-08.

Usage:
  python3 scripts/template_leak_lint.py <file.html> [...]   # exit 1 on any leak, naming file:line
  python3 scripts/template_leak_lint.py --self-test           # proves fails-on-bad, passes-on-good
Stdlib only.
"""
from __future__ import annotations

import re
import sys

HIDDEN = re.compile(r"<(script|style|template|textarea|code|pre)\b.*?</\1\s*>|<!--.*?-->", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
LEAK = re.compile(r"\$\{|\)\s*\.join\(")


def leaks(html: str) -> list[tuple[int, str]]:
    """(line, snippet) for every leak in the visible text. Line numbers follow the source."""
    # Blank hidden regions but keep their newlines so reported lines match the file.
    vis = HIDDEN.sub(lambda m: "\n" * m.group(0).count("\n"), html)
    vis = TAG.sub(lambda m: "\n" * m.group(0).count("\n"), vis)
    out = []
    for i, line in enumerate(vis.splitlines(), 1):
        m = LEAK.search(line)
        if m:
            out.append((i, line.strip()[:90]))
    return out


def self_test() -> int:
    bad = '<div class="seg">${Array.from({length:20},(_,i)=>`<i></i>`).join("")}</div>'
    good = ('<div class="seg"><i></i><i></i></div>'
            '<script>const s = `${n} rounds`; [1].map(x => x).join("")</script>'
            '<!-- ${commented} --><code>${shown as code on purpose}</code>')
    attr = '<div title="${x}">ok</div>'  # attributes are not visible text
    ok = bool(leaks(bad)) and not leaks(good) and not leaks(attr)
    print(("PASS" if ok else "FAIL") + " template_leak_lint self-test: bad caught, script/comment/code/attr ignored")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return self_test()
    bad = 0
    for path in argv[1:]:
        try:
            html = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"template-leak: cannot read {path}: {e}")
            bad += 1
            continue
        for line, snip in leaks(html):
            print(f"✖ template-leak {path}:{line}: unevaluated template code in visible text: {snip}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
