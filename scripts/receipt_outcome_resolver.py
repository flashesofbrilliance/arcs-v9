#!/usr/bin/env python3
"""receipt_outcome_resolver.py — the receipt-side resolver for the believability ledger.

The believability ledger (scripts/believability_ledger.py) scores stated confidence vs
revealed accuracy over an EXTERNALLY-adjudicated corpus. Its git-side resolver is data-
floor-limited (~2 low-ruin staked reel-ins after exhaustive linking). Its receipt-side
resolver was left an HONEST STUB returning [] because `Outcome.matched` is SELF-graded
(the decision-maker grades their own decision = capture, not adjudication) and only 2/247
outcomes exist.

This module is that stub, made real — WITHOUT violating the external-adjudication invariant:
it scores an outcome ONLY when it carries an EXTERNAL verdict (a signal from someone/something
other than the receipt's author, arriving after T0). Self-graded `matched` is read but NEVER
scored; it is reported separately, exactly as the git resolver reports unlinked corrections.

It reads a JSONL EXPORT rather than the DB, so it runs anywhere (no Prisma, no DB driver,
no prod credentials). The export producer (an admin-gated route or CLI over the live DB) is
the remaining gated piece — see the co-build spec. Each export row:

    {"receipt_id": str, "nci_score": int,           # stated confidence (0..100)
     "external_verdict": "held"|"reeled"|null,      # EXTERNAL adjudication, or null=pending
     "self_matched": bool|null,                     # self-graded — reported, never scored
     "ruin": "high"|"med"|"low",                    # decision surface (default med)
     "adjudicated_by": str|null, "note": str|null}

CONTRACT: yields ClaimRow-compatible dicts {claim_id, confidence, outcome, weight, meta}
consumable by believability_ledger.score_ledger(). Wire on co-merge with the ledger.

USAGE:  python3 scripts/receipt_outcome_resolver.py [--export receipt_outcomes.jsonl] [--json OUT]
Stdlib only. No network. Read-only.
"""
from __future__ import annotations

import argparse
import json
import sys

_RUIN_W = {"high": 3, "med": 2, "low": 1}


def resolve(rows: list[dict]) -> tuple[list[dict], dict]:
    """Return (scorable_rows, diagnostics). Scores ONLY externally-adjudicated outcomes."""
    scorable: list[dict] = []
    self_only = pending = excluded_over100 = no_stake = 0
    for r in rows:
        nci = r.get("nci_score")
        if not isinstance(nci, int):
            no_stake += 1
            continue
        if nci > 100:
            excluded_over100 += 1           # uninterpretable as a probability (ledger rule)
            continue
        ext = r.get("external_verdict")
        if ext not in ("held", "reeled"):
            # no external signal — count why, never fabricate an outcome
            if r.get("self_matched") is not None:
                self_only += 1              # self-graded exists but is NOT adjudication
            else:
                pending += 1
            continue
        w = _RUIN_W.get(r.get("ruin", "med"), 2)
        scorable.append({
            "claim_id": r["receipt_id"],
            "confidence": nci / 100.0,
            "outcome": 1.0 if ext == "held" else 0.0,
            "weight": w,
            "meta": {"confidence_source": "receipt.nciScore", "confidence_raw": nci,
                     "resolution": "held" if ext == "held" else "reeled_in",
                     "resolution_source": "external-adjudication",
                     "adjudicated_by": r.get("adjudicated_by"), "ruin": r.get("ruin", "med"),
                     "note": r.get("note")},
        })
    diag = {
        "export_rows": len(rows),
        "externally_adjudicated_scored": len(scorable),
        "self_graded_only_seen_not_scored": self_only,
        "pending_no_signal": pending,
        "excluded_nci_over_100": excluded_over100,
        "excluded_no_stake": no_stake,
    }
    return scorable, diag


def load_export(path: str | None) -> list[dict]:
    if not path:
        return []
    rows: list[dict] = []
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except FileNotFoundError:
        return []
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", type=str, default=None, help="JSONL of receipt-outcome rows")
    ap.add_argument("--json", type=str, default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rows = load_export(args.export)
    scorable, diag = resolve(rows)

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"resolver": "receipt-outcome", "diagnostics": diag, "rows": scorable}, fh, indent=2)

    if not args.quiet:
        print("── receipt-outcome resolver ──────────────────────────────────")
        if not rows:
            print("export: NONE provided (or empty).")
            print("  → 0 rows. The seam is wired and invariant-safe, but the receipt corpus")
            print("    yields no externally-adjudicated outcomes to score (expected: 2/247 exist,")
            print("    none external). Unblock: (1) add Outcome.externalVerdict + adjudicatedBy,")
            print("    (2) an export producer over the live DB, (3) actual adjudication signal.")
            return 0
        print(f"export rows                    : {diag['export_rows']}")
        print(f"externally-adjudicated (SCORED): {diag['externally_adjudicated_scored']}")
        print(f"self-graded only (NOT scored)  : {diag['self_graded_only_seen_not_scored']}  (matched != adjudication)")
        print(f"pending / no signal            : {diag['pending_no_signal']}")
        print(f"excluded — NCI>100 / no stake  : {diag['excluded_nci_over_100']} / {diag['excluded_no_stake']}")
        if diag["externally_adjudicated_scored"] == 0:
            print("⚠ NON-CONTRIBUTING: no external verdicts yet — feeds 0 to the Brier (honest null).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
