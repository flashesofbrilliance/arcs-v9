#!/usr/bin/env python3
"""signal_receipt.py — a self-measuring shipped-vs-reworked signal instrument.

The ARCS instinct turned on itself: instead of vibes ("that felt productive"),
compute a DETERMINISTIC receipt from git that makes a work window's signal-to-noise
legible. Same git range -> byte-identical output.

Mirrors scripts/belief_log_emit.py exactly in shape: a single source of truth
(here, the git object store at a FIXED set of commit SHAs) -> a lawful transform
(the receipt) -> a baked-in `--check` gate that proves the transform never drifts
from its source (WORLD.md Field Geometry; the belief-log's F27 open-loop-decay).

--------------------------------------------------------------------------------
RED THREAD -- the metric definitions, pinned here BEFORE the code (honest first):

A "window" is an ordered list of NON-MERGE commits (merges are bookkeeping, not
authored work). It is resolved once, at emit time, from a spec (--branch / --since
/ --range) into concrete SHAs and STORED in the receipt. Every number below is a
pure function of that SHA list + the git object store, so a re-run recomputes the
exact same bytes -- that is what --check verifies.

  shipped          = commits landed in the window (count) + net-new deliverable
                     files added in the window (git diff-filter=A, distinct paths).
                     This is the "net-new shipped work" numerator.

  rework           = churn that re-touches ground already covered in the SAME
                     window. A file is REWORKED if EITHER:
                       (a) it is touched in MORE THAN ONE commit in the window
                           (same-file re-touch), OR
                       (b) it is touched by a revert- or fix-typed commit
                           (subject matches ^(revert|fix)\\b, case-insensitive:
                           conventional `fix:`, `fix(scope):`, `revert:`, and the
                           default `Revert "..."` message all match).

  total_touched    = count of DISTINCT files touched anywhere in the window.

  churn_ratio      = reworked_files / total_touched   (in [0,1]; 0.0 if nothing
                     was touched). rework / total, exactly as specified.

  verdict          = a fixed band on churn_ratio (no wall-clock, no judgement):
                       churn_ratio <  0.25  -> "mostly-shipped"
                       0.25 <= churn_ratio < 0.50 -> "mixed"
                       churn_ratio >= 0.50  -> "mostly-rework"

KNOWN BLIND SPOT (KINTSUGI -- show the seam, do not hide it): force-pushes leave
NO trace in the commit graph of a fresh clone (the reflog is local and expires),
so a deterministic receipt computed from `git log` CANNOT count them. Rework here
is the git-visible proxy (re-touch + revert/fix commits), never the whole truth.
This is recorded in the receipt's `blind_spots` field, not silently dropped.

NEEDLE (falsifiable kill condition, pre-registered -- run `--selftest`):
  A window engineered to be MOSTLY REWORK -- the same file edited across several
  commits plus a revert -- MUST score churn_ratio >= 0.50 / verdict "mostly-rework".
  A window engineered to be MOSTLY SHIPPED -- N distinct files each added in one
  commit, none re-touched, no revert/fix -- MUST score churn_ratio < 0.25 /
  "mostly-shipped". If EITHER fails, the metric is lying about signal-to-noise and
  this tool must be killed or redefined. `--selftest` builds both in throwaway git
  repos and asserts it; it runs in CI so the kill condition is never just a comment.
--------------------------------------------------------------------------------

Usage:
    # emit a receipt for a branch's commits not yet on its base (default base: main)
    python3 scripts/signal_receipt.py --branch claude/x --id my-window
    python3 scripts/signal_receipt.py --since 2026-09-01 --id sept
    python3 scripts/signal_receipt.py --range A..B --id ab

    python3 scripts/signal_receipt.py --check       # audit: recompute every stored
                                                    # receipt from its own SHAs and
                                                    # verify byte-identical (exit 1 on drift)
    python3 scripts/signal_receipt.py --selftest    # prove the falsifiable kill condition

stdlib-only (AGENTS.md foundation rule). No network. Reads git via subprocess.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECEIPTS_DIR = ROOT / "_STATE" / "signal-receipts"
OUT_HTML = ROOT / "_STATE" / "signal-receipt.html"
TEMPLATE = ROOT / "scripts" / "signal_receipt_template.html"
DATA_MARKER = "/*SIGNAL_DATA*/"

# Verdict bands on churn_ratio (pinned in the RED THREAD above).
MIXED_FLOOR = 0.25
REWORK_FLOOR = 0.50

# A commit is "rework-typed" if its subject starts with revert or fix (any case),
# on a word boundary so `fixture:` / `revertible` don't false-match.
REWORK_SUBJECT = re.compile(r"^\s*(revert|fix)\b", re.IGNORECASE)

# Schema version -- bump only on a breaking change to the receipt shape so old
# receipts fail --check loudly rather than silently comparing against a new layout.
# v2: dropped totals.insertions/deletions (numstat line counts were git-version /
# .gitattributes sensitive, breaking determinism); the metric is file-level only.
SCHEMA = "signal-receipt/v2"


# --------------------------------------------------------------------------- git

def git(args: list[str], cwd: pathlib.Path = ROOT) -> str:
    """Run a git command, return stdout. Raises on non-zero (fail loud)."""
    res = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, check=False
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({res.returncode}): {res.stderr.strip()}"
        )
    return res.stdout


def resolve_commits(spec: dict, cwd: pathlib.Path = ROOT) -> list[str]:
    """Resolve a spec into an ORDERED (oldest-first) list of non-merge commit SHAs.

    spec is one of:
      {"branch": "<ref>", "base": "<baseref>"}  -> base..branch
      {"since": "<date>", "until": "<date?>", "ref": "<ref>"}
      {"range": "<A..B>"}
    """
    args = ["rev-list", "--reverse", "--no-merges"]
    if "branch" in spec:
        base = spec.get("base", "main")
        args.append(f"{base}..{spec['branch']}")
    elif "range" in spec:
        args.append(spec["range"])
    elif "since" in spec:
        args += [f"--since={spec['since']}"]
        if spec.get("until"):
            args.append(f"--until={spec['until']}")
        args.append(spec.get("ref", "HEAD"))
    else:
        raise ValueError(f"unrecognized spec: {spec}")
    out = git(args, cwd=cwd).strip()
    return out.splitlines() if out else []


def commit_details(shas: list[str], cwd: pathlib.Path = ROOT) -> list[dict]:
    """For each SHA (in the given order), return {sha, subject, files:[...]}.

    Determinism is the whole point, so this uses PLUMBING with stable, documented
    output contracts rather than porcelain:

      * subjects: one `git log --no-walk --format=%H<US>%s` call. %s is the first
        message line, stable across versions.
      * changed files: `git diff-tree` PER commit. diff-tree reports a path as
        changed iff the two tree entries' blob OIDs differ -- a pure function of
        the immutable objects, independent of git version, `.gitattributes`,
        core.autocrlf, or any diff/textconv filter. `-r` recurses, `--root` emits
        a root commit's full tree, `--no-renames` makes a rename add(new)+del(old)
        (both counted as touched), `--no-commit-id --name-only` prints bare paths.

    Earlier revisions used `git show --numstat` (line counts vary by git version /
    attributes) and then `git show --no-walk=unsorted <many-shas>` (`--no-walk` is a
    `git log` option whose `git show` handling differs between 2.43 and 2.55); both
    broke `--check` on CI while passing locally. diff-tree by OID is the fix."""
    if not shas:
        return []
    subj_out = git(["log", "--no-walk", "--format=%H\x1f%s", *shas], cwd=cwd)
    subjects: dict[str, str] = {}
    for line in subj_out.splitlines():
        if "\x1f" in line:
            h, s = line.split("\x1f", 1)
            subjects[h] = s
    details: list[dict] = []
    for sha in shas:  # requested order (oldest-first) preserved directly
        out = git(
            ["diff-tree", "--no-commit-id", "--no-renames", "-r", "--root", "--name-only", sha],
            cwd=cwd,
        )
        files = [line for line in out.splitlines() if line.strip()]
        details.append({"sha": sha, "subject": subjects.get(sha, ""), "files": files})
    return details


# ----------------------------------------------------------------------- compute

def compute(details: list[dict]) -> dict:
    """Pure function of the commit details -> the metric block. No git, no clock."""
    touch_count: dict[str, int] = {}          # file -> number of commits touching it
    added_files: set[str] = set()             # first-seen files (net-new proxy at file level)
    seen: set[str] = set()
    rework_files: set[str] = set()
    revert_fix: list[dict] = []

    for c in details:
        is_rework_commit = bool(REWORK_SUBJECT.match(c["subject"]))
        if is_rework_commit:
            revert_fix.append({"sha": c["sha"][:12], "subject": c["subject"]})
        for f in c["files"]:
            touch_count[f] = touch_count.get(f, 0) + 1
            if f not in seen:
                seen.add(f)
                added_files.add(f)
            if is_rework_commit:
                rework_files.add(f)  # (b) touched by a revert/fix commit

    # (a) re-touch: a file touched in more than one commit in the window
    retouched = {f for f, n in touch_count.items() if n > 1}
    rework_files |= retouched

    total_touched = len(touch_count)
    reworked = len(rework_files)
    churn = round(reworked / total_touched, 4) if total_touched else 0.0
    verdict = (
        "mostly-rework" if churn >= REWORK_FLOOR
        else "mixed" if churn >= MIXED_FLOOR
        else "mostly-shipped"
    )

    return {
        "totals": {
            "commits": len(details),
            "files_touched": total_touched,
        },
        "shipped": {
            "commits": len(details),
            "files_added": len(added_files),
        },
        "rework": {
            "reworked_files": reworked,
            "retouched_files": sorted(retouched),
            "revert_fix_commits": revert_fix,
        },
        "churn_ratio": churn,
        "verdict": verdict,
    }


def build_receipt(receipt_id: str, spec: dict, details: list[dict]) -> dict:
    """Assemble the full, self-describing receipt. Everything git-derived is fixed
    given the SHAs, so this is deterministic."""
    metrics = compute(details)
    head = details[-1]["sha"] if details else None
    return {
        "schema": SCHEMA,
        "receipt_id": receipt_id,
        "spec": spec,
        "window": {
            "head": head,
            "commit_count": len(details),
            # The SSOT anchor: recompute reads exactly these SHAs (oldest-first).
            "commits": [d["sha"] for d in details],
        },
        **metrics,
        "definitions": {
            "shipped": "commits in window + distinct files added (diff-filter=A)",
            "rework": "files re-touched across >1 window commit OR touched by a revert/fix commit",
            "churn_ratio": "reworked_files / files_touched",
            "verdict_bands": {
                "mostly-shipped": f"churn_ratio < {MIXED_FLOOR}",
                "mixed": f"{MIXED_FLOOR} <= churn_ratio < {REWORK_FLOOR}",
                "mostly-rework": f"churn_ratio >= {REWORK_FLOOR}",
            },
        },
        "blind_spots": [
            "force-pushes are invisible to git log in a fresh clone (reflog is local/ephemeral); "
            "rework here is the git-visible proxy only",
            "merge commits are excluded (--no-merges); rework measures authored work, not merge bookkeeping",
        ],
    }


def serialize(receipt: dict) -> str:
    """Canonical JSON: sorted keys, 2-space indent, one trailing newline.
    Byte-identical for identical content."""
    return json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


# -------------------------------------------------------------------------- html

def load_receipts() -> list[dict]:
    rows: list[dict] = []
    if not RECEIPTS_DIR.exists():
        return rows
    for p in sorted(RECEIPTS_DIR.glob("*.json")):
        rows.append(json.loads(p.read_text(encoding="utf-8")))
    return rows


def render_html(receipts: list[dict]) -> str:
    """Inject a projection of every receipt into the drift-ribbon template.
    `<` escaped so no field can break out of the <script> tag."""
    ordered = sorted(receipts, key=lambda r: r["receipt_id"])
    data = [
        {
            "receipt_id": r["receipt_id"],
            "verdict": r["verdict"],
            "churn_ratio": r["churn_ratio"],
            "commits": r["totals"]["commits"],
            "files_touched": r["totals"]["files_touched"],
            "files_added": r["shipped"]["files_added"],
            "reworked_files": r["rework"]["reworked_files"],
            "head": (r["window"]["head"] or "")[:12],
        }
        for r in ordered
    ]
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    template = TEMPLATE.read_text(encoding="utf-8")
    if DATA_MARKER not in template:
        sys.exit(f"AUDIT FAIL: {TEMPLATE.name} is missing the {DATA_MARKER} injection marker.")
    return template.replace(DATA_MARKER, blob)


# -------------------------------------------------------------------------- modes

def do_emit(receipt_id: str, spec: dict) -> int:
    details = commit_details(resolve_commits(spec), cwd=ROOT)
    receipt = build_receipt(receipt_id, spec, details)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS_DIR / f"{receipt_id}.json"
    path.write_text(serialize(receipt), encoding="utf-8")
    OUT_HTML.write_text(render_html(load_receipts()), encoding="utf-8")
    m = receipt
    print(
        f"wrote {path.relative_to(ROOT).as_posix()} + signal-receipt.html — "
        f"{m['totals']['commits']} commits, churn {m['churn_ratio']:.2f} -> {m['verdict']}."
    )
    return 0


def do_check() -> int:
    """Recompute every stored receipt from its own SHAs; verify byte-identical.
    Also verify the HTML view is current. Exit 1 on any drift."""
    receipts = load_receipts()
    if not receipts:
        print("OK — no signal receipts to audit.")
        return 0
    stale: list[str] = []
    for p in sorted(RECEIPTS_DIR.glob("*.json")):
        stored = p.read_text(encoding="utf-8")
        r = json.loads(stored)
        if r.get("schema") != SCHEMA:
            stale.append(f"{p.name} (schema {r.get('schema')!r} != {SCHEMA!r})")
            continue
        shas = r["window"]["commits"]
        try:
            details = commit_details(shas, cwd=ROOT)
        except RuntimeError as e:
            stale.append(f"{p.name} (range unreachable — need full history: {e})")
            continue
        got = {d["sha"] for d in details}
        if got != set(shas):
            stale.append(f"{p.name} (stored commits not all present in this clone)")
            continue
        recomputed = serialize(build_receipt(r["receipt_id"], r["spec"], details))
        if recomputed != stored:
            stale.append(f"{p.name} (recompute != stored — hand-edited or algo changed)")
    html_expected = render_html(receipts)
    html_actual = OUT_HTML.read_text(encoding="utf-8") if OUT_HTML.exists() else ""
    if html_actual != html_expected:
        stale.append("signal-receipt.html")
    if stale:
        print(f"DRIFT: {', '.join(stale)} — re-run `python3 scripts/signal_receipt.py --branch/--since ...`.")
        return 1
    print(f"OK — {len(receipts)} signal receipt(s) current with git (audit clean).")
    return 0


# ---------------------------------------------------------------------- selftest

def _git_init_repo(path: pathlib.Path) -> None:
    for args in (
        ["init", "-q", "-b", "main"],
        ["config", "user.email", "selftest@arcs.local"],
        ["config", "user.name", "selftest"],
        ["config", "commit.gpgsign", "false"],
    ):
        git(args, cwd=path)


def _commit(path: pathlib.Path, filename: str, content: str, subject: str) -> None:
    (path / filename).write_text(content, encoding="utf-8")
    git(["add", filename], cwd=path)
    git(["commit", "-q", "-m", subject], cwd=path)


def do_selftest() -> int:
    """Pre-registered falsifiable kill condition, proven in throwaway git repos."""
    failures: list[str] = []

    # Case A: MOSTLY REWORK — one file edited across 4 commits + a revert.
    with tempfile.TemporaryDirectory() as d:
        repo = pathlib.Path(d)
        _git_init_repo(repo)
        for i in range(4):
            _commit(repo, "same.txt", f"rev {i}\n", f"edit round {i}")
        _commit(repo, "same.txt", "reverted\n", 'Revert "edit round 3"')
        details = commit_details(resolve_commits({"range": "HEAD"}, cwd=repo), cwd=repo)
        m = compute(details)
        if not (m["churn_ratio"] >= REWORK_FLOOR and m["verdict"] == "mostly-rework"):
            failures.append(
                f"REWORK case scored churn={m['churn_ratio']} verdict={m['verdict']} "
                f"(expected >= {REWORK_FLOOR} / mostly-rework)"
            )

    # Case B: MOSTLY SHIPPED — 8 distinct files, each added once, no re-touch/revert.
    with tempfile.TemporaryDirectory() as d:
        repo = pathlib.Path(d)
        _git_init_repo(repo)
        for i in range(8):
            _commit(repo, f"feature_{i}.txt", f"new {i}\n", f"feat: add feature {i}")
        details = commit_details(resolve_commits({"range": "HEAD"}, cwd=repo), cwd=repo)
        m = compute(details)
        if not (m["churn_ratio"] < MIXED_FLOOR and m["verdict"] == "mostly-shipped"):
            failures.append(
                f"SHIPPED case scored churn={m['churn_ratio']} verdict={m['verdict']} "
                f"(expected < {MIXED_FLOOR} / mostly-shipped)"
            )

    if failures:
        print("SELFTEST FAIL (kill condition tripped):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SELFTEST OK — mostly-rework and mostly-shipped both score as pre-registered.")
    return 0


# -------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="shipped-vs-reworked signal receipt (deterministic, from git)")
    ap.add_argument("--check", action="store_true", help="audit stored receipts vs git; no write (exit 1 on drift)")
    ap.add_argument("--selftest", action="store_true", help="prove the falsifiable kill condition")
    ap.add_argument("--id", help="receipt id (basename of the emitted JSON)")
    ap.add_argument("--branch", help="emit for commits on <branch> not on --base")
    ap.add_argument("--base", default="main", help="base ref for --branch (default: main)")
    ap.add_argument("--since", help="emit for commits since <date> on --ref")
    ap.add_argument("--until", help="upper date bound for --since")
    ap.add_argument("--ref", default="HEAD", help="ref for --since (default: HEAD)")
    ap.add_argument("--range", dest="rng", help="emit for an explicit rev range A..B")
    args = ap.parse_args()

    if args.check:
        return do_check()
    if args.selftest:
        return do_selftest()

    if not args.id:
        ap.error("--id is required when emitting a receipt")
    if args.branch:
        spec = {"branch": args.branch, "base": args.base}
    elif args.rng:
        spec = {"range": args.rng}
    elif args.since:
        spec = {"since": args.since, "ref": args.ref}
        if args.until:
            spec["until"] = args.until
    else:
        ap.error("give one of --branch, --since, or --range")
    return do_emit(args.id, spec)


if __name__ == "__main__":
    raise SystemExit(main())
