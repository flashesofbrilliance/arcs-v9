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

Unvalidated status (2026-10-17, ADR-088): an entry may carry "status": "unvalidated" plus a "source" that
points at the audit saying so (e.g. "audit:_CANON/living/ARCS-Technical-Overview-April2026.md:171"). That
is a TRIAGE mark, not evidence: it does NOT cover the metric (the gate still fails), it only moves the
metric from "uncovered" to "acknowledged unvalidated" in the message and in canon_claims_report. Any other
status value, or a marked entry with no source, is a hard error (exit 2).

Two more triage marks (2026-10-17, final triage): "illustrative" (a worked example, sample output or
hypothetical, not a claim about the world) and "parameter" (a design constant, threshold, weight or
definition: a specification, not a measurement). Same semantics: never cover, gate still fails, need a source.

Projection status (2026-10-17): "status": "projection" marks a plan, forecast or target (market size,
price point, revenue scenario) that the text presents as a number to aim at, not a measured fact. Same
semantics as unvalidated: never covers, gate still fails, needs a source, only labelled differently.

Usage:
  python3 scripts/provenance_lint.py <file.html|.txt> [...]        # exit 1 on any uncovered metric
  python3 scripts/provenance_lint.py --ledger <path> <file> [...]  # explicit ledger
  python3 scripts/provenance_lint.py --self-test
