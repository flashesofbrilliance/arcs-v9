#!/usr/bin/env python3
"""provenance_lint: every quantified claim on an enrolled customer surface must cite evidence.

Root cause it gates (banked 2026-09-25): a "40+ demos / 75% pilot conversion" metric entered a
resume via session scratch (TAILOR-NOTES) and rode to the near-final draft with NO provenance in
any vetted master. slop_lint catches STYLE fabrication (cliches); this catches FACTUAL fabrication
(invented numbers) -- the "are you grounding each claim in evidence" gap. See memory
false-null-requires-provenance, coherence-is-not-correctness, control-integrity-described-vs-wired.

Model: an enrolled surface carries a sibling `evidence.jsonl` ledger. Each risky metric in the
rendered text (dollars, percents, latency, "N+"/"more than N" counts) must be COVERED by a ledger
entry's regex; an uncovered metric FAILS. Self-reported-by-the-subject is valid evidence -- the
ledger records the source ("vetted-master:file:line" or "self-reported:Zach:2026-09-25"), so the
gate enforces that a human vouched for each number, not that a number is objectively true.

Opt-in: a file with NO sibling evidence.jsonl is NOT enrolled -> PASS (note). This lets the gate
roll out surface-by-surface instead of blocking every existing page. 4-digit years and date ranges
are excluded (they are not claims).

Ledger line shape (JSONL):
  {"pattern": "\\$7B|\\$7\\s?billion", "source": "vetted-master:resume-vico...:106", "note": "..."}

Usage:
  python3 scripts/provenance_lint.py <file.html|.txt> [...]        # exit 1 on any uncovered metric
  python3 scripts/provenance_lint.py --ledger <path> <file> [...]  # explicit ledger
  python3 scripts/provenance_lint.py --self-test
"""
import re, sys, os, json

# risky metric tokens (fabrication hides in numbers). Years/date-ranges excluded separately.
METRIC = re.compile(r"""
    \$\s?\d[\d.,]*\s?(?:B|M|K|bn|billion|million|thousand)?     # money: $7B, $850K, $2M
  | \b\d[\d.]*\s?%                                              # 35% (percent sign, no trailing \b)
  | \b\d[\d.]*\s?percent\b                                      # 20 percent
  | \b\d+\s?(?:ms|milliseconds|seconds)\b                       # 120ms, 120 milliseconds
  | \b\d+\+                                                     # 40+
  | \b(?:more\ than|over|up\ to)\s+\d[\d.,]*\b                  # more than 40, up to 12
""", re.I | re.X)
YEAR = re.compile(r"^(?:19|20)\d{2}$")

def strip_to_text(s: str) -> str:
    s = re.sub(r"<script\b[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style\b[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", s)
    return re.sub(r"[ \t]+", " ", s)

def find_ledger(path, explicit=None):
    if explicit:
        return explicit if os.path.exists(explicit) else None
    sib = os.path.join(os.path.dirname(path), "evidence.jsonl")
    return sib if os.path.exists(sib) else None

def load_ledger(lpath):
    pats = []
    for ln in open(lpath, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        e = json.loads(ln)
        pats.append((re.compile(e["pattern"], re.I), e.get("source", "?")))
    return pats

def candidates(text):
    out = []
    for m in METRIC.finditer(text):
        tok = m.group(0).strip()
        if YEAR.match(tok):
            continue
        out.append((tok, m.start(), m.end()))
    return out

def report(path, text, ledger_path):
    cands = candidates(text)
    if ledger_path is None:
        return True, {"file": path, "ok": True, "enrolled": False,
                      "note": f"not enrolled (no evidence.jsonl); {len(cands)} metric(s) unchecked"}
    pats = load_ledger(ledger_path)
    covered_spans = []
    for rx, _ in pats:
        for m in rx.finditer(text):
            covered_spans.append((m.start(), m.end()))
    def is_covered(s, e):
        return any(cs <= s and e <= ce for cs, ce in covered_spans)
    unverified = sorted({tok for tok, s, e in cands if not is_covered(s, e)})
    ok = not unverified
    return ok, {"file": path, "ok": ok, "enrolled": True, "ledger": ledger_path,
                "metrics_found": len(cands), "unverified": unverified}

# ---- self-test: fails-on-bad (uncovered number) + passes-on-good (covered) -----------------
def self_test():
    import tempfile
    d = tempfile.mkdtemp()
    led = os.path.join(d, "evidence.jsonl")
    open(led, "w").write(json.dumps({"pattern": r"\$7B", "source": "vetted-master:x:1"}) + "\n")
    good = "Led a $7B regulated launch in 2024."          # $7B covered, 2024 is a year
    bad = "Led a $7B launch and delivered 40+ demos at 75% conversion."  # 40+ / 75% uncovered
    ok_g, rg = report(os.path.join(d, "g.txt"), good, led)
    ok_b, rb = report(os.path.join(d, "b.txt"), bad, led)
    passed = ok_g and (not ok_b) and set(rb["unverified"]) >= {"40+", "75%"}
    print("SELF-TEST (fail-on-bad + pass-on-good)")
    print(f"  good (only covered $7B) -> {'PASS (correct)' if ok_g else 'FAIL (WRONG)'}  unver={rg.get('unverified')}")
    print(f"  bad  (40+/75% uncovered) -> {'FAIL (correct)' if not ok_b else 'PASS (WRONG)'}  unver={rb.get('unverified')}")
    print("  RESULT:", "OK" if passed else "BROKEN")
    return 0 if passed else 1

def main(argv):
    if "--self-test" in argv:
        return self_test()
    explicit = None
    if "--ledger" in argv:
        i = argv.index("--ledger"); explicit = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    files = [a for a in argv if not a.startswith("--")]
    bad = False
    for path in files:
        text = strip_to_text(open(path, encoding="utf-8", errors="replace").read())
        ledger = find_ledger(path, explicit)
        ok, r = report(path, text, ledger)
        bad = bad or not ok
        if not r.get("enrolled"):
            print(f"[skip] {path} - {r['note']}")
        elif ok:
            print(f"[PASS] {path} - {r['metrics_found']} metric(s), all cite evidence ({os.path.basename(ledger)})")
        else:
            print(f"[FAIL] {path} - uncovered metric(s) with NO evidence-ledger entry: {', '.join(r['unverified'])}")
            print(f"       add each to {ledger} with its source, or cut the claim.")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
