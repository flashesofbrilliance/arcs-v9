# Jack and Jill roles, graded (2026-11-04)

Source: two Jack and Jill emails (2026-11-03, 2026-11-04). Job descriptions were read from each
company's own board (Ashby, General Catalyst) on 2026-11-04, not from Jack's summaries. OnCorps
returned 403 to an automated read, so its JD is unread. Tags follow H2' and the Fonzi slice amendment
in `hypothesis-ledger.md`: `channel=cold` (Jack and Jill sources the role; it does not introduce you),
`intermediary=direct`, `warm_path=0`, `req_reality=2` (JD posted).

Hard screen used (from the Fonzi profile and memory): base at or above $220K, NYC metro or remote,
no sponsorship needed, no relocation. A role fails only on a stated requirement that cannot be met or
argued, not on a stretch.

## Ranking

| # | Role | Arm | Hard screen | Verdict | Time to apply |
|---|---|---|---|---|---|
| 1 | GovWell, AI Product Engineer | C | Pass ($200K to $300K, NYC 3 days) | PURSUE, bundle | about 2 hours |
| 2 | Cursor, Forward Deployed Strategist (Remote) | B | Pass on stated terms; comp not posted | PURSUE, bundle | about 2 hours |
| 3 | Lunos, Founding Forward Deployed Engineer | A | Unknown: comp not posted, pre-seed | HOLD: ask comp first | 10 minutes to ask |
| 4 | OnCorps, Forward Deployed Engineer | A | Unknown: JD unread | HOLD: paste the JD | 5 minutes to paste |
| - | GovWell, Forward Deployed Software Engineer | A | Pass on comp; years gate (see below) | Do not apply in parallel with #1 | - |

Sources: JDs saved at `_ARTIFACTS/forge-govwell-ai-product-engineer/jd-full.txt` and
`_ARTIFACTS/forge-cursor-forward-deployed-strategist/jd-full.txt`; Lunos read from the General Catalyst board
(jobs.generalcatalyst.com, req R9). Bundle cost basis: `_ARTIFACTS/forge-aircall-fde/cost.json` (about 240K tokens).

Time is the binding budget. Two bundles at about 2 hours each is the cap for this batch. Lunos and
OnCorps get a 10-minute check each before any bundle spend.

## 1. GovWell, AI Product Engineer

- **Need to have (from the JD):** LLM work beyond prompt wrappers (RAG, eval harness, hallucination
  control) in a system people depended on; full-stack shipping (UI, API, retrieval); product judgment;
  NYC office 3+ days a week. **Met:** ARCS has an eval layer, retrieval and context management, and
  ships on TypeScript and Postgres; NYC hybrid fits.
- **Nice to have:** RedwoodJS, GraphQL, AWS; multi-model routing (theirs is Gemini and OpenAI). Your
  model-tier routing work maps; the stack names are a learning curve, not a gate.
- **Insurmountable:** none stated. The Ashby posting has no years-of-experience line (one aggregator
  copy says 5+ years of software engineering; the source does not).
- **Objections and answers:**
  - "Your engineering is one self-founded product, not a team codebase." Answer with the eval harness
    and the routing between deterministic logic and the model, and with production usage you measured.
  - "Gemini and OpenAI shop, you build on Claude." Answer: the routing and eval layer is model-agnostic
    in design; say so carefully, since ARCS runs on Claude today.
  - "Posted 2026-02-24, open nine months." Either hard to fill (good for you) or stale. It was still
    listed on GovWell's Ashby board on 2026-11-04; check again on the day you apply.
- **Scenarios:** Best: CTO screen in 2 weeks off the eval-harness story, a loop by early December.
  Base: 21-day silence (most cold sends). Worst: screen, then a coding exercise in RedwoodJS where
  the lack of a team-codebase history shows.
- **Why not the GovWell FDE role too:** it requires "5+ years as a full-stack or forward deployed
  engineer in a production SaaS environment." That is a hard line you would have to argue. Two
  applications to one small company also split the signal. Apply to one.

## 2. Cursor, Forward Deployed Strategist (Remote, US)

- **Need to have:** 6+ years in solutions architecture, deployment strategy, technical consulting or an
  engagement-manager seat owning scoping and delivery with a technical team; enough agentic-coding and
  LLM depth to hold your own with senior engineers; hands-on at the configuration layer; reads Python
  and JS/TS; executive presence. **Met or arguable:** Grayscale product lead, the Mañana advisory
  engagements, and ARCS cover scoping, delivery and C-suite work; you write TS and Python.
- **Source:** `_ARTIFACTS/forge-cursor-forward-deployed-strategist/jd-full.txt` (Ashby posting
  6960dfef, published 2026-07-23). Resume claims trace to that bundle's `evidence.jsonl`.
- **Nice to have:** domain depth in financial services, insurance, telecom, high-tech, healthcare or
  semiconductors. Grayscale is the financial-services proof.
- **Comp:** not posted. Levels.fyi (2026-11-04) shows a Cursor software engineer median of $950K total
  comp and no strategist data, so the $220K base floor is very unlikely to bind. Confirm in the screen.
- **Insurmountable:** none on the stated terms. The years line is the stretch: your seats were product
  and advisory, not titled solutions architecture. Map them in the resume, do not relabel them.
- **Verify before applying:** the Cursor-hosted posting's company section describes SpaceX and SpaceXSI
  (Grok). Either Cursor now sits inside that company or the posting carries the wrong template.
  Confirm which, and decide if that changes your interest.
- **Objections and answers:**
  - "No Cursor-scale enterprise deployments." Answer with scoped, time-boxed engagements and their
    outcomes (Grayscale release cycle cut 35%; WTA's first data partnerships, $850K+ year one).
  - "Stampede role at a prestige company." Expected; it is a cold shot at the lowest odds of the batch.
- **Scenarios:** Best: recruiter screen, then a case on scoping a customer deployment, which is your
  strongest format. Base: silence (high applicant volume). Worst: screen fails on the titled-years filter.

## 3. Lunos, Founding Forward Deployed Engineer (HOLD)

- Requires production third-party API integrations (OAuth, sync, rate limits, idempotency, write-back),
  strong TypeScript and SQL, and careful handling of financial data. Your Sugar/Zapier work was in a
  sandbox, so the production-integration line is a real gap.
- Comp is not posted; a $5M pre-seed founding role often pays base below $220K plus equity. That would
  fail your floor. **One email to ask the band before any bundle.**

## 4. OnCorps, Forward Deployed Engineer (HOLD)

- JD not read (403 on the only copy found). Paste it from the Jack and Jill dashboard and it gets graded
  the same way. Financial-services domain matches Grayscale.

## Sources checked on 2026-11-04

- Ashby public boards: GovWell and Cursor found (both roles live). Lunos and OnCorps are not on Ashby.
- Greenhouse and Lever public boards: none of the four companies found under the obvious slugs
  (`oncorps`, `oncorpsai`, `oncorps-ai`, `lunos`, `lunosai`, `lunos-ai`).
- The jobs pipeline (`scripts/jobs_sources.mjs`, Greenhouse + Lever + Ashby adapters) does not index any
  of the four: none appear in `employer-index/index.json`. Jack and Jill surfaced roles the board missed.
- Levels.fyi robots.txt: `ClaudeBot` and `anthropic-ai` may read only /about, /blog, /offerings,
  /api-access, /2025 and /llms.txt; `Claude-User` (a fetch a person asks for) may read everything. So a
  one-off lookup on request is allowed, and a recurring Levels.fyi scrape adapter is not.
