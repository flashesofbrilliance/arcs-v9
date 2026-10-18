#!/usr/bin/env python3
"""librarian_hook: pre-commit WARNING for ADR-088 triggers T2 (uncovered metric) and T3 (new term).

Looks only at lines ADDED in the staged diff of _CANON/**/*.md and operators/arcs_primitives.py.
Never blocks (always exit 0), never edits, never runs /echo-scan: it prints at most one line per
trigger, with the cost of each next step. T1 (novelty words) stays in /prior-art (ADR-088).
Disable for one commit with LIBRARIAN_HOOK=0.

  python3 scripts/librarian_hook.py            # staged diff
  python3 scripts/librarian_hook.py --report   # acceptance rule: ADR-088 K1
  python3 scripts/librarian_hook.py --self-test

Acceptance rule (Zach, 2026-10-17): a logged suggestion is ACCEPTED when a later commit adds a
ledger (evidence.jsonl), glossary or rosetta line for the flagged token; PENDING for 14 days;
then DECLINED. K1: accepted / (accepted + declined) < 1/3 after 10 distinct firing days.
The log lives in the git common dir (shared by every worktree, never tracked).
"""
import datetime, json, os, re, subprocess, sys, tempfile
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

def messages(t2, t3, ack=frozenset()):
    """At most one line per trigger (rate limit). ack: tokens the ledger already marks unvalidated."""
    out = []
    new = [x for x in t2 if x[2] not in ack]
    old = [x for x in t2 if x[2] in ack]
    if new:
        f, n, tok = new[0]
        out.append(f"Librarian T2: {len(new)} metric(s) with no evidence-ledger cover, first `{tok}` at {f}:{n}. {COST}")
    elif old:
        f, n, tok = old[0]
        out.append(f"Librarian T2: {len(old)} added metric(s) re-use a figure the ledger marks unvalidated or projection, first `{tok}` at {f}:{n}. "
                   "Cite evidence or label it in the text; nothing new to triage.")
    if t3:
        terms = sorted({t for _, _, t in t3})
        out.append(f"Librarian T3: {len(terms)} new canon term(s) not in glossary, rosetta or HEAD canon: {', '.join(terms[:3])}"
                   + (" ..." if len(terms) > 3 else "") + f". {COST}")
    return out

def acknowledged(t2, f_to_unval):
    return {tok for f, _, tok in t2 if any(rx.search(tok) for rx, _ in f_to_unval(f))}

ACCEPT_PATHS = (":(glob)**/evidence.jsonl", ":(glob)**/*.evidence.jsonl", GLOSSARY, ROSETTA)
MUTE_DAYS = 14          # pending window; a declined row then mutes its token another MUTE_DAYS
WARN_MUTE_DAYS = 2 * MUTE_DAYS
K2_ROWS, K2_DAYS = 5, 3  # ADR-088 K2: >=5 declined within any 3 consecutive firing days

def log_path():
    d = git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    return os.path.join(d, "librarian-suggestions.jsonl") if d else None

def _now():
    return datetime.datetime.now(datetime.timezone.utc)

def _read_log(path):
    if not path or not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

def record(t2, t3, path=None, now=None):
    """Append one row per new (trigger, token, file); the first firing is the one that counts."""
    path = path or log_path()
    if not path:
        return 0
    n_ = now or _now()
    seen = {(r["trigger"], r["token"], r["file"]) for r in _read_log(path)
            if (n_ - datetime.datetime.fromisoformat(r["ts"])).days < WARN_MUTE_DAYS}
    rows = [("T2", t) for t in t2] + [("T3", t) for t in t3]
    n = 0
    with open(path, "a", encoding="utf-8") as fh:
        for trig, (f, ln, tok) in rows:
            if (trig, tok, f) in seen:
                continue
            seen.add((trig, tok, f))
            fh.write(json.dumps({"ts": (now or _now()).isoformat(), "trigger": trig, "token": tok,
                                 "file": f, "line": ln}) + "\n")
            n += 1
    return n

def muted(trigger, token, rows, now=None):
    """True while the latest logged row for this token is pending, or declined less than
    MUTE_DAYS ago (age < WARN_MUTE_DAYS). After that the token may warn, and log, again."""
    n_ = now or _now()
    ages = [(n_ - datetime.datetime.fromisoformat(r["ts"])).days for r in rows
            if r["trigger"] == trigger and r["token"] == token]
    return bool(ages) and min(ages) < WARN_MUTE_DAYS

