#!/usr/bin/env python3
"""Fixtures for integrity_gate.py matcher fixes: directory ancestors and placeholder-truncated cites.

Builds a synthetic git repo (never reads the live tree). Run: python3 scripts/integrity_gate_selftest.py
Each fail-on-bad case must FAIL, each pass-on-good case must pass (AGENTS.md gotcha 15).
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("integrity_gate", HERE / "integrity_gate.py")
ig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ig)

FILES = {
    "src/app/api/cron/route.ts": "x",
    "_DECISIONS/ADR-001-test.md": "x",
    "_DECISIONS/index.json": '[{"id": "ADR-001"}]',
}


def build_repo(root: Path) -> None:
    run = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True)
    run("init", "-q")
    for rel, body in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)
    run("add", "-A")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")


def verdicts(state, text: str) -> dict:
    """cite -> level for every finding gate() produces on text."""
    f = Path(state_dir) / "doc.md"
    f.write_text(text)
    rep = ig.gate(str(f), state)
    return {x["cite"]: x["level"] for x in rep["findings"]}


def main() -> int:
    global state_dir
    fails = []
    with tempfile.TemporaryDirectory() as d:
        state_dir = d
        root = Path(d)
        build_repo(root)
        ig.REPO = root
        state = ig.RefState("HEAD", set())

        def check(name, ok):
            print(("ok   " if ok else "FAIL ") + name)
            if not ok:
                fails.append(name)

        # pass-on-good
        v = verdicts(state, "see `src/app/api` and `src/app/api/` here")
        check("dir holding only subdirs passes (src/app/api)", v.get("src/app/api") == "OK" and v.get("src/app/api/") == "OK")
        for ph in ("*", "<", "{"):
            _, _, paths, _ = ig.extract(f"cite `_DECISIONS/ADR-{ph}x` end")
            check(f"cite followed by {ph!r} is not extracted", not paths)
        # fail-on-bad
        v = verdicts(state, "see `src/app/nope/` and `src/app/api/cron/missing.ts`")
        check("missing dir still FAILS", v.get("src/app/nope/") == "FAIL")
        check("typo in full path still FAILS", v.get("src/app/api/cron/missing.ts") == "FAIL")
        v = verdicts(state, "see `_DECISIONS/ADR-0` and `_DECISIONS/ADR-001-te`")
        check("truncated-looking cite without placeholder still FAILS",
              v.get("_DECISIONS/ADR-0") == "FAIL" and v.get("_DECISIONS/ADR-001-te") == "FAIL")
        # regressions: ADR and SHA handling unchanged
        v = verdicts(state, "per ADR-001 and ADR-999")
        check("ADR: existing OK, missing FAIL", v.get("ADR-001") == "OK" and v.get("ADR-999") == "FAIL")
        head = subprocess.run(["git", "rev-parse", "--short=10", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
        v = verdicts(state, f"commit {head} and deadbeef1")
        check("SHA: merged commit OK, unknown not OK", v.get(head) == "OK" and v.get("deadbeef1") != "OK")
    print("PASS" if not fails else f"FAILED: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
