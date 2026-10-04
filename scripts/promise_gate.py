#!/usr/bin/env python3
"""promise_gate.py: fail when a customer-facing promise stops being true.

Reads runtime/specs/public-promises.json (the promise ledger). For every active promise:
  1. each surface still shows the promised text (copy drift forces a ledger update), and
  2. each verifier passes: grep (code shape), gh-api (live GitHub state), sql (live DB,
     only when $PROMISE_DATABASE_URL is set), manual (a dated human check, fails when stale).

Born 2026-10-04: /trust, /privacy, /terms and the trust contract said "source code stays
public" while `gh repo view` returned PRIVATE. Nothing checked the claim against the world.

Usage:
  python3 scripts/promise_gate.py              # all verifiers; gh-api skipped if gh unavailable
  python3 scripts/promise_gate.py --offline    # pre-commit: skip gh-api and sql
  python3 scripts/promise_gate.py --strict     # CI: a skipped gh-api check is a failure
  python3 scripts/promise_gate.py --self-test  # prove each verifier fails on bad, passes on good
Exit 0 = all promises hold, 1 = a promise is broken, 2 = ledger malformed / bad usage.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = "runtime/specs/public-promises.json"
TYPES = {"grep", "gh-api", "sql", "manual"}


def _files(root, globs):
    out = set()
    for g in globs:
        out.update(p for p in root.glob(g) if p.is_file())
    return sorted(out)


def _rx(pattern):
    return re.compile(pattern, re.M)


def check_grep(v, root, **_):
    errs = []
    for c in v.get("must_contain", []):
        p = root / c["path"]
        if not p.is_file():
            errs.append(f"missing file {c['path']}")
        elif not _rx(c["pattern"]).search(p.read_text(errors="replace")):
            errs.append(f"{c['path']} no longer matches /{c['pattern']}/")
    for c in v.get("must_not_contain", []):
        rx = _rx(c["pattern"])
        for p in _files(root, c["paths"]):
            m = rx.search(p.read_text(errors="replace"))
            if m:
                line = p.read_text(errors="replace")[: m.start()].count("\n") + 1
                errs.append(f"{p.relative_to(root)}:{line} contains forbidden {m.group(0)!r}")
    for c in v.get("only_in", []):
        rx, allowed = _rx(c["pattern"]), set(c["allowed"])
        for p in _files(root, c["paths"]):
            rel = str(p.relative_to(root))
            if rel not in allowed and rx.search(p.read_text(errors="replace")):
                errs.append(f"{rel} matches /{c['pattern']}/, allowed only in {sorted(allowed)}")
    return ("fail", "; ".join(errs)) if errs else ("pass", "")


def _gh(endpoint, field):
    if not shutil.which("gh"):
        return None
    r = subprocess.run(["gh", "api", endpoint, "--jq", f".{field}"], capture_output=True, text=True, timeout=30)
    return r.stdout.strip() if r.returncode == 0 else None


def check_gh(v, offline=False, strict=False, gh=_gh, **_):
    if offline:
        return "skip", "offline"
    got = gh(v["endpoint"], v["field"])
    if got is None:
        return ("fail" if strict else "skip"), "gh unavailable or unauthenticated"
    if got.lower() != str(v["expect"]).lower():
        return "fail", f"{v['endpoint']} .{v['field']} = {got!r}, promise expects {v['expect']!r}. {v.get('on_fail', '')}".strip()
    return "pass", ""


def check_sql(v, offline=False, **_):
    url = os.environ.get("PROMISE_DATABASE_URL")
    if offline or not url or not shutil.which("psql"):
        return "skip", "no PROMISE_DATABASE_URL / psql"
    r = subprocess.run(["psql", url, "-tAc", v["query"]], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return "skip", "query error: " + r.stderr.strip()[:160]
    got = r.stdout.strip()
    return ("pass", "") if got == str(v["expect"]) else ("fail", f"query returned {got!r}, expects {v['expect']!r}")


def check_manual(v, today=None, **_):
    today = today or dt.date.today()
    age = (today - dt.date.fromisoformat(v["verified_on"])).days
    if age > int(v["max_age_days"]):
        return "fail", f"last human check {v['verified_on']} is {age}d old (max {v['max_age_days']}d). Re-verify: {v['how']}"
    return "pass", ""


CHECKS = {"grep": check_grep, "gh-api": check_gh, "sql": check_sql, "manual": check_manual}


def validate(ledger):
    errs, seen = [], set()
    for i, p in enumerate(ledger.get("promises", [])):
        pid = p.get("id") or f"#{i}"
        for k in ("id", "status", "text", "surfaces", "verifiers"):
            if k not in p:
                errs.append(f"{pid}: missing '{k}'")
        if pid in seen:
            errs.append(f"{pid}: duplicate id")
        seen.add(pid)
        if p.get("status") not in ("active", "retired"):
            errs.append(f"{pid}: status must be active|retired")
        if p.get("status") == "retired" and not p.get("reason"):
            errs.append(f"{pid}: retired promise needs a reason")
        if p.get("status") == "active" and not p.get("verifiers"):
            errs.append(f"{pid}: active promise has no verifier")
        for v in p.get("verifiers", []):
            if v.get("type") not in TYPES:
                errs.append(f"{pid}: unknown verifier type {v.get('type')!r}")
    return errs


def run(ledger, root, offline=False, strict=False, gh=_gh, today=None, quiet=False):
    errs = validate(ledger)
    if errs:
        for e in errs:
            print(f"✖ ledger: {e}", file=sys.stderr)
        return 2
    broken = 0
    counts = {"pass": 0, "fail": 0, "skip": 0}
    for p in ledger["promises"]:
        if p["status"] != "active":
            continue
        fails = []
        for s in p["surfaces"]:
            f = root / s["path"]
            if not f.is_file():
                fails.append(f"surface {s['path']} missing")
            elif s["contains"] not in f.read_text(errors="replace"):
                fails.append(f"surface {s['path']} no longer shows: {s['contains'][:80]!r} (copy changed? update the ledger in the same commit)")
        for v in p["verifiers"]:
            state, why = CHECKS[v["type"]](v, root=root, offline=offline, strict=strict, gh=gh, today=today)
            counts[state] += 1
            if state == "fail":
                fails.append(f"[{v['type']}] {why}")
            elif state == "skip" and not quiet:
                print(f"  skip {p['id']} [{v['type']}]: {why}", file=sys.stderr)
        if fails:
            broken += 1
            print(f"✖ promise '{p['id']}' broken: {p['text']}", file=sys.stderr)
            for f in fails:
                print(f"    {f}", file=sys.stderr)
    active = sum(1 for p in ledger["promises"] if p["status"] == "active")
    if not quiet or broken:
        print(f"promise-gate: {active - broken}/{active} active promises hold · checks pass {counts['pass']} fail {counts['fail']} skip {counts['skip']}")
    return 1 if broken else 0


def self_test():
    import contextlib, io
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()) as out:
        rc = _self_test()
    print("\n".join(l for l in out.getvalue().splitlines() if l.lstrip().startswith(("ok", "FAIL"))))
    print(f"promise-gate self-test: {'PASS' if rc == 0 else 'FAIL'}")
    return rc


def _self_test():
    ok = True

    def expect(name, got, want):
        nonlocal ok
        mark = "ok" if got == want else "FAIL"
        ok &= got == want
        print(f"  {mark:4} {name}: got {got}, want {want}")

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "src").mkdir()
        (r / "src/page.tsx").write_text("Nothing stored without sign-in\nif (userId) {\n")
        (r / "src/route.ts").write_text("prisma.lead.create(x)\n")
        base = {"id": "p", "status": "active", "text": "t",
                "surfaces": [{"path": "src/page.tsx", "contains": "Nothing stored without sign-in"}]}
        G = lambda v: {"promises": [dict(base, verifiers=[v])]}
        expect("grep must_contain good", run(G({"type": "grep", "must_contain": [{"path": "src/page.tsx", "pattern": r"if \(userId\)"}]}), r, quiet=True), 0)
        expect("grep must_contain bad", run(G({"type": "grep", "must_contain": [{"path": "src/page.tsx", "pattern": r"if \(admin\)"}]}), r, quiet=True), 1)
        expect("grep must_not good", run(G({"type": "grep", "must_not_contain": [{"paths": ["src/**/*.tsx"], "pattern": "(?i)repo is public"}]}), r, quiet=True), 0)
        (r / "src/bad.tsx").write_text("Repo is public and forkable\n")
        expect("grep must_not bad", run(G({"type": "grep", "must_not_contain": [{"paths": ["src/**/*.tsx"], "pattern": "(?i)repo is public"}]}), r, quiet=True), 1)
        expect("grep only_in good", run(G({"type": "grep", "only_in": [{"paths": ["src/**/*.ts"], "pattern": r"prisma\.lead\.create", "allowed": ["src/route.ts"]}]}), r, quiet=True), 0)
        (r / "src/other.ts").write_text("prisma.lead.create(y)\n")
        expect("grep only_in bad", run(G({"type": "grep", "only_in": [{"paths": ["src/**/*.ts"], "pattern": r"prisma\.lead\.create", "allowed": ["src/route.ts"]}]}), r, quiet=True), 1)
        ghv = {"type": "gh-api", "endpoint": "repos/x/y", "field": "visibility", "expect": "private"}
        expect("gh-api good", run(G(ghv), r, gh=lambda e, f: "PRIVATE", quiet=True), 0)
        expect("gh-api bad (repo flipped)", run(G(ghv), r, gh=lambda e, f: "public", quiet=True), 1)
        expect("gh-api unavailable, lenient", run(G(ghv), r, gh=lambda e, f: None, quiet=True), 0)
        expect("gh-api unavailable, strict", run(G(ghv), r, gh=lambda e, f: None, strict=True, quiet=True), 1)
        man = {"type": "manual", "verified_on": "2026-10-04", "max_age_days": 90, "how": "h"}
        expect("manual fresh", run(G(man), r, today=dt.date(2026, 11, 1), quiet=True), 0)
        expect("manual stale", run(G(man), r, today=dt.date(2027, 3, 1), quiet=True), 1)
        drift = {"promises": [dict(base, surfaces=[{"path": "src/page.tsx", "contains": "Nothing stored, ever"}], verifiers=[man])]}
        expect("surface copy drift", run(drift, r, today=dt.date(2026, 10, 5), quiet=True), 1)
        expect("ledger: active without verifier", run({"promises": [dict(base, verifiers=[])]}, r, quiet=True), 2)
        expect("ledger: unknown type", run(G({"type": "vibes"}), r, quiet=True), 2)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="skip gh-api and sql verifiers")
    ap.add_argument("--strict", action="store_true", help="a gh-api check that cannot run is a failure")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--ledger", default=LEDGER)
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    try:
        ledger = json.loads((ROOT / a.ledger).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"✖ ledger unreadable: {e}", file=sys.stderr)
        sys.exit(2)
    sys.exit(run(ledger, ROOT, offline=a.offline, strict=a.strict))


if __name__ == "__main__":
    main()
