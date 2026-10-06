#!/usr/bin/env python3
"""resume_location_gate.py: every resume / cover letter / ATS artifact's location line reads exactly
"New York Metro" (memory resume-location-new-york-metro-only). Frustration Gate for the class that
propagated "Fully remote (US)" and "New York City (on site 3 days)" through forge cuts via
edit-from-seed (2026-10-05); extended to cover letters and non-forge resumes the same day.

  python3 scripts/resume_location_gate.py                # check every in-scope file (exit 1 on any miss)
  python3 scripts/resume_location_gate.py FILE...         # check just these (pre-commit passes staged files)
  python3 scripts/resume_location_gate.py --fix [FILE...] # rewrite offending lines to "New York Metro"

Scope: resume / cover files (.html, .txt) one folder under _ARTIFACTS/, and in public/,
that carry Zach's email (someone else's resume, e.g. Saul's, is never touched).
What counts as the location:
  .html  the first segment of the contact block, up to <br> or " | " (tags stripped). A block that
         opens with the email, LinkedIn or GitHub has no location, which is fine.
  .txt   in the header only (lines above the email line): a line, or its first " | " / " · " segment,
         that starts like a location (New York / NYC / Remote / Fully remote / Hybrid / On site) or
         names Fairfield. Job lines lower down ("New York, Behavioral Health") are not looked at.
"""
import glob
import os
import re
import sys

WANT = "New York Metro"
EMAIL = "zach.harris@gmail.com"
HTML_RE = re.compile(r'(<div class="contact">\s*)((?:(?!<br|\|)[^\n])*?)(\s*(?:<br>|\|))')
LOC_RE = re.compile(r"^(?:New York|NYC|Fully remote|Remote|Hybrid|On[- ]site)\b|Fairfield", re.I)
SEP_RE = re.compile(r"(\s+[|·]\s+)")
TAG_RE = re.compile(r"<[^>]+>")
GLOBS = ["_ARTIFACTS/*/*resume*", "_ARTIFACTS/*/*cover*", "public/*resume*", "public/*cover*"]


def in_scope(f):
    if not f.endswith((".html", ".txt")):
        return False
    name = os.path.basename(f)
    return "resume" in name or "cover" in name


def default_files():
    out = set()
    for g in GLOBS:
        out |= {f for f in glob.glob(g) if in_scope(f)}
    return sorted(out)


def fix_html(src, bad):
    def sub(m):
        text = TAG_RE.sub("", m.group(2)).strip()
        if not text or "@" in text or re.match(r"(linkedin|github)\.", text, re.I):
            return m.group(0)
        if text != WANT:
            bad.append(text)
            return m.group(1) + WANT + m.group(3)
        return m.group(0)
    return HTML_RE.sub(sub, src, count=1)


def fix_txt(src, bad):
    lines = src.split("\n")
    end = next((i for i, l in enumerate(lines) if EMAIL in l), min(len(lines), 12))
    for i in range(min(end + 1, len(lines))):
        parts = SEP_RE.split(lines[i])
        head = parts[0]
        loc = head.strip()
        if loc and LOC_RE.search(loc) and loc != WANT:
            bad.append(loc)
            parts[0] = head[: len(head) - len(head.lstrip())] + WANT
            lines[i] = "".join(parts)
    return "\n".join(lines)


def check(path, fix):
    src = open(path, encoding="utf-8").read()
    if EMAIL not in src:
        return []
    bad = []
    new = fix_html(src, bad) if path.endswith(".html") else fix_txt(src, bad)
    if fix and bad:
        open(path, "w", encoding="utf-8").write(new)
    return bad


def main(argv):
    fix = "--fix" in argv
    files = [a for a in argv if not a.startswith("--")]
    files = [f for f in files if in_scope(f) and os.path.exists(f)] if files else default_files()
    fails = 0
    for f in files:
        for loc in check(f, fix):
            fails += 1
            print(f"{'FIXED' if fix else 'FAIL'} {f}: location {loc!r} (want {WANT!r})")
    if fails and not fix:
        print(f"resume-location gate: {fails} line(s) off-rule; run with --fix", file=sys.stderr)
        return 1
    print(f"resume-location gate: {len(files)} file(s) checked, {fails} {'fixed' if fix else 'off-rule'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
