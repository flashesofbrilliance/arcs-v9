#!/usr/bin/env python3
"""seed_ledger_gate: a seed may not be born without a receipt.

WHY. On 2026-10-15 the seed bank had 23 of 70 index rows with no ledger row. Fifteen came from two
feature commits (3847ec41f, 24c1bf019) that added rows to _SEEDS/index.jsonl and none to
_SEEDS/ledger.jsonl; eight more had the same history. Planting a seed had no step that coupled the
index row to a ledger row, and seedbank_drift_check only noticed days later at session start.

RULE (pre-commit, staged state): every index row ADDED by this commit needs at least one ledger row
whose `seed` equals the row's alias (first token) or whose `seed_id` equals the row's id, in the
ledger as it will exist after the commit. Editing an existing row needs nothing new. A row that
claims status `germinated` must have a `germinated` event in the ledger (a status is a claim, and a
claim needs its receipt); that part is a WARN on rows this commit adds or re-statuses.

  seed_ledger_gate.py              check the staged state (what the pre-commit hook runs)
  seed_ledger_gate.py --self-test  throwaway git repo: fails on bad, passes on good, never touches this repo

Stdlib only. Exit 1 blocks the commit.
"""
import json, os, subprocess, sys, tempfile

INDEX = "_SEEDS/index.jsonl"
LEDGER = "_SEEDS/ledger.jsonl"


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def _rows(text):
    out = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def _staged(path, cwd):
    """File content as it will be committed (index), falling back to the working tree."""
    r = _git(["show", f":{path}"], cwd)
    return r.stdout if r.returncode == 0 else ""


def _head(path, cwd):
    r = _git(["show", f"HEAD:{path}"], cwd)
    return r.stdout if r.returncode == 0 else ""


def _alias(row):
    return (row.get("alias") or "").split(" ")[0]


def check(cwd="."):
    idx_new = _rows(_staged(INDEX, cwd))
    idx_old = {r.get("id"): r for r in _rows(_head(INDEX, cwd))}
    led = _rows(_staged(LEDGER, cwd))
    by_seed = {e.get("seed") for e in led}
    by_id = {e.get("seed_id") for e in led}
    events = {}
    for e in led:
        events.setdefault(e.get("seed_id") or e.get("seed"), set()).add(e.get("event"))
    fails, warns = [], []
    for r in idx_new:
        rid = r.get("id")
        old = idx_old.get(rid)
        added = old is None
        has = _alias(r) in by_seed or rid in by_id or rid.replace("seed-", "").replace("repo-", "") in by_seed
        if added and not has:
            fails.append(f"{rid}: new index row with no ledger row (seed '{_alias(r)}')")
        restated = added or (old is not None and old.get("status") != r.get("status"))
        if restated and r.get("status") == "germinated":
            evs = events.get(rid, set()) | events.get(_alias(r), set())
            if "germinated" not in evs:
                warns.append(f"{rid}: status 'germinated' but no 'germinated' event in the ledger")
    return fails, warns


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    fails, warns = check(".")
    for w in warns:
        print("WARN seed_ledger_gate:", w, file=sys.stderr)
    if fails:
        for f in fails:
            print("✖ seed_ledger_gate:", f, file=sys.stderr)
        print("  fix: append a ledger row (event 'planted' is honest for a new seed) in the same commit:", file=sys.stderr)
        print('  {"ts": "<date>", "seed": "<alias>", "seed_id": "<id>", "event": "planted", "tier": "<A|B|C>", "conformance": "...", "gaps": [...], "receipt": "..."}', file=sys.stderr)
        sys.exit(1)
    print("✓ seed_ledger_gate: every new index row has a ledger row")


