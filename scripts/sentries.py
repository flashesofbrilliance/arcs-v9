#!/usr/bin/env python3
"""sentries: five read-only watchers (stdlib only). Warn, never block, never write.

  seed-ledger  candidates with 0 uses after 7 days of ledger age; gate failures (kill lines tripped, drift)
  claims       over-claim phrases in docs and agent specs changed vs origin/main
  main-drift   main checkout off origin/main, so new .claude/ agents never load
  open-loops   rows in runtime/specs/honest-notes-owed.jsonl still open (merge receipts, honest-note fixes)
  discovery    an engagement whose unpaid hours passed its cap (scripts/engagement_hours.py --check)

  python3 scripts/sentries.py            # run all, print SENTRY lines, exit 0
  python3 scripts/sentries.py --self-test
"""
import json, os, re, subprocess, sys, tempfile, time

OVERCLAIM = re.compile(r"\b(era-true|authentic to|verified 19\d\d|proves? (it|the|that)|is fake|detects? fake)\b", re.I)
HEDGE = re.compile(r"\b(never|not|cannot|can't|refuse|must|grep|kill|flag|claim|says?)\b", re.I)

def sh(*a, cwd="."):
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""

def seed_ledger(root, now=None):
    out, now = [], now or time.time()
    p = os.path.join(root, "runtime/specs/agent-seed-ledger.jsonl")
    if not os.path.exists(p): return ["WARN seed-ledger: ledger missing"]
    age = now - float(sh("git", "log", "-1", "--format=%ct", "--", p, cwd=root) or now)
    for ln in open(p):
        if not ln.strip(): continue
        r = json.loads(ln)
        if r["status"] == "CANDIDATE" and not r.get("uses") and age > 7 * 86400:
            out.append(f"WARN seed-ledger: {r['name']} CANDIDATE with 0 uses after {int(age // 86400)}d; use it or kill it")
        nh = sum(1 for u in r.get("uses", []) if u.get("verdict") == "not_helpful")
        if r["status"] != "KILLED" and nh >= 2:
            out.append(f"ALARM seed-ledger: {r['name']} has {nh} not_helpful uses, kill line tripped")
    gate = os.path.join(root, "scripts/agent_seed_gate.py")
    if os.path.exists(gate):
        g = subprocess.run([sys.executable, gate, "--check"], cwd=root, capture_output=True, text=True)
        out += [f"ALARM seed-ledger: {l[5:]}" for l in g.stdout.splitlines() if l.startswith("FAIL ")]
    return out

def claims(root):
    changed = sh("git", "diff", "--name-only", "origin/main...HEAD", cwd=root).splitlines()
    out = []
    for f in changed:
        if not (f.startswith(("_PATTERNS/", ".claude/agents/", "_DECISIONS/")) and f.endswith(".md")): continue
        fp = os.path.join(root, f)
        if not os.path.exists(fp): continue
        for i, ln in enumerate(open(fp, encoding="utf-8"), 1):
            if OVERCLAIM.search(ln) and not HEDGE.search(ln):
                out.append(f"WARN claims: {f}:{i} unhedged over-claim phrase: {ln.strip()[:80]}")
    return out

def main_drift(root):
    main = sh("git", "worktree", "list", "--porcelain", cwd=root).splitlines()
    main = next((l[9:] for l in main if l.startswith("worktree ")), "")
    if not main: return []
    sh("git", "fetch", "-q", "origin", "main", cwd=main)
    head, om = sh("git", "rev-parse", "HEAD", cwd=main), sh("git", "rev-parse", "origin/main", cwd=main)
    out = []
    if head and om and head != om:
        out.append(f"WARN main-drift: main checkout at {head[:8]}, origin/main at {om[:8]}; new .claude/ agents do not load until it matches")
    ledger = os.path.join(main, "runtime/specs/agent-seed-ledger.jsonl")
    if os.path.exists(ledger):
        for ln in open(ledger):
            if ln.strip():
                n = json.loads(ln)["name"]
                if json.loads(ln)["status"] != "KILLED" and not os.path.exists(os.path.join(main, f".claude/agents/{n}.md")):
                    out.append(f"WARN main-drift: {n} not present in main checkout's .claude/agents/")
    return out

def open_loops(root):
    p = os.path.join(root, "runtime/specs/honest-notes-owed.jsonl")
    if not os.path.exists(p): return []
    out = []
    for ln in open(p):
        if ln.strip():
            r = json.loads(ln)
            if r.get("state") == "OPEN": out.append(f"WARN open-loops: {r['ref']} owes {r['owed']} (since {r['since']})")
    return out

def discovery(root):
    tool = os.path.join(root, "scripts/engagement_hours.py")
    if not os.path.exists(tool): return []
    r = subprocess.run([sys.executable, tool], cwd=root, capture_output=True, text=True)
    return [f"WARN discovery: {l.strip()}; free work past the cap is a choice, make it on purpose"
            for l in r.stdout.splitlines() if "OVER CAP" in l]

def kit_catalysts(root):
    tool = os.path.join(root, "scripts/kit_periodic_table.py")
    if not os.path.exists(tool): return []
    n = sh(sys.executable, tool, "--behind", cwd=root)
    return [f"WARN kit-catalysts: ledger is {n} kit-manifest commit(s) behind; run python3 scripts/kit_periodic_table.py --sync"] if n not in ("", "0") else []

SENTRIES = [("seed-ledger", seed_ledger), ("claims", claims), ("main-drift", main_drift), ("open-loops", open_loops), ("discovery", discovery), ("kit-catalysts", kit_catalysts)]

def self_test():
    ok = True
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "runtime/specs"))
        row = {"name": "idea-x", "status": "CANDIDATE", "prior": .6, "belief": "b", "kill_line": "k", "uses": [{"ref": "r", "verdict": "not_helpful"}] * 2}
        open(os.path.join(d, "runtime/specs/agent-seed-ledger.jsonl"), "w").write(json.dumps(row) + "\n")
        open(os.path.join(d, "runtime/specs/honest-notes-owed.jsonl"), "w").write(json.dumps({"ref": "PR 1", "owed": "receipt", "since": "x", "state": "OPEN"}) + "\n")
        a = seed_ledger(d); b = open_loops(d)
        for label, cond in [("tripped kill alarms", any("kill line tripped" in x for x in a)), ("open row warns", bool(b))]:
            ok &= cond; print("PASS" if cond else "FAIL", label)
    bad, good = "Frame is era-true.", "The gate must never say era-true."
    for label, ln, want in [("unhedged over-claim hits", bad, True), ("hedged mention passes", good, False)]:
        got = bool(OVERCLAIM.search(ln) and not HEDGE.search(ln)); ok &= got == want
        print("PASS" if got == want else "FAIL", label)
    return ok

if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(0 if self_test() else 1)
    root = sh("git", "rev-parse", "--show-toplevel") or "."
    lines = [l for _, f in SENTRIES for l in f(root)]
    for l in lines: print("SENTRY", l)
    print(f"sentries: {len(lines)} finding(s), read-only")