def k2(res):
    """res: [(row, status)]. Declined rows per firing day; trip when any 3 consecutive firing days hold >=5."""
    per = {}
    for r, st in res:
        if st == "declined":
            per[r["ts"][:10]] = per.get(r["ts"][:10], 0) + 1
    days = sorted({r["ts"][:10] for r, _ in res})
    worst = max((sum(per.get(d, 0) for d in days[i:i + K2_DAYS]) for i in range(len(days))), default=0)
    return worst, worst >= K2_ROWS

def is_accepted(row, added):
    """added: '+' lines (without the plus) from ledger/glossary/rosetta commits after row['ts']."""
    tok = row["token"]
    for line in added:
        if tok.lower() in line.lower():
            return True
        try:
            pat = json.loads(line).get("pattern")
            if pat and re.search(pat, tok, re.I):
                return True
        except (ValueError, AttributeError, re.error):
            pass
    return False

def added_since(ts):
    out = []
    for ln in git("log", f"--since={ts}", "-p", "--format=", "--", *ACCEPT_PATHS).splitlines():
        if ln.startswith("+") and not ln.startswith("+++"):
            out.append(ln[1:])
    return out

def status(row, added, now=None):
    if is_accepted(row, added):
        return "accepted"
    age = (now or _now()) - datetime.datetime.fromisoformat(row["ts"])
    return "pending" if age.days < MUTE_DAYS else "declined"

def report(path=None, now=None, added_fn=added_since):
    rows = _read_log(path or log_path())
    res = [(r, status(r, added_fn(r["ts"]), now)) for r in rows]
    acc = sum(1 for _, s_ in res if s_ == "accepted")
    dec = sum(1 for _, s_ in res if s_ == "declined")
    pend = sum(1 for _, s_ in res if s_ == "pending")
    days = len({r["ts"][:10] for r in rows})
    ratio = acc / (acc + dec) if acc + dec else None
    k1 = "NOT YET MEASURABLE" if days < 10 or ratio is None else ("TRIPPED: throttle to T2 / stakes high" if ratio < 1/3 else "ok")
    worst, k2_trip = k2(res)
    lines = [f"suggestions {len(rows)}: accepted {acc}, pending {pend}, declined {dec}; firing days {days}",
             "K1 accepted/(accepted+declined): " + ("n/a" if ratio is None else f"{ratio:.2f}") + f" -> {k1}",
             f"K2 declined in worst {K2_DAYS} consecutive firing days: {worst} -> "
             + ("TRIPPED: mute T1 until re-registered (T1 is not built, so no live effect)" if k2_trip else "ok")]
    return lines, res

