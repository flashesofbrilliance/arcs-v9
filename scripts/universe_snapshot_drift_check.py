#!/usr/bin/env python3
"""universe_snapshot_drift_check: is the committed universe snapshot (the HUD's field data) stale?

The snapshot (runtime/specs/universe-snapshot.json, projected to src/data/universe-field.json) is a
pure function of the tracked tree, but nothing regenerates it between commits: the pre-commit hook
only runs `universe_snapshot_emit.py --check` when the snapshot's own inputs are staged. So the
HUD's counts drift with every file added (measured 2026-10-18: 335 commits and +146 tracked files,
3.4%, in about a day), and its history stamp (epoch, as_of_sha, as_of_date) is null until
`--refresh` has completed once, so the HUD cannot say how old a reading is.

This script is the OPEN-end receipt, the same shape as lattice_drift_check.py:
  - calls the emitter's own check() (a pure render; nothing is written to the snapshot outputs),
  - reads the committed history stamp and the age of the last regeneration commit,
  - prints one line and appends one receipt row to _INBOX/universe-snapshot-drift.jsonl
    (gitignored; the rows give the drift RATE over time).
It never regenerates and never runs --refresh (that pushes to origin/main by design and stays
human-gated). Stdlib only. Exit 0 always (hook-safe): a drift is a receipt, not a failure.

  universe_snapshot_drift_check.py              # print one line, append a receipt
  universe_snapshot_drift_check.py --self-test  # pure-function cases + the fail-safe path
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EMITTER = os.path.join(HERE, "universe_snapshot_emit.py")
RECEIPTS = os.path.join(ROOT, "_INBOX", "universe-snapshot-drift.jsonl")
SNAP = "runtime/specs/universe-snapshot.json"


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT, check=True).stdout
    except Exception:
        return ""


def summarize(r: dict) -> str:
    """One line. Pure, so the self-test can pin it."""
    n = len(r["stale"])
    st = r.get("stamp_epoch")
    stamp = "null (--refresh has never completed)" if st is None else "epoch %s as of %s %s" % (st, r.get("stamp_sha") or "?", r.get("stamp_date") or "?")
    if n == 0:
        return "universe-snapshot: fresh · committed content matches the tracked tree · history stamp %s" % stamp
    bits = ["STALE · %d file(s)" % n]
    if r.get("age_days") is not None:
        bits.append("last regenerated %sd ago (%s)" % (r["age_days"], r.get("last_regen") or "?"))
    if r.get("files_added_since") is not None and r.get("files_then"):
        bits.append("+%d tracked files (%.1f%%) since" % (r["files_added_since"], 100.0 * r["files_added_since"] / r["files_then"]))
    bits.append("history stamp %s" % stamp)
    return "universe-snapshot: " + " · ".join(bits)


def load_emitter(path: str):
    spec = importlib.util.spec_from_file_location("universe_snapshot_emit", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def reading(emitter_path: str = EMITTER) -> dict:
    m = load_emitter(emitter_path)
    stale = [p.replace("stale: ", "", 1) for p in m.check()]
    try:
        snap = json.load(open(os.path.join(ROOT, SNAP), encoding="utf-8"))
    except Exception:
        snap = {}
    last = git("log", "-1", "--format=%h %cs", "--", SNAP).split()
    age = None
    if len(last) == 2:
        try:
            age = (datetime.date.today() - datetime.date.fromisoformat(last[1])).days
        except ValueError:
            pass
    files_now = len([f for f in git("ls-files").split("\n") if f])
    files_then = len([f for f in git("ls-tree", "-r", "--name-only", last[0]).split("\n") if f]) if last else 0
    return {
        "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "head": git("rev-parse", "--short", "HEAD").strip(),
        "stale": stale, "last_regen": last[0] if last else None, "age_days": age,
        "files_then": files_then, "files_added_since": (files_now - files_then) if files_then else None,
        "stamp_epoch": snap.get("epoch"), "stamp_sha": snap.get("as_of_sha"), "stamp_date": snap.get("as_of_date"),
    }


def run(emitter_path: str = EMITTER, receipts: str = RECEIPTS) -> int:
    try:
        r = reading(emitter_path)
        print(summarize(r))
        os.makedirs(os.path.dirname(receipts), exist_ok=True)
        with open(receipts, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    except Exception as e:  # never fail the hook
        print("universe-snapshot: no reading (%s)" % type(e).__name__)
    return 0


def self_test() -> int:
    base = {"stale": [], "stamp_epoch": None, "age_days": 1, "last_regen": "abc1234", "files_then": 4000, "files_added_since": 120}
    stale = dict(base, stale=["a", "b", "c", "d"])
    stamped = dict(base, stamp_epoch=3, stamp_sha="deadbee", stamp_date="2026-10-18")
    cases = [
        ("fresh reads fresh, not STALE", "fresh" in summarize(base) and "STALE" not in summarize(base)),
        ("stale (bad) is caught and counted", "STALE" in summarize(stale) and "4 file(s)" in summarize(stale)),
        ("rate is shown as a percentage", "+120 tracked files (3.0%)" in summarize(stale)),
        ("null stamp says it never completed", "never completed" in summarize(base)),
        ("a stamp prints epoch, sha and date", "epoch 3 as of deadbee 2026-10-18" in summarize(stamped)),
    ]
    import contextlib
    import io
    import tempfile
    with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()) as buf:
        rc = run(os.path.join(d, "missing_emitter.py"), os.path.join(d, "r.jsonl"))
    cases.append(("a broken emitter never fails the hook (exit 0, one line)", rc == 0 and buf.getvalue().startswith("universe-snapshot: no reading")))
    ok = True
    for name, passed in cases:
        print(("✓ " if passed else "✖ ") + name)
        ok = ok and passed
    print("universe-snapshot-drift self-test: %d/%d" % (sum(1 for _, p in cases if p), len(cases)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else run())
