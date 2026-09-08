# Reproducible DB audit — the last un-closed strand (2026-09-05)

**Why this exists.** Throughout the ARCS-on-ARCS session the production-DB claims (247 receipts,
189 founder, 2 outcomes, degeneracy) were verified *by Claude via Supabase MCP* but never captured
as a reproducible artifact — so they were "trust-me," the one strand `claims-skeptic` couldn't audit
(it lacks Supabase). This closes that gap the honest way: not independence-by-another-agent (no agent
has both DB access and context), but **reproducibility-by-anyone** — the exact SQL + results, so any
future session or human can re-run and falsify. Ran against project `xbbpiryokswwvcrcutge` (arcs_app),
read-only.

## Query 1 — core counts
```sql
select json_build_object(
 'receipts', (select count(*) from "Receipt"),
 'outcomes', (select count(*) from "Outcome"),
 'receipts_with_horizon', (select count(*) from "Receipt" where horizon is not null),
 'distinct_users', (select count(distinct "userId") from "Receipt"),
 'top_user_receipt_count', (select max(c) from (select count(*) c from "Receipt" group by "userId") s),
 'outcomes_matched_true', (select count(*) from "Outcome" where matched = true),
 'outcomes_with_regret', (select count(*) from "Outcome" where "regretScore" is not null)
) as audit;
```
Result: `receipts=247 · outcomes=2 · receipts_with_horizon=0 · distinct_users=5 · top_user_receipt_count=189 · outcomes_matched_true=2 · outcomes_with_regret=2`

## Query 2 — resolving the horizon discrepancy (window vs doorClass)
```sql
select json_build_object(
 'horizon_not_null', (select count(*) from "Receipt" where horizon is not null and horizon <> ''),
 'window_not_null', (select count(*) from "Receipt" where "window" is not null and "window" <> ''),
 'horizonLocked_true', (select count(*) from "Receipt" where "horizonLocked" = true),
 'doorClass_not_null', (select count(*) from "Receipt" where "doorClass" is not null and "doorClass" <> ''),
 'doorClass_oneway', (select count(*) from "Receipt" where "doorClass" ilike '%one%'),
 'doorClass_values', (select json_agg(row_to_json(t)) from (select "doorClass", count(*) c from "Receipt" group by "doorClass" order by c desc) t)
) as audit;
```
Result: `horizon_not_null=0 · window_not_null=247 · horizonLocked_true=0 · doorClass_not_null=247 · doorClass_oneway=88 · doorClass_values=[TWO_WAY:159, ONE_WAY:88]`

## Confirmed (load-bearing facts — GREEN, reproducible)
- **247 receipts** total.
- **189 from one user** (the founder dogfood — top_user_receipt_count); 5 distinct identified users; the rest anon (null userId).
- **2 outcomes**, BOTH matched=true AND regret-scored — i.e. both founder-self-graded. **~0 externally-validated.** The keel (outcome-capture RATE) holds: 2/247.
- **247/247 have a `window`**; **88 ONE_WAY / 159 TWO_WAY** `doorClass`.

## Correction booked (deceipt #14)
The session's prior phrase **"247/247 horizon, 88 one-way"** was a **field mislabel**:
- The 247/247 field is **`window`**, not `horizon`.
- `horizon` (text) is **all-NULL (0/247)** — a genuinely unused/degenerate column; `horizonLocked` is all-false too.
- The 88 one-way count is **`doorClass`** (correct number, wrong field name attached to it earlier).
Numbers intact; the label was wrong. Corrected in snapshot.json + pickup-prompt this commit.

## Reproducibility = the closure
The gap was never "Claude ran it" — it was "no re-runnable artifact." Anyone with read access to
the project can paste the two queries above and get these exact numbers (barring new writes). That is
the falsifiable close: trust-me → re-run-me.
