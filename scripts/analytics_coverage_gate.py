#!/usr/bin/env python3
"""analytics_coverage_gate: every served public/*.html must carry the Vercel Web Analytics snippet.

Why this exists (banked 2026-09-26): leak_check.sh already asserts whole-tree analytics coverage,
but that assertion sits MID-CASCADE (it only runs once the internal-marker leak gate passes) and
there is no commit-time check, so a brand-new public page ships WITHOUT the snippet and nobody
notices until the cascade is otherwise green. That is exactly how public/good-fears.html landed
uncovered days after a 65-page coverage sweep. This is the Frustration Gate for that class
(AGENTS.md #15): the cheapest mechanical check that FAILS a NEW public page missing the snippet,
wired into the always-run pre-commit path, so the coverage gap cannot re-open one page at a time.

Contract: a served page carries analytics iff its HTML contains one of the canonical markers
(kept in sync with leak_check.sh's analytics gate):
    /_vercel/insights   |   va.vercel-scripts   |   @vercel/analytics
The canonical snippet is:  <script defer src="/_vercel/insights/script.js"></script>
(before </head> on wrapped pages; at EOF on bare-fragment pages that have no <head>).

SCOPE: files under public/ ending in .html. Nothing is exempt — the gate mirrors leak_check's
"every external surface is instrumented" policy. If a genuine exemption ever arises, add it to
EXEMPT with a why (as nftt_meta_gate.py does for its listing page).

PRE-COMMIT POSTURE: ADDED-only (see scripts/git-hooks/pre-commit). The repo's pre-existing
uncovered pages (being cleared in a separate sweep) must NOT block an unrelated edit to a legacy
page, so the hook gates only brand-new public pages — the recurrence population. The whole-tree
assertion for the existing corpus stays in leak_check.sh. `--all` here is for CI / manual sweeps
and goes green once the corpus is fully covered.

Usage:
  python3 scripts/analytics_coverage_gate.py <file.html> [...]   # per-file (pre-commit on new pages)
  python3 scripts/analytics_coverage_gate.py --all               # sweep every public/**/*.html
  python3 scripts/analytics_coverage_gate.py --self-test         # fail-on-bad + pass-on-good
Exit 0 = all checked files carry the snippet; 1 = at least one is missing it.
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEMPT = set()  # e.g. {"public/some-redirect-stub.html"} — none today (mirror leak_check policy)
SNIPPET_RE = re.compile(r"_vercel/insights|va\.vercel-scripts|@vercel/analytics")
SUGGESTED = '<script defer src="/_vercel/insights/script.js"></script>'


def missing_snippet(text):
    """True iff the page carries NO analytics marker."""
    return not SNIPPET_RE.search(text)


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
        # only gate served HTML under public/; ignore anything else a glob/hook hands in
        if "--self-test" not in sys.argv and not (r.startswith("public/") and r.endswith(".html")):
            continue
        try:
            text = open(p, encoding="utf-8").read()
        except OSError as e:
            print(f"[skip] {r}: {e}", file=sys.stderr)
            continue
        if missing_snippet(text):
            bad = True
            print(f"GATE FAIL: {r}: missing the Vercel analytics snippet", file=sys.stderr)
            print(f"    add before </head> (or at EOF if the page has no <head>): {SUGGESTED}", file=sys.stderr)
    return 1 if bad else 0


def self_test():
    good = [
        '<head><script defer src="/_vercel/insights/script.js"></script></head>',
        '<title>x</title>\n...\n<script defer src="/_vercel/insights/script.js"></script>',  # fragment/EOF
        '<script src="https://va.vercel-scripts.com/v1/script.js"></script>',
        'import { Analytics } from "@vercel/analytics/react";',
    ]
    for g in good:
        assert not missing_snippet(g), f"good sample should pass: {g!r}"
    for bad in ['<head><title>x</title></head><body>no analytics here</body>', '']:
        assert missing_snippet(bad), f"bad sample should fail: {bad!r}"
    print("self-test OK: fail-on-bad + pass-on-good")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if "--all" in argv:
        paths = sorted(
            glob.glob(os.path.join(ROOT, "public", "**", "*.html"), recursive=True)
        )
    else:
        paths = [a for a in argv[1:] if not a.startswith("-")]
    if not paths:
        print("usage: analytics_coverage_gate.py <file.html> [...] | --all | --self-test", file=sys.stderr)
        return 0
    return check(paths)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
