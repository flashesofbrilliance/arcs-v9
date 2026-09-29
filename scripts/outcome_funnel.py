#!/usr/bin/env python3
"""outcome_funnel.py: the Accountant's raw feed. READ-ONLY.

Reports the external decision funnel (receipts created -> horizon/review date
present -> debrief sent -> outcome logged -> closure rate), ALWAYS split
founder vs external vs anonymous. Founder rows are never blended into the
external figures (the 2/247 lesson: a founder-QA artifact read as a product
funnel for three months).

Ground truth is the Prisma-managed prod tables (Receipt, User, Outcome,
PrepSession). This script never writes to them.

Modes
  --sql                 print the canonical queries (run them via the Supabase
                        MCP execute_sql, or psql, against the prod project)
  --ingest RESULTS.json build the dated report from the query results, keyed
                        segments / external_users / horizon_y / globals /
                        fears_attribution (each = the JSON rows the query
                        returned), and write _STATE/outcome-funnel/<date>.json
  --run                 execute the queries directly (needs psycopg + a
                        DATABASE_URL env var; UNTESTED here: no local psql or
                        DATABASE_URL on the build machine). Then ingest.
  --self-test           prove the ingest arithmetic on a fixture

Founder identity is the explicit email below, not ADMIN_EMAILS (the health
route's operator split depends on a Vercel env value this script cannot read).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "_STATE" / "outcome-funnel"
FOUNDER_EMAIL = "zach.harris@gmail.com"

# Kill-clause fingerprints from public/good-fears.html. A compass question
# opened from a fear card carries the clause verbatim unless the visitor edits
# it, so this is attribution-by-text (stated limitation: an edited question
# breaks the match; the primary signal is external inflow at all, which was
# zero for 79 days on 2026-09-27).
FEARS_FINGERPRINTS = [
    "consequential decisions made by people falls below",
    "already met, by the example inside the same item",
    "published internal evaluations exceed released-model evaluations",
    "agent-to-agent transaction volume exceeds human-initiated volume",
    "deployed $100B into agents",
    "major networks block personal agents",
    "Chinese frontier models match US frontier models",
    "domestic control of all four",
    "depression prevalence is flat or falling ten years out",
    "incumbents lose more share than challengers",
    "an agent never gets around a stated guardrail",
]

SEG_CASE = (
    "CASE WHEN r.\"userId\" IS NULL THEN 'anonymous' "
    f"WHEN lower(u.email) = '{FOUNDER_EMAIL}' THEN 'founder' "
    "ELSE 'external' END"
)

QUERIES: dict[str, str] = {
    "segments": f"""
WITH r AS (
  SELECT r.*, o.id AS oid, o.matched, {SEG_CASE} AS seg
  FROM "Receipt" r LEFT JOIN "User" u ON u.id=r."userId" LEFT JOIN "Outcome" o ON o."receiptId"=r.id
)
SELECT seg, count(*) receipts, count(DISTINCT "userId") users,
 count(*) FILTER (WHERE horizon IS NOT NULL) with_horizon,
 count(*) FILTER (WHERE "reviewDate" IS NOT NULL) with_review_date,
 count(*) FILTER (WHERE "reminderDate" IS NOT NULL) with_reminder_date,
 count(*) FILTER (WHERE "debriefSentAt" IS NOT NULL) debrief_sent,
 count(*) FILTER (WHERE "debriefSentAt" IS NULL AND oid IS NULL AND "reminderDate" <= to_char(now(),'YYYY-MM-DD')) past_due_never_sent,
 count(*) FILTER (WHERE "debriefSentAt" IS NULL AND "reminderDate" > to_char(now(),'YYYY-MM-DD')) waiting_for_cron,
 count(oid) closed, count(oid) FILTER (WHERE matched) closed_matched, count(oid) FILTER (WHERE NOT matched) closed_drifted,
 min("createdAt")::date first_receipt, max("createdAt")::date last_receipt,
 count(*) FILTER (WHERE "createdAt" > now()-interval '30 days') last_30d,
 count(*) FILTER (WHERE "createdAt" > now()-interval '7 days') last_7d,
 count(*) FILTER (WHERE surface='EPHEMERAL_SAVE') ephemeral_saves,
 count(*) FILTER (WHERE "prepId" IS NOT NULL) with_prep
FROM r GROUP BY seg ORDER BY seg;
""",
    # Pseudonymized: no email, no id leaves the DB. Ordered by first receipt.
    "external_users": f"""
