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
  python3 scripts/kit_primitive_sync.py --kit            exit 1 if a "composed with" copy is stale or a part breaks ds-parity.json
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

def composed_check(kb):
    bad = 0
    # Kit parts that copy another part's rules for their own preview say so in one comment,
    # "/* composed with, from 28-chip, 32-evidence-ref and 37-fidelity-grain */". Each named block's
    # rules it carries must match the source word for word, so a fix to the source part cannot leave stale copies behind
    # (2026-11-13: nine parts kept the pre-design-system chip after 28 changed).
    for f in sorted(os.listdir(KIT)):
        if not re.match(r'\d\d-.*\.html$', f): continue
        src = open(os.path.join(KIT, f), encoding="utf-8").read()
        for m in re.finditer(r'/\* composed with, from ([^*]+?) \*/', src):
            for n in re.split(r',\s*|\s+and\s+', m.group(1).strip()):
                if n not in kb: bad += 1; print(f"✖ {f}: composed with {n}, which no kit file owns"); continue
                # a copy may leave rules out; a rule it does carry (same selector) must match the source word for word
                kit_rules = {l.split("{")[0].strip(): l for l in kb[n][1].split("\n") if "{" in l and not l.startswith(".section-label")}
                stale = [kit_rules[l.split("{")[0].strip()] for l in src.split("\n") if "{" in l and l.split("{")[0].strip() in kit_rules and l != kit_rules[l.split("{")[0].strip()]]
                if stale: bad += 1; print(f"✖ {f}: its copy of {n} differs from {kb[n][0]}, first: {stale[0][:80]}")
    return bad

def parity_check(kb):
    """Each part listed in ds-parity.json must carry the design-system declarations it names."""
    import json
    spec = json.load(open(os.path.join(KIT, "ds-parity.json"), encoding="utf-8"))["parts"]; bad = 0
    for n, sp in spec.items():
        if n not in kb: bad += 1; print(f"✖ ds-parity names {n}, which no kit file owns"); continue
        rules = {l.split("{")[0].strip(): l.split("{", 1)[1] for l in kb[n][1].split("\n") if "{" in l}
        for sel, decls in sp["rules"].items():
            if sel not in rules: bad += 1; print(f"✖ {n}: no {sel} rule ({sp['component']})"); continue
            have = {k.strip(): v.strip() for k, _, v in (d.partition(":") for d in rules[sel].rstrip(" }").split(";")) if v.strip()}
            for k, v in decls.items():
                if have.get(k) != v: bad += 1; print(f"✖ {n} {sel}: {k} is {have.get(k)!r}, design system says {v!r} ({sp['component']})")
    return bad

def boxsize_check(kb):
    """A rule with a fixed px height and a border must be border-box, or the border adds 2px to the
    height on every page that inlines it (no page, _tokens.css or part sets a global box-sizing).
    2026-11-13: the 22px design-system chip measured 24px on the Gravity pages for exactly this reason."""
    # Known debt (2026-11-13), allowed so the gate fails only on new cases: renders 2px over its stated size on every
    # page that inlines it. Remove a selector here in the same change that makes it border-box. (The first list also
    # held .shnav-menu, .dprefs-aa, .dprefs-theme and .toast-close: all are <button>s, which browsers already size
    # border-box, measured 48x48 and 44x44 in Chrome on 2026-11-13; two also have border: 0. They were false flags.)
    KNOWN = {("60-heat-take", ".heat-pips b")}
    UA_BORDER_BOX = {"button", "input", "select", "textarea"}
    bad = 0
    for n, (f, body, _) in kb.items():
        markup = open(os.path.join(KIT, f), encoding="utf-8").read()
        for l in body.split("\n"):
            if "{" not in l or (n, l.split("{")[0].strip()) in KNOWN: continue
            sel, d = l.split("{", 1)
            cls = re.findall(r'\.([\w-]+)', sel.split(",")[0].split()[-1]) if sel.strip() else []
            tags = {t.lower() for c in cls[:1] for t in re.findall(r'<(\w+)[^>]*class="[^"]*\b' + re.escape(c) + r'\b', markup)}
            if tags and tags <= UA_BORDER_BOX: continue  # browsers size these border-box already
            if re.search(r'(^|[;{\s])height:\s*\d+px', d) and re.search(r'(^|[;{\s])border(-width)?:(?!\s*(none|0)\b)', d) and "box-sizing: border-box" not in d:
                bad += 1; print(f"✖ {n} ({f}): fixed height with a border but no box-sizing: border-box, so it renders 2px taller: {l.strip()[:80]}")
    return bad

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
    bad += composed_check(kb)
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
    if "--kit" in sys.argv:  # kit-internal only (composed copies + design-system parity); pre-commit runs it on any kit part change
        kb = kit_blocks(); n = composed_check(kb) + parity_check(kb) + boxsize_check(kb)
        print("✓ composed copies match their source parts; listed parts match the design system; fixed heights are border-box" if not n else f"✖ {n} kit finding(s)"); sys.exit(1 if n else 0)
    sys.exit(main(sys.argv[1:]) if "--check" in sys.argv or len(sys.argv) == 1 else 2)
