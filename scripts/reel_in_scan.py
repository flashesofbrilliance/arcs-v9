#!/usr/bin/env python3
"""reel_in_scan.py — the deterministic scout for float→reel-in events across the WHOLE ref graph.

A reel-in is a staked claim/aspiration caught and corrected before it became durable error.
A keyword hit is NOT a reel-in (Norse-ROM "Loki" naming, KINTSUGI field names, blog prose that
merely USES "reel-in"). This scout separates the machine-certain reel-ins from the residue that
needs human/agent judgment — teleport-to-terminal for what's mechanically scorable, spend
judgment only on the rest.

PROVENANCE-COMPLETE BY CONSTRUCTION (the false-null lesson):
  scans `git log --all` — NOT origin/main. Reel-ins that were reverted/superseded/abandoned on
  an unmerged branch never reach main and are the highest-signal stated→revealed gaps; a
  main-only count is a false null. Cross-branch sha twins of one logical event are collapsed by
  patch-id so the count can't be inflated by branch duplication.

VERDICTS (per logical event):
  GENUINE-AUTO   : a git-revert trailer ("This reverts commit <sha>") — a machine fact, no judgment.
  NEEDS-RATIFY   : correction vocabulary + reversal language (overstated/confabulated/false/not-X-but-Y).
                   Real-candidate; feed to claims-skeptic or a human before counting.
  WEAK           : correction vocabulary but no reversal language. MOSTLY forward work
                   ("catch-up territory number", "reconcile lockfile") — but NOT pure noise:
                   a genuine reel-in whose subject doesn't self-describe as a reversal
                   ("correct 5 verification failures", "verify X was a timeout not credits")
                   lands here too. Sample before discarding; this is judgment residue, not a verdict.

OUTPUT: JSONL of logical events (+ their sha variants, on-main flag, archetype signals) and a
summary with keyword-UB vs machine-certain per archetype. Pairs with corrections_link.py, which
sha-links the NEEDS-RATIFY set to staked claims for the believability ledger.

USAGE (repo root):  python3 scripts/reel_in_scan.py [--json OUT.jsonl] [--quiet]
Stdlib only. No network. Read-only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field

_FLD = "\x1f"
_REC = "\x1e"
_VOCAB = re.compile(r"\b(revert|overclaim|supersed|corrected|correct|confabulat|retract|reclassif|false[- ]claim|walk[- ]?back|reel[- ]?in)\b", re.I)
# stems carry \w* so inflected forms match ("overstated", "confabulated", "reclassified");
# a bare trailing \b after a stem would (wrongly) require the word end AT the stem.
_REVERSAL = re.compile(r"\b(overstat\w*|overclaim\w*|confabulat\w*|phantom|mislabel\w*|not (?:proven|live|true|a|yet)|didn'?t hold|walk[- ]?back|retract\w*|false\w*|stale\w*|wrong\w*|reclassif\w*|supersed\w*)\b", re.I)
_REVERT_TRAILER = re.compile(r"This reverts commit ([0-9a-f]{7,40})", re.I)
_SUBJECT_REVERT = re.compile(r"^(revert\(|revert:|Revert )")

# archetype signal lexicon (best-effort tags, not authoritative)
_ARCH = {
    "claims-skeptic": re.compile(r"\b(claims?-skeptic|verif|fact-?check|re-?audit|verification failures?|provenance)\b", re.I),
    "described-vs-wired": re.compile(r"\b(false claim|not proven|mechanisms? not|kill false|align.*(reality|record)|described.*wired|proven-at-scale)\b", re.I),
    "kintsugi": re.compile(r"\b(kintsugi|repair|heal|to the record)\b", re.I),
    "drift-sentinel": re.compile(r"\b(drift|sentinel|spin cycle|entropy)\b", re.I),
    "loki": re.compile(r"\b(loki|adversar|pre-?commit test|advisor tool)\b", re.I),
}


def _git(*args: str) -> str:
    # check the returncode: a swallowed git error would surface as a clean "0 events",
    # indistinguishable from real absence (the repo's false-null failure mode).
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])}… failed (exit {r.returncode}): {r.stderr.strip()[:200]}")
    return r.stdout


def patch_id(sha: str) -> str:
    """Stable id for a commit's DIFF — collapses cross-branch/rebased twins of one logical change."""
    show = subprocess.run(["git", "show", sha], capture_output=True, text=True).stdout
    out = subprocess.run(["git", "patch-id", "--stable"], input=show, capture_output=True, text=True).stdout
    pid = out.split(" ")[0].strip()
    return pid or ("subj:" + sha)  # empty-diff commits: fall back to sha (won't dedupe, honest)


@dataclass
class Cand:
    sha: str
    subject: str
    body_has_trailer: bool


def gather() -> list[Cand]:
    raw = _git("log", "--all", "--no-merges", "-i", "-E", "--grep",
               "revert|overclaim|supersed|correct|confabulat|retract|reclassif|reverts commit",
               f"--pretty=tformat:%H{_FLD}%s{_FLD}%b{_REC}")
    cands: list[Cand] = []
    for rec in raw.split(_REC):
        rec = rec.strip("\n")
        if not rec:
            continue
        sha, _, rest = rec.partition(_FLD)
        subject, _, body = rest.partition(_FLD)
        if not sha:
            continue
        if not (_VOCAB.search(subject) or _REVERT_TRAILER.search(body)):
            continue
        cands.append(Cand(sha, subject, bool(_REVERT_TRAILER.search(body))))
    return cands


