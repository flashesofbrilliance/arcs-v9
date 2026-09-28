#!/usr/bin/env python3
"""
arcs_accountant.py — Operator 19, the Accountant (CFO · "measure outcomes" · The Scoreboard).

Periodic table row 19 (operators/docs/PERIODIC-TABLE.md; numbering LOCKED). Bound in
scripts/operator_registry_emit.py as `call: callable`, entrypoint `run`, so the MCP bridge
exposes it as run_operator("19", payload={"receipts": [...], "outcomes": [...]}).

WHAT IT COUNTS
  A Receipt is an open position (a bearing taken under a stated horizon). An Outcome is the
  human closing that position: matched (did reality land where the bearing pointed) and a
  regret score. The Accountant counts what closed, per cohort, and reports whether the
  closed set is large enough to say anything about calibration of nciScore against outcome.

WHAT IT REFUSES
  - It never draws a calibration curve below CALIBRATION_MIN_N closed positions in a cohort
    (and never with only one outcome class present). Below that it says
    `sufficiency: insufficient` and reports n. A scoreboard with n=3 says n=3.
  - It never invents a field. A receipt missing nci_score is counted in `missing_fields`
    and excluded from the NCI statistics; it is not defaulted to 50.
  - It does not compute EXPIRED: no expiry rule is registered (runtime/specs/fates.json
    marks the receipt class soft and Receipt carries no status column), so the fate is
    reported as `not_computed`, not as 0.

COHORTS (first-class dimension, per the 2026-09-24 correction that retired "2/247")
  founder | external | anonymous (no userId; cannot be attributed to either). The operator
  does not decide cohort membership; the adapter (operators/prod_receipt_to_accountant.py)
  stamps `cohort` on each receipt from the export. An unstamped receipt lands in
  `unattributed` and is reported, never silently folded into a cohort.

INPUT CONTRACT (snake_case, adapter-produced; every key optional except receipt_id)
  receipt: {receipt_id, cohort, nci_score:int, horizon:str, stakes:str, mode:str,
            drift_state:str, created_epoch:int}
  outcome: {receipt_id, matched:bool, regret_score:int, logged_at:str}

Vocabulary: fates from runtime/specs/fates.json class `receipt`:
  status  OPEN (non-terminal) | LOGGED | EXPIRED ; drift LANDED | DRIFTING.

Stdlib only. `python3 arcs_accountant.py --self-test` proves the two refusals.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

OPERATOR = 19
SYMBOL = "Acco"
NAME = "Accountant"

# Minimum closed positions in ONE cohort before any NCI-vs-outcome figure is emitted.
# 30 is the conventional floor at which a rank correlation stops being dominated by two
# or three points; it is stated here so the report can cite it, and so the number can be
# argued with in one place rather than assumed.
CALIBRATION_MIN_N = 30

RECEIPT_FATES = {"OPEN": "non_terminal", "LOGGED": "terminal", "EXPIRED": "terminal"}
DRIFT_FATES = ("LANDED", "DRIFTING")
KNOWN_COHORTS = ("founder", "external", "anonymous")


# ── report shape ────────────────────────────────────────────────────────────

@dataclass
class Calibration:
    sufficiency: str                      # "sufficient" | "insufficient"
    n: int
    threshold: int = CALIBRATION_MIN_N
    reason: Optional[str] = None
    # populated only when sufficiency == "sufficient"
    mean_nci_matched: Optional[float] = None
    mean_nci_unmatched: Optional[float] = None
    spearman_nci_vs_regret: Optional[float] = None
    n_matched: Optional[int] = None
    n_unmatched: Optional[int] = None


@dataclass
class CohortScore:
    cohort: str
    receipts: int = 0
    receipts_with_horizon: int = 0
    by_horizon: dict = field(default_factory=dict)
    by_mode: dict = field(default_factory=dict)
    outcomes_logged: int = 0
    matched: int = 0
    unmatched: int = 0
    fate: dict = field(default_factory=dict)         # OPEN / LOGGED counts; EXPIRED not_computed
    drift: dict = field(default_factory=dict)        # LANDED / DRIFTING / other observed values
    closure_rate: Optional[float] = None             # outcomes_logged / receipts; None when receipts == 0
    regret_scores: list = field(default_factory=list)  # the raw closed values, so n is visible
    mean_regret: Optional[float] = None
    mean_nci_all: Optional[float] = None
    nci_scored: int = 0                              # receipts that actually carried nci_score
    calibration: Optional[Calibration] = None
    missing_fields: dict = field(default_factory=dict)


@dataclass
class AccountantReport:
    schema: str = "arcs-accountant-report/v1"
    operator: int = OPERATOR
    symbol: str = SYMBOL
    name: str = NAME
    generated_at: str = ""
    thresholds: dict = field(default_factory=lambda: {"calibration_min_n": CALIBRATION_MIN_N})
    totals: dict = field(default_factory=dict)
    cohorts: dict = field(default_factory=dict)      # cohort -> CohortScore
    sufficiency: str = "insufficient"                # any cohort sufficient -> "sufficient"
    refusals: list = field(default_factory=list)     # what the report declined to compute, and why
    orphans: dict = field(default_factory=dict)      # outcomes whose receipt_id is not in receipts
    vocabulary: dict = field(default_factory=lambda: {
        "receipt_fates": RECEIPT_FATES, "drift_fates": list(DRIFT_FATES),
        "source": "runtime/specs/fates.json (class receipt)"})


# ── helpers (stdlib; no defaults ever substituted for missing data) ─────────

def _mean(xs: list) -> Optional[float]:
    return round(sum(xs) / len(xs), 3) if xs else None


def _rank(xs: list) -> list:
    """Average ranks (ties share the mean rank)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def spearman(x: list, y: list) -> Optional[float]:
    if len(x) != len(y) or len(x) < 3:
        return None
    rx, ry = _rank(x), _rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return round(num / den, 4) if den else None


