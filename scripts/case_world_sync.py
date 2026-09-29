#!/usr/bin/env python3
"""case_world_sync: stamp the canonical Case World blocks from the kit into every enrolled page.

Single source: src/ui-kit/recoil-report/15-case-world.html carries four marked blocks
(css, scene, dock, runtime). A page enrolls by carrying the same four marker pairs; this
script replaces whatever sits between them with the kit's version, so playable cases share
one world instead of drifting copies (AGENTS.md gotcha #13: net-new shapes become kit
primitives; #15: the Frustration Gate makes the whole class fail, not just the instance).

Markers (CSS block lives inside the page's <style>; the rest are HTML comments):
  /* case-world:css:begin */ ... /* case-world:css:end */
  <!-- case-world:scene:begin --> ... <!-- case-world:scene:end -->
  <!-- case-world:dock:begin --> ... <!-- case-world:dock:end -->
  <!-- case-world:runtime:begin --> ... <!-- case-world:runtime:end -->

Usage:
  python3 scripts/case_world_sync.py              # stamp all enrolled public/*.html
  python3 scripts/case_world_sync.py --check      # exit 1 if any enrolled page drifted
  python3 scripts/case_world_sync.py [--check] <page.html> ...

Enrolled = a public/*.html file containing any case-world marker. A page with some but not
all marker pairs is an error (half-enrolled pages are how drift starts). Stdlib only.
"""
import glob, os, re, sys

KIT = "src/ui-kit/recoil-report/15-case-world.html"
BLOCKS = {
    "css": ("/* case-world:css:begin */\n", "\n/* case-world:css:end */"),
    "scene": ("<!-- case-world:scene:begin -->\n", "\n<!-- case-world:scene:end -->"),
    "dock": ("<!-- case-world:dock:begin -->\n", "\n<!-- case-world:dock:end -->"),
    "runtime": ("<!-- case-world:runtime:begin -->\n", "\n<!-- case-world:runtime:end -->"),
}


def span(text, name):
    """Return (start, end) of the content between a block's markers, or None if absent."""
    begin, end = BLOCKS[name]
    i = text.find(begin)
    if i < 0:
        return None
    j = text.find(end, i + len(begin))
    if j < 0:
        return None
    if text.find(begin, i + 1) >= 0:
        raise ValueError(f"block '{name}' appears more than once")
    return i + len(begin), j


def kit_blocks(root):
    text = open(os.path.join(root, KIT), encoding="utf-8").read()
    out = {}
    for name in BLOCKS:
        s = span(text, name)
        if s is None:
            sys.exit(f"✖ case-world: kit {KIT} is missing block '{name}'")
        out[name] = text[s[0]:s[1]]
    return out


def enrolled(root):
    pages = []
    for p in sorted(glob.glob(os.path.join(root, "public", "*.html"))):
        if "case-world:" in open(p, encoding="utf-8").read():
            pages.append(os.path.relpath(p, root))
    return pages


def main(argv):
    check = "--check" in argv
    args = [a for a in argv if a != "--check"]
    root = os.getcwd()
    canon = kit_blocks(root)
    pages = args or enrolled(root)
    bad = 0
    for page in pages:
        text = open(os.path.join(root, page), encoding="utf-8").read()
        try:
            spans = {n: span(text, n) for n in BLOCKS}
        except ValueError as e:
            print(f"✖ case-world: {page}: {e}"); bad += 1; continue
        missing = [n for n, s in spans.items() if s is None]
        if missing:
            print(f"✖ case-world: {page} is half-enrolled, missing block(s): {', '.join(missing)}"); bad += 1; continue
        drifted = [n for n, (a, b) in spans.items() if text[a:b] != canon[n]]
        if not drifted:
            print(f"✓ case-world: {page} matches the kit"); continue
        if check:
            print(f"✖ case-world: {page} drifted from the kit in: {', '.join(drifted)}. Run python3 scripts/case_world_sync.py to restamp (edit the kit, not the page).")
            bad += 1; continue
        # stamp back-to-front so earlier offsets stay valid
        for n, (a, b) in sorted(spans.items(), key=lambda kv: kv[1][0], reverse=True):
            text = text[:a] + canon[n] + text[b:]
        open(os.path.join(root, page), "w", encoding="utf-8").write(text)
        print(f"↻ case-world: {page} restamped ({', '.join(drifted)})")
    if not pages:
        print("case-world: no enrolled pages")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