def self_test():
    ok = True

    def check_(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as d:
        def sh(*a):
            return _git(list(a), d)
        sh("init", "-q")
        sh("config", "user.email", "t@t")
        sh("config", "user.name", "t")
        os.makedirs(os.path.join(d, "_SEEDS"))
        row = lambda i, a, **k: json.dumps({"id": i, "alias": a, **k}) + "\n"
        led = lambda s, i, e="planted": json.dumps({"ts": "2026-01-01", "seed": s, "seed_id": i, "event": e}) + "\n"
        w = lambda p, t: open(os.path.join(d, p), "w").write(t)
        w(INDEX, row("seed-a", "a"))
        w(LEDGER, led("a", "seed-a"))
        sh("add", "-A")
        sh("commit", "-q", "-m", "base")
        # bad: new index row, no ledger row
        w(INDEX, row("seed-a", "a") + row("seed-b", "b"))
        sh("add", "-A")
        f, _ = check(d)
        check_("fails on a new index row with no ledger row", len(f) == 1 and "seed-b" in f[0])
        # good: ledger row added in the same commit
        w(LEDGER, led("a", "seed-a") + led("b", "seed-b"))
        sh("add", "-A")
        f, _ = check(d)
        check_("passes when the ledger row is added in the same commit", f == [])
        sh("commit", "-q", "-m", "add b")
        # editing an existing row needs nothing new
        w(INDEX, row("seed-a", "a", note="edited") + row("seed-b", "b"))
        sh("add", "-A")
        f, _ = check(d)
        check_("editing an existing row needs no new ledger row", f == [])
        # alias match with a suffix token
        w(INDEX, row("seed-a", "a") + row("seed-b", "b") + row("seed-c", "c (proposed repo)"))
        w(LEDGER, led("a", "seed-a") + led("b", "seed-b") + led("c", "seed-c"))
        sh("add", "-A")
        f, _ = check(d)
        check_("alias with a '(suffix)' still matches its ledger row", f == [])
        # germinated claim without a germinated event warns
        w(INDEX, row("seed-a", "a") + row("seed-b", "b") + row("seed-c", "c (proposed repo)") + row("seed-d", "d", status="germinated"))
        w(LEDGER, led("a", "seed-a") + led("b", "seed-b") + led("c", "seed-c") + led("d", "seed-d"))
        sh("add", "-A")
        f, wn = check(d)
        check_("a germinated status with only a planted event warns, does not block", f == [] and len(wn) == 1)
    # entry point as the hook runs it: a subprocess in a repo, exit code 1 on bad and 0 on good
    me = os.path.abspath(__file__)
    with tempfile.TemporaryDirectory() as d:
        def sh(*a):
            return _git(list(a), d)
        sh("init", "-q"); sh("config", "user.email", "t@t"); sh("config", "user.name", "t")
        os.makedirs(os.path.join(d, "_SEEDS"))
        open(os.path.join(d, INDEX), "w").write(json.dumps({"id": "seed-a", "alias": "a"}) + "\n")
        open(os.path.join(d, LEDGER), "w").write(json.dumps({"seed": "a", "seed_id": "seed-a", "event": "planted"}) + "\n")
        sh("add", "-A"); sh("commit", "-q", "-m", "base")
        open(os.path.join(d, INDEX), "a").write(json.dumps({"id": "seed-b", "alias": "b"}) + "\n")
        sh("add", "-A")
        bad = subprocess.run([sys.executable, me], cwd=d, capture_output=True, text=True)
        check_("CLI exits 1 and names the seed on a bad staged state", bad.returncode == 1 and "seed-b" in bad.stderr and "Traceback" not in bad.stderr)
        open(os.path.join(d, LEDGER), "a").write(json.dumps({"seed": "b", "seed_id": "seed-b", "event": "planted"}) + "\n")
        sh("add", "-A")
        good = subprocess.run([sys.executable, me], cwd=d, capture_output=True, text=True)
        check_("CLI exits 0 on a good staged state", good.returncode == 0 and "Traceback" not in good.stderr)
    print("seed_ledger_gate self-test:", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    main()
