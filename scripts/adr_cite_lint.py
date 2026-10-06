#!/usr/bin/env python3
"""adr_cite_lint: flag bare ADR-0NN citations whose surrounding text shares no vocabulary with that ADR.

integrity_gate already proves a cited ADR EXISTS. It cannot tell that `flight-manual:16` cites
ADR-032 (zero-trust) for Brief rendering. This is the cheap mechanical half of that check: for each
line citing exactly one or two ADRs, compare the line's words with the cited ADR's title and
opening section. No overlap at all -> SUSPECT, for a human to read. Report only; never edits.

It is a heuristic with false positives (a cite can be about the decision, not the topic words).
Lines citing three or more ADRs are skipped (lists). Stdlib only.

  python3 scripts/adr_cite_lint.py [FILES...]        # default: tracked .md/.html under repo root dirs
  python3 scripts/adr_cite_lint.py --self-test
"""
import argparse, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ADR_RE = re.compile(r"\bADR-0*(\d{1,3})\b")
WORD = re.compile(r"[a-z][a-z-]{4,}")
STOP = set("""about above after again against agent agents because before being between could decision
decisions design during every first found further governing great having itself their there these
those through under until using where which while would status context should shall other
""".split())
SKIP_PREFIX = ("_DECISIONS/", "_ARCHIVE/", "_RELEASES/", "node_modules/", ".next/")


def words(text):
    return {w for w in WORD.findall(text.lower()) if w not in STOP}


def load_adrs():
    out = {}
    d = os.path.join(ROOT, "_DECISIONS")
    for f in os.listdir(d):
        m = re.match(r"ADR-0*(\d{1,3})-", f)
        if not m or not f.endswith(".md"):
            continue
        head = "".join(open(os.path.join(d, f), errors="replace").readlines()[:60])
        out[int(m.group(1))] = (f, words(f.replace("-", " ") + " " + head))
    return out


def lint_text(path, text, adrs):
    sus = []
    for i, line in enumerate(text.splitlines(), 1):
        nums = {int(n) for n in ADR_RE.findall(line)}
        if not nums or len(nums) > 2:
            continue
        ctx = words(ADR_RE.sub(" ", line))
        if len(ctx) < 4:
            continue
        for n in sorted(nums):
            if n not in adrs:
                continue
            if not (ctx & adrs[n][1]):
                sus.append((path, i, f"ADR-{n:03d}", adrs[n][0], line.strip()[:140]))
    return sus


def tracked():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "*.md", "*.html"], capture_output=True, text=True).stdout
    return [f for f in out.split("\n") if f and not f.startswith(SKIP_PREFIX)]


def self_test():
    adrs = {32: ("ADR-032-zero-trust-posture.md", words("zero trust posture threat surface identities"))}
    bad = lint_text("x.md", "The Brief rendering path follows ADR-032 for layout of the cartography output.", adrs)
    good = lint_text("x.md", "Public surfaces follow the zero trust posture in ADR-032 for every new route.", adrs)
    assert len(bad) == 1, bad          # fail-on-bad: the known flight-manual shape is flagged
    assert not good, good              # pass-on-good: a topical cite is not
    print("adr_cite_lint self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    adrs = load_adrs()
    files = a.files or tracked()
    total = 0
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(ROOT, f)
        try:
            text = open(p, errors="replace").read()
        except OSError:
            continue
        for path, ln, cite, adrfile, ctx in lint_text(os.path.relpath(p, ROOT), text, adrs):
            total += 1
            print(f"{path}:{ln}  {cite} ({adrfile}) shares no words with: {ctx}")
    print(f"adr_cite_lint: {total} suspect cite(s) in {len(files)} file(s); report only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
