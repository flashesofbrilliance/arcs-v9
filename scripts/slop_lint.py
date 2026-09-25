#!/usr/bin/env python3
"""slop_lint: customer-facing surfaces must read as human-written, not AI slop.

Root cause it gates (banked 2026-09-25): a designed resume for the Success Academy AI PM
role read as "AI slop" to the hiring manager (Jarrod Wolf, who is allergic to it) and the
recruiter refused to send it. Design slop is already caught by the impeccable detector; this
gate is the WRITING-slop half — the "Elements of Style for AI prose" the design guide lacks.

SPLIT (deliberate — see memory FE-gate=tripwire-not-verdict, metabolic-router):
  MECHANICAL (this script, HARD FAIL): high-precision clichés with ~zero legitimate use on a
    resume or marketing surface, plus em-dashes (Zach's standing 0 rule). A grep can decide
    these with no judgment, so they block the commit.
  JUDGMENT (the rubric, NOT this script): structural tells (binary-contrast "not X, it's Y",
    rule-of-three triads, dramatic colon reveals, robotic rhythm) have legitimate uses — the
    live success-academy page deliberately uses one binary-contrast line. Scoring those is the
    LLM-eval / human rubric's job (_PATTERNS/slop-free-rubric.md), not a mechanical block.

Deterministic, stdlib-only. Scans RENDERED TEXT only: <script>/<style> bodies and all tags are
stripped first, so CSS var names (--secondary) and inline JS never false-fire.

TIER A (FAIL): near-zero legit use in candidate/marketing copy.
TIER B (WARN): real slop signal but has legitimate uses — warn, never block.
EM-DASH (FAIL): folds the existing 0-em-dash rule into one report.

Ratchet (like token_source_gate): with --pair <staged> <head|->, a term already present in the
HEAD version is WARN not FAIL, so a legacy page stays editable while new slop cannot be born.

Usage:
  python3 scripts/slop_lint.py <file.html|.txt|.md> [...]         # exit 1 on any TIER-A / em-dash
  python3 scripts/slop_lint.py --pair <staged.html> <head.html|-> [...]   # ratcheted (pre-commit)
  python3 scripts/slop_lint.py --json <file> [...]               # machine-readable
  python3 scripts/slop_lint.py --self-test                       # fail-on-bad + pass-on-good eval
"""
import re, sys, json

# ---- catalogs (sourced from the 2026-09-25 anti-AI-slop writing research) -----------------
# TIER A: word-boundary, case-insensitive. Hard fail on a customer-facing surface.
TIER_A = [
    "delve", "leverage", "leverages", "leveraging", "leveraged",
    "spearhead", "spearheaded", "spearheading",
    "synergy", "synergies", "results-driven", "results driven",
    "detail-oriented", "detail oriented", "self-starter", "go-getter",
    "proven track record", "thought leader", "best-in-class", "best in class",
    "world-class", "world class", "move the needle", "paradigm shift",
    "tapestry", "testament to", "at the end of the day", "it's worth noting",
    "it is worth noting", "bleeding edge", "supercharge", "supercharged",
    "team player", "hit the ground running", "wheelhouse", "boil the ocean",
    "low-hanging fruit", "circle back", "needle-moving",
]
# TIER B: warn only (legit uses exist).
TIER_B = [
    "robust", "seamless", "seamlessly", "cutting-edge", "cutting edge",
    "transformative", "passionate", "dynamic", "innovative", "foster",
    "elevate", "unlock", "ever-evolving", "next-generation", "next generation",
    "game-changer", "game changer", "value-add", "navigate the landscape",
    "in today's fast-paced", "realm of", "underscore", "underscores",
]

