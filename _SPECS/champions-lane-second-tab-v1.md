# Spec — Champions lane (second tab on the board) · v1 · DRAFT/YELLOW

**Intent (Zach, 2026-09-08):** a second tab beside the postings board that stack-ranks best→worst-fit
CHAMPIONS from Zach's own network scan, same UX as the roles/companies board, with an outreach bundle
per champion. Turns the static `champion-shortlist-v1` into a living, swipeable, re-rankable surface.

## Reuse, not net-new
Compose the existing jobs-board machinery (`src/app/jobs`, the swipe board): tiered stack-rank, the
**Weight Lab** live re-rank, swipe left/right, ATS/search/company filters, "Generate on swipe". The
champions tab is the same shell with a different rubric + data source.

## Rubric (Weight Lab dims) — from `champion-fit-heuristic`
Pre-contact (drive the rank): `crossover_recognition` (3), **`warm_path` (3, DOMINANT here — real
values from the scan, unlike postings where it's inert)**, `domain_fit` (2), `shape_over_title` (2),
`org_design_literacy` (1). On-call dims (`bet_on_person`, `advocacy_conversion`, `effortless_register`,
`relational_carrier`) are post-contact — captured as outcome after outreach, not in the initial rank.

## Data source (reusable)
`_STATE/job-search/champion-shortlist-v1.tsv` (84 rows) + the deterministic filter over
`~/Downloads/Complete_LinkedInDataExport_*.zip → Connections.csv` (see `champion-shortlist-v1-sourced`
memory). Each row tagged lane = **EXT-search** | **INT-basin** (the ADR-077 routing key). Re-run the
filter on each new quarterly export to refresh.

## Bundle on swipe (the ADR-077 pairing)
- **EXT-search →** the two-tier recruiter enablement (`recruithaus.arcs.care` pattern: open positioning
  + gated ammo), tuned to that recruiter's register.
- **INT-basin →** a founder-aimed forge (`blacksmith.arcs.care` pattern) for their company.
- Acceptance test captured as the swipe-right outcome: did they name the crossover rarity back
  unprompted/effortlessly (the Amy signal)?

## PII — already covered by the surface's OAuth gate (Zach, 2026-09-08 correction)
The tab holds **real names + LinkedIn URLs from Zach's private network**, but **the entire product
surface (app/jobs.arcs.care) is already OAuth-gated**, which satisfies the air-gap: no world-readable
static, no public exposure. So do **NOT** add a redundant second `/recoil`-style `ADMIN_EMAILS` gate —
the existing session gate is sufficient. Serve the champions data server-side behind the existing auth
(same as the rest of the board); just never emit it to a public/unauthenticated path or static file.
**Residual to confirm (not a blocker):** OAuth-gated = any signed-in user. If the board is ever
multi-tenant, scope the champions data to the owner (per-user), since it is Zach's private list, not
every authenticated user's. Single-tenant → no action needed. Standing exclusion: **Fanatics**.

## Falsifiers / done-when
- Done: gated tab renders the 84 stack-ranked by warm_path-weighted fit, Weight Lab re-ranks live,
  swipe-right generates the correct lane bundle, and no PII is reachable unauthenticated (verify the
  fail-closed gate before shipping).
- Falsifier: if the champion rank is indistinguishable from the postings rank (warm_path not actually
  dominating), the rubric wasn't re-weighted — fix before calling it a champions lane.

## Not in v1
On-call dim capture UI (post-contact scoring), enrichment refresh, network_scan 2nd-order signals.
Start from the tsv; add those only if the tab earns them.
