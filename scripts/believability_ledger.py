#!/usr/bin/env python3
"""
believability_ledger.py — the one construct in the audit stack that is falsifiable
NOW, without waiting on product outcomes (of which there are 2/247, none externally
adjudicated — see docs/sage-firing-diagnosis-and-solution.md, "Bedrock").

WHAT IT MEASURES
  Stated confidence at claim time  vs  revealed accuracy at resolution time,
  scored as a Brier score, weighted by ruin-potential, over an EXTERNALLY-resolved
  corpus. "Externally resolved" is the whole point: a self-graded outcome is capture,
  not adjudication. Git is the external judge here — a `git revert` is a fact about
  the world, not a self-assessment. Nobody grades their own claim as "held"; the
  claim held iff the corpus never reeled it back in.

PRE-REGISTERED DEFINITIONS (committed BEFORE reading the corpus — pre-register-rule-
before-counting; every tag carries reach-metadata: source + confidence + what it confirms)

  CLAIM (a staked assertion with a stated confidence)
    A commit whose subject carries a numeric [NCI:NN] tag with 0 <= NN <= 100.
      confidence p := NN / 100  ==  the claimed probability the change HOLDS
                                      (NCI is a coherence/durability conviction from
                                       the ADR-035 rubric; used here as a monotone
                                       proxy for P(holds), NOT as a calibrated
                                       probability — this assumption is load-bearing
                                       and is stated in the ledger, not hidden).
    EXCLUDED, null-honestly (tracked, never scored):
      - [NCI:SKIP] / [NCI:SKIP docs]  -> no stake declared.
      - [NCI:NN] with NN > 100        -> the tag is out of the rubric's 0..100 range
                                          (the repo uses NCI>100 as an accumulator in
                                          some conventions); as a probability it is
                                          UNINTERPRETABLE. Coercing it would be the
                                          exact placeholder-number dishonesty the
                                          audit exists to catch.

  REEL-IN (the corpus revealing a claim did NOT hold) — HIGH PRECISION by design.
    A false reel-in wrongly punishes a claim, so precision beats recall here.
      source=git-revert-trailer (confidence=high): a later commit body contains
        "This reverts commit <sha>" pointing AT the claim's sha. This is machine-
        generated and unambiguous.
      source=subject-revert (confidence=med): a later commit subject begins with
        "revert(" or "Revert " AND its body sha-links the claim. Same link, human-
        authored wrapper.
    NOT counted as reel-in (deliberately): bare "fix:" / "correct" / "supersede"
      subjects with no sha pointer. 337 fix-family commits exist; the vast majority
      are forward work, not retractions of a prior CLAIM. Counting them would be a
      false-positive disaster. They are tallied separately as UNLINKED-CORRECTIONS
      for visibility, and never scored against a specific claim.

  RESOLUTION of a claim C:
      reeled_in : some later commit reels C in (as above)        -> outcome o = 0.0
      held      : NOT reeled_in AND age(C) >= maturity_window     -> outcome o = 1.0
      unresolved: NOT reeled_in AND age(C) <  maturity_window     -> o = None (EXCLUDED
                    from Brier — too young to have earned "held". Explicit null.)

  BRIER (over RESOLVED claims only):  mean_i (p_i - o_i)^2      (lower = better)
    Reported against two baselines so hedging cannot look like skill:
      - always-0.5 Brier (max-hedge)         -> skill must beat 0.25
      - base-rate Brier (predict the corpus hold-rate for everyone) -> the honest bar;
        model_skill := base_rate_brier - weighted_brier  (>0 means stated confidence
        carried information beyond just knowing reel-ins are rare).

  RUIN WEIGHT w (an error on an irreversible surface counts more — BAR edge):
      high (w=3): touches prisma/ , src/lib/auth , src/app/api/ , a migration
      med  (w=2): any other src/
      low  (w=1): docs / _STATE / _SEEDS / _ARTIFACTS / .claude / scripts-docs
    weighted_brier := sum_i w_i (p_i - o_i)^2 / sum_i w_i

REUSABLE SEAM (build-reusable-by-default)
  A Resolver yields (claim_id, confidence, outcome|None, meta) rows; the pure
  score_ledger() Brier engine consumes ANY resolver. Two are declared:
    - GitRevertResolver  -> BUILT (this file).
    - ReceiptOutcomeResolver -> DEBT MARKER, NOT WIRED. It would map a Receipt's
      stated conviction (yConviction / nciScore) against Outcome.matched, but
      Outcome.matched is SELF-graded (capture, not adjudication) AND only 2/247 exist,
      so it is intentionally left as an honest stub returning [] rather than faked.
      Wiring it needs (a) a receipt+outcome export and (b) an external adjudication
      field on Outcome. See docs/sage-firing-diagnosis-and-solution.md.

RUN (from repo root):
    python3 scripts/believability_ledger.py [--maturity-days 30] [--as-of ISO8601]
                                            [--json OUT.json] [--quiet]
Stdlib only. No network. Reads git via subprocess.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# ── git plumbing ──────────────────────────────────────────────────────────────

def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


# Records are delimited so subjects/bodies with newlines survive parsing.
_REC = "\x1e"   # record sep
_FLD = "\x1f"   # field sep
_NCI = re.compile(r"\[NCI:([^\]]+)\]")
_REVERT_TRAILER = re.compile(r"This reverts commit ([0-9a-f]{7,40})", re.I)
_SUBJECT_REVERT = re.compile(r"^(revert\(|revert:|Revert )", )
_CORRECTION_HINT = re.compile(r"\b(supersed|retract|overclaim|reel[- ]?in|walk[- ]?back|corrects?)\b", re.I)

_HIGH = ("prisma/", "src/lib/auth", "src/app/api/")
_LOW = ("docs/", "_STATE/", "_SEEDS/", "_ARTIFACTS/", ".claude/", "_DECISIONS/", "_PATTERNS/")


@dataclass
class Commit:
    sha: str
    ts: datetime
    subject: str
    files: list[str] = field(default_factory=list)   # lazily filled for claim commits only


def load_commits(as_of: datetime) -> list[Commit]:
    """One line per commit (subject only — no multiline body, which corrupts record
    boundaries). Files/body are fetched on demand for the small claim/revert subsets."""
    raw = _git("log", "--all", "--no-merges", f"--pretty=tformat:%H{_FLD}%cI{_FLD}%s")
    commits: list[Commit] = []
    for line in raw.splitlines():
        parts = line.split(_FLD)
        if len(parts) < 3:
            continue
        sha, ts_s, subject = parts[0], parts[1], parts[2]
        try:
            ts = datetime.fromisoformat(ts_s)
        except ValueError:
            continue
        if ts > as_of:
            continue
        commits.append(Commit(sha, ts, subject))
    return commits


def files_for(sha: str) -> list[str]:
    try:
        out = _git("show", "--no-patch", "--pretty=format:", "--name-only", sha)
    except subprocess.CalledProcessError:
        return []
    return [ln for ln in out.splitlines() if ln.strip()]


def revert_targets(as_of: datetime) -> dict[str, str]:
    """sha-of-reverted-commit -> sha-of-the-revert-commit (git-generated trailer)."""
    raw = _git("log", "--all", "--no-merges", "--grep", "This reverts commit",
               f"--pretty=tformat:%H{_FLD}%cI{_FLD}%b{_REC}")
    out: dict[str, str] = {}
    for rec in raw.split(_REC):
        rec = rec.strip("\n")
        if not rec:
            continue
        head, _, body = rec.partition(_FLD)  # head=revert sha
        rev_sha = head
        _ts, _, body2 = body.partition(_FLD)
        m = _REVERT_TRAILER.search(body2)
        if m:
            out.setdefault(m.group(1), rev_sha)
    return out


# ── ruin weight ───────────────────────────────────────────────────────────────

def ruin_weight(files: list[str]) -> tuple[int, str]:
    if any(f.startswith(p) for f in files for p in _HIGH) or any("migration" in f for f in files):
        return 3, "high"
    if any(f.startswith("src/") for f in files):
        return 2, "med"
    return 1, "low"


# ── resolvers ─────────────────────────────────────────────────────────────────

@dataclass
class ClaimRow:
    claim_id: str
    confidence: float
    outcome: Optional[float]           # 1.0 held · 0.0 reeled · None unresolved
    weight: int
    meta: dict


class GitRevertResolver:
    """Externally-resolved calibration from git revert history."""

    name = "git-revert"

    def resolve(self, commits: list[Commit], as_of: datetime, maturity_days: int) -> tuple[list[ClaimRow], dict]:
        # sha-linked reverts (target-prefix -> revert sha), matched by prefix.
        targets = revert_targets(as_of)
        by_full = {c.sha: c for c in commits}
        reeled: dict[str, str] = {}   # claim full-sha -> revert sha
        for tgt, rev in targets.items():
            full = next((s for s in by_full if s.startswith(tgt)), None)
            if full:
                reeled[full] = rev

        # visible-but-unscored corrections (no sha pointer)
        unlinked_corrections = sum(
            1 for c in commits
            if (_SUBJECT_REVERT.match(c.subject) or _CORRECTION_HINT.search(c.subject))
            and c.sha not in reeled
        )

        maturity = maturity_days * 86400
        rows: list[ClaimRow] = []
        skipped_no_stake = skipped_out_of_range = 0
        for c in commits:
            m = _NCI.search(c.subject)
            if not m:
                continue
            tok = m.group(1).strip()
            if not re.fullmatch(r"\d+", tok):
                skipped_no_stake += 1          # SKIP / SKIP docs / non-numeric
                continue
            nn = int(tok)
            if nn > 100:
                skipped_out_of_range += 1       # uninterpretable as a probability
                continue
            p = nn / 100.0
            w, w_label = ruin_weight(files_for(c.sha))
            if c.sha in reeled:
                rows.append(ClaimRow(c.sha[:12], p, 0.0, w, {
                    "confidence_source": "nci-tag", "confidence_raw": nn,
                    "resolution": "reeled_in", "resolution_source": "git-revert-trailer",
                    "resolution_confidence": "high", "reeled_by": reeled[c.sha][:12],
                    "ruin": w_label, "subject": c.subject[:90],
                    "what_it_confirms": "a staked claim was later reverted",
                }))
            else:
                age = (as_of - c.ts).total_seconds()
                if age >= maturity:
                    rows.append(ClaimRow(c.sha[:12], p, 1.0, w, {
                        "confidence_source": "nci-tag", "confidence_raw": nn,
                        "resolution": "held", "resolution_source": "git-survival",
                        "resolution_confidence": "med",
                        "resolution_note": f"never reeled in, matured >= {maturity_days}d",
                        "ruin": w_label, "subject": c.subject[:90],
                        "what_it_confirms": "a staked claim survived the maturity window",
                    }))
                else:
                    rows.append(ClaimRow(c.sha[:12], p, None, w, {
                        "confidence_source": "nci-tag", "confidence_raw": nn,
                        "resolution": "unresolved", "resolution_source": None,
                        "resolution_confidence": None,
                        "resolution_note": f"too young (<{maturity_days}d) — explicit null, excluded from Brier",
                        "ruin": w_label, "subject": c.subject[:90],
                        "what_it_confirms": None,
                    }))
        diag = {
            "staked_claims_found": len(rows),
            "excluded_no_stake_nci_skip_or_nonnumeric": skipped_no_stake,
            "excluded_nci_over_100_uninterpretable": skipped_out_of_range,
            "unlinked_corrections_seen_not_scored": unlinked_corrections,
            "distinct_reel_ins_linked": len(reeled),
        }
        return rows, diag


class ReceiptOutcomeResolver:
    """DEBT MARKER — not wired. See module docstring. Returns [] honestly."""

    name = "receipt-outcome"

    def resolve(self, *_a, **_k) -> tuple[list[ClaimRow], dict]:
        return [], {
            "status": "NOT_WIRED",
            "reason": "Outcome.matched is self-graded (capture, not external adjudication) "
                      "and only 2/247 exist; wiring requires a receipt+outcome export and an "
                      "external adjudication field. Faking it would violate null-honesty.",
        }


# ── pure Brier engine ─────────────────────────────────────────────────────────

def score_ledger(rows: list[ClaimRow]) -> dict:
    resolved = [r for r in rows if r.outcome is not None]
    unresolved = [r for r in rows if r.outcome is None]
    if not resolved:
        return {
            "resolved": 0, "unresolved": len(unresolved),
            "note": "no resolved claims — Brier undefined (null-honest, not 0.0)",
            "brier_unweighted": None, "brier_weighted": None,
            "base_rate_hold": None, "model_skill_vs_base_rate": None,
        }
    n = len(resolved)
    hold_rate = sum(r.outcome for r in resolved) / n
    brier_unw = sum((r.confidence - r.outcome) ** 2 for r in resolved) / n
    wsum = sum(r.weight for r in resolved)
    brier_w = sum(r.weight * (r.confidence - r.outcome) ** 2 for r in resolved) / wsum
    brier_hedge = sum((0.5 - r.outcome) ** 2 for r in resolved) / n
    brier_base = sum((hold_rate - r.outcome) ** 2 for r in resolved) / n
    # Weighted base-rate baseline: model skill compares a WEIGHTED model Brier against a
    # WEIGHTED base-rate Brier, so the comparison is on one measure. Mixing weighted-vs-
    # unweighted let the ruin-weighting scheme masquerade as calibration skill (review #3).
    w_hold = sum(r.weight * r.outcome for r in resolved) / wsum
    brier_base_w = sum(r.weight * (w_hold - r.outcome) ** 2 for r in resolved) / wsum
    # reliability buckets
    buckets: dict[str, dict] = {}
    for r in resolved:
        lo = min(int(r.confidence * 10) * 10, 90)   # clamp top bucket: p=1.0 → "90-100%"
        b = f"{lo}-{100 if lo == 90 else lo + 9}%"
        d = buckets.setdefault(b, {"n": 0, "mean_conf": 0.0, "mean_outcome": 0.0})
        d["n"] += 1
        d["mean_conf"] += r.confidence
        d["mean_outcome"] += r.outcome
    for d in buckets.values():
        d["mean_conf"] = round(d["mean_conf"] / d["n"], 3)
        d["mean_outcome"] = round(d["mean_outcome"] / d["n"], 3)
    reel_ins = sum(1 for r in resolved if r.outcome == 0.0)
    # Seaworthiness: a Brier near 0 is meaningless if almost nothing was ever reeled
    # in — it just reflects the base rate, not calibration skill. Degeneracy is only
    # visible in aggregate (the inlier trap); say it out loud.
    if reel_ins < 3 or hold_rate >= 0.99:
        seaworthy = False
        verdict = (f"NON-DISCRIMINATING: only {reel_ins} reel-in event(s) among {n} "
                   f"resolved claims. Brier reflects the base rate, not calibration "
                   f"skill. NOT a seaworthy calibration test on this corpus yet — the "
                   f"external reel-in signal is too sparse (needs sha-linked corrections "
                   f"or the receipt->outcome loop with external adjudication).")
    else:
        seaworthy = True
        verdict = "discriminating: reel-in events present; Brier is a real calibration signal."
    return {
        "resolved": n,
        "unresolved": len(unresolved),
        "reel_ins": reel_ins,
        "seaworthy": seaworthy,
        "verdict": verdict,
        "base_rate_hold": round(hold_rate, 4),
        "brier_unweighted": round(brier_unw, 4),
        "brier_weighted": round(brier_w, 4),
        "brier_always_0.5_hedge": round(brier_hedge, 4),
        "brier_base_rate": round(brier_base, 4),
        "brier_base_rate_weighted": round(brier_base_w, 4),
        "model_skill_vs_base_rate": round(brier_base_w - brier_w, 4),
        "reliability_buckets": dict(sorted(buckets.items())),
    }


def high_conf_reel_ins(rows: list[ClaimRow]) -> list[dict]:
    """The calibration debt worth a human's eyes: confident claims that got reversed."""
    out = []
    for r in rows:
        if r.outcome == 0.0 and r.confidence >= 0.85:
            out.append({"claim": r.claim_id, "confidence": r.confidence,
                        "reeled_by": r.meta.get("reeled_by"), "ruin": r.meta.get("ruin"),
                        "subject": r.meta.get("subject")})
    return sorted(out, key=lambda x: -x["confidence"])


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--maturity-days", type=int, default=30)
    ap.add_argument("--as-of", type=str, default=None, help="ISO8601; default now (UTC)")
    ap.add_argument("--json", type=str, default=None, help="write full ledger JSON here")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    as_of = (datetime.fromisoformat(args.as_of) if args.as_of else datetime.now(timezone.utc))
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)

    commits = load_commits(as_of)
    resolver = GitRevertResolver()
    rows, diag = resolver.resolve(commits, as_of, args.maturity_days)
    score = score_ledger(rows)
    debt = ReceiptOutcomeResolver().resolve()[1]
    debt_flags = high_conf_reel_ins(rows)

    ledger = {
        "generated": as_of.isoformat(),
        "commits_scanned": len(commits),
        "maturity_days": args.maturity_days,
        "resolver": resolver.name,
        "assumption": "confidence p = NCI/100 = P(claim holds); NCI is a coherence "
                      "conviction used as a monotone proxy, NOT a calibrated probability.",
        "corpus_diagnostics": diag,
        "score": score,
        "high_confidence_reel_ins": debt_flags,
        "receipt_resolver_debt": debt,
        "claims": [{"claim_id": r.claim_id, "confidence": r.confidence,
                    "outcome": r.outcome, "weight": r.weight, **r.meta} for r in rows],
    }

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(ledger, fh, indent=2)

    if not args.quiet:
        s = score
        print("── ARCS Believability Ledger ─────────────────────────────────")
        print(f"commits scanned         : {len(commits)}   as-of {as_of.date()}   maturity {args.maturity_days}d")
        print(f"staked claims (0..100)  : {diag['staked_claims_found']}")
        print(f"  excluded — no stake   : {diag['excluded_no_stake_nci_skip_or_nonnumeric']} (NCI:SKIP / non-numeric)")
        print(f"  excluded — NCI>100    : {diag['excluded_nci_over_100_uninterpretable']} (uninterpretable as p)")
        print(f"  unlinked corrections  : {diag['unlinked_corrections_seen_not_scored']} (seen, NOT scored)")
        print(f"  distinct reel-ins     : {diag['distinct_reel_ins_linked']} (sha-linked reverts)")
        print("──")
        if s["resolved"] == 0:
            print(f"resolved claims         : 0  →  {s['note']}")
        else:
            print(f"resolved / unresolved   : {s['resolved']} / {s['unresolved']}   reel-ins {s['reel_ins']}")
            flag = "✓" if s["seaworthy"] else "⚠"
            print(f"{flag} SEAWORTHINESS        : {s['verdict']}")
            print(f"base-rate hold          : {s['base_rate_hold']}")
            print(f"Brier (weighted)        : {s['brier_weighted']}   (unweighted {s['brier_unweighted']})")
            print(f"  vs always-0.5 hedge   : {s['brier_always_0.5_hedge']}")
            print(f"  vs base-rate baseline : {s['brier_base_rate']}")
            print(f"  model skill vs base   : {s['model_skill_vs_base_rate']}  (>0 = confidence carried info)")
        if debt_flags:
            print("──\nHIGH-CONFIDENCE REEL-INS (calibration debt):")
            for d in debt_flags:
                print(f"  {d['claim']}  p={d['confidence']}  ruin={d['ruin']}  {d['subject']}")
        print("──")
        print(f"receipt-side resolver   : {debt['status']} (debt marker — self-graded, 2/247)")
        if args.json:
            print(f"full ledger written     : {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
