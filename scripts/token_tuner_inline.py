#!/usr/bin/env python3
"""token_tuner_inline: put the token tuner into a single-file page, take it out, or check the copy is current.

    python3 scripts/token_tuner_inline.py FILE.html [...]           inline (or refresh) src/ui-kit/token-tuner.js first in <body>
    python3 scripts/token_tuner_inline.py --strip FILE.html [...]   remove it (do this before a counterpart send copy)
    python3 scripts/token_tuner_inline.py --check FILE.html [...]   exit 1 if a page carries a stale copy
    python3 scripts/token_tuner_inline.py --self-test

The tuner only runs when the page URL has ?tune or ?edit, so an internal page can keep it. It goes first in <body>,
before the page's own scripts, so its matchMedia wrapper is in place when they read a breakpoint. A counterpart copy must not:
scripts/page_gate.py --counterpart fails any page that contains the marker (MARKER below).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "ui-kit", "token-tuner.js")
MARKER = "arcs-token-tuner"
START, END = "<!-- arcs-token-tuner:start -->", "<!-- arcs-token-tuner:end -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)


def block():
    with open(SRC, encoding="utf-8") as fh:
        return f"{START}\n<script>\n{fh.read().rstrip()}\n</script>\n{END}\n"


def strip(html):
    return BLOCK_RE.sub("", html)


def inline(html):
    html = strip(html)
    m = re.search(r"<body[^>]*>\n?", html, re.I)
    if m:
        return html[:m.end()] + block() + html[m.end():]
    i = html.lower().find("<main")  # an Artifact body has no <body>: go before the content
    if i < 0:
        raise ValueError("no <body> or <main> tag")
    return html[:i] + block() + html[i:]


def has_tuner(html):
    return MARKER in html


def self_test():
    page = "<html><body><p>x</p></body></html>"
    a = inline(page)
    assert a.count(START) == 1 and has_tuner(a), "inline adds one block"
    assert inline(a) == a, "inline is idempotent"
    assert strip(a) == page, "strip restores the page"
    assert not has_tuner(strip(a)), "a stripped page carries no marker"
    assert a.index(START) < a.index("<p>x</p>"), "the tuner runs before the page's own content and scripts"
    print("token_tuner_inline self-test: ok")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    mode = "inline"
    if argv[:1] in (["--strip"], ["--check"]):
        mode, argv = argv[0][2:], argv[1:]
    if not argv:
        print(__doc__)
        return 2
    want = block()
    bad = 0
    for f in argv:
        with open(f, encoding="utf-8") as fh:
            html = fh.read()
        if mode == "check":
            m = BLOCK_RE.search(html)
            if m and m.group(0).rstrip("\n") != want.rstrip("\n"):
                print(f"✖ {f}: stale token tuner copy; rerun scripts/token_tuner_inline.py {f}")
                bad += 1
            continue
        new = strip(html) if mode == "strip" else inline(html)
        if mode == "strip" and has_tuner(new):
            print(f"✖ {f}: marker '{MARKER}' still present outside the sentinel block; remove it by hand")
            bad += 1
        if new != html:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(new)
        print(f"{'stripped' if mode == 'strip' else 'inlined'}: {f}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) or 0)
