#!/usr/bin/env python3
"""inline_token_sync: pages that inline src/ui-kit/recoil-report/_tokens.css carry it verbatim.

A self-contained page inlines the kit tokens inside a <style> block that starts with the sentinel
"/* ARCS Recoil Report — Design Tokens */" and runs up to the closing brace of the first :root rule.
This script compares that block with the kit file and can rewrite it.

  python3 scripts/inline_token_sync.py --check <page.html> [...]   exit 1 if a page's inlined block differs
  python3 scripts/inline_token_sync.py --write <page.html> [...]   rewrite the page's block from the kit
  python3 scripts/inline_token_sync.py --check --all               every _ARTIFACTS and public page that has the sentinel
Stdlib only. Pages without the sentinel (they <link> the kit) are skipped.
"""
import os, re, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report/_tokens.css")
SENT = "/* ARCS Recoil Report — Design Tokens */"

def kit_block():
    t = open(KIT, encoding="utf-8").read()
    i = t.index(SENT); j = t.index("\n}", t.index(":root", i)) + 2
    return t[i:j]

def page_span(t):
    i = t.find(SENT)
    if i < 0: return None
    try: return i, t.index("\n}", t.index(":root", i)) + 2
    except ValueError: return None

def main(a):
    write = "--write" in a; files = [x for x in a if not x.startswith("--")]
    if "--all" in a:
        files = sorted(set(glob.glob(os.path.join(ROOT, "_ARTIFACTS/*.html")) + glob.glob(os.path.join(ROOT, "public/*.html"))))
    if not files: print(__doc__); return 2
    kb = kit_block(); bad = 0
    for f in files:
        t = open(f, encoding="utf-8").read(); sp = page_span(t)
        if not sp:
            if "--all" not in a: print(f"- {f}: no inlined tokens (links the kit or none)")
            continue
        cur = t[sp[0]:sp[1]]
        if cur == kb:
            if "--all" not in a: print(f"✓ {f}: inlined tokens identical to the kit")
        elif write:
            open(f, "w", encoding="utf-8").write(t[:sp[0]] + kb + t[sp[1]:]); print(f"↻ {f}: rewrote the inlined token block from the kit")
        else:
            bad += 1; print(f"✖ {f}: inlined tokens differ from the kit (run --write)")
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