def unval_for(f):
    led = ccr.nearest_ledger(f, "_CANON" if f.startswith("_CANON/") else os.path.dirname(f))
    return pl.load_marked(led) if led else []

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
    # unvalidated acknowledgement: different wording, never silent
    unv = lambda f: [(re.compile("76%"), "audit:x")]
    t2b, _ = analyze(bad, lambda f: cov, known)
    ackset = acknowledged(t2b, unv)
    m_ack = messages(t2b, [], ackset)
    check("unvalidated re-use: still warns, labelled as a marked figure", len(m_ack) == 1 and "unvalidated or projection" in m_ack[0])
    check("unvalidated re-use: a different new metric still gets the normal warning",
          "no evidence-ledger cover" in messages(t2b + [("_CANON/a.md", 4, "91%")], [], ackset)[0])
    # acceptance rule: pure
    row = {"ts": "2026-10-01T00:00:00+00:00", "trigger": "T3", "token": "Zorblax-Kappa", "file": "_CANON/a.md", "line": 1}
    r2 = {**row, "trigger": "T2", "token": "76%"}
    soon = datetime.datetime.fromisoformat("2026-10-05T00:00:00+00:00")
    late = datetime.datetime.fromisoformat("2026-10-20T00:00:00+00:00")
    check("accept: glossary line naming the term", status(row, ["- Zorblax-Kappa: a protocol"], soon) == "accepted")
    check("accept: ledger pattern matching the metric", status(r2, ['{"pattern": "76%", "source": "x"}'], soon) == "accepted")
    check("pending inside 14 days with no entry", status(row, ["- unrelated"], soon) == "pending")
    check("declined after 14 days with no entry", status(row, ["- unrelated"], late) == "declined")
    check("unrelated ledger pattern does not accept", status(r2, ['{"pattern": "5%", "source": "x"}'], late) == "declined")
    with tempfile.TemporaryDirectory() as t:
        lg = os.path.join(t, "log.jsonl")
        n1 = record([("_CANON/a.md", 1, "76%")], [("_CANON/a.md", 1, "Zorblax-Kappa")], lg)
        n2 = record([("_CANON/a.md", 9, "76%")], [], lg)
        check("log: first firing recorded, repeat deduped", n1 == 2 and n2 == 0)
        lines, res = report(lg, soon, lambda ts: ["- Zorblax-Kappa: x"])
        check("report: accepted 1 pending 1, K1 not yet measurable", "accepted 1, pending 1" in lines[0] and "NOT YET" in lines[1])
    # re-warning mute
    def ago(days): return (late - datetime.timedelta(days=days)).isoformat()
    mk = lambda days, tok="76%", trig="T2": {"ts": ago(days), "trigger": trig, "token": tok, "file": "f", "line": 1}
    check("mute: pending (5d) token is muted", muted("T2", "76%", [mk(5)], late))
    check("mute: declined 20d ago still muted (<28d)", muted("T2", "76%", [mk(20)], late))
    check("mute: expires after 28d", not muted("T2", "76%", [mk(30)], late))
    check("mute: other token / other trigger not muted", not muted("T2", "5%", [mk(5)], late) and not muted("T3", "76%", [mk(5)], late))
    with tempfile.TemporaryDirectory() as t:
        lg = os.path.join(t, "log.jsonl")
        open(lg, "w").write(json.dumps(mk(30)) + "\n")
        check("log: expired row allows a fresh row for the same token", record([("f", 1, "76%")], [], lg, late) == 1)
    # K2
    def drow(day, i): return ({"ts": f"2026-10-{day:02d}T0{i}:00:00+00:00", "trigger": "T3", "token": f"t{day}{i}", "file": "f", "line": 1}, "declined")
    five = [drow(1, 1), drow(1, 2), drow(2, 1), drow(2, 2), drow(3, 1)]
    check("K2: 5 declined in 3 consecutive firing days trips", k2(five) == (5, True))
    check("K2: 4 declined does not trip", k2(five[:4])[1] is False)
    spread = [drow(1, 1), drow(2, 1), drow(3, 1), drow(4, 1), drow(5, 1)]
    check("K2: 5 declined spread one per day does not trip", k2(spread) == (3, False))
    check("K2: accepted and pending rows do not count", k2([(r, "accepted") for r, _ in five]) == (0, False))
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
        lg = os.path.join(t, ".git", "librarian-suggestions.jsonl")
        check("CLI: firing logged in git common dir, tree stays clean of logs", os.path.exists(lg) and "librarian" not in run("git", "status", "--porcelain").stdout)
        again = run(sys.executable, me)
        check("CLI: same token is silent on the second firing (muted) and not re-logged",
              again.returncode == 0 and "T2" not in again.stderr and "T3" not in again.stderr
              and len(open(lg).read().splitlines()) == 2)
        os.makedirs(os.path.join(t, "runtime", "echo"), exist_ok=True)
        open(os.path.join(t, "_CANON", "evidence.jsonl"), "w").write(json.dumps({"pattern": "76%", "source": "self-reported:Z:2026-10-17"}) + "\n")
        run("git", "add", "-A"); run("git", "commit", "-qm", "ledger")
        r = run(sys.executable, me, "--report")
        check("CLI: --report counts the ledger commit as acceptance", "accepted 1" in r.stdout)
    return 0 if ok else 1

def main():
    if "--self-test" in sys.argv:
        return self_test()
    if "--report" in sys.argv:
        print("\n".join(report()[0]))
        return 0
    if os.environ.get("LIBRARIAN_HOOK") == "0":
        return 0
    lines = added_lines()
    if not lines:
        return 0
    t2, t3 = analyze(lines, ledger_for, known_text())
    try:
        rows = _read_log(log_path())
        t2 = [x for x in t2 if not muted("T2", x[2], rows)]
        t3 = [x for x in t3 if not muted("T3", x[2], rows)]
    except (OSError, ValueError):
        pass  # a broken log must never break a commit
    try:
        ack = acknowledged(t2, unval_for)
    except (pl.LedgerError, OSError, ValueError):
        ack = frozenset()
    for m in messages(t2, t3, ack):
        print("⚠ " + m, file=sys.stderr)
    try:
        record(t2, t3)
    except OSError:
        pass  # logging must never break a commit
    return 0

if __name__ == "__main__":
    sys.exit(main())
