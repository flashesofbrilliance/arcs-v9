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
       python3 scripts/token_source_gate.py --doc-ts [--write]

--doc-ts (2026-11-11, row recoil-token-unify): src/document/tokens.ts is GENERATED. Every color it shares
with the HTML pages is read from _tokens.css; DOC_MAP names the CSS variable behind each T key. The few
reader-kit values the kit lacks live in DOC_EXTRA below (not in a stylesheet: classname_guard allows only
the sanctioned set, and an edit to _tokens.css regenerates ~54 pages that inline it whole, incl. the
release-held dj.html). A DOC_EXTRA name that _tokens.css also declares FAILS (one home per value).
Fold DOC_EXTRA into _tokens.css at the next kit release. Without --write it exits 1 when tokens.ts differs from what the CSS produces (a hand edit,
or a CSS change that was not regenerated); with --write it rewrites tokens.ts.
"""
import re, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_candidates

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
    trial = design_candidates.tokens_for(text)  # names a declared, unexpired candidate trials at this value
    foreign = sorted({n for n, v in hits if n not in CANON and trial.get(n, "").lower() != v.lower()})
    if inherits and not foreign and any(n not in CANON for n, _ in hits):
        return ("PASS", "inherits _tokens.css; non-canonical names are a declared design candidate (runtime/specs/design-candidates.json)")
    if inherits and not foreign:
        return ("PASS", "inherits _tokens.css" + (" (inlined verbatim)" if SENTINEL in text else " (linked)"))
    if inherits and foreign:
        return ("FAIL", f"inherits _tokens.css but ALSO re-declares signal hexes under foreign names: {', '.join(foreign)}")
    return ("FAIL", f"re-authors the ARCS palette ({len(hits)} signal hex props, names: {', '.join(foreign or sorted({n for n,_ in hits}))}) without _tokens.css. Inline it verbatim (keep the sentinel line) or link it.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT_CSS = os.path.join(ROOT, "src/ui-kit/recoil-report/_tokens.css")
# Reader-kit values _tokens.css lacks. --rule-dim (#5e6975, 3.67:1 on --bg) is for rules and marks, never text.
# The four reader type steps are px; label never below 12px.
DOC_EXTRA = {
    "--shell": "#060a0f", "--border-hi": "rgba(205,225,240,0.12)", "--rule-dim": "#5e6975",
    "--doc-fs-label": "12px", "--doc-fs-body": "14px", "--doc-fs-headline": "20px", "--doc-fs-display": "24px",
    "--doc-font-sans": "'Inter', system-ui, sans-serif",
    "--doc-font-mono": "'JetBrains Mono', 'IBM Plex Mono', monospace",
}
DOC_TS = os.path.join(ROOT, "src/document/tokens.ts")
# Print palette (R6 recoil-print-target, spec 8 Q2: Zach 2026-11-12, light for print). TP is read from the
# @media print block of _tokens-light.css; DOC_EXTRA_PRINT holds the light twins of DOC_EXTRA's colors only.
KIT_LIGHT = os.path.join(ROOT, "src/ui-kit/recoil-report/_tokens-light.css")
DOC_EXTRA_PRINT = {"--shell": "#eef1f5", "--border-hi": "rgba(28,36,48,0.14)", "--rule-dim": "#9aa4b1"}
# T key -> CSS custom property in _tokens.css. Order is the emitted order.
DOC_MAP = [
    ("bg", "--bg"), ("surface", "--surface"), ("elevated", "--elevated"), ("shell", "--shell"),
    ("border", "--border"), ("borderHi", "--border-hi"),
    ("fg1", "--text"), ("fg2", "--text-secondary"), ("fg3", "--dimmed"), ("fg4", "--rule-dim"),
    ("cyan", "--cyan"), ("green", "--green"), ("gold", "--gold"), ("orange", "--orange"), ("red", "--red"),
    ("steel", "--text-secondary"), ("purple", "--violet"), ("magenta", "--magenta"),
    ("sans", "--doc-font-sans"), ("mono", "--doc-font-mono"),
    ("fsLabel", "--doc-fs-label"), ("fsBody", "--doc-fs-body"), ("fsHeadline", "--doc-fs-headline"), ("fsDisplay", "--doc-fs-display"),
]
DECL_RE = re.compile(r'(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);')

def doc_ts_text():
    css = re.sub(r'/\*.*?\*/', '', open(KIT_CSS, encoding="utf-8").read(), flags=re.S)
    vals = {}
    for n, v in DECL_RE.findall(css):
        vals.setdefault(n, v.strip())
    dup = sorted(set(vals) & set(DOC_EXTRA))
    if dup:
        raise SystemExit(f"✖ token_source_gate --doc-ts: DOC_EXTRA re-declares kit tokens from _tokens.css: {', '.join(dup)}")
    vals.update(DOC_EXTRA)
    lines = []
    for key, var in DOC_MAP:
        if var not in vals:
            raise SystemExit(f"✖ token_source_gate --doc-ts: {var} (for T.{key}) is not declared in _tokens.css or DOC_EXTRA")
        v = vals[var]
        m = re.fullmatch(r'(\d+(?:\.\d+)?)px', v)
        lit = m.group(1) if m else json.dumps(v)
        lines.append(f"  {key}: {lit},  // {var}")
    light = re.search(r'@media print\{:root\{([^}]*)\}', open(KIT_LIGHT, encoding="utf-8").read())
    if not light:
        raise SystemExit("✖ token_source_gate --doc-ts: _tokens-light.css has no @media print{:root{...}} block")
    pv = dict((n, v.strip()) for n, v in DECL_RE.findall(light.group(1) + ";"))
    dup = sorted(set(pv) & set(DOC_EXTRA_PRINT))
    if dup:
        raise SystemExit(f"✖ token_source_gate --doc-ts: DOC_EXTRA_PRINT re-declares print tokens: {', '.join(dup)}")
    pv.update(DOC_EXTRA_PRINT)
    plines = []
    for key, var in DOC_MAP:
        if not vals[var].startswith(("#", "rgb")):
            continue  # fonts and type steps do not change in print
        if var not in pv:
            raise SystemExit(f"✖ token_source_gate --doc-ts: {var} (for TP.{key}) has no print value in _tokens-light.css or DOC_EXTRA_PRINT")
        plines.append(f"  {key}: {json.dumps(pv[var])},  // {var}")
    return ("// GENERATED by scripts/token_source_gate.py --doc-ts --write from src/ui-kit/recoil-report/_tokens.css\n"
            "// (+ DOC_EXTRA in that script for the values the kit lacks). Do not edit by hand: pre-commit fails on\n"
            "// drift. Change _tokens.css or DOC_EXTRA and regenerate.\n"
            "// fg4 is for rules and marks only (3.67:1 on bg); text uses fg3 or brighter.\n"
            "// fsLabel/fsBody/fsHeadline/fsDisplay are the four reader type steps, in px.\n\n"
            "export const T = {\n" + "\n".join(lines) + "\n} as const\n\n"
            "// TP: the print palette (light, spec 8 Q2), from the @media print block of _tokens-light.css\n"
            "// (+ DOC_EXTRA_PRINT). Same color keys as T; a screen that prints swaps T for TP under @media print.\n"
            "export const TP = {\n" + "\n".join(plines) + "\n} as const\n\n"
            "export const DIM = (c: string) => `${c}16`\n"
            "export const BDR = (c: string) => `${c}35`\n"
            "export const GLOW = (c: string) => `${c}55`\n")

def doc_ts(write):
    want = doc_ts_text()
    have = open(DOC_TS, encoding="utf-8").read() if os.path.exists(DOC_TS) else ""
    if have == want:
        print("✓ token_source_gate --doc-ts: src/document/tokens.ts matches the kit CSS"); return 0
    if write:
        open(DOC_TS, "w", encoding="utf-8").write(want)
        print("✓ token_source_gate --doc-ts: wrote src/document/tokens.ts"); return 0
    print("✖ token_source_gate --doc-ts: src/document/tokens.ts differs from what the kit CSS generates.\n"
          "  It is generated: edit _tokens.css (or DOC_MAP / DOC_EXTRA), then run python3 scripts/token_source_gate.py --doc-ts --write")
    return 1

def main(argv):
    if not argv:
        print(__doc__); return 0
    if argv[0] == "--doc-ts":
        return doc_ts("--write" in argv[1:])
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
