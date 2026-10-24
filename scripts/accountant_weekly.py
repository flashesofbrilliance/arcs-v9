#!/usr/bin/env python3
"""accountant_weekly.py: the weekly Operator 19 (Accountant) scoreboard. READ-ONLY on prod.

Wraps the two pieces that already exist; reimplements neither:
  operators/prod_receipt_to_accountant.py  EXPORT_SQL, load_rows, adapt (the faithful adapter)
  operators/arcs_accountant.py             AccountantOperator.run (the scoreboard)

How the export is taken (same path as the 2026-09-27 one-off run): the read-only EXPORT_SQL
runs through the Supabase connector's execute_sql against prod project xbbpiryokswwvcrcutge.
No DATABASE_URL, no psql/psycopg, no secret on disk or in CI: the connector holds the auth.
The export carries no decision text (outcome text as lengths) and no addresses (email sha256).

Modes
  --sql                 print LEAN_SQL (18 adapter columns, one JSON object) for execute_sql
  --sql-full            print the adapter's full EXPORT_SQL
  --ingest EXPORT.json  lean {cols, rows} object, or full rows (bare list or raw execute_sql text) -> _STATE/<date>-accountant-scoreboard.json
  --self-test           run the pipeline on the committed 2026-09-27 export and check it

The export file itself stays local (pass a scratch path); the scoreboard records its sha256
and row count so a later run can be matched to the exact rows it saw.
Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "operators"))
from prod_receipt_to_accountant import EXPORT_SQL, adapt, load_rows  # noqa: E402
from arcs_accountant import AccountantOperator  # noqa: E402

SCHEMA = "arcs-accountant-report/v1"
# The columns the adapter actually reads (grep of row.get in adapt_receipt/adapt_outcome/
# cohort_of), same joins and expressions as EXPORT_SQL, packed as one {cols, rows} object so
# the weekly agent transcribes ~1/3 of the full export. Adapter output is identical.
LEAN_COLS = ["id", "receiptId", "userId", "user_email_sha256", "created_epoch", "nciScore", "horizon",
             "window", "stakes", "mode", "driftState", "yState", "outcome_id", "outcome_matched",
             "outcome_regret_score", "outcome_logged_at", "outcome_what_len", "outcome_learning_len",
             "provenance", "outcome_synthetic"]
LEAN_SQL = """
select json_build_object('cols', json_build_array(%s),
  'rows', json_agg(json_build_array(r.id, r."receiptId", r."userId",
    encode(sha256(convert_to(lower(u.email),'UTF8')),'hex'), extract(epoch from r."createdAt")::bigint,
    r."nciScore", r.horizon, r.window, r.stakes, r.mode, r."driftState", r."yState",
    o.id, o.matched, o."regretScore", o."loggedAt", length(o.what), length(o.learning), r.provenance, o.synthetic)
    order by r."createdAt")) as export
from "Receipt" r
left join "User" u on u.id = r."userId"
left join "Outcome" o on o."receiptId" = r.id
""".strip() % ", ".join("'%s'" % c for c in LEAN_COLS)

# Keys that would mean the export leaked text or addresses; refuse rather than write.
FORBIDDEN_KEYS = {"email", "user_email", "what", "learning", "question", "outcome_what", "outcome_learning"}


def read_export(path: Path) -> list:
    """Full export (list of row dicts, bare or MCP-wrapped) or the lean {cols, rows} object."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return load_rows(str(path))
    if isinstance(data, dict) and isinstance(data.get("result"), str):
        # execute_sql envelope (what the harness saves when the result is too large to inline):
        # the rows sit inside the <untrusted-data-...> boundary; parse only that span as data.
        body = data["result"]
        end = body.index("</untrusted-data-")  # the preamble names the tag too; anchor on the close
        i = body.index(">", body.rindex("<untrusted-data-", 0, end)) + 1
        data = json.loads(body[i:end])
    if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict) and "export" in data[0]:
        data = data[0]["export"]  # execute_sql returns [{"export": {...}}]
    if isinstance(data, dict) and "cols" in data:
        return [dict(zip(data["cols"], r)) for r in data["rows"]]
    return data


