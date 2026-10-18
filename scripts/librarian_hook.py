#!/usr/bin/env python3
"""librarian_hook: pre-commit WARNING for ADR-088 triggers T2 (uncovered metric) and T3 (new term).

Looks only at lines ADDED in the staged diff of _CANON/**/*.md and operators/arcs_primitives.py.
Never blocks (always exit 0), never edits, never runs /echo-scan: it prints at most one line per
trigger, with the cost of each next step. T1 (novelty words) stays in /prior-art (ADR-088).
Disable for one commit with LIBRARIAN_HOOK=0.

  python3 scripts/librarian_hook.py            # staged diff
  python3 scripts/librarian_hook.py --self-test
"""
import json, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import provenance_lint as pl
import canon_claims_report as ccr

WATCH = ("_CANON/", "operators/arcs_primitives.py")
TERM = re.compile(r"\b[A-Z][a-z]+(?:-[A-Z][a-z]+)+\b|\b[A-Z]{3,6}\b")
GLOSSARY = "_CANON/ordinals/ARCS-Glossary-v0.1.md"
ROSETTA = "runtime/echo/rosetta.jsonl"
COST = "free: add a ledger entry / glossary line; /echo-scan costs ~15-25k tokens (offer only, not run)"

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout

def added_lines():
    """(file, lineno, text) for staged added lines in watched paths."""
    out, f, n = [], None, 0
    for ln in git("diff", "--cached", "-U0", "--diff-filter=AM", "--", *WATCH).splitlines():
        if ln.startswith("+++ b/"):
            f = ln[6:]
        elif ln.startswith("@@"):
            m = re.search(r"\+(\d+)", ln); n = int(m.group(1)) if m else 0
        elif ln.startswith("+") and not ln.startswith("+++") and f:
            out.append((f, n, ln[1:])); n += 1
    return out

def known_text():
    """Lower-cased corpus of terms already in the canon at HEAD, glossary and rosetta."""
    parts = []
    for p in git("ls-tree", "-r", "--name-only", "HEAD", "_CANON").split():
        if p.endswith(".md"):
            parts.append(git("show", f"HEAD:{p}"))
    for p in (GLOSSARY, ROSETTA):
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8", errors="replace").read())
    return "\n".join(parts).lower()

def analyze(lines, ledger_for, known):
    """Pure core. lines: [(file, lineno, text)]; ledger_for(file) -> compiled patterns."""
    t2, t3 = [], []
    for f, n, text in lines:
        pats = ledger_for(f)
        for m in list(pl.METRIC.finditer(text)) + list(ccr.EXTRA.finditer(text)):
            tok = m.group(0).strip()
            if pl.YEAR.match(tok):
                continue
            if not any(rx.search(text) and any(c.start() <= m.start() and m.end() <= c.end()
                       for c in rx.finditer(text)) for rx, _ in pats):
                t2.append((f, n, tok))
        if f.startswith("_CANON/"):
            for m in TERM.finditer(text):
                if m.group(0).lower() not in known:
                    t3.append((f, n, m.group(0)))
    return t2, t3

def messages(t2, t3):
    """At most one line per trigger (rate limit)."""
    out = []
    if t2:
        f, n, tok = t2[0]
        out.append(f"Librarian T2: {len(t2)} metric(s) with no evidence-ledger cover, first `{tok}` at {f}:{n}. {COST}")
    if t3:
        terms = sorted({t for _, _, t in t3})
        out.append(f"Librarian T3: {len(terms)} new canon term(s) not in glossary, rosetta or HEAD canon: {', '.join(terms[:3])}"
                   + (" ..." if len(terms) > 3 else "") + f". {COST}")
    return out

def ledger_for(f):
    led = ccr.nearest_ledger(f, "_CANON" if f.startswith("_CANON/") else os.path.dirname(f))
    return pl.load_ledger(led) if led else []

def self_test():
    ok = True
    def check(name, cond):
        nonlocal ok; print(("PASS " if cond else "FAIL ") + name); ok &= bool(cond)
    cov = [(re.compile("87%", re.I), "x")]
    known = "the glossary knows kintsugi and rom"
    bad = [("_CANON/a.md", 3, "First system reaching 76% accuracy via the Zorblax-Kappa protocol")]
    good = [("_CANON/a.md", 3, "Seam repair is Kintsugi, 87% held in 2026")]
    t2, t3 = analyze(bad, lambda f: cov, known)
    check("bad: uncovered 76% flagged (T2)", [t for _, _, t in t2] == ["76%"])
    check("bad: new term Zorblax-Kappa flagged (T3)", [t for _, _, t in t3] == ["Zorblax-Kappa"])
    t2, t3 = analyze(good, lambda f: cov, known)
    check("good: covered 87%, known term, year ignored => silent", t2 == [] and t3 == [])
    many = [("_CANON/a.md", i, f"Aaaa-Bbbb{'x'*i} and 5{i}% more") for i in range(1, 9)]
    msgs = messages(*analyze(many, lambda f: [], ""))
    check("rate limit: <=1 line per trigger", len(msgs) == 2)
    check("every message states its cost", all("tokens" in m for m in msgs))
    # CLI end to end in a throwaway git repo: warns, exits 0, writes nothing
    me = os.path.abspath(__file__)
    with tempfile.TemporaryDirectory() as t:
        run = lambda *a: subprocess.run(a, cwd=t, capture_output=True, text=True,
                                        env={**os.environ, "PYTHONPATH": os.path.dirname(me)})
        run("git", "init", "-q"); run("git", "config", "user.email", "t@t"); run("git", "config", "user.name", "t")
        os.makedirs(os.path.join(t, "_CANON")); open(os.path.join(t, "_CANON", "a.md"), "w").write("seed\n")
        run("git", "add", "-A"); run("git", "commit", "-qm", "i")
        open(os.path.join(t, "_CANON", "a.md"), "a").write("Zorblax-Kappa gives 76% accuracy\n")
        run("git", "add", "-A")
        r = run(sys.executable, me)
        check("CLI: warns on bad staged diff and exits 0", r.returncode == 0 and "T2" in r.stderr and "T3" in r.stderr)
    return 0 if ok else 1

def main():
    if "--self-test" in sys.argv:
        return self_test()
    if os.environ.get("LIBRARIAN_HOOK") == "0":
        return 0
    lines = added_lines()
    if not lines:
        return 0
    for m in messages(*analyze(lines, ledger_for, known_text())):
        print("⚠ " + m, file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
