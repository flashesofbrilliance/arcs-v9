# Anthropic API spend audit (2026-10-06)

Measured without paid calls: prod DB counts (Supabase, last 30 days), `gh run list` for CI, prompt sizes from source.
Prices: Claude API list, per MTok in/out. Haiku 4.5 $1/$5 · Sonnet 5.5 $2/$10 · Opus 4.5/4.7/4.8 $5/$25 · Opus 4.1 $15/$75.

## Callers, ranked by estimated monthly cost

| # | Caller | Model | Volume (30d) | Est. size per call | Est. $/month before |
|---|---|---|---|---|---|
| 1 | CI security review (`security.yml`) | **opus-4-1** (action default; `claude-model` unset) | ~20 scans/day after the 10-05 path filter (82 runs on 10-06, ~25 real scans) | agentic: ~100k-300k in, ~5-15k out | **~$1,200-3,500** |
| 2 | `/api/jobs/score` | haiku-4-5 | 829 rows ≈ 70 calls | ~18k in, ~3.6k out | ~$2.50 |
| 3 | writer routes (cover letter, edit-from-seed) | sonnet-5-5 | not logged in DB (est. <30) | ~15k in, ~4-8k out | ~$2 |
| 4 | `/api/compass` COURT | sonnet-5-5 | 8 | ~3k in, ~6k out | ~$0.50 |
| 5 | `/api/brief` (brief + entity) | sonnet-5-5 | 21 (x2 calls) | ~2k in, ~1.5k out | ~$0.80 |
| 6 | compass QUICKMOVE/PLAN, tribune, annotations, health probes | haiku-4-5 | ~40 | small | <$0.30 |
| 7 | `/api/guide` | opus-4-5 | 0 (3 ever) | ~2k in, 3k out | ~$0 |
| 8 | scripts/ evals (slop_eval, brief_eval, deep_model_eval, network_scan, verb-eval judge) | various | manual, rare | | one-off, a few $ per run |

The 10-05 drain was item 1: ~120 scans/day on Opus 4.1. Product traffic is a rounding error next to it.

## Levers

| Lever | Change | Before | After (est.) | Status |
|---|---|---|---|---|
| CI model | `claude-model` = registry role `security` (opus-4-8, $5/$25) | ~$1,200-3,500 | **~$400-1,150 (-67%)** | **done in this PR** |
| CI context | `exclude-directories` for archive/static/generated trees | | further cut in agent read turns (unmeasured) | **done in this PR** |
| CI triggers | paths filter + once per PR + `security-review` label | 120/day | ~20/day | already shipped 10-05; gate still fails red on API errors |
| Prompt caching | see below | | | **not recommended at current volume** |
| Batch API | see below | | ~$1/month | **not recommended yet** |
| Haiku roles | see below | | | proposal, Zach approves per role |

Why opus-4-8 and not a 5.x model: Opus 5.5 / Sonnet 5.5 run a `cyber` refusal classifier, which a vulnerability review is
likely to trip. Opus 4.8 is a stronger reviewer than 4.1 at a third of the per-token price. A refusal or API error still
turns the job red (`scripts/security_review_gate.sh`). Check the first scan after merge: if it reviewed normally, the change holds.

## Prompt caching: measured, not added

Minimum cacheable prefix: Haiku 4.5 and Opus 4.5 **4096 tokens**, Sonnet 5.5 512.

| Prompt | Model | ~Tokens | Caches? |
|---|---|---|---|
| compass `SYSTEM` | haiku (QUICKMOVE/PLAN) | ~1.8k | **no**: existing marker is a silent no-op |
| compass `SYSTEM` | sonnet-5-5 (COURT) | ~1.8k | yes (marker already present) |
| tribune, jobs scorer, rescore-dims | haiku | <2k | **no**: existing markers are no-ops |
| `BRIEF_SYSTEM` | sonnet-5-5 | ~640 | could |
| `ENTITY_SYSTEM` | sonnet-5-5 | ~290 | no |
| `GUIDE_SYSTEM` | opus-4-5 | ~900 | no |

A cache write costs 1.25x and a read pays off only inside the 5-minute TTL. At 21 briefs and 8 COURT runs a month,
almost every request is a cold write, so adding markers would **raise** cost slightly. The Haiku markers are harmless
(no write happens below the minimum), so they stay. Revisit when any route sees more than one call per 5 minutes.
The one cheap verification left: one compass COURT call and a repeat within 5 minutes should show
`cache_read_input_tokens` of ~1.8k. That call is not made here (account credit is low).

## Batch API: not worth the code yet

The bulk paths (jobs score / rescore-dims) are HTTP routes the board calls and waits on. Batches take minutes to hours
and need a poller, which is a new background job. Saving 50% of ~$2.50/month is ~$1.25. The eval scripts run by hand a
few times a month. Revisit if jobs scoring passes ~10k rows/month or an eval becomes a scheduled job.

## Model-role proposals (not applied)

| Role | Now | Proposal | Saving | Quality risk |
|---|---|---|---|---|
| `scorer`, `fast` | haiku-4-5 | keep | none | already the cheapest tier |
| health probes (`/api/health`, `/api/jobs/model-health`) | haiku, max_tokens 1 | keep | ~0 | a probe of the real role's model is the point |
| `guide` | opus-4-5 ($5/$25) | sonnet-5-5 ($2/$10) | -60% per call, but 0 calls/30d | medium: longest structured output; needs an eval before switching |
| `max` (network_scan) | opus-4-7 | keep | manual script | judgment work |
| `deep`, `writer` | sonnet-5-5 | keep | | picked by eval 10-06; Haiku would visibly lower prose quality |

None of these moves the bill. The real lever is item 1.
