#!/usr/bin/env python3
"""token_tuner_inline: put the token tuner into a single-file page, take it out, or check the copy is current.

    python3 scripts/token_tuner_inline.py FILE.html [...]           inline (or refresh) src/ui-kit/token-tuner.js first in <body>
    python3 scripts/token_tuner_inline.py --strip FILE.html [...]   remove it (do this before a counterpart send copy)
    python3 scripts/token_tuner_inline.py --check FILE.html [...]   exit 1 if a page carries a stale copy
    python3 scripts/token_tuner_inline.py --apply-text EDITS.json SOURCE.html
                                       apply the tuner's "Copy edits" list ([{old, new}] text pairs) to a page's SOURCE;
                                       refuses (and writes nothing) if any old text is missing or not unique
    python3 scripts/token_tuner_inline.py --self-test

The tuner only runs when the page URL has ?tune or ?edit, so an internal page can keep it. It goes first in <body>,
before the page's own scripts, so its matchMedia wrapper is in place when they read a breakpoint. A counterpart copy must not:
scripts/page_gate.py --counterpart fails any page that contains the marker (MARKER below).
"""
import html as htmllib
import json
import os
import re
import sys
from html.entities import codepoint2name

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


def text_pattern(old):
    """Regex for a DOM text value as it may be written in source: each character literal or as an entity."""
    parts = []
    for c in old:
        alts = [re.escape(c), "&#%d;" % ord(c), "&#[xX]0*%x;" % ord(c)]
        if ord(c) in codepoint2name:
            alts.append("&%s;" % codepoint2name[ord(c)])
        if c == "'":
            alts.append("&apos;")
        parts.append("(?:" + "|".join(alts) + ")")
    return "".join(parts)


def apply_text(src, edits):
    """Apply [{old, new[, html]}] pairs to src. Returns (new_src, errors); on any error src is returned unchanged."""
    errors, spans = [], []
    for i, e in enumerate(edits):
        old, new = e.get("old", ""), e.get("new", "")
        if not old.strip():
            errors.append(f"edit {i + 1}: empty old text")
            continue
        pat = re.escape(old) if e.get("html") else text_pattern(old)
        hits = list(re.finditer(pat, src))
        if len(hits) != 1:
            errors.append(f"edit {i + 1}: old text found {len(hits)} times, need exactly 1: {old[:60]!r}")
            continue
        spans.append((hits[0].start(), hits[0].end(), new if e.get("html") else htmllib.escape(new, quote=False)))
    spans.sort()
    for a, b in zip(spans, spans[1:]):
        if a[1] > b[0]:
            errors.append("two edits overlap in the source")
    if errors:
        return src, errors
    for start, end, rep_ in reversed(spans):
        src = src[:start] + rep_ + src[end:]
    return src, []


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
    src = "<p>Tom &amp; Jerry&rsquo;s plan</p><p>two</p><p>two</p><li>one</li>"
    out, err = apply_text(src, [{"old": "Tom & Jerry\u2019s plan", "new": "Tom & Jerry's <new> plan"}])
    assert not err and "<p>Tom &amp; Jerry's &lt;new&gt; plan</p>" in out, ("apply-text matches entities, escapes new text", out, err)
    out, err = apply_text(src, [{"old": "one", "new": "1"}, {"old": "two", "new": "2"}])
    assert err and out == src, "apply-text refuses a non-unique old text and writes nothing"
    out, err = apply_text(src, [{"old": "absent", "new": "x"}])
    assert err and out == src, "apply-text refuses a missing old text"
    out, err = apply_text(src, [{"old": "one", "new": "<b>1</b>", "html": True}])
    assert not err and "<li><b>1</b></li>" in out, "apply-text takes an html pair verbatim"
    print("token_tuner_inline self-test: ok")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--apply-text"]:
        if len(argv) != 3:
            print(__doc__)
            return 2
        with open(argv[1], encoding="utf-8") as fh:
            edits = json.load(fh)
        with open(argv[2], encoding="utf-8") as fh:
            src = fh.read()
        if has_tuner(src):
            print(f"✖ {argv[2]}: carries the tuner; apply edits to the page's source, not a tuned copy")
            return 1
        new, errors = apply_text(src, edits)
        for e in errors:
            print(f"✖ {e}")
        if errors:
            print(f"nothing written to {argv[2]}")
            return 1
        with open(argv[2], "w", encoding="utf-8") as fh:
            fh.write(new)
        print(f"applied {len(edits)} edit(s): {argv[2]} (rebuild the page from it)")
        return 0
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