WITH ext AS (
  SELECT u.id uid, r."createdAt", r.horizon, r."yState", r."debriefSentAt", r.surface, r."prepId", o.id oid
  FROM "Receipt" r JOIN "User" u ON u.id=r."userId" LEFT JOIN "Outcome" o ON o."receiptId"=r.id
  WHERE lower(u.email) <> '{FOUNDER_EMAIL}'
), ux AS (SELECT uid, dense_rank() OVER (ORDER BY min("createdAt")) idx FROM ext GROUP BY uid)
SELECT 'ext-user-'||ux.idx AS user_pseudonym, count(*) receipts,
  min(e."createdAt")::date first_receipt, max(e."createdAt")::date last_receipt,
  count(*) FILTER (WHERE e."debriefSentAt" IS NOT NULL) debrief_sent,
  count(e.oid) closed,
  count(*) FILTER (WHERE e."prepId" IS NOT NULL) with_prep,
  string_agg(DISTINCT coalesce(e.horizon,'null'), ',') horizons,
  string_agg(DISTINCT e."yState", ',') y_states,
  string_agg(DISTINCT e.surface, ',') surfaces
FROM ext e JOIN ux ON ux.uid=e.uid GROUP BY ux.idx ORDER BY ux.idx;
""",
    "horizon_y": f"""
SELECT {SEG_CASE} seg, coalesce(r.horizon,'null') horizon, r."yState", count(*) n
FROM "Receipt" r LEFT JOIN "User" u ON u.id=r."userId"
GROUP BY 1,2,3 ORDER BY 1,2,3;
""",
    "globals": f"""
SELECT (SELECT count(*) FROM "User") users_total,
 (SELECT count(*) FROM "User" WHERE lower(email) <> '{FOUNDER_EMAIL}') users_external,
 (SELECT count(*) FROM "User" u WHERE lower(email) <> '{FOUNDER_EMAIL}' AND NOT EXISTS (SELECT 1 FROM "Receipt" r WHERE r."userId"=u.id)) users_external_zero_receipts,
 (SELECT count(*) FROM "User" WHERE "debriefOptIn") users_debrief_optin,
 (SELECT count(*) FROM "User" WHERE "firstDebriefSentAt" IS NOT NULL) users_first_debrief_sent,
 (SELECT count(*) FROM "PrepSession") prep_sessions,
 (SELECT count(*) FROM "Outcome") outcomes_total,
 (SELECT max("loggedAt")::date FROM "Outcome") last_outcome;
""",
    # Attribution for the fears-card compass link (see good.arcs.care/fears).
    "fears_attribution": f"""
