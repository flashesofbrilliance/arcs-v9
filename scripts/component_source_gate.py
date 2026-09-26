#!/usr/bin/env python3
"""component_source_gate: enrolled single-file HTML surfaces assemble from the ui-kit
templates, they do not re-invent the component grammar.

The visual twin of scripts/token_source_gate.py. token_source_gate proves a page inherits
the ARCS *palette* (src/ui-kit/recoil-report/_tokens.css). This gate proves an *enrolled*
page snaps into a registered ui-kit *template* (an atomic-design composition) and that its
declared template stays bound to its slop_lint eval --mode, so the visual composition and
the anti-slop thresholds can never silently drift apart.

Class it blocks: a page that declares itself part of a template family (via the enrollment
marker) but hand-rolls a bespoke redesign instead of assembling from the kit primitives, or
declares a slop --mode that contradicts its template's mode.

OPT-IN, RATCHETED (like the whole eval suite). A page is enrolled ONLY when it carries the
marker

    <!-- @arcs-template: <name> -->            (required to enroll)
    <!-- @arcs-mode: <mode> -->                (optional; if present must match the template)

An un-enrolled page is PASS ("not enrolled") so the gate rolls out surface-by-surface and
does NOT break the ~existing pages on day one. Templates + their required signature selectors
and canonical modes live in src/ui-kit/templates.json (the manifest).

For an enrolled page the gate requires ALL of:
  1. the declared template exists in templates.json                       (else FAIL)
  2. the page inherits _tokens.css (sentinel line OR <link>)              (else FAIL)
  3. if @arcs-mode is declared, it equals the template's canonical mode   (else FAIL)
  4. the page references >= min_signatures of the template's signature    (else FAIL)
     selectors (proof it assembles from kit primitives, not bespoke CSS)

Ratchet: with --pair <staged> <head|->, an enrolled page whose HEAD version was ALSO enrolled
and already failing is WARN, not FAIL (legacy enrolled pages stay editable; new violations
cannot be born). A newly-enrolled page must pass outright.

Usage: python3 scripts/component_source_gate.py <file.html> [...]        (exit 1 on any FAIL)
       python3 scripts/component_source_gate.py --pair <staged.html> <head.html|-> [...]
       python3 scripts/component_source_gate.py --self-test
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MANIFEST = os.path.join(REPO, "src", "ui-kit", "templates.json")
SENTINEL = "/* ARCS Recoil Report — Design Tokens */"
LINK_RE = re.compile(r'<link[^>]+href="(?:\.\./)*_tokens\.css"', re.I)
TEMPLATE_RE = re.compile(r'<!--\s*@arcs-template:\s*([a-z0-9-]+)\s*-->', re.I)
MODE_RE = re.compile(r'<!--\s*@arcs-mode:\s*([a-z0-9-]+)\s*-->', re.I)


def load_manifest(path=MANIFEST):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh).get("templates", {})
    except Exception:
        return {}


def inherits_tokens(text):
    return (SENTINEL in text) or bool(LINK_RE.search(text))


def analyze(text, templates):
    """Return (status, message). status in {PASS, FAIL}."""
    m = TEMPLATE_RE.search(text)
    if not m:
        return ("PASS", "not enrolled (no @arcs-template marker)")
    name = m.group(1).lower()
    tpl = templates.get(name)
    if tpl is None:
        known = ", ".join(sorted(templates)) or "(manifest empty/missing)"
        return ("FAIL", f"declares unknown template '{name}'. Registered: {known}")
    if not inherits_tokens(text):
        return ("FAIL", f"template '{name}' but does not inherit _tokens.css (inline verbatim with its sentinel line, or <link> it)")
    mode_m = MODE_RE.search(text)
    canon_mode = tpl.get("mode")
    if mode_m and canon_mode and mode_m.group(1).lower() != canon_mode.lower():
        return ("FAIL", f"template '{name}' is bound to slop --mode '{canon_mode}' but the page declares @arcs-mode '{mode_m.group(1)}' (visual template and eval mode must not drift)")
    sigs = tpl.get("signature_selectors", [])
    need = tpl.get("min_signatures", 1)
    present = [s for s in sigs if s in text]
    if sigs and len(present) < need:
        return ("FAIL", f"template '{name}' declared but only {len(present)}/{need} required signature selectors present ({', '.join(sigs)}). Assemble from the kit primitives, do not hand-roll a bespoke redesign.")
    return ("PASS", f"enrolled in template '{name}' (mode={canon_mode}); inherits tokens; {len(present)} signature selector(s) present")


def _read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def run(pairs, templates):
    worst = 0
    for path, head in pairs:
        try:
            text = _read(path)
        except Exception as e:
            print(f"✖ component_source_gate FAIL {path}  — unreadable ({e})"); worst = 1; continue
        status, msg = analyze(text, templates)
        if status == "PASS":
            print(f"✓ component_source_gate PASS {path}  — {msg}")
            continue
        # FAIL — check ratchet
        if head and head != "-" and os.path.exists(head):
            hstatus, _ = analyze(_read(head), templates)
            henrolled = bool(TEMPLATE_RE.search(_read(head)))
            if henrolled and hstatus == "FAIL":
                print(f"⚠ component_source_gate WARN {path}  — {msg}  (HEAD already enrolled+failing; ratcheted)")
                continue
        print(f"✖ component_source_gate FAIL {path}  — {msg}"); worst = 1
    return worst


def self_test():
    templates = {
        "candidate-brief": {"mode": "persuade", "signature_selectors": [".verdict", ".pursue-score", ".qa-block"], "min_signatures": 1},
    }
    tok = "\n<style>/* ARCS Recoil Report — Design Tokens */\n:root{--cyan:#00F0FF}\n.verdict{color:var(--cyan)}</style>\n"
    bespoke_style = "\n<style>/* ARCS Recoil Report — Design Tokens */\n:root{--cyan:#00F0FF}\n.my-own-thing{color:red}</style>\n"
    cases = []
    # PASS: unenrolled
    cases.append(("unenrolled", "<html><body>plain page</body></html>", "PASS"))
    # PASS: enrolled, tokens, signature present, mode matches
    cases.append(("good", f"<!-- @arcs-template: candidate-brief --><!-- @arcs-mode: persuade -->{tok}<div class='verdict'>x</div>", "PASS"))
    # FAIL: enrolled, unknown template
    cases.append(("unknown-template", f"<!-- @arcs-template: made-up -->{tok}<div class='verdict'>x</div>", "FAIL"))
    # FAIL: enrolled but no tokens
    cases.append(("no-tokens", "<!-- @arcs-template: candidate-brief --><div class='verdict'>x</div>", "FAIL"))
    # FAIL: enrolled, tokens, but no signature selectors (bespoke redesign)
    cases.append(("bespoke", f"<!-- @arcs-template: candidate-brief -->{bespoke_style}<div class='my-own-thing'>x</div>", "FAIL"))
    # FAIL: mode mismatch
    cases.append(("mode-drift", f"<!-- @arcs-template: candidate-brief --><!-- @arcs-mode: resume -->{tok}<div class='verdict'>x</div>", "FAIL"))
    ok = True
    for label, text, expect in cases:
        status, msg = analyze(text, templates)
        good = status == expect
        ok = ok and good
        mark = "ok " if good else "XX "
        print(f"  [{mark}] {label:18s} expected {expect:4s} got {status:4s}  — {msg}")
    print("component_source_gate self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if not argv or "--self-test" in argv:
        if "--self-test" in argv:
            return self_test()
        print(__doc__); return 0
    templates = load_manifest()
    if argv[0] == "--pair":
        a = argv[1:]
        pairs = [(a[i], a[i + 1]) for i in range(0, len(a) - 1, 2)]
    else:
        pairs = [(p, None) for p in argv]
    return run(pairs, templates)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
