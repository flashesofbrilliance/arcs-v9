#!/usr/bin/env python3
"""branch_hygiene_check — surface cross-harness worktree/branch hazards.

The ADR-number collisions trace partly to many concurrent worktrees (Claude Code + Hermes)
off one monorepo. This does NOT touch git — it reports two things:

  HAZARD  two+ worktrees checked out on the SAME branch → concurrent commits race, one
          session's work can land on another's branch. This is the real danger.
  SMELL   a worktree whose directory name doesn't match its branch name → a branch was
          reused/borrowed across tasks (how the wrong-branch collisions start). Advisory only.

Read-only, stdlib, exit 0 (a hazard is a report, not a failure). Run before starting work,
or from a preflight hook.
"""
import subprocess, os, re, sys
from collections import defaultdict


def worktrees():
    out = subprocess.run(["git", "worktree", "list", "--porcelain"],
                         capture_output=True, text=True).stdout
    wts, cur = [], {}
    for line in out.splitlines():
        if line.startswith("worktree "):
            if cur:
                wts.append(cur)
            cur = {"path": line[len("worktree "):]}
        elif line.startswith("branch "):
            cur["branch"] = line[len("branch "):].replace("refs/heads/", "")
        elif line.strip() == "" and cur:
            wts.append(cur); cur = {}
    if cur:
        wts.append(cur)
    return wts


def base_slug(s):
    return re.sub(r"[^a-z0-9]+", "", os.path.basename(s).lower())


def main():
    wts = worktrees()
    by_branch = defaultdict(list)
    for w in wts:
        if w.get("branch"):
            by_branch[w["branch"]].append(w["path"])

    hazards = {b: ps for b, ps in by_branch.items() if len(ps) > 1}
    smells = []
    for w in wts:
        b = w.get("branch")
        if not b:
            continue
        wt, br = base_slug(w["path"]), base_slug(b)
        # main checkout + short-hash-suffixed names differ legitimately; flag only when
        # neither name is a prefix of the other (a genuine borrow, not a suffix trim).
        if wt and br and wt not in br and br not in wt and not br.endswith(wt[-8:]):
            smells.append((w["path"], b))

    print(f"branch-hygiene: {len(wts)} worktrees · {len(hazards)} same-branch HAZARD(s) · {len(smells)} name-mismatch SMELL(s)")
    for b, ps in hazards.items():
        print(f"  ✖ HAZARD  branch '{b}' checked out in {len(ps)} worktrees:")
        for p in ps:
            print(f"            {p}")
    for p, b in smells[:20]:
        print(f"  ⚠ smell   {os.path.basename(p)}  →  {b}")
    if len(smells) > 20:
        print(f"  … {len(smells) - 20} more smells")
    if not hazards:
        print("branch-hygiene: no two worktrees share a branch — the collision-critical invariant holds.")


if __name__ == "__main__":
    main()
