#!/usr/bin/env python3
"""
Excavate worktree artifacts without treating branches as version control.

For each worktree, diff against main and classify:
- SESSION-only: only project lore files changed (CLAUDE.md, MEMORY.md, AGENTS.md, WORLD.md, SKILL.md, README.md, JOB_REQ.md, PRODUCT.md, SESSION-HANDOFF-*)
- ARTIFACT: real code, ADRs, specs, scripts, or new files
- MIXED: both
- EMPTY: no diff (branch == main or no changes)

Also extract a flat list of all non-session files touched across all worktrees.
"""

import subprocess, re, json
from pathlib import Path
from collections import defaultdict

REPO = Path("/Users/zharris/arcs-v9")

def git(*args):
    r = subprocess.run(
        ["git", "-C", str(REPO)] + list(args),
        capture_output=True, text=True, timeout=10
    )
    return r.stdout.strip(), r.returncode

def main_commit():
    """Derive main branch HEAD dynamically — no hardcoded commit."""
    out, rc = git("rev-parse", "refs/heads/main")
    if rc != 0:
        out, rc = git("symbolic-ref", "HEAD")
        if rc == 0:
            ref = out.strip()
            out, rc = git("rev-parse", ref)
    if rc != 0 or not out:
        out, rc = git("rev-parse", "HEAD")
    return out.split()[0] if out else "unknown"

MAIN = main_commit()

SESSION_FILES = {
    'CLAUDE.md', 'MEMORY.md', 'AGENTS.md', 'WORLD.md', 'SKILL.md',
    'README.md', 'JOB_REQ.md', 'PRODUCT.md',
    'SESSION-HANDOFF-2026-05-26.md', 'DESIGN.md',
    'next-env.d.ts', 'tsconfig.json', 'tsconfig.tsbuildinfo',
    'LICENSE', 'vercel.json', 'package.json', 'package-lock.json',
    'postcss.config.mjs', 'eslint.config.mjs', 'playwright.config.ts',
    'prisma.config.ts', '.DS_Store',
}

def git(*args):
    r = subprocess.run(
        ["git", "-C", str(REPO)] + list(args),
        capture_output=True, text=True, timeout=10
    )
    return r.stdout.strip(), r.returncode

# List worktrees
out, _ = git("worktree", "list")
lines = [l for l in out.split("\n") if l.strip()]
worktrees = []
for line in lines:
    parts = line.split()
    if len(parts) < 3:
        continue
    path = parts[0]
    commit = parts[1]
    bm = re.search(r'\[([^\]]+)\]', line)
    branch = bm.group(1) if bm else "unknown"
    worktrees.append({"path": path, "commit": commit, "branch": branch})

print(f"Excavating {len(worktrees)} worktrees against main ({MAIN})\n")

# Session lore files that get touched in nearly every session
# (these show up in almost every diff because each session updates them)
#
# We want to flag worktrees where the ONLY changes are to these files
# — those are session checkpoint artifacts, not real work products.

# Classify each worktree
results = []
artifact_touched = defaultdict(list)  # filename -> list of worktree branches

for wt in worktrees:
    commit = wt["commit"]
    branch = wt["branch"]
    path = wt["path"]

    # Diff against main
    diff_out, rc = git("diff", "--name-only", f"{MAIN}...{commit}")
    diff_out, rc = git("diff", "--name-only", f"{MAIN}...{commit}")
    if rc != 0 or not diff_out:
        diff_out, rc = git("diff", "--name-only", f"{commit}...{MAIN}")
    
    changed_files = [f.strip() for f in diff_out.split("\n") if f.strip()] if diff_out else []
    
    # Separate session files from real artifacts
    session_changed = [f for f in changed_files if f in SESSION_FILES or any(f.endswith(s) for s in ['.md']) and f in SESSION_FILES]
    session_only = [f for f in changed_files if f in SESSION_FILES]
    real_changed = [f for f in changed_files if f not in SESSION_FILES]
    
    # Re-check: session_only is too strict — let me use changed_files vs SESSION_FILES
    session_touched = [f for f in changed_files if f in SESSION_FILES]
    non_session = [f for f in changed_files if f not in SESSION_FILES]
    
    if not changed_files:
        classification = "EMPTY"
    elif not non_session:
        classification = "SESSION-ONLY"
    elif not session_touched:
        classification = "ARTIFACT"
    else:
        classification = "MIXED"
    
    # Extract subject
    subject, _ = git("log", "--format=%s", "-1", commit)
    subject = subject.split("\n")[0] if subject else "(no subject)"
    
    # New files (added, not modified) — show for artifact-rich worktrees
    new_files_out, _ = git("diff", "--name-only", "--diff-filter=A", f"{MAIN}...{commit}")
    if not new_files_out:
        new_files_out, _ = git("diff", "--name-only", "--diff-filter=A", f"{commit}...{MAIN}")
    new_files = [f.strip() for f in new_files_out.split("\n") if f.strip()] if new_files_out else []
    
    # Only show non-session new files
    non_session_new = [f for f in new_files if f not in SESSION_FILES]
    
    # File stat
    stat_out, _ = git("diff", "--stat", f"{MAIN}...{commit}")
    if not stat_out:
        stat_out, _ = git("diff", "--stat", f"{commit}...{MAIN}")
    
    results.append({
        "branch": branch,
        "commit": commit,
        "subject": subject,
        "classification": classification,
        "changed_files_count": len(changed_files),
        "session_files": session_touched,
        "non_session_files": non_session,
        "new_non_session_files": non_session_new,
        "diff_stat": stat_out.split("\n")[-1] if stat_out else "",
    })
    
    # Track artifact files
    for f in non_session:
        artifact_touched[f].append(branch)

