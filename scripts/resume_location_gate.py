#!/usr/bin/env python3
"""resume_location_gate.py: every resume / ATS artifact's location line reads exactly
"New York Metro" (memory resume-location-new-york-metro-only). Frustration Gate for the
class that propagated "Fully remote (US)" and "New York City (on site 3 days)" through
31+ forge cuts via edit-from-seed (2026-10-05).

  python3 scripts/resume_location_gate.py               # check every forge resume (exit 1 on any miss)
  python3 scripts/resume_location_gate.py FILE...        # check just these (pre-commit passes staged files)
  python3 scripts/resume_location_gate.py --fix [FILE...] # rewrite offending lines to "New York Metro"

What counts as the location line:
  .html  the first <br>-terminated text of the contact block (a block that opens with the email = no location, fine)
  .txt   any whole line that starts like a location (New York / NYC / Remote / Fully remote /
         Hybrid / On site) or names Fairfield; it must equal "New York Metro"
"""
import glob
import os
import re
import sys

WANT = "New York Metro"
HTML_RE = re.compile(r'(<div class="contact">\s*)([^<\n]*?)(\s*<br>)')
TXT_RE = re.compile(r"^(\s*)((?:New York|NYC|Fully remote|Remote|Hybrid|On[- ]site)\b.*|.*Fairfield.*)$",
                    re.I | re.M)


def default_files():
    out = []
    for ext in ("html", "txt"):
        out += glob.glob(f"_ARTIFACTS/forge-*/resume-*.{ext}")
    return sorted(out)


def in_scope(f):
    name = f.rsplit("/", 1)[-1]
    return name.startswith("resume-") and f.endswith((".html", ".txt"))


def check(path, fix):
    src = open(path, encoding="utf-8").read()
    bad = []
    if path.endswith(".html"):
        def sub(m):
            loc = m.group(2).strip()
            if loc and loc != WANT:
                bad.append(loc)
                return m.group(1) + WANT + m.group(3)
            return m.group(0)
        new = HTML_RE.sub(sub, src)
    else:
        def sub(m):
            if m.group(2).strip() != WANT:
                bad.append(m.group(2).strip())
                return m.group(1) + WANT
            return m.group(0)
        new = TXT_RE.sub(sub, src)
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
