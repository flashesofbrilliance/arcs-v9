#!/usr/bin/env python3
"""token_source_gate: single-file HTML surfaces inherit the ARCS tokens, they do not re-author them.

Class it blocks (2026-09-11): an artifact ships its own hex palette block under its own variable
names (e.g. --palette-bearing:#00F0FF) instead of carrying src/ui-kit/recoil-report/_tokens.css.
Three files did this (profile-scan-hud, target-role-scan-hud, and the first cut of the
manufactured-role post-mortem), so the one palette lived in four places with two vocabularies.
The fieldos design-system memory says "do not re-derive"; this makes re-deriving un-committable.

Rule (deterministic, stdlib-only):
  A checked HTML file that paints ANY ARCS signal hex (#00F0FF #00FF9D #FFD700 #FF4D6D, case-
  insensitive) inside a CSS custom-property definition MUST either
    (a) <link rel="stylesheet" href="_tokens.css"> (kit primitives), or
    (b) inline _tokens.css verbatim, detected by its sentinel header line
        "/* ARCS Recoil Report — Design Tokens */" (self-contained artifacts).
  Otherwise FAIL, and any non-canonical variable name carrying a signal hex is listed.
  Files with no signal hex in a custom property are PASS (not an ARCS-palette surface).

Ratchet (like the informativeness gate): when run with --ratchet <HEAD-version-path>, a file
whose HEAD version already violated is WARN, not FAIL, so legacy pages stay editable while new
violations cannot be born. The pre-commit block passes the HEAD blob for modified files.

Usage: python3 scripts/token_source_gate.py <file.html> [...]        (exit 1 on any FAIL)
       python3 scripts/token_source_gate.py --pair <staged.html> <head.html|-> [...]
"""
import re, sys, os

SENTINEL = "/* ARCS Recoil Report — Design Tokens */"
LINK_RE = re.compile(r'<link[^>]+href="(?:\.\./)*_tokens\.css"', re.I)
SIGNAL = {"#00f0ff", "#00ff9d", "#ffd700", "#ff4d6d"}
PROP_RE = re.compile(r'(--[a-zA-Z0-9_-]+)\s*:\s*(#[0-9a-fA-F]{6})\b')
CANON = {"--cyan", "--green", "--gold", "--red"}

def analyze(text):
    hits = [(n, v) for n, v in PROP_RE.findall(text) if v.lower() in SIGNAL]
    if not hits:
        return ("PASS", "no ARCS signal hex in a custom property (not a palette surface)")
    inherits = (SENTINEL in text) or bool(LINK_RE.search(text))
    foreign = sorted({n for n, _ in hits if n not in CANON})
    if inherits and not foreign:
        return ("PASS", "inherits _tokens.css" + (" (inlined verbatim)" if SENTINEL in text else " (linked)"))
    if inherits and foreign:
        return ("FAIL", f"inherits _tokens.css but ALSO re-declares signal hexes under foreign names: {', '.join(foreign)}")
    return ("FAIL", f"re-authors the ARCS palette ({len(hits)} signal hex props, names: {', '.join(foreign or sorted({n for n,_ in hits}))}) without _tokens.css. Inline it verbatim (keep the sentinel line) or link it.")

def main(argv):
    if not argv:
        print(__doc__); return 0
    pairs = []
    if argv[0] == "--pair":
        a = argv[1:]
        pairs = [(a[i], a[i+1]) for i in range(0, len(a) - 1, 2)]
    else:
        pairs = [(p, None) for p in argv]
    worst = 0
    for path, head in pairs:
        try:
            text = open(path, errors="ignore").read()
        except Exception as e:
            print(f"✖ token_source_gate FAIL {path}  — unreadable ({e})"); worst = 1; continue
        v, msg = analyze(text)
        # NFTT literary family exemption: blog-nftt-*.html is a sanctioned, self-contained
        # design system (Newsreader serif template, cloned verbatim per the nftt-story-factory
        # skill), NOT a recoil-report/HUD surface. It legitimately does not carry _tokens.css.
        # Exempt ONLY when it uses the CANONICAL token names — a renamed palette still FAILs,
        # so the gate's real target (re-vocabularying the palette) stays protected.
        if v == "FAIL" and os.path.basename(path).startswith("blog-nftt-"):
            hits = [(n, val) for n, val in PROP_RE.findall(text) if val.lower() in SIGNAL]
            foreign = sorted({n for n, _ in hits if n not in CANON})
            if not foreign:
                v, msg = "PASS", "NFTT literary family: self-contained design system, canonical token names"
        if v == "FAIL" and head and head != "-":
            try:
                hv, _ = analyze(open(head, errors="ignore").read())
                if hv == "FAIL":
                    v = "WARN"; msg += "  [pre-existing in HEAD: not blocking; ratchet]"
            except Exception:
                pass
        mark = {"PASS": "✓", "WARN": "⚠", "FAIL": "✖"}[v]
        print(f"{mark} token_source_gate {v:4} {path}  — {msg}")
        if v == "FAIL": worst = 1
    return worst

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