# Sort: ARTIFACT first, then MIXED, then SESSION-ONLY, then EMPTY
order = {"ARTIFACT": 0, "MIXED": 1, "SESSION-ONLY": 2, "EMPTY": 3}
results.sort(key=lambda r: (order.get(r["classification"], 9), r["branch"]))

# Print
print(f"{'CLASS':16s} {'BRANCH':50s} FILES  DETAIL")
print("-" * 120)

for r in results:
    cls = r["classification"]
    branch = r["branch"][:48]
    n = r["changed_files_count"]
    
    detail = ""
    if cls == "ARTIFACT":
        detail = f"non-session: {', '.join(r['non_session_files'][:5])}{'...' if len(r['non_session_files']) > 5 else ''}"
        if r["new_non_session_files"]:
            detail += f"  NEW: {', '.join(r['new_non_session_files'][:3])}{'...' if len(r['new_non_session_files']) > 3 else ''}"
    elif cls == "MIXED":
        detail = f"session: {len(r['session_files'])}f, artifact: {len(r['non_session_files'])}f"
        if r["non_session_files"]:
            detail += f"  [{', '.join(r['non_session_files'][:4])}{'...' if len(r['non_session_files']) > 4 else ''}]"
    elif cls == "SESSION-ONLY":
        detail = f"session lore only ({len(r['session_files'])} files)"
    else:
        detail = "(no diff from main)"
    
    print(f"{cls:16s} {branch:50s} {n:5d}  {detail}")

# Summary stats
art_count = sum(1 for r in results if r["classification"] == "ARTIFACT")
mixed_count = sum(1 for r in results if r["classification"] == "MIXED")
session_count = sum(1 for r in results if r["classification"] == "SESSION-ONLY")
empty_count = sum(1 for r in results if r["classification"] == "EMPTY")

print(f"\n=== CLASSIFICATION SUMMARY ===")
print(f"ARTIFACT-only:  {art_count} worktrees (real code/ADR/spec work, no session lore)")
print(f"MIXED:          {mixed_count} worktrees (both session lore + artifacts)")
print(f"SESSION-ONLY:   {session_count} worktrees (session checkpoint, no real artifacts)")
print(f"EMPTY:          {empty_count} worktrees (no diff from main)")

# List all unique non-session files touched across all worktrees
all_artifact_files = sorted(set(f for r in results for f in r["non_session_files"]))
print(f"\n=== UNIQUE ARTIFACT FILES TOUCHED ({len(all_artifact_files)} total) ===")
for f in all_artifact_files:
    bt = artifact_touched[f]
    print(f"  {f}  ← {len(bt)} worktree{'s' if len(bt)>1 else ''}")

# Group artifact files by directory
by_dir = defaultdict(list)
for f in all_artifact_files:
    d = str(Path(f).parent)
    if d == '.':
        d = '(root)'
    by_dir[d].append(f)

print(f"\n=== ARTIFACT FILES BY DIRECTORY ===")
for d in sorted(by_dir):
    files = by_dir[d]
    print(f"\n{d}/ ({len(files)} files):")
    for f in sorted(files):
        print(f"  {f}")

# Write full JSON
result = {
    "main_commit": MAIN,
    "count": len(results),
    "summary": {
        "artifact_only": art_count,
        "mixed": mixed_count,
        "session_only": session_count,
        "empty": empty_count,
    },
    "unique_artifact_files": all_artifact_files,
    "worktrees": results,
}
out_path = REPO / "_STATE" / "worktree-excavation.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(result, indent=2))
print(f"\nFull excavation → {out_path}")
