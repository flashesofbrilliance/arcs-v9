#!/usr/bin/env python3
"""nftt_series: denote NFTT posts that are serialized, in every part, from one source.

Why this exists (2026-10-04): seven essays shipped together in PR #411 as one serialized thread,
isomorphic rather than chronological: the same methodological pipeline (name the mechanism, then
state plainly what would prove you wrong) run on seven different subjects. Only the last part
said so. The other six carried no series name, no part number, and no link to their siblings,
so a reader landing on any one of them could not see the thread.

SSOT: runtime/specs/nftt-series.json (part order and roles are the author's, from the series map
in tuning-into-the-distortion-field). This script writes two marked blocks into each part:
  1. a series line right after the byline: "The serialized thread · Part 4 of 7 · <tagline>",
     linking down to the panel
  2. the series panel right before <footer>: the method stated once, every part listed by its
     role, the current part marked, siblings linked
The index builder reads the same SSOT for its "Part N of 7" card tags.

Usage:
  python3 scripts/nftt_series.py stamp       # write/refresh the blocks in every part
  python3 scripts/nftt_series.py --check     # exit 1 if any part is missing or stale
  python3 scripts/nftt_series.py --self-test
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSOT = os.path.join(ROOT, "runtime", "specs", "nftt-series.json")
LINK = "color:var(--cyan-dim);text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:1px"
LINE_RE = re.compile(r"\n?\s*<!-- nftt-series:line -->.*?<!-- /nftt-series:line -->", re.S)
PANEL_RE = re.compile(r"\s*<!-- nftt-series:panel -->.*?<!-- /nftt-series:panel -->\n?", re.S)
BYLINE_RE = re.compile(r'(<p class="byline">.*?</p>)', re.S)
# The hand-written map tuning-into-the-distortion-field shipped with; the panel supersedes it.
LEGACY_RE = re.compile(r'\s*<div class="panel thread">\s*<h4>The serialized thread</h4>.*?</div>\s*<p>[^<]*</p>\s*</div>\n?', re.S)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load():
    with open(SSOT, encoding="utf-8") as f:
        return json.load(f)["series"]


def blocks(sid, series, slug):
    parts = series["parts"]
    n = next(i for i, p in enumerate(parts) if p["slug"] == slug) + 1
    line = (f'<!-- nftt-series:line --><p class="byline"><a href="#{sid}" style="color:inherit">'
            f'{esc(series["title"])} &middot; Part {n} of {len(parts)} &middot; {esc(series["tagline"])}'
            f'</a></p><!-- /nftt-series:line -->')
    rows = []
    for i, p in enumerate(parts, 1):
        k = f'<span class="k">{i} &middot; {esc(p["role"])}</span>'
        if p["slug"] == slug:
            rows.append(f'      {k}<b><em>{esc(p["title"])}</em>: you are here.</b>')
        else:
            rows.append(f'      {k}<b><a href="/blog/nftt/{p["slug"]}" style="{LINK}">{esc(p["title"])}</a>: {esc(p["gloss"])}</b>')
    panel = (f'<!-- nftt-series:panel -->\n  <div class="panel" id="{sid}">\n'
             f'    <h4>{esc(series["title"])} &middot; {esc(series["tagline"])}</h4>\n'
             f'    <p>{esc(series["method"])}</p>\n'
             f'    <div class="step">\n' + "\n".join(rows) + '\n    </div>\n'
             f'    <p>{esc(series["coda"])}</p>\n'
             f'  </div>\n  <!-- /nftt-series:panel -->')
    return line, panel


def stamp_text(html, sid, series, slug):
    line, panel = blocks(sid, series, slug)
    html = LINE_RE.sub("", html)
    html = PANEL_RE.sub("\n", html)
    html = LEGACY_RE.sub("\n", html)
    html, n1 = BYLINE_RE.subn(lambda m: m.group(1) + "\n    " + line, html, count=1)
    if n1 == 0:
        raise ValueError("no plain <p class=\"byline\"> to follow")
    i = html.find("  <footer>")
    if i < 0:
        raise ValueError("no <footer> to precede")
    html = html[:i].rstrip("\n ") + "\n\n  " + panel + "\n\n" + html[i:]
    return html


def path(slug):
    return os.path.join(ROOT, "public", f"blog-nftt-{slug}.html")


def each():
    for sid, series in load().items():
        for p in series["parts"]:
            yield sid, series, p["slug"]


def cmd_stamp():
    for sid, series, slug in each():
        with open(path(slug), encoding="utf-8") as f:
            before = f.read()
        after = stamp_text(before, sid, series, slug)
        if after != before:
            with open(path(slug), "w", encoding="utf-8") as f:
                f.write(after)
            print(f"[nftt-series] stamped {slug}")
    return 0


def cmd_check():
    bad = []
    for sid, series, slug in each():
        if not os.path.exists(path(slug)):
            bad.append(f"{slug}: listed in the series but has no post file")
            continue
        with open(path(slug), encoding="utf-8") as f:
            html = f.read()
        if stamp_text(html, sid, series, slug) != html:
            bad.append(f"{slug}: series line/panel missing or stale (run: nftt_series.py stamp)")
    for b in bad:
        print(f"[nftt-series] FAIL {b}", file=sys.stderr)
    if bad:
        return 1
    print(f"[nftt-series] check: {sum(1 for _ in each())} serialized parts current")
    return 0


def self_test():
    s = {"title": "T", "tagline": "one method", "method": "M.", "coda": "C.",
         "parts": [{"slug": "a", "role": "Origin", "title": "A", "gloss": "ga."},
                   {"slug": "b", "role": "Range", "title": "B", "gloss": "gb."}]}
    page = '<p class="byline">Published x</p>\n<section>body</section>\n  <footer>f</footer>'
    ok = 0
    once = stamp_text(page, "t", s, "b")
    ok += stamp_text(once, "t", s, "b") == once                         # idempotent
    ok += "Part 2 of 2" in once and once.count("<!-- nftt-series:panel -->") == 1
    ok += "<em>B</em>: you are here." in once and 'href="/blog/nftt/a"' in once
    ok += 'href="/blog/nftt/b"' not in once                              # never links to itself
    ok += once.index("nftt-series:line") > once.index("Published x")      # after the dated byline
    ok += once.index("nftt-series:panel") < once.index("<footer>")
    legacy = page.replace("  <footer>", '  <div class="panel thread">\n    <h4>The serialized thread</h4>\n'
                          '    <div class="step"><span class="k">x</span></div>\n    <p>old</p>\n  </div>\n\n  <footer>')
    ok += "panel thread" not in stamp_text(legacy, "t", s, "b")          # hand map superseded
    try:
        stamp_text("<footer>", "t", s, "a")
    except ValueError:
        ok += 1                                                          # no byline is loud
    ok_cli, n_cli = cli_self_test()
    ok += ok_cli
    total = 8 + n_cli
    print(f"[nftt-series] self-test {ok}/{total}")
    return 0 if ok == total else 1


def cli_self_test():
    """Run this script as a subprocess from a copy inside a throwaway repo (ROOT follows __file__,
    so the copy's ROOT is the temp dir). Asserts argv strictness and that look-only modes write nothing."""
    s = {"title": "T", "tagline": "one method", "method": "M.", "coda": "C.",
         "parts": [{"slug": "a", "role": "Origin", "title": "A", "gloss": "ga."},
                   {"slug": "b", "role": "Range", "title": "B", "gloss": "gb."}]}
    page = '<p class="byline">Published x</p>\n<section>body</section>\n  <footer>f</footer>'
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "scripts"))
        os.makedirs(os.path.join(tmp, "runtime", "specs"))
        os.makedirs(os.path.join(tmp, "public"))
        me = os.path.join(tmp, "scripts", "nftt_series.py")
        shutil.copy(os.path.abspath(__file__), me)
        with open(os.path.join(tmp, "runtime", "specs", "nftt-series.json"), "w") as f:
            json.dump({"series": {"t": s}}, f)
        for slug in ("a", "b"):
            with open(os.path.join(tmp, "public", f"blog-nftt-{slug}.html"), "w") as f:
                f.write(page)

        def snap():
            out = {}
            for d, _, fs in os.walk(tmp):
                for fn in fs:
                    fp = os.path.join(d, fn)
                    with open(fp, "rb") as f:
                        out[fp] = (os.stat(fp).st_mtime_ns, hashlib.sha256(f.read()).hexdigest())
            return out

        def run(*a):
            return subprocess.run([sys.executable, me, *a], cwd=tmp, capture_output=True, text=True).returncode

        def case(name, ok):
            results.append(ok)
            if not ok:
                print(f"[nftt-series] FAIL cli: {name}")

        base = snap()
        case("unknown flag exits 2", run("--bogus") == 2)
        case("unknown flag on stamp exits 2", run("stamp", "--bogus") == 2)
        case("extra positional on stamp exits 2", run("stamp", "extra") == 2)
        case("unknown command exits 2", run("stomp") == 2)
        case("no args exits 2", run() == 2)
        case("--check on stale fixture exits 1", run("--check") == 1)
        case("--check writes nothing", snap() == base)
        case("rejected argv writes nothing", snap() == base)
        case("real stamp exits 0", run("stamp") == 0)
        after = snap()
        case("real stamp writes the posts", after != base)
        case("--check after stamp exits 0", run("--check") == 0)
        case("--check on current fixture writes nothing", snap() == after)
    return sum(results), len(results)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="nftt_series.py", description="Denote serialized NFTT posts in every part.")
    ap.add_argument("--check", action="store_true", help="exit 1 if any part is missing or stale (writes nothing)")
    ap.add_argument("--self-test", action="store_true", help="run the built-in tests (writes only to a temp dir)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("stamp", help="write/refresh the blocks in every part")
    args = ap.parse_args(argv)
    # Precedence kept from the hand parser: --self-test, then --check, then the subcommand.
    if args.self_test:
        return self_test()
    if args.check:
        return cmd_check()
    if args.cmd == "stamp":
        return cmd_stamp()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
