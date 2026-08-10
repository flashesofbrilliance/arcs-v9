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

if __name__ == "__main__":
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
