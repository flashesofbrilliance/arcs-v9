#!/usr/bin/env python3
"""cruft_sweep — survey, classify, and safely reclaim stale git worktrees.

Extracted 2026-08-29 from a live 68-worktree sweep. Every rule below is priced tuition:
a naive version of this script gets each one WRONG.

  1. `ahead` count is MEANINGLESS as a staleness signal. A history rewrite (filter-repo)
     inflates every pre-rewrite branch to ahead=700-1047 of pure ghost commits.
  2. Classify by BLOB CONTENT, not path. Renames (e.g. the ADR collision remap 024->058)
     make identical content look like "unique work" under a path-only diff.
  3. A background hook continuously re-dirties _INBOX/*.jsonl and _STATE/snapshot.json,
     so `git merge` (which checks tree cleanliness) loses a race and refuses to start.
     Those files are REGENERABLE - exclude them from every dirty calculation.
  4. `git checkout <ref> -- a b c` aborts the WHOLE checkout if ANY path is absent in
     that ref. Use `git show <ref>:<path>` (immutable blob read) to deliver files.
  5. NEVER `git stash push/pop` - the stash stack is shared across all worktrees.
     `git stash create` is safe BUT does not capture untracked files; to capture
     everything use a WIP commit (`git add -A && git commit`).
  6. Bundle BEFORE removing. `git bundle create <file> <branch>` (positional ref, not
     --branches=glob which refuses "empty bundle"). Restore: git clone <file>.
  7. NEVER trust a command's exit code as proof. Verify with `git ls-files <file>`.
  8. A path on the branch but absent from base is NOT automatically un-landed work: base may
     have DELETED it deliberately (e.g. `sec(warroom): migrate briefs behind admin auth`
     removed public/*.html internal briefs). Restoring those would UNDO a security fix.
     Check `git log <base> --diff-filter=D -- <path>`; if base deleted it, treat as ghost.

Verdicts:
  SAFE    - no uncommitted work AND no branch-unique content blobs -> bundle+prune ok
  REVIEW  - has uncommitted work or unique content -> human decides
  PROTECT - on the protect list -> never touched

Usage:
  cruft_sweep.py survey                     # read-only table (default)
  cruft_sweep.py survey --json              # machine-readable
  cruft_sweep.py inspect <worktree>         # per-file DUP/DIFFERS/UNIQUE for its dirt
  cruft_sweep.py spread --files a,b         # deliver files from main to all worktrees
  cruft_sweep.py prune <wt> [<wt>...]       # capture->bundle->verify->remove (SAFE only
                                            #   unless --capture-dirty is passed)
Flags: --repo PATH --base main --bundles DIR --protect a,b --capture-dirty --dry-run
"""
import argparse, json, os, subprocess, sys

REGENERABLE = ("_INBOX/", "_STATE/snapshot.json", "public/family-roster.json")
CONTENT_RE = ("public/", "runtime/recoil/generated/", "_ARTIFACTS/", "src/",
              "_DECISIONS/ADR-", "_CANON/", "operators/", "prisma/", "scripts/")


def git(repo, *args, check=False):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def is_regenerable(path):
    return any(path.startswith(p) or p in path for p in REGENERABLE)


def real_dirty(wt):
    """Uncommitted files, EXCLUDING regenerable hook state (rule 3)."""
    out = git(wt, "status", "--porcelain")
    return [l[3:] for l in out.splitlines() if l and not is_regenerable(l[3:])]


def deleted_from_base(repo, base, path):
    """True if base deliberately deleted this path (rule 8) - ghost, not lost work."""
    return bool(git(repo, "log", base, "--oneline", "-1", "--diff-filter=D", "--", path))


def content_blobs(repo, ref):
    """{blob_sha: [paths]} for deliverable content only (rule 2: compare by content)."""
    out = git(repo, "ls-tree", "-r", ref)
    blobs = {}
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4 and parts[1] == "blob":
            path = parts[3]
            if any(path.startswith(p) for p in CONTENT_RE):
                blobs.setdefault(parts[2], []).append(path)
    return blobs


