#!/usr/bin/env python3
"""Catalog all 61 git worktrees in arcs-v9: branch, commit, subject, diff vs main, artifact files."""

import subprocess, re, json
from pathlib import Path

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

# 1. List worktrees
out, rc = git("worktree", "list")
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

print(f"Found {len(worktrees)} worktrees\n")

# 2. Per-worktree detail
catalog = []
for wt in worktrees:
    commit = wt["commit"]
    branch = wt["branch"]
    path = wt["path"]

    # commit subject
    subject, _ = git("log", "--format=%s", "-1", commit)
    subject = subject.split("\n")[0] if subject else "(no subject)"

    # commit date
    date, _ = git("log", "--format=%ai", "-1", commit)
    date = date.split("\n")[0] if date else ""

    # diff stat vs main (try both directions)
    MAIN = main_commit()
    diff_out, _ = git("diff", "--stat", f"{MAIN}...{commit}")
    if not diff_out:
        diff_out, _ = git("diff", "--stat", f"{commit}...{MAIN}")
    
    files_changed = insertions = deletions = 0
    if diff_out:
        for line in diff_out.split("\n"):
            line = line.strip()
            if "files changed" in line:
                m = re.search(r'(\d+) files? changed', line)
                if m: files_changed = int(m.group(1))
                m2 = re.search(r'(\d+) insertions?\(\+\)', line)
                if m2: insertions = int(m2.group(1))
                m3 = re.search(r'(\d+) deletions?\(-\)', line)
                if m3: deletions = int(m3.group(1))

    # top-level artifact files (skip node_modules, .git, common config)
    skip = {
        'node_modules', '.git', '.next', '.vercel', '.github', 'node_modules',
        'package-lock.json', 'tsconfig.tsbuildinfo', '.DS_Store',
        'package.json', 'next.config.ts', 'tsconfig.json',
        'postcss.config.mjs', 'eslint.config.mjs', 'playwright.config.ts',
        'prisma.config.ts',
    }
    wt_path = Path(path)
    top_files = []
    if wt_path.exists():
        try:
            for f in wt_path.iterdir():
                if f.is_file() and f.name not in skip and not f.name.startswith('.'):
                    top_files.append(f.name)
        except (PermissionError, OSError):
            pass

    catalog.append({
        "path": path,
        "branch": branch,
        "commit": commit,
        "subject": subject,
        "date": date,
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "top_files": top_files[:15],
    })

# Sort by branch
catalog.sort(key=lambda x: x["branch"])

# 3. Print
print(f"=== CATALOG: {len(catalog)} worktrees ===\n")
for i, c in enumerate(catalog, 1):
    path_short = c["path"].replace("/Users/zharris/arcs-v9/", "")
    print(f"{i:3d}. [{c['branch']}]")
    print(f"    commit:  {c['commit']}")
    print(f"    date:    {c['date']}")
    print(f"    subject: {c['subject']}")
    print(f"    diff:    {c['files_changed']}f  +{c['insertions']}/-{c['deletions']}")
    if c["top_files"]:
        print(f"    files:   {', '.join(c['top_files'])}")
    print()

# 4. Group by prefix
print("\n=== GROUPED BY PREFIX ===\n")
groups = {}
for c in catalog:
    parts = c["branch"].split("/")
    prefix = parts[0] if len(parts) == 2 else "other"
    groups.setdefault(prefix, []).append(c)

for prefix, items in sorted(groups.items()):
    print(f"\n{prefix} ({len(items)} worktrees):")
    for item in items:
        print(f"  • {item['branch']}")
        print(f"    {item['subject']}  [{item['files_changed']}f +{item['insertions']}/-{item['deletions']}]")

# 5. Stats
total_files = sum(c["files_changed"] for c in catalog)
total_ins = sum(c["insertions"] for c in catalog)
total_del = sum(c["deletions"] for c in catalog)
print(f"\n=== TOTALS ===")
print(f"Worktrees:        {len(catalog)}")
print(f"Total files touched: {total_files}")
print(f"Total insertions:    {total_ins}")
print(f"Total deletions:     {total_del}")

# 6. Write JSON
MAIN = main_commit()
result = {
    "main_commit": MAIN,
    "count": len(catalog),
    "totals": {
        "files_changed": total_files,
        "insertions": total_ins,
        "deletions": total_del,
    },
    "worktrees": catalog,
}
out_path = REPO / "_STATE" / "worktree-catalog.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(result, indent=2))
print(f"\nFull catalog → {out_path}")
