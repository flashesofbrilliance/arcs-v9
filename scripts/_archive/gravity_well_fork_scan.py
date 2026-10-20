#!/usr/bin/env python3
"""gravity_well_fork_scan — the ziggurat decomposition detector.

A net-new folksonomy cluster is not flat forever. Once it accretes enough MASS
(member count) and GRAVITY (cross-repo/cross-domain spread), it should DECOMPOSE
into its own organism — a dedicated spec / ADR family / seed — rather than stay a
line item. This is the mechanized version of the manual Norse-witness-stack fork
(runtime/specs/ROM-CANDIDATES-norse-witness.md).

It does NOT fork anything. It DETECTS density and emits a FORK RECOMMENDATION into
the canon-propagation queue (kind:"fork", default "no"). The human forks via
/canon-review. NOTOMATION: detect + recommend, never author under write-lock.

  score = mass (count) × gravity (distinct repos among member_refs)
  fork recommended when score >= FORK_SCORE_MIN AND count >= FORK_MASS_MIN.

High-value SINGLE-repo net-news (e.g. the Norse stack: 8 members, 1 repo) do NOT
fork on mass×gravity — their pull is value, not cross-domain mass; they graduate
via the ESCALATE→promotion path instead. That distinction is intentional.

Usage:  python3 scripts/_archive/gravity_well_fork_scan.py <folksonomy.json> [--emit]
        --emit appends fork items to _INBOX/canon-propagation-queue.json.
        python3 scripts/_archive/gravity_well_fork_scan.py --self-test
Without --emit it is read-only. Stdlib only. Exit 0 on success; 2 on a bad
command line (unknown flag, extra or missing positional).
"""
import argparse, hashlib, json, os, sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
QUEUE = os.path.join(ROOT, "_INBOX/canon-propagation-queue.json")

FORK_SCORE_MIN = 16   # e.g. count 8 × 2 repos, or 6 × 3 — a real cross-domain well
FORK_MASS_MIN = 5     # floor: a cluster under 5 members isn't dense enough to fork


def repos_of(member_refs):
    out = set()
    for r in member_refs or []:
        out.add(r.split(":", 1)[0].strip() if ":" in r else "?")
    return out


def scan(folk):
    recs = []
    for c in folk.get("clusters", []):
        mass = int(c.get("count", 0))
        repos = repos_of(c.get("member_refs"))
        gravity = len(repos)
        score = mass * gravity
        if score >= FORK_SCORE_MIN and mass >= FORK_MASS_MIN:
            recs.append({
                "id": f"fork-{c.get('tag','?')}",
                "kind": "fork",
                "default": "no",
                "title": f"{c.get('tag','?')} ({mass} members × {gravity} repos = {score})",
                "proposal": (f"gravity-well: cluster '{c.get('tag')}' has mass {mass} across "
                             f"{gravity} repos ({', '.join(sorted(repos))}) — dense enough to fork "
                             f"into its own organism (spec/ADR/seed). {c.get('promotion_pattern','')}"),
                "score": score,
            })
    recs.sort(key=lambda r: -r["score"])
    return recs


def _snapshot(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            fp = os.path.join(dp, f)
            with open(fp, "rb") as fh:
                out[fp] = (hashlib.sha256(fh.read()).hexdigest(), os.stat(fp).st_mtime_ns)
    return out


def _self_test():
    import shutil, subprocess, tempfile
    tmp = tempfile.mkdtemp(prefix="gravity-well-selftest-")
    fails = total = 0
    try:
        me = os.path.join(tmp, "gravity_well_fork_scan.py")
        shutil.copy2(os.path.abspath(__file__), me)
        os.makedirs(os.path.join(tmp, "_INBOX"))
        folk = os.path.join(tmp, "folk.json")
        with open(folk, "w", encoding="utf-8") as fh:
            json.dump({"clusters": [
                {"tag": "wide", "count": 8, "member_refs": ["a:1", "b:2", "c:3"]},
                {"tag": "solo", "count": 9, "member_refs": ["a:1", "a:2"]}]}, fh)
        queue = os.path.join(tmp, "_INBOX/canon-propagation-queue.json")
        env = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)

        def run(*a):
            return subprocess.run([sys.executable, me, *a], capture_output=True, text=True, cwd=tmp, env=env)

        def ok(name, cond):
            nonlocal fails, total
            total += 1
            print(("  PASS  " if cond else "  FAIL  ") + name)
            fails += 0 if cond else 1

        before = _snapshot(tmp)
        ok("unknown flag exits 2", run("--bogus", folk).returncode == 2)
        ok("unknown flag with --emit exits 2 and writes nothing",
           run("--emit", "--bogus", folk).returncode == 2 and _snapshot(tmp) == before)
        ok("extra positional exits 2", run(folk, "extra").returncode == 2)
        ok("missing positional exits 2", run().returncode == 2)
        ok("--self-test with a path exits 2", run("--self-test", folk).returncode == 2)
        r = run(folk)
        ok("preview exits 0 and finds 1 fork", r.returncode == 0 and "1 fork-worthy" in r.stdout
           and "fork-wide" not in r.stdout and "wide (8 members" in r.stdout)
        ok("preview writes nothing", _snapshot(tmp) == before and not os.path.exists(queue))
        r = run(folk, "--emit")
        q = json.load(open(queue, encoding="utf-8")) if os.path.exists(queue) else {}
        ok("--emit appends 1 item", r.returncode == 0 and [i["id"] for i in q.get("items", [])] == ["fork-wide"])
        run(folk, "--emit")
        q = json.load(open(queue, encoding="utf-8")) if os.path.exists(queue) else {}
        ok("--emit is idempotent", len(q.get("items", [])) == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"gravity_well_fork_scan self-test: {total - fails}/{total}")
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gravity_well_fork_scan.py",
                                 description="Detect fork-worthy folksonomy clusters (mass x gravity).")
    ap.add_argument("folksonomy", nargs="?", help="folksonomy.json")
    ap.add_argument("--emit", action="store_true", help="append fork items to _INBOX/canon-propagation-queue.json")
    ap.add_argument("--self-test", action="store_true", help="assert the argv contract on synthetic input")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    if a.self_test:
        if a.folksonomy or a.emit:
            ap.error("--self-test takes no other arguments")
        return _self_test()
    if not a.folksonomy:
        ap.error("the following arguments are required: <folksonomy.json>")
    emit = a.emit
    folk = json.load(open(a.folksonomy, encoding="utf-8"))
    recs = scan(folk)
    print(f"gravity-well: {len(recs)} fork-worthy cluster(s) (score>={FORK_SCORE_MIN}, mass>={FORK_MASS_MIN})")
    for r in recs:
        print(f"  FORK  score={r['score']:>3}  {r['title']}")
    if emit and recs:
        q = {"items": []}
        if os.path.exists(QUEUE):
            try:
                q = json.load(open(QUEUE, encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        existing = {i.get("id") for i in q.get("items", [])}
        added = [r for r in recs if r["id"] not in existing]
        q.setdefault("items", []).extend(added)
        json.dump(q, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"gravity-well: appended {len(added)} fork item(s) to the canon-propagation queue")
    elif not emit:
        print("gravity-well: dry-run (pass --emit to append fork recommendations to the queue)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
