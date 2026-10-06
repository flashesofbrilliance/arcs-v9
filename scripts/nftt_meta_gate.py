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
  4. at most one <h1> -- a post is one essay (the loop HUD carries none, by design). Added 2026-09-30 after a clone that cut the
     template at a <body> tag the platinum master never writes: the new post shipped with
     the whole take-home-trap essay above it, and every other gate passed.
  5. every class used in the body is defined in the page's own <style>, and every link inside a
     paragraph is styled (inline style=, or a CSS rule for paragraph links). Added 2026-09-30: a
     post mixed one template's head with another's body, so its masthead class had no CSS and
     its inline link rendered browser-default blue; every other gate passed.
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
H1_RE = re.compile(r"<h1[\s>]")
STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
CLASS_RE = re.compile(r'class="([^"]+)"')
P_RE = re.compile(r"<p[\s>].*?</p>", re.S)
# a link rule counts unless it is scoped to chrome (.more, footer, nav, masthead)
LINK_SEL_RE = re.compile(r"(?:^|[,}])\s*([^{},]*?)(?<![\w-])a(?::[\w-]+)?\s*(?=[{,])")
CHROME = (".more", "footer", "nav", ".topbar", ".cls")


def has_body_link_rule(css):
    return any(not any(c in m.group(1) for c in CHROME) for m in LINK_SEL_RE.finditer(css))


def style_violations(text):
    out = []
    css = " ".join(STYLE_RE.findall(text))
    end = text.rfind("</style>")
    body = text[end:] if end >= 0 else text
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    def styled(c):
        return re.search(r"\." + re.escape(c) + r"(?![\w-])", css)
    # an element fails only when NONE of its classes has a rule (a bare modifier beside a
    # styled class, like "arc arc-ladder", is fine)
    undefined = sorted({m for m in CLASS_RE.findall(body) if not any(styled(c) for c in m.split())})
    if undefined:
        out.append("elements whose classes have no CSS in this page: " + ", ".join(undefined))
    if not has_body_link_rule(css):
        body = re.sub(r'<(div|p) class="more">.*?</\1>|<footer.*?</footer>', "", body, flags=re.S)
        bare = [a for par in P_RE.findall(body) for a in re.findall(r"<a\s[^>]*>", par) if "style=" not in a and "class=" not in a]
        if bare:
            out.append(f"{len(bare)} unstyled link(s) inside paragraphs render browser-default blue")
    return out


def violations(text):
    out = []
    if not TITLE_RE.search(text):
        out.append("title missing '· NFTT' suffix")
    if not DESC_RE.search(text):
        out.append("description meta missing or too short (>=10 chars)")
    if not ROBOTS_RE.search(text):
        out.append("robots meta missing")
    n_h1 = len(H1_RE.findall(text))
    if n_h1 > 1:
        out.append(f"found {n_h1} <h1> tags: a second essay body is pasted into this page")
    return out + style_violations(text)


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
    good = '<title>X · NFTT</title>\n<meta name="description" content="A real ten-plus char summary.">\n<meta name="robots" content="index">\n<h1>One</h1>'
    assert violations(good) == [], "good sample should pass"
    assert violations('<style>.cls{} p a{color:red}</style>' + good + '<div class="cls"><p><a href="/x">x</a></p></div>') == [], "styled page should pass"
    assert violations('<style>.x{}</style>' + good + '<p><a href="/x" style="color:red">x</a></p>') == [], "inline-styled link should pass"
    for bad in [
        '<title>X</title>\n<meta name="description" content="long enough here">\n<meta name="robots" content="index">',
        '<title>X · NFTT</title>\n<meta name="robots" content="index">',
        '<title>X · NFTT</title>\n<meta name="description" content="short">\n<meta name="robots" content="index">',
        '<title>X · NFTT</title>\n<meta name="description" content="long enough summary text">',
        good + '\n<h1>A second essay pasted in</h1>',
        '<style>.hero{}</style>' + good + '<div class="topbar"></div>',
        '<style>.hero{}</style>' + good + '<p>see <a href="/x">x</a></p>',
        '<style>.more a{color:red}</style>' + good + '<p>see <a href="/x">x</a></p>',
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
