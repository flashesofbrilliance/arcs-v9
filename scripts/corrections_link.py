#!/usr/bin/env python3
"""corrections_link.py — git-ground the believability ledger's "unlinked corrections".

The believability ledger (scripts/believability_ledger.py) only scores a REEL-IN when
a correction sha-links to a prior *numeric-NCI* staked claim — because its premise is
external adjudication (git is the judge), never self-grading. It therefore SEES ~58
"corrected/superseded/overclaim" commits but leaves them UNSCORED: they carry no
"This reverts commit <sha>" trailer, so the claim they reversed is unknown.

This script recovers that missing link as a GIT FACT, not a judgment call: for each
correction commit it blames the lines the correction REMOVED against the parent tree,
finds the commit(s) that introduced them, and — when an introducing commit carries a
numeric [NCI:NN] tag — emits a candidate CLAIM->CORRECTION reel-in link.

HIGH PRECISION BY DESIGN (a false link wrongly punishes a staked claim; precision > recall):
  - only lines actually removed/replaced by the correction are blamed (not context)
  - only introducing commits with numeric NCI 0..100 are candidates (must be a stake)
  - strength = fraction of removed lines attributable to that one claim
  - a self-link (correction reverses the SAME session's own just-written claim) is
    flagged, since it is a weaker "reveal" than a later session catching an older claim
  - candidates are EMITTED FOR HUMAN RATIFICATION, not auto-scored into the Brier —
    judgment stays human-owned (mirrors the lattice/seedbank drift-hook pattern).

USAGE (from repo root):
    python3 scripts/corrections_link.py [--min-strength 0.30] [--json OUT.jsonl] [--quiet]

Stdlib only. No network. Read-only (git via subprocess).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field

# Same correction/revert vocabulary the ledger tallies as "unlinked corrections".
_CORRECTION_HINT = re.compile(r"\b(supersed|retract|overclaim|reel[- ]?in|walk[- ]?back|corrects?|corrected|confabulat|reclassif|false[- ]claim)\b", re.I)
_SUBJECT_REVERT = re.compile(r"^(revert\(|revert:|Revert )")
_NCI = re.compile(r"\[NCI:([^\]]+)\]")
_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@")


def _git(*args: str, allow_fail: bool = False) -> str:
    # check the returncode by default: a swallowed error would read as "no link found",
    # a false null. Callers that legitimately expect failure (blame on a path absent at
    # the parent, e.g. a rename) pass allow_fail=True to degrade quietly.
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0 and not allow_fail:
        raise RuntimeError(f"git {' '.join(args[:3])}… failed (exit {r.returncode}): {r.stderr.strip()[:200]}")
    return r.stdout


def numeric_nci(subject: str) -> int | None:
    m = _NCI.search(subject)
    if not m:
        return None
    tok = m.group(1).strip()
    return int(tok) if re.fullmatch(r"\d+", tok) else None


@dataclass
class Correction:
    sha: str
    subject: str


def correction_commits() -> list[Correction]:
    raw = _git("log", "--all", "--no-merges", "--pretty=tformat:%H\x1f%s")
    out: list[Correction] = []
    for line in raw.splitlines():
        sha, _, subj = line.partition("\x1f")
        if not sha:
            continue
        if _SUBJECT_REVERT.match(subj) or _CORRECTION_HINT.search(subj):
            out.append(Correction(sha, subj))
    return out


def removed_lines_by_file(sha: str) -> dict[str, list[int]]:
    """Map file -> list of OLD-file line numbers the correction removed/replaced."""
    diff = _git("show", sha, "--no-color", "--unified=0", "--pretty=format:")
    files: dict[str, list[int]] = {}
    cur: str | None = None
    old_ln = 0
    for line in diff.splitlines():
        # Key off the OLD-file header (--- a/…), since removed lines live in the parent and
        # we blame the parent. Handles whole-file deletion (--- a/foo → +++ /dev/null) which
        # a +++ b/ key would mis-attribute to the previous file (review #4).
        if line.startswith("--- a/"):
            cur = line[6:]
            files.setdefault(cur, [])
            continue
        if line == "--- /dev/null":       # new file — no removed (old) lines to attribute
            cur = None
            continue
        if line.startswith("+++ ") or line.startswith("diff --git"):
            continue
        h = _HUNK.match(line)
        if h:
            old_ln = int(h.group(1))
            continue
        if cur is None:
            continue
        if line.startswith("-") and not line.startswith("---"):
            files[cur].append(old_ln)
            old_ln += 1
        elif line.startswith("+"):
            pass  # additions don't advance the old-file counter
    return {f: ls for f, ls in files.items() if ls}


def blame_introducers(parent: str, path: str, lines: list[int]) -> dict[str, int]:
    """OLD-file line numbers -> introducing commit sha, tallied per commit."""
    tally: dict[str, int] = defaultdict(int)
    # blame the whole file once at the parent; index sha per line.
    # allow_fail: the path may not exist at the parent (a rename/copy correction) — that is a
    # KNOWN recall gap (review #5), degraded quietly rather than crashing. Precision-preserving:
    # a missing blame drops links, never invents one.
    out = _git("blame", "-p", f"{parent}", "--", path, allow_fail=True)
    if not out:
        return tally
    line_sha: dict[int, str] = {}
    cur_sha = None
    for ln in out.splitlines():
        m = re.match(r"^([0-9a-f]{40}) \d+ (\d+)", ln)
        if m:
            cur_sha = m.group(1)
            final_line = int(m.group(2))
            line_sha[final_line] = cur_sha
    for L in lines:
        s = line_sha.get(L)
        if s:
            tally[s] += 1
    return tally


@dataclass
class Candidate:
    correction_sha: str
    correction_subject: str
    claim_sha: str
    claim_nci: int
    claim_subject: str
    linked_lines: int
    total_removed: int
    files: list[str] = field(default_factory=list)

    @property
    def strength(self) -> float:
        return round(self.linked_lines / self.total_removed, 3) if self.total_removed else 0.0

    @property
    def self_link(self) -> bool:
        return self.correction_sha.startswith(self.claim_sha) or self.claim_sha.startswith(self.correction_sha)


def subjects_for(shas: set[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for s in shas:
        subj = _git("show", "--no-patch", "--pretty=format:%s", s).strip()
        if subj:
            out[s] = subj
    return out


def build(min_strength: float) -> list[Candidate]:
    corrections = correction_commits()
    cands: list[Candidate] = []
    for c in corrections:
        by_file = removed_lines_by_file(c.sha)
        if not by_file:
            continue
        total_removed = sum(len(v) for v in by_file.values())
        parent = f"{c.sha}^"
        introducer_tally: dict[str, int] = defaultdict(int)
        introducer_files: dict[str, set[str]] = defaultdict(set)
        for path, lines in by_file.items():
            t = blame_introducers(parent, path, lines)
            for isha, n in t.items():
                introducer_tally[isha] += n
                introducer_files[isha].add(path)
        if not introducer_tally:
            continue
        subs = subjects_for(set(introducer_tally))
        for isha, n in introducer_tally.items():
            nci = numeric_nci(subs.get(isha, ""))
            if nci is None:
                continue  # introducing commit was not a staked (numeric-NCI) claim
            cand = Candidate(c.sha[:12], c.subject[:90], isha[:12], nci,
                             subs[isha][:90], n, total_removed,
                             sorted(introducer_files[isha]))
            if cand.strength >= min_strength:
                cands.append(cand)
    cands.sort(key=lambda x: (-x.strength, -x.claim_nci))
    return cands


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-strength", type=float, default=0.30)
    ap.add_argument("--json", type=str, default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cands = build(args.min_strength)

    if args.json:
        with open(args.json, "w") as fh:
            for c in cands:
                fh.write(json.dumps({
                    "correction_sha": c.correction_sha, "correction_subject": c.correction_subject,
                    "claim_sha": c.claim_sha, "claim_nci": c.claim_nci, "claim_subject": c.claim_subject,
                    "strength": c.strength, "linked_lines": c.linked_lines,
                    "total_removed": c.total_removed, "self_link": c.self_link, "files": c.files,
                }) + "\n")

    if not args.quiet:
        cross = [c for c in cands if not c.self_link]
        print("── Corrections → staked-claim link candidates ────────────────")
        print(f"candidate reel-in links (strength >= {args.min_strength}): {len(cands)}")
        print(f"  cross-session (claim != correction, the strong reveals) : {len(cross)}")
        print(f"  self-links   (same-commit / same-session, weaker)       : {len(cands) - len(cross)}")
        print(f"  distinct staked claims implicated                       : {len({c.claim_sha for c in cands})}")
        print("── candidates (ratify before scoring) ──")
        for c in cands:
            tag = "SELF" if c.self_link else "XSES"
            print(f"  [{tag}] p={c.claim_nci/100:.2f} str={c.strength} "
                  f"claim {c.claim_sha} <- corr {c.correction_sha}")
            print(f"         claim: {c.claim_subject}")
            print(f"         corr : {c.correction_subject}")
        print("──")
        print("NOTE: candidates are for HUMAN RATIFICATION. Only ratified cross-session")
        print("links should be fed to the ledger as reel-ins (outcome=0.0). Judgment stays")
        print("human-owned — a blame link is necessary evidence, not sufficient proof.")
        if args.json:
            print(f"written: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