def worktrees(repo):
    out, cur = [], {}
    for line in git(repo, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            cur = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            cur["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
            out.append(cur)
        elif line == "" and cur.get("path"):
            cur = {}
    return out


def survey(a):
    base_blobs = set(content_blobs(a.repo, a.base))
    protect = set(x for x in (a.protect or "").split(",") if x)
    rows = []
    for wt in worktrees(a.repo):
        path, br = wt["path"], wt.get("branch", "")
        if os.path.realpath(path) == os.path.realpath(a.repo):
            continue
        name = os.path.basename(path)
        try:
            dirty = real_dirty(path)
            base_paths = set()
            for paths in content_blobs(a.repo, a.base).values():
                base_paths.update(paths)
            uniq_paths = []
            for sha, paths in content_blobs(path, "HEAD").items():
                if sha in base_blobs:
                    continue  # identical content exists on base (rule 2: renames)
                for pth in paths:
                    if pth in base_paths:
                        continue  # base has this path with different content = stale version
                    if deleted_from_base(a.repo, a.base, pth):
                        continue  # rule 8: base deliberately removed it = ghost
                    uniq_paths.append(pth)
            behind = git(path, "rev-list", "--count", f"HEAD..{a.base}")
        except Exception as e:
            rows.append({"name": name, "branch": br, "verdict": "ERROR", "note": str(e)[:60]})
            continue
        if br in protect or name in protect:
            v = "PROTECT"
        elif dirty or uniq_paths:
            v = "REVIEW"
        else:
            v = "SAFE"
        rows.append({"name": name, "branch": br, "verdict": v, "dirty": len(dirty),
                     "unique": len(uniq_paths), "behind": behind,
                     "unique_sample": uniq_paths[:3]})
    return rows


def cmd_survey(a):
    rows = survey(a)
    if a.json:
        print(json.dumps(rows, indent=2)); return
    order = {"SAFE": 0, "REVIEW": 1, "PROTECT": 2, "ERROR": 3}
    rows.sort(key=lambda r: (order.get(r["verdict"], 9), r["name"]))
    print(f"{'WORKTREE':<44}{'VERDICT':<9}{'dirty':<7}{'uniq':<6}{'behind':<8}unique-sample")
    for r in rows:
        s = ",".join(r.get("unique_sample", []))[:56]
        print(f"{r['name']:<44}{r['verdict']:<9}{r.get('dirty',''):<7}"
              f"{r.get('unique',''):<6}{r.get('behind',''):<8}{s}")
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))


def cmd_inspect(a):
    """Per-file keep-vs-archive classification of a worktree's uncommitted work."""
    wt = a.target if os.path.isdir(a.target) else os.path.join(a.repo, ".claude/worktrees", a.target)
    for f in real_dirty(wt):
        f = f.rstrip("/")
        on_base = subprocess.run(["git", "-C", a.repo, "cat-file", "-e", f"{a.base}:{f}"],
                                 capture_output=True).returncode == 0
        if not on_base:
            print(f"  UNIQUE          {f}")
        else:
            local = git(wt, "hash-object", os.path.join(wt, f)) if os.path.isfile(os.path.join(wt, f)) else ""
            base = git(a.repo, "rev-parse", f"{a.base}:{f}")
            print(f"  {'DUP-IDENTICAL' if local == base else 'ON-BASE-DIFFERS':<15} {f}")