def verdict(c: Cand) -> str:
    if c.body_has_trailer:
        return "GENUINE-AUTO"
    if _SUBJECT_REVERT.match(c.subject) or _REVERSAL.search(c.subject):
        return "NEEDS-RATIFY"
    return "WEAK"


def archetypes(subject: str) -> list[str]:
    return [name for name, rx in _ARCH.items() if rx.search(subject)]


@dataclass
class Event:
    patch: str
    verdict: str
    subject: str
    shas: list[str] = field(default_factory=list)
    on_main: bool = False
    archetypes: list[str] = field(default_factory=list)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=str, default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    # Resolve the mainline ref robustly. A silently-empty main set would flip EVERY event
    # to off-main — the exact false-null inversion this scout exists to prevent (review #1).
    main_shas: set[str] = set()
    main_ref: str | None = None
    for ref in ("origin/main", "main"):
        try:
            shas = _git("log", ref, "--no-merges", "--pretty=tformat:%H").split()
        except RuntimeError:
            continue
        if shas:
            main_shas, main_ref = set(shas), ref
            break
    cands = gather()
    # transparency: how many commits matched the vocab only in the BODY (low-precision,
    # excluded by the subject-scoped scout — surfaced so 'cands' isn't read as exhaustive).
    full_grep = len([l for l in _git("log", "--all", "--no-merges", "-i", "-E", "--grep",
                    "revert|overclaim|supersed|correct|confabulat|retract|reclassif|reverts commit",
                    "--pretty=tformat:%H").splitlines() if l.strip()])
    body_only_excluded = max(0, full_grep - len(cands))

    # collapse cross-branch twins by patch-id -> one logical event
    by_patch: dict[str, Event] = {}
    for c in cands:
        pid = patch_id(c.sha)
        v = verdict(c)
        ev = by_patch.get(pid)
        if ev is None:
            ev = Event(pid, v, c.subject[:100], [], False, archetypes(c.subject))
            by_patch[pid] = ev
        ev.shas.append(c.sha[:12])
        if c.sha in main_shas:
            ev.on_main = True
        # strongest verdict wins (AUTO > RATIFY > WEAK)
        order = {"GENUINE-AUTO": 3, "NEEDS-RATIFY": 2, "WEAK": 1}
        if order[v] > order[ev.verdict]:
            ev.verdict = v

    # If no mainline ref resolved, on-main is UNKNOWN — never claim off-main (false-null guard).
    if main_ref is None:
        for e in by_patch.values():
            e.on_main = None
    events = sorted(by_patch.values(), key=lambda e: (-{"GENUINE-AUTO":3,"NEEDS-RATIFY":2,"WEAK":1}[e.verdict], e.on_main is not False))

    if args.json:
        with open(args.json, "w") as fh:
            for e in events:
                fh.write(json.dumps({
                    "patch_id": e.patch, "verdict": e.verdict, "subject": e.subject,
                    "shas": e.shas, "sha_variants": len(e.shas), "on_main": e.on_main,
                    "off_main_only": e.on_main is False, "archetypes": e.archetypes,
                }) + "\n")

    if not args.quiet:
        auto = [e for e in events if e.verdict == "GENUINE-AUTO"]
        rat = [e for e in events if e.verdict == "NEEDS-RATIFY"]
        weak = [e for e in events if e.verdict == "WEAK"]
        offmain = [e for e in events if e.on_main is False and e.verdict != "WEAK"]
        print("── reel-in scout (all refs, logical events) ──────────────────")
        if main_ref is None:
            print("⚠ mainline ref (origin/main / main) did NOT resolve — on/off-main is UNDETERMINED,")
            print("  not reported as off-main. Fetch or name the remote to restore the provenance split.")
        elif main_ref != "origin/main":
            print(f"note: origin/main absent — used '{main_ref}' as the mainline ref.")
        print(f"raw vocab candidates (subject)   : {len(cands)}   [+{body_only_excluded} body-only, excluded as low-precision]")
        print(f"logical events (patch-id deduped): {len(events)}   [twin-collapse killed {len(cands)-len(events)}]")
        print(f"  GENUINE-AUTO (revert-trailer)  : {len(auto)}")
        print(f"  NEEDS-RATIFY (judgment residue): {len(rat)}")
        print(f"  WEAK (vocab, no reversal lang) : {len(weak)}  (mostly fwd work; may hide reel-ins — sample, don't discard)")
        print(f"off-main-only (AUTO+RATIFY)      : {len(offmain)}  <- a main-only sweep misses these")
        print("── per-archetype: keyword-UB vs machine-certain ──")
        for name in _ARCH:
            ub = sum(1 for e in events if name in e.archetypes)
            cert = sum(1 for e in auto if name in e.archetypes)
            ratn = sum(1 for e in rat if name in e.archetypes)
            print(f"  {name:20s} UB={ub:3d}  auto-genuine={cert:2d}  needs-ratify={ratn:2d}")
        print("── off-main-only reveals (the false-null tail) ──")
        for e in offmain[:12]:
            print(f"  [{e.verdict}] {e.subject}")
        print("──")
        print("NEEDS-RATIFY = the residue for claims-skeptic / a human. GENUINE-AUTO is machine-")
        print("certain (git revert trailer). corrections_link.py sha-links these to staked claims.")
        if args.json:
            print(f"written: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
