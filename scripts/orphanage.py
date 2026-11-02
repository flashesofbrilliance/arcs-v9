#!/usr/bin/env python3
"""orphanage.py: find tools that live only on unmerged branches, and give each one a fate.

WHY: dreaming pass 3 (2026-11-02) found 8 memories telling sessions to run tools that never
reached main; a sweep of 539 unmerged branches then found 49 such tool files, 12 of them
cited by memory or docs. A memory that points at a stranded tool sends every session that
trusts it to a file that is not there.

An orphan is a file under a tool path (scripts/, .claude/skills/, .claude/agents/, operators/,
src/lib/) that an unmerged remote branch adds and that main never had (not now, not deleted
earlier). Orphans that a memory or doc cites by file name come first.

The register, _QUEUE/orphanage.jsonl, holds one row per orphan:
  path, branch, last_commit, last_date, cited_by[], fate, recommended, note, ruled_at
Fates: INTAKE (found, awaiting Zach) | ADOPT (land it on main via a PR) | FOSTER (keep the
branch; note says who and when to revisit) | RETIRE (bundle the branch to cold storage
first, then mark the citing memories retired). Nothing here deletes a branch.

USAGE
  python3 scripts/orphanage.py              # scan, print orphans, write _STATE/orphanage-scan.json
  python3 scripts/orphanage.py --intake     # add unregistered CITED orphans to the register as INTAKE
  python3 scripts/orphanage.py --check      # exit 1 if a cited orphan is not in the register
EXIT  0 ok · 1 --check found an unregistered cited orphan
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "_QUEUE" / "orphanage.jsonl"
SCAN_OUT = ROOT / "_STATE" / "orphanage-scan.json"
TOOL_PATHS = ["scripts", ".claude/skills", ".claude/agents", "operators", "src/lib"]
MEMORY = Path.home() / ".claude" / "projects" / "-Users-zharris-arcs-v9" / "memory"
CITE_ROOTS = [MEMORY, ROOT / "_PATTERNS", ROOT / "_DECISIONS", ROOT / ".claude" / "rules",
              ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "WORLD.md"]
# a name this generic matches unrelated text, so it cannot count as a cite
GENERIC = {"SKILL.md", "README.md", "index.ts", "index.js", "__init__.py", "package.json",
           "requirements.txt", "VERSION", "utils.py", "types.ts"}
FATES = {"INTAKE", "ADOPT", "FOSTER", "RETIRE"}


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout


def scan():
    on_main = set(git("ls-tree", "-r", "--name-only", "origin/main").split("\n"))
    ever_deleted = set(git("log", "origin/main", "--diff-filter=D", "--name-only", "--format=").split("\n"))
    main_stems = {}
    for p in on_main:
        main_stems.setdefault((p.split("/")[0], Path(p).stem), []).append(p)
    branches = [b.strip() for b in git("branch", "-r", "--no-merged", "origin/main").split("\n")
                if b.strip() and "HEAD" not in b]
    orphans = {}
    for b in branches:
        added = git("diff", "--name-only", "--diff-filter=A", f"origin/main...{b}", "--", *TOOL_PATHS)
        for p in filter(None, added.split("\n")):
            if p in on_main or p in ever_deleted or p in orphans:
                continue
            moved = (main_stems.get((p.split("/")[0], Path(p).stem), [])
                     + main_stems.get(("_ARCHIVE", Path(p).stem), []))
            if moved and Path(p).name not in GENERIC:
                continue  # same name on main elsewhere, or kept in _ARCHIVE: rehomed, not orphaned
            last = git("log", "-1", "--format=%h %ad", "--date=short", b, "--", p).split()
            orphans[p] = {"path": p, "branch": b.removeprefix("origin/"),
                          "last_commit": last[0] if last else "", "last_date": last[1] if len(last) > 1 else ""}
    # cites: the file name (or the skill folder name) appears in memory or docs
    texts = []
    for r in CITE_ROOTS:
        files = [r] if r.is_file() else (sorted(r.rglob("*.md")) if r.is_dir() else [])
        for f in files:
            try:
                texts.append((f, f.read_text(errors="replace")))
            except OSError:
                pass
    for o in orphans.values():
        name = Path(o["path"]).name
        if name in GENERIC and o["path"].startswith(".claude/skills/"):
            name = o["path"].split("/")[2]  # a skill is cited by its folder name
        if name in GENERIC or len(name) < 6:
            o["cited_by"] = []
            continue
        # whole-name match: "models.ts" must not match inside "claude-models.ts"
        rx = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")
        o["cited_by"] = sorted({(("memory/" + f.name) if MEMORY in f.parents else str(f.relative_to(ROOT)))
                                for f, t in texts if rx.search(t)})
    return sorted(orphans.values(), key=lambda o: (-len(o["cited_by"]), o["path"]))


def read_register():
    if not REGISTER.exists():
        return {}
    rows = {}
    for line in REGISTER.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("fate") not in FATES:
                sys.exit(f"orphanage: bad fate {r.get('fate')!r} for {r.get('path')}")
            rows[r["path"]] = r
    return rows


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--intake", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    orphans = scan()
    reg = read_register()
    cited = [o for o in orphans if o["cited_by"]]
    if a.check:
        missing = [o for o in cited if o["path"] not in reg]
        pending = [r for r in reg.values() if r["fate"] == "INTAKE"]
        for o in missing:
            print(f"✖ unregistered cited orphan: {o['path']} (branch {o['branch']}), cited by {', '.join(o['cited_by'][:3])}")
        print(f"orphanage --check: {len(orphans)} orphans, {len(cited)} cited, {len(missing)} unregistered, "
              f"{len(pending)} awaiting a fate")
        return 1 if missing else 0
    if a.intake:
        new = [o for o in cited if o["path"] not in reg]
        with REGISTER.open("a") as fh:
            for o in new:
                fh.write(json.dumps({**o, "fate": "INTAKE", "recommended": "", "note": "", "ruled_at": ""}) + "\n")
        print(f"orphanage --intake: {len(new)} cited orphan(s) added to {REGISTER.relative_to(ROOT)}")
        return 0
    SCAN_OUT.parent.mkdir(parents=True, exist_ok=True)
    SCAN_OUT.write_text(json.dumps(orphans, indent=1))
    for o in orphans:
        mark = reg.get(o["path"], {}).get("fate", "-")
        print(f"{len(o['cited_by']):2} cites  {mark:7} {o['last_date']}  {o['path']}  ({o['branch']})")
    print(f"orphanage: {len(orphans)} orphans on unmerged branches, {len(cited)} cited -> {SCAN_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
