#!/usr/bin/env python3
"""kit_primitive_sync: the Instrument Lab primitives promoted from Phosphor stay identical to the page.

Each kit organism (src/ui-kit/recoil-report/NN-*.html, @dsCard group="Instrument Lab") owns a marked
block  /* @prim:begin <name> */ ... /* @prim:end <name> */  of CSS rules. The same rules, line for line,
must appear in _ARTIFACTS/phosphor.html (pages inline the kit; the kit is the source).

  python3 scripts/kit_primitive_sync.py --check          exit 1 if any kit block is missing or differs in the page
  python3 scripts/kit_primitive_sync.py --write          copy each kit block into the page (replacing the page's rules)
  python3 scripts/kit_primitive_sync.py --extract        one-time: build the kit blocks from the page's current rules
Stdlib only.
"""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "src/ui-kit/recoil-report")
PAGE = os.path.join(ROOT, "_ARTIFACTS/phosphor.html")
BLK = re.compile(r'/\* @prim:begin (\S+) \*/\n(.*?)/\* @prim:end \1 \*/', re.S)

def kit_blocks():
    out = {}
    for f in sorted(os.listdir(KIT)):
        if re.match(r'\d\d-.*\.html$', f):
            for n, body in BLK.findall(open(os.path.join(KIT, f), encoding="utf-8").read()):
                out[n] = (f, body)
    return out

def main(a):
    page = open(PAGE, encoding="utf-8").read(); bad = 0
    for n, (f, body) in kit_blocks().items():
        lines = [l for l in body.split("\n") if l.strip()]
        missing = [l for l in lines if l not in page]
        if missing:
            bad += 1; print(f"✖ {n} ({f}): {len(missing)} rule(s) differ from the page, first: {missing[0][:90]}")
        else: print(f"✓ {n} ({f}): {len(lines)} rules identical in the page")
    if not kit_blocks(): print("✖ no @prim blocks found"); return 1
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) if "--check" in sys.argv or len(sys.argv) == 1 else 2)