def _is_int(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and not math.isnan(float(v))


# ── the operator ────────────────────────────────────────────────────────────

class AccountantOperator:
    """Operator 19. Construct with no args (bridge does `sym(**params)`), then `.run(...)`."""

    def __init__(self, calibration_min_n: int = CALIBRATION_MIN_N):
        self.calibration_min_n = int(calibration_min_n)

    def run(self, receipts: list, outcomes: list, **_ignored) -> dict:
        rep = AccountantReport(generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        rep.thresholds["calibration_min_n"] = self.calibration_min_n
        receipts = receipts or []
        outcomes = outcomes or []

        by_receipt: dict[str, dict] = {}
        for o in outcomes:
            rid = o.get("receipt_id")
            if rid is None:
                rep.orphans.setdefault("outcomes_without_receipt_id", 0)
                rep.orphans["outcomes_without_receipt_id"] += 1
                continue
            by_receipt[str(rid)] = o
        seen_ids = {str(r.get("receipt_id")) for r in receipts if r.get("receipt_id") is not None}
        orphan_ids = sorted(set(by_receipt) - seen_ids)
        if orphan_ids:
            rep.orphans["outcomes_with_unknown_receipt"] = orphan_ids

        scores: dict[str, CohortScore] = {}
        # per-cohort working sets for the calibration decision
        closed_nci: dict[str, list] = {}
        closed_regret: dict[str, list] = {}
        closed_matched: dict[str, list] = {}
        all_nci: dict[str, list] = {}

        for r in receipts:
            cohort = r.get("cohort")
            if cohort not in KNOWN_COHORTS:
                cohort = "unattributed"
            cs = scores.setdefault(cohort, CohortScore(cohort=cohort))
            cs.receipts += 1

            hz = r.get("horizon")
            if hz:
                cs.receipts_with_horizon += 1
                cs.by_horizon[hz] = cs.by_horizon.get(hz, 0) + 1
            else:
                cs.missing_fields["horizon"] = cs.missing_fields.get("horizon", 0) + 1

            md = r.get("mode")
            if md:
                cs.by_mode[md] = cs.by_mode.get(md, 0) + 1

            nci = r.get("nci_score")
            if _is_int(nci):
                cs.nci_scored += 1
                all_nci.setdefault(cohort, []).append(float(nci))
            else:
                cs.missing_fields["nci_score"] = cs.missing_fields.get("nci_score", 0) + 1

            ds = r.get("drift_state")
            if ds:
                cs.drift[ds] = cs.drift.get(ds, 0) + 1
            else:
                cs.missing_fields["drift_state"] = cs.missing_fields.get("drift_state", 0) + 1

            rid = str(r.get("receipt_id")) if r.get("receipt_id") is not None else None
            o = by_receipt.get(rid) if rid else None
            if o is None:
                cs.fate["OPEN"] = cs.fate.get("OPEN", 0) + 1
                continue

            cs.fate["LOGGED"] = cs.fate.get("LOGGED", 0) + 1
            cs.outcomes_logged += 1
            m = o.get("matched")
            if isinstance(m, bool):
                if m:
                    cs.matched += 1
                else:
                    cs.unmatched += 1
            else:
                cs.missing_fields["outcome.matched"] = cs.missing_fields.get("outcome.matched", 0) + 1
            rg = o.get("regret_score")
            if _is_int(rg):
                cs.regret_scores.append(rg)
            else:
                cs.missing_fields["outcome.regret_score"] = cs.missing_fields.get("outcome.regret_score", 0) + 1
            if _is_int(nci) and _is_int(rg) and isinstance(m, bool):
                closed_nci.setdefault(cohort, []).append(float(nci))
                closed_regret.setdefault(cohort, []).append(float(rg))
                closed_matched.setdefault(cohort, []).append(m)

        any_sufficient = False
        for cohort, cs in scores.items():
            cs.fate["EXPIRED"] = "not_computed"
            for d in DRIFT_FATES:
                cs.drift.setdefault(d, 0)
            cs.closure_rate = round(cs.outcomes_logged / cs.receipts, 4) if cs.receipts else None
            cs.mean_regret = _mean(cs.regret_scores)
            cs.mean_nci_all = _mean(all_nci.get(cohort, []))
            cs.calibration = self._calibrate(cohort, closed_nci.get(cohort, []),
                                             closed_regret.get(cohort, []), closed_matched.get(cohort, []), rep)
            any_sufficient = any_sufficient or cs.calibration.sufficiency == "sufficient"

        rep.sufficiency = "sufficient" if any_sufficient else "insufficient"
        rep.refusals.append("EXPIRED not computed: no expiry rule registered for receipt horizons "
                            "(fates.json receipt class is soft; Receipt has no status column).")
        rep.totals = {
            "receipts": len(receipts),
            "outcomes": len(outcomes),
            "outcomes_joined": sum(cs.outcomes_logged for cs in scores.values()),
            "cohorts": {c: cs.receipts for c, cs in scores.items()},
            "closed_by_cohort": {c: cs.outcomes_logged for c, cs in scores.items()},
        }
        rep.cohorts = {c: asdict(cs) for c, cs in sorted(scores.items())}
        return asdict(rep)

    def _calibrate(self, cohort: str, nci: list, regret: list, matched: list, rep: AccountantReport) -> Calibration:
        n = len(nci)
        if n < self.calibration_min_n:
            rep.refusals.append(f"{cohort}: calibration refused, n={n} closed positions with nci+outcome "
                                f"< threshold {self.calibration_min_n}")
            return Calibration(sufficiency="insufficient", n=n, threshold=self.calibration_min_n,
                               reason=f"n={n} < {self.calibration_min_n}; a curve at this n would be two or three "
                                      f"points dressed as a trend")
        n_m, n_u = sum(1 for m in matched if m), sum(1 for m in matched if not m)
        if n_m == 0 or n_u == 0:
            rep.refusals.append(f"{cohort}: calibration refused, only one outcome class present "
                                f"(matched={n_m}, unmatched={n_u})")
            return Calibration(sufficiency="insufficient", n=n, threshold=self.calibration_min_n,
                               reason=f"one outcome class only (matched={n_m}, unmatched={n_u}); "
                                      f"nothing to discriminate")
        return Calibration(
            sufficiency="sufficient", n=n, threshold=self.calibration_min_n,
            mean_nci_matched=_mean([x for x, m in zip(nci, matched) if m]),
            mean_nci_unmatched=_mean([x for x, m in zip(nci, matched) if not m]),
            spearman_nci_vs_regret=spearman(nci, regret),
            n_matched=n_m, n_unmatched=n_u,
        )


def run(receipts: list, outcomes: list, **kw) -> dict:
    """Module-level convenience; the registry binds the class + `run` entrypoint."""
    return AccountantOperator(**kw).run(receipts, outcomes)


# ── self-test ───────────────────────────────────────────────────────────────

def _synthetic(n_receipts: int, n_closed: int, cohort: str, seed: int = 7):
    import random
    rnd = random.Random(seed)
    receipts, outcomes = [], []
    for i in range(n_receipts):
        rid = f"{cohort}-{i}"
        receipts.append({"receipt_id": rid, "cohort": cohort, "nci_score": rnd.randint(20, 90),
                         "horizon": rnd.choice(["TODAY", "WEEK", "QUARTER", "YEARS"]),
                         "mode": "QUICKMOVE", "drift_state": "ON_TRACK", "created_epoch": 1_700_000_000 + i})
        if i < n_closed:
            # regret loosely anti-correlated with nci so a real curve exists at large n
            nci = receipts[-1]["nci_score"]
            regret = max(0, min(10, round((100 - nci) / 10 + rnd.uniform(-1.5, 1.5))))
            outcomes.append({"receipt_id": rid, "matched": regret <= 4, "regret_score": regret,
                             "logged_at": "2026-01-01T00:00:00Z"})
    return receipts, outcomes


def self_test() -> int:
    fails = 0

    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {str(detail)[:120]}")
        fails += 0 if cond else 1

    print("self-test: arcs_accountant (Operator 19)")
    op = AccountantOperator()

    # 1. small n: refuses to draw a curve, reports n
    r, o = _synthetic(200, 3, "founder")
    rep = op.run(r, o)
    cal = rep["cohorts"]["founder"]["calibration"]
    check("n=3 -> sufficiency insufficient", rep["sufficiency"] == "insufficient" and cal["sufficiency"] == "insufficient", cal["reason"])
    check("n=3 reported verbatim", cal["n"] == 3 and rep["cohorts"]["founder"]["outcomes_logged"] == 3)
    check("no calibration figure leaked at n=3", cal["spearman_nci_vs_regret"] is None and cal["mean_nci_matched"] is None)
    check("closure rate = 3/200", rep["cohorts"]["founder"]["closure_rate"] == 0.015)
    check("refusal recorded", any("founder: calibration refused" in x for x in rep["refusals"]))

    # 2. large n: draws the curve
    r, o = _synthetic(200, 60, "external")
    rep = op.run(r, o)
    cal = rep["cohorts"]["external"]["calibration"]
    check("n=60 -> sufficient", cal["sufficiency"] == "sufficient" and rep["sufficiency"] == "sufficient", cal)
    check("n=60 spearman negative (nci vs regret)", cal["spearman_nci_vs_regret"] is not None and cal["spearman_nci_vs_regret"] < 0, cal["spearman_nci_vs_regret"])

    # 3. one outcome class only at large n: refuses
    r, o = _synthetic(100, 40, "founder")
    for x in o:
        x["matched"] = True
    rep = op.run(r, o)
    check("one class only -> refused", rep["cohorts"]["founder"]["calibration"]["sufficiency"] == "insufficient",
          rep["cohorts"]["founder"]["calibration"]["reason"])

    # 4. missing fields are counted, never invented
    r = [{"receipt_id": "a", "cohort": "external"},                     # no nci, no horizon, no drift
         {"receipt_id": "b", "cohort": "external", "nci_score": 70, "horizon": "WEEK", "drift_state": "LANDED"}]
    o = [{"receipt_id": "a", "matched": True},                          # no regret_score
         {"receipt_id": "zzz", "matched": False, "regret_score": 5}]    # orphan
    rep = op.run(r, o)
    ex = rep["cohorts"]["external"]
    check("missing nci_score counted, not defaulted", ex["missing_fields"].get("nci_score") == 1 and ex["nci_scored"] == 1 and ex["mean_nci_all"] == 70.0, ex["missing_fields"])
    check("missing regret counted", ex["missing_fields"].get("outcome.regret_score") == 1 and ex["regret_scores"] == [])
    check("orphan outcome surfaced", rep["orphans"].get("outcomes_with_unknown_receipt") == ["zzz"])
    check("EXPIRED reported not_computed", ex["fate"]["EXPIRED"] == "not_computed")
    check("drift LANDED counted from receipt", ex["drift"]["LANDED"] == 1 and ex["drift"]["DRIFTING"] == 0)

    # 5. unstamped cohort -> unattributed, never folded in
    rep = op.run([{"receipt_id": "q", "nci_score": 50}], [])
    check("unstamped cohort -> unattributed", list(rep["cohorts"]) == ["unattributed"])

    # 6. output is JSON-serializable (bridge envelope)
    try:
        json.dumps(rep); check("report JSON-serializable", True)
    except Exception as e:
        check("report JSON-serializable", False, e)

    print("self-test:", "OK" if fails == 0 else f"{fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    print(__doc__)
