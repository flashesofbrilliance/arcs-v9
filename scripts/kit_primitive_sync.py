#!/usr/bin/env python3
"""kit_primitive_sync: the Instrument Lab primitives promoted from Phosphor stay identical to the page.

Each kit organism (src/ui-kit/recoil-report/NN-*.html, @dsCard group="Instrument Lab") owns a marked
block  /* @prim:begin <name> */ ... /* @prim:end <name> */  of CSS rules. The same rules, line for line,
must appear in _ARTIFACTS/phosphor.html (pages inline the kit; the kit is the source).

Molecules and other groups (27 on) are not Phosphor's, so phosphor is checked only for Instrument Lab
blocks (2026-11-04: the unscoped check failed on main for 27 to 37 since they landed). Any other page that
marks a block  /* @prim:begin <name> */  is checked too: every kit rule must appear in that page and the marked
block may hold no rule the kit block lacks. A kit rule whose classes the page never uses in its markup may be
left out (public/good-audit-check.html drops the unused .section-label line that every molecule block carries).

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

SCAN = ("public", "_ARTIFACTS", "src")

def kit_blocks():
    out = {}
    for f in sorted(os.listdir(KIT)):
        if re.match(r'\d\d-.*\.html$', f):
            src = open(os.path.join(KIT, f), encoding="utf-8").read()
            lab = 'group="Instrument Lab"' in src.split("\n", 1)[0]
            for n, body in BLK.findall(src):
                out[n] = (f, body, lab)
    return out

def marked_pages():
    for top in SCAN:
        for d, _, fs in os.walk(os.path.join(ROOT, top)):
            if "node_modules" in d: continue
            for f in fs:
                p = os.path.join(d, f)
                if f.endswith(".html") and not (os.path.dirname(p) == KIT and re.match(r'\d\d-', f)):
                    src = open(p, encoding="utf-8", errors="replace").read()
                    if "@prim:begin" in src: yield os.path.relpath(p, ROOT), src

def main(a):
    page = open(PAGE, encoding="utf-8").read(); bad = 0; kb = kit_blocks()
    for rp, src in marked_pages():
        for n, body in BLK.findall(src):
            if n not in kb: bad += 1; print(f"✖ {rp}: marks {n}, which no kit file owns"); continue
            kl = [l for l in kb[n][1].split("\n") if l.strip()]
            extra = [l for l in body.split("\n") if l.strip() and l not in kl]
            body_html = src.split("</style>")[-1]
            used = lambda l: not re.findall(r"\.([\w-]+)", l.split("{")[0]) or any(re.search(r'class="[^"]*\b%s\b' % c, body_html) for c in re.findall(r"\.([\w-]+)", l.split("{")[0]))
            gone = [l for l in kl if l not in src and used(l)]
            if extra or gone: bad += 1; print(f"✖ {rp}: block {n} differs from {kb[n][0]}, first: {(extra or gone)[0][:80]}")
            else: print(f"✓ {rp}: {n} identical to the kit")
    for n, (f, body, lab) in kb.items():
        if not lab: continue
        lines = [l for l in body.split("\n") if l.strip()]
        missing = [l for l in lines if l not in page]
        if missing:
            bad += 1; print(f"✖ {n} ({f}): {len(missing)} rule(s) differ from the page, first: {missing[0][:90]}")
        else: print(f"✓ {n} ({f}): {len(lines)} rules identical in the page")
    if not kb: print("✖ no @prim blocks found"); return 1
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) if "--check" in sys.argv or len(sys.argv) == 1 else 2)
