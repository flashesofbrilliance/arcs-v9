#!/usr/bin/env python3
"""prod_receipt_to_accountant — faithful adapter: prod Receipt LEFT JOIN Outcome rows ->
Operator 19 (Accountant) input. Sibling of prod_receipt_to_op20_seed.py; same doctrine:
map the REAL columns, never fabricate a field the row does not carry.

Input row shape (one row per Receipt, outcome columns null when no Outcome exists), as
produced by the read-only export query recorded in `EXPORT_SQL` below and saved under
_STATE/<date>-receipt-outcome-export.json. The export carries NO decision text: the
Outcome `what`/`learning` columns travel as lengths only, and the user email travels as a
sha256 so the cohort split is reproducible without shipping addresses.

Faithful mappings:
  receipt.receipt_id     <- id (the Prisma cuid; Outcome.receiptId joins on it)
  receipt.dewy_receipt_id<- receiptId (ARCS-ORIENT-... formatted id, may be null)
  receipt.cohort         <- founder  if user_email_sha256 == sha256(FOUNDER_EMAIL)
                            external if userId present and not founder
                            anonymous if userId is null (cannot be attributed)
  receipt.nci_score      <- nciScore
  receipt.horizon        <- horizon (schema canonical); falls back to legacy `window`
                            ONLY when horizon is null, and records which was used
  receipt.stakes/mode    <- stakes / mode
  receipt.drift_state    <- driftState (ON_TRACK | DRIFTING | LANDED | LOCKED)
  receipt.created_epoch  <- created_epoch
  outcome.matched        <- outcome_matched ; outcome.regret_score <- outcome_regret_score
  outcome.logged_at      <- outcome_logged_at

Usage:
  python3 prod_receipt_to_accountant.py <export.json> [--report out.json] [--adapted out.json]
Stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# The founder cohort is one account (the product's own QA loop). The address is already
# on record in _QUEUE/induced-backlog.jsonl (outcome-capture-rate-keel-gap); only its
# sha256 is compared here so the export can carry hashes, not addresses.
FOUNDER_EMAILS = ("zach.harris@gmail.com",)
FOUNDER_SHA256 = {hashlib.sha256(e.lower().encode("utf-8")).hexdigest() for e in FOUNDER_EMAILS}

EXPORT_SQL = """
select r.id, r."receiptId", r."userId",
       encode(sha256(convert_to(lower(u.email),'UTF8')),'hex') as user_email_sha256,
       r."createdAt", extract(epoch from r."createdAt")::bigint as created_epoch,
       r."nciScore", r."nciByLens", r.horizon, r.window, r.stakes, r.mode, r."doorClass",
       r."driftState", r."yState", r."yConviction", r."yPolarity", r.surface,
       r."validationState", r."yOverride", r."macroTags", r."clarityMode",
       r."renderResolution", r."promotedTo",
       o.id as outcome_id, o.matched as outcome_matched, o."regretScore" as outcome_regret_score,
       o."loggedAt" as outcome_logged_at, length(o.what) as outcome_what_len,
       length(o.learning) as outcome_learning_len
from "Receipt" r
left join "User" u on u.id = r."userId"
left join "Outcome" o on o."receiptId" = r.id
order by r."createdAt"
""".strip()


def cohort_of(row: dict) -> str:
    if not row.get("userId"):
        return "anonymous"
    sha = row.get("user_email_sha256")
    email = row.get("user_email")
    if (sha and sha in FOUNDER_SHA256) or (email and email.lower() in FOUNDER_EMAILS):
        return "founder"
    return "external"


def adapt_receipt(row: dict) -> dict:
    horizon, horizon_source = row.get("horizon"), "horizon"
    if not horizon and row.get("window"):
        horizon, horizon_source = row.get("window"), "window(legacy)"
    r = {
        "receipt_id": row.get("id"),
        "dewy_receipt_id": row.get("receiptId"),
        "cohort": cohort_of(row),
        "nci_score": row.get("nciScore"),
        "horizon": horizon,
        "horizon_source": horizon_source if horizon else None,
        "stakes": row.get("stakes"),
        "mode": row.get("mode"),
        "drift_state": row.get("driftState"),
        "y_state": row.get("yState"),
        "created_epoch": row.get("created_epoch"),
    }
    return r


def adapt_outcome(row: dict) -> dict | None:
    if row.get("outcome_id") is None:
        return None
    return {
        "receipt_id": row.get("id"),
        "outcome_id": row.get("outcome_id"),
        "matched": row.get("outcome_matched"),
        "regret_score": row.get("outcome_regret_score"),
        "logged_at": row.get("outcome_logged_at"),
        "what_len": row.get("outcome_what_len"),
        "learning_len": row.get("outcome_learning_len"),
    }


def adapt(rows: list) -> dict:
    receipts, outcomes = [], []
    for row in rows:
        receipts.append(adapt_receipt(row))
        o = adapt_outcome(row)
        if o:
            outcomes.append(o)
    return {"receipts": receipts, "outcomes": outcomes}


def load_rows(path: str) -> list:
    """Accept a raw JSON array or a saved MCP tool-result envelope (same as the op20 adapter)."""
    raw = Path(path).read_text(encoding="utf-8")
    try:
        env = json.loads(raw)
        if isinstance(env, dict) and "result" in env:
            raw = env["result"]
        elif isinstance(env, list):
            return env
    except (ValueError, TypeError):
        pass
    i, j = raw.find("[{"), raw.rfind("}]") + 2
    return json.loads(raw[i:j])


def main(argv: list) -> int:
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    rows = load_rows(argv[0])
    payload = adapt(rows)
    if "--adapted" in argv:
        out = argv[argv.index("--adapted") + 1]
        Path(out).write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"adapted {len(payload['receipts'])} receipts / {len(payload['outcomes'])} outcomes -> {out}")
    if "--report" in argv:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from arcs_accountant import AccountantOperator
        rep = AccountantOperator().run(**payload)
        rep["provenance"] = {
            "source_export": Path(argv[0]).name,
            "source_query": "read-only SELECT on prod Receipt LEFT JOIN User LEFT JOIN Outcome (EXPORT_SQL in operators/prod_receipt_to_accountant.py)",
            "adapter": "operators/prod_receipt_to_accountant.py",
            "cohort_rule": "founder = sha256(email) in FOUNDER_SHA256; external = other userId; anonymous = null userId",
            "rows_in": len(rows),
        }
        out = argv[argv.index("--report") + 1]
        Path(out).write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"report -> {out}  sufficiency={rep['sufficiency']}  closed_by_cohort={rep['totals']['closed_by_cohort']}")
    if "--adapted" not in argv and "--report" not in argv:
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
