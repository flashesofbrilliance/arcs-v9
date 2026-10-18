#!/usr/bin/env python3
"""phosphor_build: build the single-file Phosphor page from its sources (stdlib only).

Sources live in _ARTIFACTS/phosphor-src/: page.tpl (markup, with the two markers below), style.css, app.js.
  <!--@style.css-->  is replaced by style.css verbatim (the kit tokens inside must stay byte-identical).
  <!--@app.js-->     is replaced by app.js with leading indentation and blank lines removed (the one size saving).
The result is _ARTIFACTS/phosphor.html, which stays committed so the artifact, the gates and the checks are unchanged.
  python3 scripts/phosphor_build.py           write the page
  python3 scripts/phosphor_build.py --check   exit 1 if the committed page differs from a fresh build
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_ARTIFACTS/phosphor-src"); OUT = os.path.join(ROOT, "_ARTIFACTS/phosphor.html")

def rd(n): return open(os.path.join(SRC, n), encoding="utf-8").read()

def build():
    page, css, js = rd("page.tpl"), rd("style.css").rstrip("\n"), rd("app.js")
    lines = [l.lstrip(" \t") for l in js.split("\n")]
    js = "\n".join(l for l in lines if l.strip() != "")
    for m in ("<!--@style.css-->", "<!--@app.js-->"):
        if page.count(m) != 1: sys.exit("marker %s must appear exactly once in page.tpl" % m)
    out = page.replace("<!--@style.css-->", css).replace("<!--@app.js-->", js)
    return out

if __name__ == "__main__":
    out = build()
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read()
        if cur != out: print("phosphor_build: _ARTIFACTS/phosphor.html differs from a fresh build; edit _ARTIFACTS/phosphor-src/ and run python3 scripts/phosphor_build.py"); sys.exit(1)
        print("phosphor_build: page matches its sources (%d bytes)" % len(out.encode())); sys.exit(0)
    open(OUT, "w", encoding="utf-8").write(out); print("phosphor_build: wrote %d bytes" % len(out.encode()))
