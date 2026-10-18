#!/usr/bin/env python3
"""Fail when a resume/cover/page claims the ARCS repo or commit trail is public.

arcs-v9 and perplexity-mcp are private (gh api verified 2026-10-14). Public repos:
germinate, rosetta-shell, resume-tailor-skill. Usage: public_claim_gate.py FILE...
Exit 1 on any hit. stdlib only.
"""
import re, sys

BAD = re.compile(r"public commit trail|public repo\b|public GitHub (?:repo|commit)|a live commit trail", re.I)
OK_NEAR = re.compile(r"germinate|rosetta|resume-tailor", re.I)

def main(paths):
    bad = 0
    for p in paths:
        try:
            text = open(p, encoding="utf-8").read()
        except OSError:
            continue
        for m in BAD.finditer(text):
            ctx = text[max(0, m.start() - 80):m.end() + 80]
            if OK_NEAR.search(ctx):
                continue
            bad += 1
            print(f"{p}: '{m.group(0)}' -- arcs-v9 is private; say 'live app (app.arcs.care), commit history on request'", file=sys.stderr)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