def cmd_spread(a):
    """Deliver files from base to every worktree via immutable blob read (rules 4)."""
    files = [f for f in a.files.split(",") if f]
    for wt in worktrees(a.repo):
        path = wt["path"]
        if os.path.realpath(path) == os.path.realpath(a.repo):
            continue
        got = 0
        for f in files:
            blob = subprocess.run(["git", "-C", a.repo, "show", f"{a.base}:{f}"],
                                  capture_output=True)
            if blob.returncode != 0:
                continue
            dest = os.path.join(path, f)
            if a.dry_run:
                got += 1; continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as fh:
                fh.write(blob.stdout)
            git(path, "add", f)
            got += 1
        if got and not a.dry_run:
            subprocess.run(["git", "-C", path, "commit", "-q", "-o", *files,
                            "-m", "chore(doctrine): spread shared files from base [NCI:SKIP]"],
                           capture_output=True)
        # rule 7: verify, never trust exit codes
        ok = sum(1 for f in files if git(path, "ls-files", f))
        print(f"{os.path.basename(path):<44} delivered={got} verified={ok}/{len(files)}")


def cmd_prune(a):
    os.makedirs(a.bundles, exist_ok=True)
    manifest = os.path.join(a.bundles, "MANIFEST.tsv")
    for target in a.targets:
        wt = target if os.path.isdir(target) else os.path.join(a.repo, ".claude/worktrees", target)
        name = os.path.basename(wt.rstrip("/"))
        if not os.path.isdir(wt):
            print(f"SKIP-MISSING {name}"); continue
        br = git(wt, "rev-parse", "--abbrev-ref", "HEAD")
        dirty = real_dirty(wt)
        if dirty and not a.capture_dirty:
            print(f"SKIP-DIRTY   {name} ({len(dirty)} files; pass --capture-dirty to WIP-commit)")
            continue
        if a.dry_run:
            print(f"DRY-RUN      {name} [{br}] dirty={len(dirty)}"); continue
        if dirty:  # rule 5: WIP commit captures untracked too, unlike stash create
            git(wt, "add", "-A")
            subprocess.run(["git", "-C", wt, "commit", "-q", "-m",
                            "wip(cruft-sweep): capture uncommitted work before archival [NCI:SKIP]"],
                           capture_output=True)
        bundle = os.path.join(a.bundles, f"{name}.bundle")
        subprocess.run(["git", "-C", a.repo, "bundle", "create", bundle, br], capture_output=True)
        verify = subprocess.run(["git", "-C", a.repo, "bundle", "verify", bundle], capture_output=True)
        if verify.returncode != 0:  # rule 6+7
            print(f"SKIP-NOBAK   {name} (bundle failed verify - NOT removed)"); continue
        rm = subprocess.run(["git", "-C", a.repo, "worktree", "remove", "--force", wt],
                            capture_output=True)
        if rm.returncode == 0:
            tip = git(a.repo, "rev-parse", "--short", br)
            with open(manifest, "a") as fh:
                fh.write(f"{name}\t{br}\t{tip}\t{name}.bundle\n")
            print(f"PRUNED       {name} [{br} @ {tip}] -> {name}.bundle")
        else:
            print(f"SKIP-REMFAIL {name} (bundle kept, worktree intact)")
    subprocess.run(["git", "-C", a.repo, "worktree", "prune"], capture_output=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["survey", "inspect", "spread", "prune"], nargs="?", default="survey")
    p.add_argument("targets", nargs="*")
    p.add_argument("--repo", default=os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    p.add_argument("--base", default="main")
    p.add_argument("--bundles", default=os.path.expanduser("~/arcs-worktree-bundles"))
    p.add_argument("--protect", default="")
    p.add_argument("--files", default="")
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--capture-dirty", action="store_true")
    a = p.parse_args()
    # repo must be the MAIN checkout for worktree listing
    a.repo = git(a.repo, "rev-parse", "--path-format=absolute", "--git-common-dir").replace("/.git", "") or a.repo
    if a.cmd == "inspect":
        a.target = a.targets[0] if a.targets else sys.exit("inspect needs a worktree")
        cmd_inspect(a)
    elif a.cmd == "spread":
        if not a.files: sys.exit("spread needs --files a,b,c")
        cmd_spread(a)
    elif a.cmd == "prune":
        if not a.targets: sys.exit("prune needs worktree name(s)")
        cmd_prune(a)
    else:
        cmd_survey(a)


if __name__ == "__main__":
    main()
