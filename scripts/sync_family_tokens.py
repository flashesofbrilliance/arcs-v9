#!/usr/bin/env python3
"""
sync_family_tokens.py — one canonical token source for the arcs.care family surfaces.

The standalone public/*.html family pages (build/good/playground/status/...) each carry
their own inline :root token block, hand-copied and drifted (see --audit). This wires them
to ONE source of truth without a runtime <link> (which the subdomain host-catch-all rewrites
would swallow, and which can't be verified offline).

SSOT: public/observatory/colors_and_type.css  →  its :root{...} declarations.

sync (default): injects/updates a marked, generated token block near the top of each page's
  first <style>. Idempotent (re-runs replace between the markers). "Wire, don't restyle":
  the block is inserted BEFORE the page's own :root, so the page's existing values still win
  the cascade — nothing changes appearance. Adoption is the offline step: delete a page's own
  redundant canonical declarations and the generated block takes over.

audit (--audit): reports hex colors used OUTSIDE the generated block that aren't in the
  canonical palette — i.e. each page's real drift / local extensions. This IS the conformance
  tripwire: exit 1 if any page carries off-canonical hues outside its markers.

Usage:
  python3 scripts/sync_family_tokens.py                 # sync all present family pages
  python3 scripts/sync_family_tokens.py --only build.html
  python3 scripts/sync_family_tokens.py --audit         # drift report (tripwire; nonzero on drift)
  python3 scripts/sync_family_tokens.py --check         # verify blocks are up to date (CI), no write
"""
import os, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSOT = os.path.join(ROOT, "public", "observatory", "colors_and_type.css")

# The family of standalone public pages that should share the canonical palette.
# Add good.html / germinate.html / arcs-field-scan.html when running the main-side rollout.
FAMILY = [
    "build.html", "playground.html", "status.html", "chan.html",
    "forge-pattern.html", "forge-cut.html", "good.html",
    "germinate.html", "arcs-field-scan.html",
]

START = "/* @family-tokens:start — generated from public/observatory/colors_and_type.css; edit the SSOT + run scripts/sync_family_tokens.py, not here */"
END = "/* @family-tokens:end */"

def parse_ssot():
    """Return (declarations_text, canonical_hexes) from the SSOT :root block."""
    css = open(SSOT, encoding="utf-8").read()
    m = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    if not m:
        sys.exit("could not find :root{} in SSOT " + SSOT)
    body = m.group(1)
    # keep only "--name: value;" declarations, strip comments/blank lines, one per line
    decls = []
    for raw in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body):
        name, val = raw[0], " ".join(raw[1].split())
        decls.append(f"  {name}: {val};")
    hexes = {h.lower() for h in re.findall(r"#[0-9A-Fa-f]{6}\b", body)}
    return "\n".join(decls), hexes

def generated_block(decls):
    return f"{START}\n:root{{\n{decls}\n}}\n{END}"

def page_path(name):
    return os.path.join(ROOT, "public", name)

def sync_page(name, block, write=True):
    """Insert/replace the generated block. Returns 'created'|'updated'|'noop'|'missing'|'nostyle'."""
    p = page_path(name)
    if not os.path.exists(p):
        return "missing"
    html = open(p, encoding="utf-8").read()
    existing = re.search(re.escape(START) + r".*?" + re.escape(END), html, re.S)
    if existing:
        if existing.group(0) == block:
            return "noop"
        new = html[:existing.start()] + block + html[existing.end():]
    else:
        m = re.search(r"<style>\s*\n", html)
        if not m:
            return "nostyle"
        new = html[:m.end()] + block + "\n" + html[m.end():]
    if write and new != html:
        open(p, "w", encoding="utf-8").write(new)
    return "updated" if existing else "created"

def audit_page(name, canon):
    """Hexes outside the generated block that aren't canonical. Returns sorted list."""
    p = page_path(name)
    if not os.path.exists(p):
        return None
    html = open(p, encoding="utf-8").read()
    outside = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
    used = {h.lower() for h in re.findall(r"#[0-9A-Fa-f]{6}\b", outside)}
    return sorted(h for h in used if h not in canon)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="operate on a single page (e.g. build.html)")
    ap.add_argument("--audit", action="store_true", help="report off-canonical hex outside markers (tripwire)")
    ap.add_argument("--check", action="store_true", help="verify blocks are current; write nothing; exit 1 if stale")
    args = ap.parse_args()

    decls, canon = parse_ssot()
    block = generated_block(decls)
    pages = [args.only] if args.only else FAMILY

    if args.audit:
        drift = 0
        print("== family token drift (hex outside the generated block, not canonical) ==")
        for name in pages:
            res = audit_page(name, canon)
            if res is None:
                continue
            flag = f"{len(res)} off-token" if res else "clean"
            print(f"  {name:22} {flag}" + (("  " + ", ".join(res)) if res else ""))
            drift += len(res)
        print(f"-- {drift} off-canonical hue(s) across family --")
        sys.exit(1 if drift else 0)

    stale = 0
    for name in pages:
        st = sync_page(name, block, write=not args.check)
        if st in ("created", "updated"):
            stale += 1
        print(f"  {name:22} {st}")
    if args.check and stale:
        print(f"-- {stale} page(s) have stale token blocks; run without --check --")
        sys.exit(1)

if __name__ == "__main__":
    main()
