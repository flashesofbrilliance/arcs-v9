#!/usr/bin/env python3
"""provenance_candidates.py: the owner's untagged receipts, listed for a one-pass tag. READ-ONLY.

Receipt.provenance ("real" | "test" | null) is set by the owner only; never guessed
(prisma/schema.prisma). The Accountant (operators/arcs_accountant.py) splits cohorts on it
through operators/prod_receipt_to_accountant.py, so every null row sits in the legacy
founder/external/anonymous split instead of the real or test cohort. Measured 2026-10-06 in
prod (Supabase project xbbpiryokswwvcrcutge): real 0, test 189, null 78 of 267.

This script lists the owner's untagged receipts (createdAt, mode, stakes, horizon, status,
outcome, link) so they can be tagged in one pass: the Provenance control on /receipt/<id>,
or POST /api/receipts/<id>/provenance with {"provenance": "real" | "test"}. It tags nothing
and writes nothing.

Modes
  --sql [--with-question]   print the read-only query. Run it through the Supabase connector's
                            execute_sql against prod (no DATABASE_URL, no psql, no secret on
                            disk: the connector holds the auth, same as accountant_weekly.py),
                            save the rows, then --ingest them. Decision text stays out of the
                            export unless --with-question adds left(decision, 80).
  --ingest ROWS.json        rows from execute_sql (bare list, {cols, rows}, or a saved tool-result
                            envelope) -> the candidates table on stdout
  --sqlite PATH             dev only: read a local Prisma SQLite db (dev.db) directly
  --self-test               prove the listing on a fixture

Options
  --email E     owner address; default is the founder address the Accountant adapter already
                keys on (operators/prod_receipt_to_accountant.py FOUNDER_EMAILS)
  --base URL    link base for the receipt page; default https://app.arcs.care
  --json        emit {summary, candidates} as JSON instead of the table
  --all         list tagged rows too (the table then carries a provenance column)

Stdlib only. Exit 0 always on a successful read, even when there is nothing to tag.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

OWNER_EMAIL_DEFAULT = "zach.harris@gmail.com"
BASE_DEFAULT = "https://app.arcs.care"
TAGS = ("real", "test")

# One row per receipt the owner holds. Tagged rows ride along so the summary can count them;
# the candidates are the null-provenance subset. No decision text unless asked for.
SQL_PG = """
select r.id, r."receiptId" as dewy_id, r."createdAt" as created_at,
       r.mode, r.stakes, r.horizon, r.status, r.provenance,
       (o.id is not null) as has_outcome, coalesce(o.synthetic, false) as outcome_synthetic{question}
from "Receipt" r
join "User" u on u.id = r."userId"
left join "Outcome" o on o."receiptId" = r.id
where lower(u.email) = lower('{email}')
order by r."createdAt"
"""

SQL_SQLITE = """
select r.id, r."receiptId" as dewy_id, r."createdAt" as created_at,
       r.mode, r.stakes, r.horizon, r.status, r.provenance,
       (o.id is not null) as has_outcome, coalesce(o.synthetic, 0) as outcome_synthetic{question}
