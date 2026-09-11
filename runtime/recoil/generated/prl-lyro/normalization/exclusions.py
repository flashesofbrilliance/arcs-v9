#!/usr/bin/env python3
"""PRL anti-ICP / spam exclusion check (extensible; reads exclusions.json).

ONE shared filter for BOTH surfaces:
  - the chatbot capture flow (prequal a wrong-fit before it becomes a lead), and
  - the Gravity Forms spam/quality filter (block spam, flag wrong-fit).

Extensible by design: all rules live in exclusions.json. Adding a keyword there (including Todd's
forthcoming list under `todd_provided`) changes behavior with NO code change. Run `python3 exclusions.py`
for the self-test.

Verdict actions:
  block   -> hard spam; do not create a lead / reject the submission.
  prequal -> real person, wrong fit (e.g. wants sheet stock, we make pellets); ask a clarifying question,
             tag low-intent so reps triage, never hard-drop.
  accept  -> clean; proceed.
"""
import json, os, re

_D = os.path.dirname(os.path.abspath(__file__))
_EX = json.load(open(os.path.join(_D, "exclusions.json")))

def _norm(s):
    return " ".join(str(s or "").lower().split())

def exclusion_check(text):
    """Return {excluded, action, kind, matched, reason, message}."""
    t = _norm(text)
    # 1) hard spam -> block. Word-boundary match so short tokens don't false-positive inside words.
    for kw in _EX["hard_spam_signals"]["keywords"]:
        if re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", t):
            return {"excluded": True, "action": "block", "kind": "hard_spam", "matched": kw,
                    "reason": "generic web-form spam", "message": None}
    # 2) anti-ICP + Todd's list -> prequal. Substring match so 'sheet' catches 'sheets', 'sheet stock'.
    for bucket in ("anti_icp_keywords", "todd_provided"):
        for entry in _EX[bucket].get("entries", []):
            for m in entry["match"]:
                if m in t:
                    return {"excluded": True, "action": entry.get("action", "prequal"), "kind": bucket,
                            "matched": m, "reason": entry.get("reason"),
                            "message": ("We compound resin pellets and custom compounds, not " + m +
                                        ". Are you after a moldable grade? A specialist can confirm the right fit.")}
    return {"excluded": False, "action": "accept", "kind": "clean", "matched": None,
            "reason": None, "message": None}

def gravity_forms_blocklist():
    """Flat keyword list for the Gravity Forms keyword-blocklist field (hard-spam + block-tagged entries)."""
    words = list(_EX["hard_spam_signals"]["keywords"])
    for bucket in ("anti_icp_keywords", "todd_provided"):
        for entry in _EX[bucket].get("entries", []):
            if entry.get("action") == "block":
                words += entry["match"]
    return sorted(set(words))

def _all_anti_icp():
    words = []
    for bucket in ("anti_icp_keywords", "todd_provided"):
        for entry in _EX[bucket].get("entries", []):
            words += entry["match"]
    return sorted(set(words))

def emit_php():
    """Emit a self-contained Gravity Forms spam-filter snippet (gform_entry_is_spam), populated from this
    SSOT. Regenerate whenever exclusions.json changes: `python3 exclusions.py --emit-php`. Paste into a
    Code Snippets / WPCode plugin (safest) or a child-theme functions.php."""
    def php_arr(words):
        return ", ".join("'" + w.replace("'", "\\'") + "'" for w in words)
    return f"""<?php
/**
 * PRL Resins - spam keyword filter for Gravity Forms.
 * Generated from normalization/exclusions.json (SSOT). Do NOT hand-edit the array;
 * update exclusions.json + re-run `python3 exclusions.py --emit-php`.
 *
 * Marks a submission as spam (routed to the Spam folder, out of the inbox) when an UNAMBIGUOUS
 * spam term appears in a text field. Runs AFTER the honeypot + submission-speed-check.
 *
 * DELIBERATELY hard-spam ONLY. The anti-ICP 'sheet' seekers are NOT auto-flagged here, because on a
 * non-interactive form 'sheet' would false-positive on real 'datasheet' / 'spec sheet' requests (high-value
 * leads). Sheet seekers are handled without that risk by (a) the required pellets-vs-sheet form-factor field
 * and (b) the chatbot's soft prequal. Uses word boundaries so short tokens don't match inside words.
 */
add_filter( 'gform_entry_is_spam', function( $is_spam, $form, $entry ) {{
    if ( $is_spam ) {{ return true; }} // already flagged upstream (honeypot / speed check)

    $blocklist = array( {php_arr(gravity_forms_blocklist())} );

    $haystack = '';
    foreach ( $entry as $key => $value ) {{
        if ( is_string( $value ) ) {{ $haystack .= ' ' . strtolower( $value ); }}
    }}
    foreach ( $blocklist as $kw ) {{
        if ( $kw !== '' && preg_match( '/\\b' . preg_quote( strtolower( $kw ), '/' ) . '\\b/', $haystack ) ) {{
            return true;
        }}
    }}
    return false;
}}, 20, 3 );
"""

if __name__ == "__main__":
    import sys
    if "--emit-php" in sys.argv:
        print(emit_php())
        sys.exit(0)
    tests = [
        ("I need a sheet of polycarbonate for a window", "prequal", "sheet"),
        ("looking for sheets of nylon", "prequal", "sheet"),
        ("do you sell plexiglass / acrylic sheet", "prequal", None),
        ("We offer SEO backlink services to help you rank higher", "block", None),
        ("increase your website traffic, affordable price, click here", "block", None),
        ("I need PC-GP1 pellets for an injection molding job", "accept", None),
        ("high temp glass filled nylon for an under-hood connector", "accept", None),
        ("equivalent to Lexan 141, moldable grade", "accept", None),
    ]
    ok = 0
    for text, exp_action, exp_match in tests:
        r = exclusion_check(text)
        passed = r["action"] == exp_action and (exp_match is None or r["matched"] == exp_match)
        ok += passed
        print(f"[{'PASS' if passed else 'FAIL'}] {text[:52]!r:54} -> {r['action']:7} ({r['kind']}"
              + (f", '{r['matched']}'" if r['matched'] else "") + ")")
    print(f"\nself-test: {ok}/{len(tests)} passed")
    print(f"Gravity Forms blocklist ({len(gravity_forms_blocklist())} terms): "
          + ", ".join(gravity_forms_blocklist()[:8]) + " ...")
