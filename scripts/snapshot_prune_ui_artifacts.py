#!/usr/bin/env python3
"""snapshot_prune_ui_artifacts.py — keep _STATE/snapshot.json `ui_artifacts` honest.

Drops every call_briefs / product_status_pages entry whose `file` no longer exists in the
tracked tree (git ls-files), and records what was pruned. Mechanical; run after retiring a
brief. Found necessary 2026-09-06 when integrity_gate flagged 9 retired public/*.html cites.

    python3 scripts/snapshot_prune_ui_artifacts.py            # apply
    python3 scripts/snapshot_prune_ui_artifacts.py --dry-run  # report only
    python3 scripts/snapshot_prune_ui_artifacts.py --self-test
"""
import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

SNAP = "_STATE/snapshot.json"


def tracked_files() -> set:
    r = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True)
    if r.returncode != 0:
        # An empty set here would prune every entry; refuse instead.
        sys.exit(f"git ls-files failed (exit {r.returncode}): {r.stderr.strip()}")
    return {p for p in r.stdout.split("\0") if p}


def prune(dry: bool) -> int:
    tracked = tracked_files()
    with open(SNAP) as f:
        snap = json.load(f)
    ui = snap.get("ui_artifacts", {})
    pruned = []
    for key in ("call_briefs", "product_status_pages"):
        keep = []
        for row in ui.get(key, []):
            (keep if row.get("file") in tracked else pruned).append(row)
        ui[key] = keep
    for r in pruned:
        print(f"prune {r.get('file')}  ({r.get('subdomain')})")
    if not pruned:
        print("nothing to prune")
    elif not dry:
        today = str(datetime.now(timezone.utc).date())
        ui["_note"] = (ui.get("_note", "").split(" STALE ")[0].strip()
                       + f" Pruned {len(pruned)} retired entries on {today} via scripts/snapshot_prune_ui_artifacts.py.")
        # Ledger by subdomain + basename only: never the repo path, or the ledger itself becomes a
        # vapor cite that integrity_gate.py rightly flags forever.
        ui["pruned"] = ui.get("pruned", []) + [{"subdomain": r.get("subdomain"), "was": os.path.basename(r.get("file") or ""), "pruned_at": today} for r in pruned]
        with open(SNAP, "w") as f:
            json.dump(snap, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {SNAP}")
    return 0


def _snapshot(root: Path) -> dict:
    out = {}
    for f in sorted(root.rglob("*")):
        if f.is_file() and ".git" not in f.relative_to(root).parts:
            out[str(f.relative_to(root))] = (hashlib.sha256(f.read_bytes()).hexdigest(), f.stat().st_mtime_ns)
    return out


def self_test() -> int:
    """Run this script as a subprocess in a throwaway git repo with a synthetic snapshot."""
    import shutil, tempfile
    tmp = Path(tempfile.mkdtemp(prefix="snapshot-prune-selftest-"))
    fails = total = 0

    def ok(name, cond):
        nonlocal fails, total
        total += 1
        print(("  PASS  " if cond else "  FAIL  ") + name)
        fails += 0 if cond else 1

    try:
        me = tmp / "prune.py"
        shutil.copy2(Path(__file__).resolve(), me)
        repo = tmp / "repo"
        (repo / "_STATE").mkdir(parents=True)
        (repo / "public").mkdir()
        (repo / "public" / "live.html").write_text("x")
        snap = {"ui_artifacts": {"_note": "base STALE old", "call_briefs": [
            {"file": "public/live.html", "subdomain": "live"},
            {"file": "public/gone.html", "subdomain": "gone"},
            {"file": "", "subdomain": "blank"}], "product_status_pages": []}}
        (repo / "_STATE" / "snapshot.json").write_text(json.dumps(snap, indent=2) + "\n")
        git = lambda *a: subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
        git("init", "-q")
        git("add", "public/live.html")

        def run(*a, cwd=repo):
            return subprocess.run([sys.executable, str(me), *a], capture_output=True, text=True, cwd=cwd)

        ok("unknown flag exits 2", run("--bogus").returncode == 2)
        ok("extra positional exits 2", run("extra").returncode == 2)
        ok("extra positional with --dry-run exits 2", run("--dry-run", "extra").returncode == 2)
        before = _snapshot(tmp)
        r = run("--dry-run")
        ok("--dry-run exits 0 and reports both dead rows",
           r.returncode == 0 and "prune public/gone.html" in r.stdout and "(blank)" in r.stdout
           and "wrote" not in r.stdout)
        ok("--dry-run writes and deletes nothing", _snapshot(tmp) == before)
        outside = tmp / "notgit"
        outside.mkdir()
        (outside / "_STATE").mkdir()
        shutil.copy2(repo / "_STATE" / "snapshot.json", outside / "_STATE" / "snapshot.json")
        before_out = _snapshot(tmp)
        r = run(cwd=outside)
        ok("git failure refuses instead of pruning everything",
           r.returncode != 0 and _snapshot(tmp) == before_out)
        r = run()
        after = json.loads((repo / "_STATE" / "snapshot.json").read_text())["ui_artifacts"]
        ok("apply prunes dead rows, keeps live one",
           r.returncode == 0 and [x["file"] for x in after["call_briefs"]] == ["public/live.html"]
           and [x["was"] for x in after["pruned"]] == ["gone.html", ""] and after["_note"].startswith("base Pruned 2"))
        ok("second apply is a no-op", run().stdout.strip() == "nothing to prune")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"snapshot_prune_ui_artifacts self-test: {total - fails}/{total}")
    return 1 if fails else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="snapshot_prune_ui_artifacts.py",
                                description="Prune retired call_briefs / product_status_pages from _STATE/snapshot.json.")
    p.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    p.add_argument("--self-test", action="store_true", help="run the argv/no-write contract tests and exit")
    args = p.parse_args(argv)
    if args.self_test:
        return self_test()
    return prune(args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