from "Receipt" r
join "User" u on u.id = r."userId"
left join "Outcome" o on o."receiptId" = r.id
where lower(u.email) = lower(?)
order by r."createdAt"
"""

WRITE_VERBS = re.compile(r"\b(update|insert|delete|drop|alter|truncate|create|grant)\b", re.I)


def sql_for(email: str, with_question: bool = False, dialect: str = "pg") -> str:
    q = ',\n       substr(r.decision, 1, 80) as question' if with_question else ""
    if dialect == "sqlite":
        return SQL_SQLITE.format(question=q)
    return SQL_PG.format(question=q, email=email.replace("'", "''"))


def load_rows(path: str) -> list:
    """Bare list, lean {cols, rows}, or a saved execute_sql tool-result envelope."""
    raw = Path(path).read_text(encoding="utf-8")
    try:
        env = json.loads(raw)
    except ValueError:
        env = None
    if isinstance(env, list):
        return env
    if isinstance(env, dict):
        if "cols" in env and "rows" in env:
            return [dict(zip(env["cols"], r)) for r in env["rows"]]
        if "result" in env:
            raw = env["result"] if isinstance(env["result"], str) else json.dumps(env["result"])
    i, j = raw.find("[{"), raw.rfind("}]") + 2
    if i < 0 or j < 2:
        sys.exit(f"{path}: no JSON row array found")
    return json.loads(raw[i:j])


def read_sqlite(path: str, email: str, with_question: bool) -> list:
    uri = f"file:{Path(path).resolve()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute(sql_for(email, with_question, dialect="sqlite"), (email,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        con.close()


def _day(v) -> str:
    if v is None:
        return "?"
    s = str(v)
    if s.isdigit():  # SQLite stores Prisma DateTime as epoch milliseconds
        import datetime as dt
        ms = int(s)
        return dt.datetime.fromtimestamp(ms / 1000 if ms > 10_000_000_000 else ms, dt.timezone.utc).strftime("%Y-%m-%d")
    return s[:10]


def _truthy(v) -> bool:
    return v in (True, 1, "1", "t", "true", "True")


def candidates(rows: list, base: str = BASE_DEFAULT, include_tagged: bool = False) -> dict:
    """Pure: never mutates rows, never tags. Returns {summary, candidates}."""
    summary = {"owner_receipts": len(rows), "real": 0, "test": 0, "untagged": 0, "untagged_with_outcome": 0}
    out = []
    for r in rows:
        prov = r.get("provenance")
        if prov in TAGS:
            summary[prov] += 1
        else:
            summary["untagged"] += 1
            if _truthy(r.get("has_outcome")):
                summary["untagged_with_outcome"] += 1
        if prov in TAGS and not include_tagged:
            continue
        row = {
            "id": r.get("id"),
            "dewy_id": r.get("dewy_id"),
            "created": _day(r.get("created_at")),
            "mode": r.get("mode") or "?",
            "stakes": r.get("stakes") or "?",
            "horizon": r.get("horizon") or "?",
            "status": r.get("status") or "?",
            "outcome": ("synthetic" if _truthy(r.get("outcome_synthetic")) else "logged") if _truthy(r.get("has_outcome")) else "-",
            "provenance": prov if prov in TAGS else None,
            "link": f"{base.rstrip('/')}/receipt/{r.get('id')}",
        }
        if "question" in r and r["question"] is not None:
            row["question"] = str(r["question"]).replace("\n", " ").strip()
        out.append(row)
    return {"summary": summary, "candidates": out}


def render(rep: dict, include_tagged: bool = False) -> str:
    s = rep["summary"]
    head = (f"owner receipts {s['owner_receipts']} · real {s['real']} · test {s['test']} · "
            f"untagged {s['untagged']} ({s['untagged_with_outcome']} with an outcome)")
    rows = rep["candidates"]
    if not rows:
        return head + "\nnothing to tag."
    cols = ["#", "created", "mode", "stakes", "horizon", "status", "outcome"]
    if include_tagged:
        cols.append("provenance")
    if any("question" in r for r in rows):
        cols.append("question")
    cols.append("link")
    table = []
    for i, r in enumerate(rows, 1):
        table.append([str(i)] + [str(r.get(c) if r.get(c) is not None else ("untagged" if c == "provenance" else "")) for c in cols[1:]])
    widths = [max(len(c), *(len(t[k]) for t in table)) for k, c in enumerate(cols)]
    lines = [head, "", "  ".join(c.ljust(w) for c, w in zip(cols, widths))]
    lines.append("  ".join("-" * w for w in widths))
    for t in table:
        lines.append("  ".join(v.ljust(w) for v, w in zip(t, widths)))
    lines.append("")
    lines.append("tag each at its link (Provenance control) or POST /api/receipts/<id>/provenance {\"provenance\": \"real\"|\"test\"}. Nothing here tags for you.")
    return "\n".join(lines)


FIXTURE = [
    {"id": "c1", "dewy_id": "ARCS-ORIENT-1", "created_at": "2026-09-01T10:00:00+00:00", "mode": "QUICKMOVE", "stakes": "LOW",
     "horizon": "THIS_WEEK", "status": "OPEN", "provenance": None, "has_outcome": False, "outcome_synthetic": False},
    {"id": "c2", "dewy_id": None, "created_at": "2026-09-02T10:00:00+00:00", "mode": "PLAN", "stakes": "HIGH",
     "horizon": "THIS_QUARTER", "status": "LOGGED", "provenance": "test", "has_outcome": True, "outcome_synthetic": True},
    {"id": "c3", "dewy_id": "ARCS-ORIENT-3", "created_at": 1788516000000, "mode": "COURT", "stakes": "CRITICAL",
     "horizon": "1-3Y", "status": "LOGGED", "provenance": None, "has_outcome": 1, "outcome_synthetic": 0},
    {"id": "c4", "dewy_id": None, "created_at": "2026-09-04T10:00:00+00:00", "mode": "PLAN", "stakes": "MEDIUM",
     "horizon": "TODAY", "status": "OPEN", "provenance": "real", "has_outcome": "f", "outcome_synthetic": "f"},
]


def self_test() -> int:
    fails = 0

    def check(name, ok, detail=""):
        nonlocal fails
        print(f"  {'ok ' if ok else 'FAIL'} {name}{(' - ' + detail) if detail and not ok else ''}")
        if not ok:
            fails += 1

    snapshot = json.dumps(FIXTURE, sort_keys=True)
    rep = candidates(FIXTURE)
    check("input never mutated", json.dumps(FIXTURE, sort_keys=True) == snapshot)
    check("summary counts", rep["summary"] == {"owner_receipts": 4, "real": 1, "test": 1, "untagged": 2, "untagged_with_outcome": 1}, str(rep["summary"]))
    ids = [c["id"] for c in rep["candidates"]]
    check("only untagged rows listed, input order kept", ids == ["c1", "c3"], str(ids))
    c3 = rep["candidates"][1]
    check("epoch-ms createdAt renders as a day", c3["created"] == "2026-09-04", c3["created"])
    check("logged outcome flagged", c3["outcome"] == "logged", c3["outcome"])
    check("link points at the receipt page", rep["candidates"][0]["link"] == "https://app.arcs.care/receipt/c1")
    check("no question column unless exported", all("question" not in c for c in rep["candidates"]))
    rep_all = candidates(FIXTURE, include_tagged=True)
    check("--all lists tagged rows with their tag", [c["provenance"] for c in rep_all["candidates"]] == [None, "test", None, "real"])
    check("synthetic outcome named as such", rep_all["candidates"][1]["outcome"] == "synthetic")
    empty = candidates([r for r in FIXTURE if r["provenance"] in TAGS])
    check("nothing to tag renders plainly", render(empty).endswith("nothing to tag."))
    text = render(rep)
    check("table carries both candidates", "c1" in text and "c3" in text and "c2" not in text)
    for dialect in ("pg", "sqlite"):
        q = sql_for("o'neil@example.com", True, dialect)
        check(f"{dialect} sql is read-only", not WRITE_VERBS.search(q), q)
        check(f"{dialect} sql keys on provenance + outcome", "provenance" in q and "outcome_synthetic" in q)
    check("pg sql escapes a quote in the address", "o''neil" in sql_for("o'neil@example.com"))
    check("default sql carries no decision text", "decision" not in sql_for("x@y.z"))
    check("--with-question adds a capped slice", "substr(r.decision, 1, 80)" in sql_for("x@y.z", True))
    # envelope ingest: a saved execute_sql tool result wrapping the same rows
    tmp = Path(__file__).resolve().parent.parent / "_STATE" / ".provenance_candidates_selftest.json"
    try:
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps({"result": "Rows:\n" + json.dumps(FIXTURE) + "\n"}), encoding="utf-8")
        check("tool-result envelope ingests", [r["id"] for r in load_rows(str(tmp))] == ["c1", "c2", "c3", "c4"])
        tmp.write_text(json.dumps({"cols": ["id", "provenance"], "rows": [["z", None]]}), encoding="utf-8")
        check("lean {cols, rows} ingests", load_rows(str(tmp)) == [{"id": "z", "provenance": None}])
    finally:
        if tmp.exists():
            tmp.unlink()
    print("self-test:", "PASS" if fails == 0 else f"FAIL ({fails})")
    return 0 if fails == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sql", action="store_true")
    g.add_argument("--ingest", metavar="ROWS.json")
    g.add_argument("--sqlite", metavar="PATH")
    g.add_argument("--self-test", action="store_true")
    ap.add_argument("--email", default=OWNER_EMAIL_DEFAULT)
    ap.add_argument("--base", default=BASE_DEFAULT)
    ap.add_argument("--with-question", action="store_true", help="add left(decision, 80) to the export")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="list tagged rows too")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.sql:
        print(sql_for(a.email, a.with_question).strip())
        return 0
    rows = read_sqlite(a.sqlite, a.email, a.with_question) if a.sqlite else load_rows(a.ingest)
    rep = candidates(rows, base=a.base, include_tagged=a.all)
    print(json.dumps(rep, indent=2) if a.json else render(rep, include_tagged=a.all))
    return 0


if __name__ == "__main__":
    sys.exit(main())
