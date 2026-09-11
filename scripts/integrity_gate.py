#!/usr/bin/env python3
"""integrity_gate.py — the Metabolic Router's GATE organ (ADR-075, Reading Room Phase 0).

Verifies that every thing a record CITES actually exists on `origin/main` — not in the
session's RAM, not on an unmerged branch, not in a description of work that never landed.

    python3 scripts/integrity_gate.py <file> [<file> ...]      # gate specific files
    python3 scripts/integrity_gate.py --staged                 # gate what's in the git index (pre-commit)
    python3 scripts/integrity_gate.py --json <file>            # machine-readable receipt
    python3 scripts/integrity_gate.py --strict <file>          # WARN also fails
    python3 scripts/integrity_gate.py --ref main <file>        # check against another ref

Three cite classes, each a pure mechanical check (zero judgment, per _SPECS/metabolic-router-v1.md §3):

  ADR-0NN        -> a matching _DECISIONS/ADR-NNN-*.md exists on <ref>      (missing = FAIL)
                    and a row with that id exists in _DECISIONS/index.json  (missing = WARN, index drift)
  commit SHA     -> `git merge-base --is-ancestor <sha> <ref>`              (exists but unmerged = FAIL,
                    object unknown to this clone = WARN, likely foreign or a hex-looking word)
  repo path      -> path present in `git ls-tree -r <ref>`                  (absent = FAIL "vapor",
                    gitignored = WARN, since it can never be on main by design)

Exit status: 1 if any FAIL (or any WARN under --strict), else 0. A record that cites vapor is
meant to be routed with a DRIFTED-AT-BIRTH tag — never silently.

Stdlib only. Batched git: one ls-tree, one cat-file --batch-check, one check-ignore.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           check=False).stdout.strip() or ".").resolve()

# ---------------------------------------------------------------- patterns
ADR_RE = re.compile(r"\bADR-0*(\d{1,3})\b")
# 7-40 hex chars, not glued to other word chars / a path. Must contain BOTH a digit and a letter:
# pure digits are numbers, pure a-f letters are words ("defaced", "decade").
SHA_RE = re.compile(r"(?<![0-9A-Za-z_/.-])([0-9a-f]{7,40})(?![0-9A-Za-z_/-])")
# Top-level dirs that a cite could legitimately point into. Bare filenames are matched separately.
PATH_ROOTS = (
    "scripts", "src", "operators", "runtime", "public", "prisma", "tests", "docs", "open-source",
    "_SPECS", "_DECISIONS", "_STATE", "_CANON", "_MEMORY", "_ARTIFACTS", "_QUEUE", "_SEEDS",
    "_PATTERNS", "_ARCHIVE", "_INBOX", ".claude", ".github",
)
PATH_RE = re.compile(r"(?<![\w/.-])((?:%s)/[\w./\[\]@+-]+)" % "|".join(re.escape(r) for r in PATH_ROOTS))
# bare script names: foo_bar.py / foo.sh / foo.ts — only when not already part of a path
BARE_RE = re.compile(r"(?<![\w/.-])([A-Za-z][\w-]*\.(?:py|sh|ts|tsx|mjs))(?![\w/-])")
TRAIL = ".,;:)]}'\"`>"
ROOT_FILES = {"CLAUDE.md", "AGENTS.md", "WORLD.md", "MEMORY.md", "SKILL.md"}


def sh(*args: str, stdin: str | None = None) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, input=stdin,
                          check=False).stdout


# ---------------------------------------------------------------- extraction
def extract(text: str) -> tuple[set[int], set[str], set[str], set[str]]:
    adrs = {int(n) for n in ADR_RE.findall(text)}
    shas = {s for s in SHA_RE.findall(text) if re.search(r"\d", s) and re.search(r"[a-f]", s)}
    paths: set[str] = set()
    for p in PATH_RE.findall(text):
        p = p.rstrip(TRAIL)
        # trailing '/' means a directory cite; keep for prefix check
        if "*" in p or "{" in p or "<" in p or "[" in p and "]" not in p:
            continue
        paths.add(p)
    bare = {b for b in BARE_RE.findall(text)}
    return adrs, shas, paths, bare


# ---------------------------------------------------------------- reference state (batched)
class RefState:
    def __init__(self, ref: str, staged: set[str]):
        self.ref = ref
        self.staged = staged
        if not sh("rev-parse", "--verify", "-q", ref).strip():
            sys.exit(f"integrity_gate: ref '{ref}' not found — run `git fetch origin main` first")
        self.tree = set(sh("ls-tree", "-r", "--name-only", ref).split("\n")) - {""}
        self.dirs = {os.path.dirname(p) for p in self.tree}
        self.basenames: dict[str, list[str]] = {}
        for p in self.tree:
            self.basenames.setdefault(os.path.basename(p), []).append(p)
        # ADRs: number -> file, from the ref's tree (+ anything staged, for self-cites)
        self.adr_files: dict[int, str] = {}
        for p in list(self.tree) + list(staged):
            m = re.match(r"_DECISIONS/ADR-0*(\d+)-.*\.md$", p)
            if m:
                self.adr_files.setdefault(int(m.group(1)), p)
        idx_raw = sh("show", f"{ref}:_DECISIONS/index.json")
        self.adr_index: set[int] = set()
        try:
            for row in json.loads(idx_raw or "[]"):
                m = ADR_RE.search(str(row.get("id", "")))
                if m:
                    self.adr_index.add(int(m.group(1)))
        except json.JSONDecodeError:
            pass

    def check_shas(self, shas: set[str]) -> dict[str, str]:
        if not shas:
            return {}
        out = sh("cat-file", "--batch-check", stdin="\n".join(sorted(shas)) + "\n")
        kinds = {}
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                kinds[parts[0]] = parts[1]
        verdict = {}
        for s in shas:
            # batch-check echoes the abbreviated input for missing objects, full sha for found ones
            full = next((k for k in kinds if k.startswith(s) and kinds[k] != "missing"), None)
            if full is None or kinds.get(s) == "missing":
                verdict[s] = "UNKNOWN"
            elif kinds[full] != "commit":
                verdict[s] = "OK"  # a blob/tree hash — exists, nothing to merge-check
            else:
                rc = subprocess.run(["git", "merge-base", "--is-ancestor", full, self.ref], cwd=REPO,
                                    capture_output=True).returncode
                verdict[s] = "OK" if rc == 0 else "UNMERGED"
        return verdict

    def check_ignored(self, paths: set[str]) -> set[str]:
        if not paths:
            return set()
        out = sh("check-ignore", "--stdin", stdin="\n".join(sorted(paths)) + "\n")
        return set(out.split("\n")) - {""}

    def has_path(self, p: str) -> bool:
        q = p.rstrip("/")
        return q in self.tree or q in self.dirs or q in self.staged


# ---------------------------------------------------------------- gate one file
def gate(path: str, state: RefState, self_path: str | None = None) -> dict:
    text = Path(path).read_text(errors="replace")
    adrs, shas, paths, bare = extract(text)
    findings: list[dict] = []

    def add(kind: str, cite: str, level: str, note: str) -> None:
        findings.append({"kind": kind, "cite": cite, "level": level, "note": note})

    for n in sorted(adrs):
        cite = f"ADR-{n:03d}"
        if n not in state.adr_files:
            add("adr", cite, "FAIL", f"no _DECISIONS/ADR-{n:03d}-*.md on {state.ref} (numbering gap or never merged)")
        elif n not in state.adr_index:
            add("adr", cite, "WARN", "file exists but no row in _DECISIONS/index.json (index drift)")
        else:
            add("adr", cite, "OK", state.adr_files[n])

    for s, v in sorted(state.check_shas(shas).items()):
        if v == "OK":
            add("commit", s, "OK", f"ancestor of {state.ref}")
        elif v == "UNMERGED":
            add("commit", s, "FAIL", f"exists locally but is NOT an ancestor of {state.ref} (unmerged)")
        else:
            add("commit", s, "WARN", "no such object in this clone (foreign sha, or a hex-looking word)")

    ignored = state.check_ignored(paths)
    for p in sorted(paths):
        if p == self_path:
            add("path", p, "OK", "self")
        elif p.rstrip("/") in state.staged:
            add("path", p, "OK", "staged in this commit")
        elif state.has_path(p):
            add("path", p, "OK", "on " + state.ref)
        elif p in ignored:
            add("path", p, "WARN", "gitignored — local-only by design, cannot be on main")
        else:
            add("path", p, "FAIL", f"vapor: not on {state.ref}")

    for b in sorted(bare):
        hits = state.basenames.get(b)
        if hits or b in ROOT_FILES:
            add("script", b, "OK", ", ".join(sorted(hits)[:3]) if hits else "root")
        else:
            add("script", b, "FAIL", f"vapor: no file named {b} anywhere on {state.ref}")

    levels = [f["level"] for f in findings]
    verdict = "FAIL" if "FAIL" in levels else "WARN" if "WARN" in levels else "OK"
    return {"file": path, "verdict": verdict, "cites": len(findings), "findings": findings}


# ---------------------------------------------------------------- cli
GATE_GLOBS = ("_DECISIONS/", "_MEMORY/", "_SPECS/", "_CANON/", "_STATE/", "_SEEDS/", "_PATTERNS/")


def staged_files() -> list[str]:
    out = sh("diff", "--cached", "--name-only", "--diff-filter=AM")
    files = [f for f in out.split("\n") if f]
    return [f for f in files
            if (f.startswith(GATE_GLOBS) or f in ROOT_FILES) and f.endswith((".md", ".json", ".jsonl"))]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="files to gate (repo-relative or absolute)")
    ap.add_argument("--staged", action="store_true", help="gate the staged .md/.json records (pre-commit mode)")
    ap.add_argument("--ref", default="origin/main", help="git ref that counts as 'real' (default origin/main)")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failing")
    ap.add_argument("--json", action="store_true", help="emit a JSON receipt instead of the table")
    ap.add_argument("-q", "--quiet", action="store_true", help="print only non-OK findings")
    a = ap.parse_args(argv)

    all_staged = set(f for f in sh("diff", "--cached", "--name-only").split("\n") if f)
    files = list(a.files)
    if a.staged:
        files += staged_files()
    if not files:
        print("integrity_gate: nothing to gate", file=sys.stderr)
        return 0

    state = RefState(a.ref, all_staged if a.staged else set())
    reports = []
    for f in files:
        p = Path(f)
        if not p.is_absolute():
            p = REPO / f
        if not p.exists():
            print(f"integrity_gate: skip {f} (no such file)", file=sys.stderr)
            continue
        rel = os.path.relpath(p, REPO)
        reports.append(gate(str(p), state, self_path=rel))

    worst = "OK"
    for r in reports:
        r["file"] = os.path.relpath(r["file"], REPO)
        if r["verdict"] == "FAIL" or (a.strict and r["verdict"] == "WARN"):
            worst = "FAIL"
        elif r["verdict"] == "WARN" and worst == "OK":
            worst = "WARN"

    if a.json:
        print(json.dumps({"ref": a.ref, "verdict": worst, "reports": reports}, indent=2))
        return 1 if worst == "FAIL" else 0

    icon = {"OK": "✓", "WARN": "⚠", "FAIL": "✖"}
    for r in reports:
        shown = [f for f in r["findings"] if not (a.quiet and f["level"] == "OK")]
        print(f"{icon[r['verdict']]} {r['file']}  — {r['cites']} cites, verdict {r['verdict']}")
        for f in shown:
            print(f"    {icon[f['level']]} {f['kind']:<7} {f['cite']:<48} {f['note']}")
    tag = "  → DRIFTED-AT-BIRTH: this record cites things that are not on " + a.ref if worst == "FAIL" else ""
    print(f"integrity_gate: {len(reports)} file(s) against {a.ref} → {worst}{tag}")
    return 1 if worst == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
