#!/usr/bin/env python3
# nftt_dropcap_lint.py — catch the drop-cap "eats the space" render bug.
# A .lead paragraph is drop-capped: the rest of the FIRST WORD hugs the big
# letter (correct: "The" -> "T"+"he"). If the first word is a SINGLE LETTER
# ("A", "I"), the next word hugs the cap with no space -> "Achangelog". This
# is invisible in source (the space is there) but wrong in render, so we flag
# the exact failure condition: a .lead whose first word is one letter and is
# followed by another word. Fix: make the space non-collapsing (&#160;) right
# after the single letter, or reword so the first word is multi-letter.
import re, sys, glob
bad = []
for f in sys.argv[1:] or glob.glob("public/blog-nftt-*.html"):
    html = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<p class="lead">\s*([^<\s]+)\s+(\S)', html):
        first = m.group(1)
        # already fixed if the char right after the single letter is a non-breaking space
        if len(first) == 1 and first.isalpha():
            after = html[m.start(1)+1: m.start(1)+7]
            if not after.lstrip().startswith("&#160;") and not after.lstrip().startswith("&nbsp;"):
                bad.append((f, first))
for f, w in bad:
    print(f"DROPCAP-SPACE: {f} — .lead starts with single letter '{w}'; drop-cap will eat the space")
print(f"{'FAIL' if bad else 'OK'}: {len(bad)} drop-cap space risk(s)")
sys.exit(1 if bad else 0)