SELECT {SEG_CASE} seg, count(*) n, min(r."createdAt")::date first_receipt
FROM "Receipt" r LEFT JOIN "User" u ON u.id=r."userId"
WHERE r."createdAt" >= '2026-09-27' AND (
  """ + " OR ".join(f"r.decision ILIKE '%{fp}%'" for fp in FEARS_FINGERPRINTS) + """
) GROUP BY 1 ORDER BY 1;
""",
}


def _n(v) -> int:
    return int(v) if v is not None else 0


def _rate(num: int, den: int) -> float | None:
    return round(num / den, 4) if den else None


def build_report(results: dict, today: str | None = None) -> dict:
    today = today or dt.date.today().isoformat()
    segs = {row["seg"]: row for row in results.get("segments", [])}
    out_segs = {}
    for name in ("founder", "external", "anonymous"):
        r = segs.get(name, {})
        rec = _n(r.get("receipts"))
        closed = _n(r.get("closed"))
        sent = _n(r.get("debrief_sent"))
        out_segs[name] = {
            "receipts": rec,
            "users": _n(r.get("users")),
            "with_horizon": _n(r.get("with_horizon")),
            "with_review_date": _n(r.get("with_review_date")),
            "with_reminder_date": _n(r.get("with_reminder_date")),
            "with_prep": _n(r.get("with_prep")),
            "ephemeral_saves": _n(r.get("ephemeral_saves")),
            "debrief_sent": sent,
            "past_due_never_sent": _n(r.get("past_due_never_sent")),
            "waiting_for_cron": _n(r.get("waiting_for_cron")),
            "closed": closed,
            "closed_matched": _n(r.get("closed_matched")),
            "closed_drifted": _n(r.get("closed_drifted")),
            "closure_rate": _rate(closed, rec),
            "closure_rate_of_debriefed": _rate(closed, sent),
            "first_receipt": r.get("first_receipt"),
            "last_receipt": r.get("last_receipt"),
            "last_30d": _n(r.get("last_30d")),
            "last_7d": _n(r.get("last_7d")),
        }
    ext_last = out_segs["external"]["last_receipt"]
    days_since_ext = None
    if ext_last:
        days_since_ext = (dt.date.fromisoformat(today) - dt.date.fromisoformat(ext_last)).days
    ext = out_segs["external"]
    stages = [
        ("visitors_on_good_arcs_care", None, "not instrumented: no pageview table, no analytics"),
        ("anonymous_compass_runs", None, "not persisted by design (trust contract: no auth = no write path)"),
        ("external_receipts_saved", ext["receipts"], None),
        ("external_with_horizon", ext["with_horizon"], None),
        ("external_debrief_sent", ext["debrief_sent"], None),
        ("external_outcomes_logged", ext["closed"], None),
    ]
    return {
        "generated": today,
        "source": "prod Supabase xbbpiryokswwvcrcutge, Prisma tables Receipt/User/Outcome/PrepSession, read-only",
        "founder_identity": FOUNDER_EMAIL,
        "queries": "python3 scripts/outcome_funnel.py --sql",
        "external_funnel": [
            {"stage": s, "n": n, **({"note": note} if note else {})} for s, n, note in stages
        ],
        "external_inflow": {
            "last_receipt": ext_last,
            "days_since_last_external_receipt": days_since_ext,
            "last_30d": ext["last_30d"],
            "last_7d": ext["last_7d"],
            "read": (
                "distribution gap: no external decision traffic, so no funnel exists to convert"
                if ext["last_30d"] == 0 else "external inflow present; funnel is measurable"
            ),
        },
        "segments": out_segs,
        "external_users": results.get("external_users", []),
        "horizon_by_y_state": results.get("horizon_y", []),
        "globals": (results.get("globals") or [{}])[0],
        "fears_attribution": results.get("fears_attribution", []),
        "calibration_usable": ext["closed"] >= 5 and ext["closed_matched"] > 0 and ext["closed_drifted"] > 0,
        "not_measured": [
            "debrief email opens/clicks (no tracking; Resend events not stored)",
            "visits to /debrief/[receiptId] (no server log table)",
            "anonymous compass runs (never persisted)",
            "whether ADMIN_EMAILS in prod equals the founder identity used here",
        ],
    }


def self_test() -> int:
    fixture = {
        "segments": [
            {"seg": "external", "receipts": 10, "users": 4, "debrief_sent": 6, "closed": 0,
             "closed_matched": 0, "closed_drifted": 0, "last_receipt": "2026-07-10", "last_30d": 0},
            {"seg": "founder", "receipts": 196, "users": 1, "debrief_sent": 135, "closed": 3,
             "closed_matched": 2, "closed_drifted": 1, "last_receipt": "2026-09-27", "last_30d": 7},
        ],
        "globals": [{"users_total": 7}],
    }
    rep = build_report(fixture, today="2026-09-27")
    assert rep["segments"]["external"]["closure_rate"] == 0.0
    assert rep["segments"]["founder"]["closure_rate"] == round(3 / 196, 4)
    assert rep["segments"]["founder"]["closure_rate_of_debriefed"] == round(3 / 135, 4)
    assert rep["segments"]["anonymous"]["receipts"] == 0 and rep["segments"]["anonymous"]["closure_rate"] is None
    assert rep["external_inflow"]["days_since_last_external_receipt"] == 79
    assert rep["external_inflow"]["read"].startswith("distribution gap")
    assert rep["calibration_usable"] is False
    # founder and external never blended
    assert rep["external_funnel"][2]["n"] == 10
    print("outcome_funnel self-test OK")
    return 0


def run_direct() -> dict:
    try:
        import psycopg  # type: ignore
    except ImportError as e:  # pragma: no cover
        sys.exit(f"--run needs psycopg ({e}); use --sql with the Supabase MCP, then --ingest")
    url = os.environ.get("DATABASE_URL") or sys.exit("--run needs DATABASE_URL")
    results = {}
    with psycopg.connect(url) as conn:  # pragma: no cover
        for k, q in QUERIES.items():
            with conn.cursor() as cur:
                cur.execute(q)
                cols = [d.name for d in cur.description]
                results[k] = [dict(zip(cols, (str(v) if isinstance(v, (dt.date, dt.datetime)) else v for v in row)))
                              for row in cur.fetchall()]
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sql", action="store_true")
    g.add_argument("--ingest", metavar="RESULTS.json")
    g.add_argument("--run", action="store_true")
    g.add_argument("--self-test", action="store_true")
    ap.add_argument("--date", help="report date (YYYY-MM-DD); default today")
    ap.add_argument("--out", help="output path; default _STATE/outcome-funnel/<date>.json")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.sql:
        for k, q in QUERIES.items():
            print(f"-- {k}\n{q.strip()}\n")
        return 0
    results = run_direct() if a.run else json.loads(Path(a.ingest).read_text())
    rep = build_report(results, today=a.date)
    out = Path(a.out) if a.out else OUT_DIR / f"{rep['generated']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=2) + "\n")
    ext = rep["segments"]["external"]
    fnd = rep["segments"]["founder"]
    print(f"wrote {out.relative_to(REPO) if out.is_relative_to(REPO) else out}")
    print(f"external: {ext['receipts']} receipts / {ext['users']} users / {ext['debrief_sent']} debriefed / {ext['closed']} closed "
          f"/ last {ext['last_receipt']} ({rep['external_inflow']['days_since_last_external_receipt']}d ago)")
    print(f"founder (reported separately): {fnd['receipts']} receipts / {fnd['debrief_sent']} debriefed / {fnd['closed']} closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
