#!/usr/bin/env python3
"""nftt_meta_gate: enforce the NFTT post head-meta contract across blog-nftt-*.html.

Why this exists (banked 2026-09-26): nftt-gates.sh checks a post's title suffix, description
meta and robots meta, but it runs ONE FILE AT A TIME (on the page being touched), so the ~9
posts + fragments that PREDATE the gate silently carried the gap for months -- each only trips
the gate when someone happens to edit it (exactly how take-home-trap-dossier's gap surfaced).
This is the Frustration Gate for that class (AGENTS.md #15): the cheapest mechanical check that
FAILS the whole class, wired into the always-run pre-commit path, so a NEW or edited NFTT page
cannot ship without the head-meta and legacy gaps cannot re-open.

Contract (mirrors nftt-gates.sh steps 2-3, kept in sync):
  1. <title>...· NFTT</title>     -- the family suffix (U+00B7 middot + ' NFTT')
  2. <meta name="description" content="..."> with >= 10 chars
  3. <meta name="robots" ...>      -- presence only; VALUE is intentional per page
     (public posts index; the redacted recon-report fragments + the HUD stay noindex -- this
     gate must never push them to index, so it checks presence, not value).

EXEMPT: public/blog-nftt-index.html -- the listing page, not an NFTT post; its '· ARCS' title
is deliberate. Exempting it here (rather than forcing a redundant 'Notes from the Trenches ·
NFTT') is the honest call.

Usage:
  python3 scripts/nftt_meta_gate.py <file.html> [...]   # per-file (pre-commit on staged posts)
  python3 scripts/nftt_meta_gate.py --all               # sweep every public/blog-nftt-*.html
  python3 scripts/nftt_meta_gate.py --self-test         # fail-on-bad + pass-on-good
Exit 0 = all checked files conform; 1 = at least one violation.
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEMPT = {"public/blog-nftt-index.html"}
TITLE_RE = re.compile(r"<title>.*· NFTT</title>")
DESC_RE = re.compile(r'<meta name="description" content="[^"]{10,}"')
ROBOTS_RE = re.compile(r'<meta name="robots"')


def violations(text):
    out = []
    if not TITLE_RE.search(text):
        out.append("title missing '· NFTT' suffix")
    if not DESC_RE.search(text):
        out.append("description meta missing or too short (>=10 chars)")
    if not ROBOTS_RE.search(text):
        out.append("robots meta missing")
    return out


def rel(path):
    try:
        return os.path.relpath(os.path.abspath(path), ROOT)
    except ValueError:
        return path


def check(paths):
    bad = False
    for p in paths:
        r = rel(p)
        if r in EXEMPT:
            continue
        if os.path.basename(r).startswith("blog-nftt-") is False and "--self-test" not in sys.argv:
            # only gate NFTT pages; ignore anything else handed in by a glob
            continue
        try:
            text = open(p, encoding="utf-8").read()
        except OSError as e:
            print(f"[skip] {r}: {e}", file=sys.stderr)
            continue
        vs = violations(text)
        if vs:
            bad = True
            for v in vs:
                print(f"GATE FAIL: {r}: {v}", file=sys.stderr)
    return 1 if bad else 0


def self_test():
    good = '<title>X · NFTT</title>\n<meta name="description" content="A real ten-plus char summary.">\n<meta name="robots" content="index">'
    assert violations(good) == [], "good sample should pass"
    for bad in [
        '<title>X</title>\n<meta name="description" content="long enough here">\n<meta name="robots" content="index">',
        '<title>X · NFTT</title>\n<meta name="robots" content="index">',
        '<title>X · NFTT</title>\n<meta name="description" content="short">\n<meta name="robots" content="index">',
        '<title>X · NFTT</title>\n<meta name="description" content="long enough summary text">',
    ]:
        assert violations(bad), f"bad sample should fail: {bad!r}"
    print("self-test OK: fail-on-bad + pass-on-good")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--all" in argv:
        paths = sorted(glob.glob(os.path.join(ROOT, "public", "blog-nftt-*.html")))
    else:
        paths = [a for a in argv[1:] if not a.startswith("-")]
    if not paths:
        print("usage: nftt_meta_gate.py <file.html> [...] | --all | --self-test", file=sys.stderr)
        return 0
    return check(paths)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