def strip_to_text(s: str) -> str:
    s = re.sub(r"<script\b[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style\b[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)                     # drop tags
    s = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", s)          # drop entities (&middot; etc.)
    return s

def _pat(term: str):
    # \b works at hyphen/space boundaries; build a boundary-safe, space-or-hyphen-flexible pattern
    esc = re.escape(term).replace(r"\ ", r"[\s\-]+")
    return re.compile(r"(?<![\w-])" + esc + r"(?![\w-])", re.I)

_A = [(t, _pat(t)) for t in TIER_A]
_B = [(t, _pat(t)) for t in TIER_B]

def scan(text: str):
    vis = strip_to_text(text)
    a = sorted({t for t, p in _A if p.search(vis)})
    b = sorted({t for t, p in _B if p.search(vis)})
    em = vis.count("—")  # em-dash
    return {"tier_a": a, "tier_b": b, "em_dashes": em}

def _head_terms(head_text):
    r = scan(head_text)
    return set(r["tier_a"]), r["em_dashes"]

def report(path, text, head_text=None):
    r = scan(text)
    ratchet_a, ratchet_em = _head_terms(head_text) if head_text is not None else (set(), 0)
    fail_a = [t for t in r["tier_a"] if t not in ratchet_a]      # new TIER-A terms only
    warn_a = [t for t in r["tier_a"] if t in ratchet_a]          # pre-existing -> demote to warn
    em_fail = r["em_dashes"] > ratchet_em                        # net-new em-dashes
    ok = not fail_a and not em_fail
    return ok, {
        "file": path, "ok": ok,
        "fail_tier_a": fail_a, "warn_tier_a_preexisting": warn_a,
        "warn_tier_b": r["tier_b"],
        "em_dashes": r["em_dashes"], "em_dash_fail": em_fail,
    }

# ---- self-test / eval: prove fails-on-bad AND passes-on-good -------------------------------
BAD = ("Results-driven product leader with a proven track record of leveraging cross-functional "
       "synergies to move the needle. Passionate self-starter who spearheaded best-in-class, "
       "world-class initiatives — a testament to my ability to delve into the realm of innovation.")
GOOD = ("Product manager and hands-on builder with two decades taking products from concept to "
        "production in regulated fields. I take end-to-end ownership of the full product lifecycle, "
        "from discovery and user research through delivery. Built ARCS, an AI product on Claude: a "
        "retrieval pipeline, an MCP server, and an evaluation layer, live in production.")

def self_test():
    ok_bad, rb = report("<bad-fixture>", BAD)
    ok_good, rg = report("<good-fixture>", GOOD)
    passed = (not ok_bad) and ok_good
    print("SELF-TEST (fail-on-bad + pass-on-good)")
    print(f"  bad fixture  -> {'FAIL (correct)' if not ok_bad else 'PASS (WRONG - gate is blind)'}"
          f"  hits={rb['fail_tier_a']} em={rb['em_dashes']}")
    print(f"  good fixture -> {'PASS (correct)' if ok_good else 'FAIL (WRONG - false positive)'}"
          f"  hits={rg['fail_tier_a']} warnB={rg['warn_tier_b']}")
    print("  RESULT:", "OK" if passed else "BROKEN")
    return 0 if passed else 1

def main(argv):
    if "--self-test" in argv:
        return self_test()
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    results, bad = [], False
    if argv and argv[0] == "--pair":
        rest = argv[1:]
        for i in range(0, len(rest), 2):
            staged, head = rest[i], rest[i + 1]
            text = open(staged, encoding="utf-8", errors="replace").read()
            head_text = "" if head == "-" else open(head, encoding="utf-8", errors="replace").read()
            ok, res = report(staged, text, head_text)
            results.append(res); bad = bad or not ok
    else:
        for path in argv:
            text = open(path, encoding="utf-8", errors="replace").read()
            ok, res = report(path, text)
            results.append(res); bad = bad or not ok
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            tag = "PASS" if r["ok"] else "FAIL"
            print(f"[{tag}] {r['file']}")
            if r["fail_tier_a"]:
                print(f"    FAIL tier-A cliche (cut these): {', '.join(r['fail_tier_a'])}")
            if r["em_dash_fail"]:
                print(f"    FAIL em-dashes: {r['em_dashes']} (rule is 0 on customer surfaces)")
            if r["warn_tier_a_preexisting"]:
                print(f"    warn (pre-existing, ratcheted): {', '.join(r['warn_tier_a_preexisting'])}")
            if r["warn_tier_b"]:
                print(f"    warn tier-B (review, not blocking): {', '.join(r['warn_tier_b'])}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
