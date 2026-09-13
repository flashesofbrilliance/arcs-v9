# Bridge employer-quality index (2026-09-11)

Employer set for the *bridge job* lane: established, less-CS-pure, NYC/hybrid/remote, parent- and
neurodiversity-friendly employers adopting AI. Built from published curated lists, resolved to
public ATS boards (the API is ground truth for a slug), filtered to Zach-shape senior+ roles, and
ingested to jobs.arcs.care as `source=bridge_scan` / `band=UNSCORED` (Thread 2 scores).

Tool: `scripts/bridge_index_scan.py` (probe / verify / pull / ingest; stdlib only).

## Sources (verbatim names, current editions; no invented names)

| file | edition | names | complete |
|---|---|---|---|
| `lists/builtin-nyc.json` | 2026 | 203 | PARTIAL |
| `lists/disabilityin.json (DEI)` | 2026 | 12 | PARTIAL |
| `lists/disabilityin.json (NDW roundtable)` | - | 42 | PARTIAL |
| `lists/fortune-100-best.json` | 2026 | 100 | yes |
| `lists/gptw-parents.json` | 2025 | 100 | yes |
| `lists/seramount-100-best.json` | 2026 | 7 | PARTIAL |

Partial lists are honest partials, not padded: Seramount publishes only a Top-10 press release
(7 names recovered from company self-announcements); Disability:IN 2026 top tier is behind a gated
report form (12 names via company press releases); Built In NYC pages paginate behind "Show more".

## Funnel

| stage | count |
|---|---|
| unique employer names across lists (`universe.json`) | 403 |
| resolved to a public GH/Ashby/Lever board (`ats-probe-cache.json`) | 151 |
| dropped as slug collisions after eyeball (`dropped-collisions.json`) | 18 |
| employers in index (`index.json`; incl. 8 prior bridge_scan employers) | 133 (84 Greenhouse / 39 Ashby / 10 Lever) |
| live reqs fetched | 7,593 |
| winnable after title/level/location filter (`reqs.jsonl`) | 578 across 84 employers |
| ingested to live board 2026-09-11 (new rows) | 578 |

Unresolved names (256; re-probed in full with `probe --retry-misses` on 2026-09-11, 0 recovered, so these are genuine no-public-board employers) are mostly Workday/SuccessFactors/iCIMS corporates (Fortune-100 /
GPTW-Parents heavy) and law/accounting firms. They are real employers on real lists but have no
public JSON board, so they are out of scope for this mechanism. A future thread can cover them via
Workday's `/wday/cxs/.../jobs` POST endpoint. List: see `unresolved.txt`.

## Filter (calibrated against the 75 rows already landed: reproduces 64/75; the 11 misses are all
spec exclusions: associate-level, research scientist, ML-eng IC, design, marketing, non-US remote)

- INCLUDE: AI/GenAI/LLM/agent · applied · forward-deployed · product manager/lead/director/mgmt ·
  transformation · innovation · solutions architect/engineer/consultant · strategy · ops/bizops ·
  business systems · platform · principal/staff · program/TPM · enablement · implementation ·
  chief of staff · data science · process improvement · head of / GM.
- LEVEL_EXCL: associate · junior · intern · specialist · coordinator · assistant · analyst I.
- HARD_EXCL (never): sales quota (AE/SDR/BDR) · recruiting/talent · design/UX · legal · clinical ·
  accounting/finance/payroll · procurement/supply chain · HR/people · marketing/content/PR ·
  devrel · admin · hourly/field · research scientist.
- SOFT_EXCL (overridable by strong shape): SWE/frontend/backend/SRE/data-eng/ML-eng · scientist ·
  analyst · customer support/success · tax. Pure SWE only survives with FDE / applied-AI / GenAI.
- Location: NYC-metro token, or remote/hybrid, or US-wide; any foreign marker (country, ISO prefix
  like `GB-`/`AU:`, foreign city in the title) requires an explicit US/NYC token.

`fit_hint` (0-10) on each req is an ORDERING heuristic only (FDE +5, AI +3, applied +2, product
+2, transformation/strategy +2, seniority +1, solutions +1, ops/platform +1). Real scoring is
Thread 2's rubric.

## Top 15 by fit-to-shape (fit_hint)

| fit | company | title | location |
|---|---|---|---|
| 10 | Snowflake | Forward Deployed Engineer, Applied AI | US-CA-Menlo Park; US-WA-Bellevue; Remote |
| 10 | Snowflake | Senior Forward Deployed Engineer, Applied AI | US-CA-Menlo Park; US-WA-Bellevue; Remote |
| 8 | Aledade | Senior Software Engineer II- (Forward Deployed AI) | Remote; Remote, United States |
| 8 | AvePoint | Forward Deployed Engineer - AI | Jersey City, NJ, United States |
| 8 | AvePoint | Forward Deployed Engineer - AI | New York, NY, USA |
| 8 | Ramp | Software Engineer, Forward Deployed AI Solutions | New York, NY (HQ); Remote |
| 8 | Snowflake | Senior Software Engineer - Cortex AI - FDE | US-CA-Menlo Park; Remote |
| 7 | Abridge AI | Forward Deployed Product Manager | SF Office; NYC Office; Remote |
| 7 | Upside | Staff Forward Deployed Engineer, GTM Platform | NYC; Remote |
| 6 | Datadog | Senior Platform Product Manager - AI SDLC Trusted Throughput | New York, New York, USA |
| 6 | Datadog | Senior Product Solutions Architect - AI Agent | Boston, Massachusetts, USA; Denver, Colorado, USA; New York, |
| 6 | Datadog | Staff Applied Scientist - Agentic Interfaces | New York, New York, USA |
| 6 | FanDuel | AI Strategy & Operations Senior Manager | New York City |
| 6 | Ironclad | Staff Product Manager, AI Data Experience | San Francisco; Remote |
| 6 | MongoDB | Staff Product Manager, AI Builder Experience | United States |

## Top employers by winnable reqs

Cloudflare (66), Datadog (43), Snowflake (43), Ramp (27), Affirm (22), Notion (20), Mercury (18), Oscar Health (18), Gusto (16), Justworks (15), MongoDB (13), Ironclad (11), Celonis (10), Adyen (9), Dropbox (9)

## Coordination notes

- jobid = `bridge-<slug>-<sha1(url)[:8]>` (same scheme as the first 75) so re-runs dedupe.
- `ingest` skips jobids already on the board: the API upsert overwrites band/composite, so a re-send
  would silently reset a row Thread 2 already scored. `--force` re-sends.
- Re-run cadence: `probe` is cached; `pull` + `ingest` are cheap (~1 min) and idempotent.
