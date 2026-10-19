#!/usr/bin/env python3
"""archive_move_gate: a file that is moved, renamed or deleted must not leave a live citer behind.

Why (2026-10-18): release_notes.py, receipt_efficacy_probe.py, tributary_backfill_probe.py and
backlog_status_migrate.py were archived in two commits (4983bd57, c42d4b68) and the records citing
them were not re-pointed. The integrity gate only reads records that are staged, so the two night-moves
digests that still cited the old paths went unnoticed until a full sweep found them as NEW failures.
This gate runs on the commit that moves the file, where the fix is one line.

What it checks. For every staged rename or delete (git diff --cached -M), the OLD path is searched
as a whole path in the index (so a citer fixed in the same commit counts as fixed). A hit is a
FAIL unless the citer is exempt:
  exempt files: _ARCHIVE/, _RELEASES/, _HANDOFFS/fragments/, generated catalogs, the integrity baseline
  warn-only:    _QUEUE/induced-backlog.jsonl (historical prose rows; the readiness card flags dead routes) and
                .json or .jsonl files under _STATE/ (point-in-time inventories that list hundreds of paths)
  skipped line: for a rename, a citer line that also names the NEW path (it documents the move, "old -> new")
  not gated:    moves OUT of _ARCHIVE/, _RELEASES/, _INBOX/, and deleted handoff fragments (a molt does that)
Not caught: a directory cited without a file name, and a bare basename. The check is by full path.

  python3 scripts/archive_move_gate.py --staged     # pre-commit: staged moves and deletes vs the index
  python3 scripts/archive_move_gate.py --rev SHA    # a past commit: SHA^..SHA, citers read from tree SHA
  python3 scripts/archive_move_gate.py --self-test

Exit 0 clean (warnings may print), 1 on a FAIL, 2 on bad usage. One-off bypass in the hook only:
ARCHIVE_MOVE_GATE=0 git commit ... (say why in the commit message). Stdlib only; reads git.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GONE_EXEMPT = ("_ARCHIVE/", "_RELEASES/", "_HANDOFFS/fragments/", "_INBOX/")
CITER_EXEMPT = ("_ARCHIVE/", "_RELEASES/", "_HANDOFFS/fragments/", "runtime/specs/artifact-reuse-catalog.",
                "runtime/specs/tool-catalog.", "runtime/specs/surface-catalog.", "scripts/integrity_baseline.json")
CITER_WARN = ("_QUEUE/induced-backlog.jsonl",)


def git(root: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True).stdout


def gone_paths(root: Path, rev: str | None) -> dict[str, str | None]:
    """{old path: new path or None} for renamed or deleted tracked files, minus the exempt prefixes."""
    args = ["diff", "--name-status", "-M", "--diff-filter=DR"]
    out = git(root, *(args + ([f"{rev}^", rev] if rev else ["--cached"])))
    gone: dict[str, str | None] = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if parts and parts[0][:1] in ("D", "R") and len(parts) >= 2:
            old = parts[1]
            if not old.startswith(GONE_EXEMPT) and old != ".gitkeep" and not old.endswith("/.gitkeep"):
                gone[old] = parts[2] if parts[0][:1] == "R" and len(parts) >= 3 else None
    return gone


def citers(root: Path, old: str, rev: str | None, also_gone: set[str], new: str | None = None) -> list[tuple[str, int, str]]:
    """(file, line, text) for every whole-path mention of `old` in the index (or tree `rev`)."""
    rx = re.compile(r"(?<![\w/.-])" + re.escape(old) + r"(?![\w/-])(?!\.\w)")
    # --cached is an option and must come before the pattern; a revision comes after it
    args = ["grep", "-n", "-I", "-F"] + ([] if rev else ["--cached"]) + ["-e", old] + ([rev] if rev else [])
    hits = []
    for line in git(root, *args).splitlines():
        if rev and line.startswith(rev + ":"):
            line = line[len(rev) + 1:]
        m = re.match(r"^(.*?):(\d+):(.*)$", line)
        if not m:
            continue
        f, n, text = m.group(1), int(m.group(2)), m.group(3)
        if f in also_gone or f == old or not rx.search(text):
            continue
        if new and new in text:
            continue  # a line that names both paths documents the move
        hits.append((f, n, text.strip()[:140]))
    return hits


def check(root: Path, rev: str | None = None) -> tuple[list, list]:
    gone = gone_paths(root, rev)
    fails, warns = [], []
    for old, new in gone.items():
        for f, n, text in citers(root, old, rev, set(gone), new):
            if f.startswith(CITER_EXEMPT):
                continue
            snapshot = f.startswith("_STATE/") and f.endswith((".json", ".jsonl"))
            (warns if (f in CITER_WARN or snapshot) else fails).append((old, f, n, text))
    return fails, warns


def report(fails: list, warns: list) -> None:
    for old, f, n, text in warns:
        print(f"  warn  {f}:{n} still names moved path {old} (historical record; not blocking)")
    if not fails:
        return
    by_old: dict[str, list] = {}
    for old, f, n, text in fails:
        by_old.setdefault(old, []).append((f, n, text))
    print(f"archive_move_gate: {len(by_old)} moved or deleted path(s) still cited by live files")
    for old, hits in by_old.items():
        print(f"  x {old}")
        for f, n, text in hits[:6]:
            print(f"      cited at {f}:{n}: {text}")
        if len(hits) > 6:
            print(f"      ... and {len(hits) - 6} more")
    print("  fix: re-point each cite to the new path (or drop it) in THIS commit, then re-stage.")
    print("  before moving a file: python3 scripts/neighbor_scan.py <path> lists who cites it.")
    print("  one-off bypass: ARCHIVE_MOVE_GATE=0 git commit ... (say why in the message).")


# ---- self-test --------------------------------------------------------------------------------
def _run(root: Path, *a: str) -> None:
    subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=True)


def self_test() -> int:
    fails = 0

    def check_(label: str, cond: bool, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label} {detail if not cond else ''}")
        fails += 0 if cond else 1

    def fresh() -> Path:
        r = Path(tempfile.mkdtemp())
        _run(r, "init", "-q")
        _run(r, "config", "user.email", "t@t")
        _run(r, "config", "user.name", "t")
        _run(r, "config", "commit.gpgsign", "false")
        for rel, body in (("scripts/a.py", "x = 1\n"), ("scripts/ab.py", "y = 2\n"),
                          ("_STATE/note.md", "see `scripts/a.py` for the probe.\n"),
                          ("_ARCHIVE/old.md", "scripts/a.py was here\n"),
                          ("_QUEUE/induced-backlog.jsonl", '{"route": "scripts/a.py"}\n'),
                          ("_HANDOFFS/fragments/f.md", "frag\n"), ("CLAUDE.md", "molted from `_HANDOFFS/fragments/f.md`\n")):
            p = r / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
        _run(r, "add", "-A")
        _run(r, "commit", "-q", "-m", "init")
        return r

    # 1. fail-on-bad: archive a cited script without touching the citer
    r = fresh()
    (r / "_ARCHIVE").mkdir(exist_ok=True)
    _run(r, "mv", "scripts/a.py", "_ARCHIVE/a.py")
    f, w = check(r)
    check_("moving a cited script FAILS and names the live citer", [x[1] for x in f] == ["_STATE/note.md"], f)
    check_("the backlog row is a warning, the _ARCHIVE mention is ignored", [x[1] for x in w] == ["_QUEUE/induced-backlog.jsonl"], w)
    # 2. pass-on-good: the same move with the citer fixed in the same commit
    (r / "_STATE/note.md").write_text("see `_ARCHIVE/a.py` for the probe.\n")
    _run(r, "add", "_STATE/note.md")
    f, w = check(r)
    check_("the same move PASSES once the citer is re-pointed in the index", f == [], f)
    # 3. --rev reads a committed move
    _run(r, "commit", "-q", "-m", "archive a")
    f, _ = check(r, "HEAD")
    check_("--rev on a clean committed move passes", f == [], f)
    # 4. --rev catches the unfixed historical shape
    r2 = fresh()
    _run(r2, "mv", "scripts/a.py", "scripts/b.py")
    _run(r2, "commit", "-q", "-m", "rename without fixing the citer")
    f, _ = check(r2, "HEAD")
    check_("--rev on an unfixed rename FAILS", [x[1] for x in f] == ["_STATE/note.md"], f)
    # 5. delete with no citers
    r3 = fresh()
    _run(r3, "rm", "-q", "scripts/ab.py")
    f, _ = check(r3)
    check_("deleting an uncited file passes (ab.py is not a mention of a.py)", f == [], f)
    # 6. boundary: a longer name must not count, a sentence-ending period must
    r4 = fresh()
    (r4 / "_STATE/note.md").write_text("see scripts/ab.py and scripts/a.py.bak only\n")
    _run(r4, "add", "-A")
    _run(r4, "commit", "-q", "-m", "boundary")
    _run(r4, "mv", "scripts/a.py", "_ARCHIVE/a.py")
    f, _ = check(r4)
    check_("scripts/ab.py and scripts/a.py.bak are not mentions of scripts/a.py", f == [], f)
    (r4 / "_STATE/note.md").write_text("the probe is scripts/a.py. Done.\n")
    _run(r4, "add", "-A")
    f, _ = check(r4)
    check_("a mention that ends a sentence still counts", [x[1] for x in f] == ["_STATE/note.md"], f)
    # 7. a molt deletes handoff fragments that CLAUDE.md names; that is not a move to guard
    r5 = fresh()
    _run(r5, "rm", "-q", "_HANDOFFS/fragments/f.md")
    f, _ = check(r5)
    check_("deleting a handoff fragment passes", f == [], f)
    # 7b. a rename documented as "old -> new" is not a stale cite; a snapshot inventory only warns
    r6 = fresh()
    (r6 / "_STATE/note.md").write_text("moved scripts/a.py -> _ARCHIVE/a.py on purpose.\n")
    (r6 / "_STATE/inventory.json").write_text('{"path": "scripts/a.py"}\n')
    _run(r6, "add", "-A")
    _run(r6, "commit", "-q", "-m", "history note")
    _run(r6, "mv", "scripts/a.py", "_ARCHIVE/a.py")
    f, w = check(r6)
    check_("a line naming both old and new path is skipped", f == [], f)
    check_("a _STATE json inventory is a warning, not a failure", any(x[1] == "_STATE/inventory.json" for x in w), w)
    # 8. argv contract
    me = str(Path(__file__).resolve())
    p = subprocess.run([sys.executable, me, "--bogus"], capture_output=True, text=True, cwd=str(r5))
    check_("an unknown flag exits 2", p.returncode == 2, p.returncode)
    print("archive_move_gate self-test: ok" if not fails else f"archive_move_gate self-test: {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    rev = None
    if argv == ["--staged"]:
        pass
    elif len(argv) == 2 and argv[0] == "--rev":
        rev = argv[1]
    else:
        print(__doc__.split("\n\n")[0] + "\nusage: archive_move_gate.py --staged | --rev SHA | --self-test", file=sys.stderr)
        return 2
    fails, warns = check(ROOT, rev)
    report(fails, warns)
    if not fails:
        print("archive_move_gate: OK" + (f" ({len(warns)} historical warning(s))" if warns else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