def build(rows: list, export_name: str, export_sha256: str) -> dict:
    leaked = FORBIDDEN_KEYS & {k for r in rows for k in r}
    if leaked:
        sys.exit(f"refusing: export carries raw fields {sorted(leaked)}; re-run EXPORT_SQL unchanged")
    adapted = adapt(rows)
    rep = AccountantOperator().run(**adapted)
    rep["synthetic_excluded"] = adapted.get("synthetic_excluded", 0)
    rep["provenance"] = {
        "source_export": export_name,
        "source_export_sha256": export_sha256,
        "source_query": "read-only SELECT on prod Receipt LEFT JOIN User LEFT JOIN Outcome "
                        "(EXPORT_SQL in operators/prod_receipt_to_accountant.py), via Supabase execute_sql",
        "adapter": "operators/prod_receipt_to_accountant.py",
        "runner": "scripts/accountant_weekly.py",
        "cohort_rule": "founder = sha256(email) in FOUNDER_SHA256; external = other userId; anonymous = null userId",
        "rows_in": len(rows),
    }
    return rep


def summary(rep: dict) -> str:
    t = rep["totals"]
    lines = [f"receipts={t['receipts']} outcomes={t['outcomes']} sufficiency={rep['sufficiency']} "
             f"synthetic_excluded={rep.get('synthetic_excluded', 0)} (plumbing probes, never scored)"]
    for name, c in rep["cohorts"].items():
        cal = c["calibration"]
        lines.append(f"  {name:9} receipts={c['receipts']:4} closed={c['outcomes_logged']:3} "
                     f"closure={c['closure_rate']} calibration={cal['sufficiency']} (n={cal['n']}/{cal['threshold']})")
    return "\n".join(lines)


def self_test() -> int:
    src = REPO / "_STATE" / "2026-09-27-receipt-outcome-export.json"
    raw = src.read_bytes()
    rows = read_export(src)
    rep = build(rows, src.name, hashlib.sha256(raw).hexdigest())
    assert rep["schema"] == SCHEMA, rep["schema"]
    assert rep["totals"]["receipts"] == 254, rep["totals"]
    assert rep["totals"]["closed_by_cohort"] == {"anonymous": 0, "founder": 3, "external": 0}
    assert rep["sufficiency"] == "insufficient"
    # lean shape must adapt identically to the full shape
    lean = {"cols": LEAN_COLS, "rows": [[r.get(c) for c in LEAN_COLS] for r in rows]}
    assert adapt([dict(zip(lean["cols"], r)) for r in lean["rows"]]) == adapt(rows), "lean != full"
    try:
        build([{"id": "x", "email": "a@b.c"}], "bad", "0")
    except SystemExit:
        pass
    else:
        raise AssertionError("raw email in export was not refused")
    print("accountant_weekly self-test OK (254 rows, closed 0/3/0, insufficient, lean == full, raw-field guard fires)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sql", action="store_true", help="print the lean export query (default path)")
    g.add_argument("--sql-full", action="store_true", help="print the adapter's full EXPORT_SQL")
    g.add_argument("--ingest", metavar="EXPORT.json")
    g.add_argument("--self-test", action="store_true")
    ap.add_argument("--date", help="report date YYYY-MM-DD; default today (local)")
    ap.add_argument("--out", help="default _STATE/<date>-accountant-scoreboard.json")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.sql or a.sql_full:
        print(EXPORT_SQL if a.sql_full else LEAN_SQL)
        return 0
    src = Path(a.ingest)
    rep = build(read_export(src), src.name, hashlib.sha256(src.read_bytes()).hexdigest())
    date = a.date or dt.date.today().isoformat()
    out = Path(a.out) if a.out else REPO / "_STATE" / f"{date}-accountant-scoreboard.json"
    out.write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(REPO) if out.is_relative_to(REPO) else out}")
    print(summary(rep))
    try:  # decision-receipt cohort (section 4k bridge); needs the gitignored universe export
        import decision_receipt_to_accountant as drta
        print(drta.summary(drta.report(drta.roq.load_receipts(), drta.roq.load_ledger())))
    except SystemExit as e:
        print(f"  decisions  skipped: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