"""
import argparse, re, sys, os, json, subprocess

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
    # per-file ledger first (<stem>.evidence.jsonl) so a single page in a shared dir (public/) can
    # enroll without a dir-wide ledger wrongly applying to its siblings; then the dir-level sibling.
    per_file = os.path.splitext(path)[0] + ".evidence.jsonl"
    if os.path.exists(per_file):
        return per_file
    sib = os.path.join(os.path.dirname(path), "evidence.jsonl")
    return sib if os.path.exists(sib) else None

class LedgerError(ValueError):
    pass

STATUSES = ("unvalidated", "projection", "illustrative", "parameter")

def _entries(lpath):
    for i, ln in enumerate(open(lpath, encoding="utf-8"), 1):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        e = json.loads(ln)
        st = e.get("status")
        if st not in (None,) + STATUSES:
            raise LedgerError(f"{lpath}:{i}: unknown status {st!r} (allowed: {', '.join(STATUSES)})")
        if st is not None and not str(e.get("source", "")).strip():
            raise LedgerError(f"{lpath}:{i}: {st} entry needs a source pointing at the audit or plan")
        yield e

def load_ledger(lpath):
    """Entries that COVER a metric. Unvalidated entries are triage marks and never cover."""
    return [(re.compile(e["pattern"], re.I), e.get("source", "?"))
            for e in _entries(lpath) if e.get("status") is None]

def load_status(lpath, status):
    return [(re.compile(e["pattern"], re.I), e.get("source", "?"))
            for e in _entries(lpath) if e.get("status") == status]

def load_unvalidated(lpath):
    return load_status(lpath, "unvalidated")

def load_projection(lpath):
    return load_status(lpath, "projection")

def load_marked(lpath):
    """Every triage mark; none of them covers a metric."""
    return [m for st in STATUSES for m in load_status(lpath, st)]

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
    def spans(st):
        return [(m.start(), m.end()) for rx, _ in load_status(ledger_path, st) for m in rx.finditer(text)]
    marks = {st: spans(st) for st in STATUSES}
    def mark_of(s, e):
        for st in STATUSES:   # precedence = STATUSES order
            if any(cs <= s and e <= ce for cs, ce in marks[st]):
                return st
        return None
    open_ = [(tok, s, e) for tok, s, e in cands if not is_covered(s, e)]
    by = {st: sorted({tok for tok, s, e in open_ if mark_of(s, e) == st}) for st in STATUSES}
    unverified = sorted({tok for tok, s, e in open_ if mark_of(s, e) is None})
    ok = not open_   # an unvalidated mark is not evidence: the gate still fails
    return ok, {"file": path, "ok": ok, "enrolled": True, "ledger": ledger_path,
                "metrics_found": len(cands), "unverified": unverified, **by}

def unit_test():
    """Original in-process cases: fails-on-bad (uncovered number) + passes-on-good (covered)."""
    import tempfile
    d = tempfile.mkdtemp()
    led = os.path.join(d, "evidence.jsonl")
    open(led, "w").write(json.dumps({"pattern": r"\$7B", "source": "vetted-master:x:1"}) + "\n")
    good = "Led a $7B regulated launch in 2024."          # $7B covered, 2024 is a year
    bad = "Led a $7B launch and delivered 40+ demos at 75% conversion."  # 40+ / 75% uncovered
    ok_g, rg = report(os.path.join(d, "g.txt"), good, led)
    ok_b, rb = report(os.path.join(d, "b.txt"), bad, led)
    return ok_g, (not ok_b) and set(rb["unverified"]) >= {"40+", "75%"}

def self_test():
    """Unit cases + CLI cases (the script run as a subprocess in a temp dir; lint is read-only)."""
    import hashlib, tempfile
    me = os.path.abspath(__file__)
    fails = total = 0
    def check(name, ok):
        nonlocal fails, total
        total += 1
        print(("PASS " if ok else "FAIL ") + name)
        fails += 0 if ok else 1
    def snap(root):
        out = {}
        for dp, _, fs in os.walk(root):
            for fn in fs:
                fp = os.path.join(dp, fn); st = os.stat(fp)
                with open(fp, "rb") as fh:
                    out[fp] = (hashlib.sha256(fh.read()).hexdigest(), st.st_mtime_ns)
        return out
    ok_g, ok_b = unit_test()
    check("good (only covered $7B) passes", ok_g)
    check("bad (40+/75% uncovered) fails", ok_b)
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "evidence.jsonl"), "w").write(json.dumps({"pattern": r"\$7B", "source": "x"}) + "\n")
        open(os.path.join(tmp, "good.html"), "w").write("<p>Led a $7B launch in 2024.</p>")
        open(os.path.join(tmp, "bad.html"), "w").write("<p>40+ demos at 75% conversion.</p>")
        os.mkdir(os.path.join(tmp, "solo"))
        open(os.path.join(tmp, "solo", "page.html"), "w").write("<p>40+ demos.</p>")
        def cli(*a):
            return subprocess.run([sys.executable, me, *a], cwd=tmp, capture_output=True, text=True)
        before = snap(tmp)
        check("unknown flag exits 2", cli("--check", "good.html").returncode == 2)
        check("typo flag exits 2", cli("--leger", "evidence.jsonl", "good.html").returncode == 2)
        check("--ledger with no value exits 2", cli("good.html", "--ledger").returncode == 2)
        check("good file exits 0", cli("good.html").returncode == 0)
        check("bad file exits 1", cli("bad.html").returncode == 1)
        check("mixed list exits 1", cli("good.html", "bad.html").returncode == 1)
        check("unenrolled file skips, exits 0", cli("solo/page.html").returncode == 0)
        check("--ledger enrolls an outside file, exits 1", cli("--ledger", "evidence.jsonl", "solo/page.html").returncode == 1)
        check("--ledger after files still applies", cli("solo/page.html", "--ledger", "evidence.jsonl").returncode == 1)
        check("no files exits 0", cli().returncode == 0)
        check("lint writes nothing", snap(tmp) == before)
        # unvalidated status: triage mark, never evidence
        u = os.path.join(tmp, "u"); os.mkdir(u)
        open(os.path.join(u, "evidence.jsonl"), "w").write(
            json.dumps({"pattern": r"87%", "status": "unvalidated", "source": "audit:TechOverview:171"}) + "\n")
        open(os.path.join(u, "page.html"), "w").write("<p>87% held.</p>")
        r = cli("u/page.html")
        check("unvalidated entry does NOT cover: gate still exits 1", r.returncode == 1)
        check("unvalidated metric is labelled UNVALIDATED, not uncovered", "UNVALIDATED" in r.stdout and "NO evidence-ledger entry" not in r.stdout)
        open(os.path.join(u, "page.html"), "w").write("<p>87% held and 76% too.</p>")
        r = cli("u/page.html")
        check("mixed: both labels reported", "UNVALIDATED" in r.stdout and "NO evidence-ledger entry" in r.stdout)
        open(os.path.join(u, "evidence.jsonl"), "w").write(json.dumps({"pattern": r"87%", "status": "unvalidated"}) + "\n")
        check("unvalidated entry without source is a hard error (exit 2)", cli("u/page.html").returncode == 2)
        open(os.path.join(u, "evidence.jsonl"), "w").write(json.dumps({"pattern": r"87%", "status": "verified", "source": "x"}) + "\n")
        check("unknown status is a hard error (exit 2)", cli("u/page.html").returncode == 2)
        open(os.path.join(u, "evidence.jsonl"), "w").write(json.dumps({"pattern": r"87%", "status": "projection", "source": "plan:x"}) + "\n")
        r = cli("u/page.html")
        check("projection entry does NOT cover and is labelled PROJECTION", r.returncode == 1 and "PROJECTION" in r.stdout and "UNVALIDATED" not in r.stdout)
        for st in ("illustrative", "parameter"):
            open(os.path.join(u, "evidence.jsonl"), "w").write(json.dumps({"pattern": r"87%", "status": st, "source": "x"}) + "\n")
            r = cli("u/page.html")
            check(f"{st} entry does NOT cover and is labelled {st.upper()}", r.returncode == 1 and st.upper() in r.stdout)
        open(os.path.join(u, "evidence.jsonl"), "w").write(json.dumps({"pattern": r"87%", "status": "projection"}) + "\n")
        check("projection entry without source is a hard error (exit 2)", cli("u/page.html").returncode == 2)
    print(f"provenance_lint self-test: {total - fails}/{total}")
    return 1 if fails else 0

def build_parser():
    ap = argparse.ArgumentParser(prog="provenance_lint.py",
                                 description="Every quantified claim on an enrolled surface must cite evidence. Read-only.")
    ap.add_argument("files", nargs="*", help="files to lint (.html/.txt); none -> exit 0")
    ap.add_argument("--ledger", metavar="PATH", help="explicit evidence ledger (overrides sibling lookup)")
    ap.add_argument("--self-test", action="store_true", help="run the self-test and exit")
    return ap

def main(argv):
    args = build_parser().parse_args(argv)  # unknown flags exit 2
    if args.self_test:
        return self_test()
    explicit = args.ledger
    bad = False
    for path in args.files:
        text = strip_to_text(open(path, encoding="utf-8", errors="replace").read())
        ledger = find_ledger(path, explicit)
        try:
            ok, r = report(path, text, ledger)
        except LedgerError as err:
            print(f"[ERROR] {err}", file=sys.stderr)
            return 2
        bad = bad or not ok
        if not r.get("enrolled"):
            print(f"[skip] {path} - {r['note']}")
        elif ok:
            print(f"[PASS] {path} - {r['metrics_found']} metric(s), all cite evidence ({os.path.basename(ledger)})")
        else:
            if r["unverified"]:
                print(f"[FAIL] {path} - uncovered metric(s) with NO evidence-ledger entry: {', '.join(r['unverified'])}")
            for st in STATUSES:
                if r[st]:
                    print(f"[FAIL] {path} - metric(s) acknowledged {st.upper()} (a triage mark, not evidence, gate still fails): {', '.join(r[st])}")
            print(f"       add each to {ledger} with its source, or cut the claim.")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
