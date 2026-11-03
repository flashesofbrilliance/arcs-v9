# The journey first, then the first product: decision page (2026-11-03)

Status: PROPOSED, waiting on Zach's yes or no on five items (bottom). Nothing was built, sent or published to make this page.

Prior art: `_PATTERNS/2026-07-13-frontend-monetization-queue.md` (July ranking), backlog rows `agent-receipts-audit-offer` (DONE) and
`agent-receipts-audit-first-conversion` (HOLDING, its one dependency is now DONE), memories on free-to-hold / metered-to-fire,
refusal to overclaim, cut not add, and the product-marketing legibility gap.

## 1. The journey, as it runs today

The test is WORLD.md's Myst rule: the world teaches you how to read it, with no tour. Proposed stages: **arrive** at the compass,
**navigate** (pick up instruments, travel by the HUD), **pause** (conscious or incubating), **rest** in the reading room, **return** from
a seed. Pause and the seed are new stages; sections 1a and 1b. Each link below was read from the live HTML or the source on 2026-11-03.

| Stage | Where it lives | What a visitor can actually do next | Verdict |
|---|---|---|---|
| Arrive | arcs.care (root) | Links to the compass (/dashboard), one sample brief, advisory, trust | Works |
| Ask | app.arcs.care/dashboard | Ask a question, get a receipt, brief, guide. Server HTML links only advisory, privacy, terms, trust | Works, but a closed room |
| Pick up instruments | good.arcs.care, /instruments, /audit, playground.arcs.care | Reachable only if you already know the address. **Nothing in the compass links to them.** Playground links onward to forge and monolith, never back to the compass | **Break 1**: no door from compass to instruments. **Break 2**: playground is a dead end |
| Rest | app.arcs.care/reading-room | Signs you in, then `notFound()` unless you are an admin (`gateDesk`). Linked only from /internal | **Break 3**: the rest stage does not exist for a visitor |
| Return | app.arcs.care/history (the ledger), receipt and brief pages | Works once signed in; the dashboard, brief and receipt pages all link to it. Whether a reminder ever brings a visitor back is not verified here | Works for the signed-in; return trigger unconfirmed |

One pattern already does the rewiring right: good.arcs.care/fears sends each fear into the compass with the question prefilled
(`/dashboard?q=...&horizon=...`). That is the instrument-to-compass loop the rest of the world is missing.

### Smallest rewiring (no new pages, four edits)

1. Compass to instruments: one quiet line on the receipt page, under the three tributaries, pointing to good.arcs.care/instruments.
2. Instruments to compass: reuse the /fears prefill link on /instruments and /audit/check ("bring this question to the compass").
3. Playground back home: one footer link on playground.arcs.care to the compass.
4. Rest: **Zach's call.** Either open a public, read-only shelf of the reading room, or name good.arcs.care/series (Lore, Receipts)
   as the public reading room and keep the desk private. The second costs one link; the first is a gate change.

### 1a. Navigate: the HUD is the transit layer, not one more instrument

The HUD moves you node to node inside a cluster (zooming along the nested ontology) and cluster to cluster through orthogonal echoes.
Three axes: **space** = the terrain lattice (ontology), **time** = the belief scrub (epistemology), **lineage** = where each idea came
from (etymology, not built). Its entry point is the seed in 1b, a null point you can always go back to.

Today: app.arcs.care/hud returns 200 to anyone, but `src/app/hud/page.tsx` passes the field data only to admins. A visitor gets the
shell with no terrain. No code path in the HUD reads echoes yet. So the transit layer is admin-only, and the cluster-to-cluster move is
not built. The clusters from section 3 are what it would travel between.

### 1b. Pause, then Return from a seed

**Pause** is a new stage between Navigate and Return. Two modes:
- **Conscious:** the Shavasana questions (Operator 25: what went out, what came in, does each claim survive without the momentum,
  certainty now vs at the start). Spec at `runtime/specs/operator-25-shavasana-v0.md`; the spec itself says row 25 is UNBUILT. The
  mechanical half runs inside handoffs (`scripts/shavasana_handoff.py`).
- **Subconscious (incubation):** the decision is put down and held until its kairos moment, so nothing one-way happens while the person
  is away. Fold, molt and handoff are how the state is put down whole. Caution on the word: `scripts/write_lock.py` today locks git
  refs between sessions (ADR-085). It does not hold a person's decision. A visitor-facing hold would reuse its idea, not its code.

**Return** runs on a **seed**: a cold-start bundle that rebuilds the most relevant context, memory, situation and spatial awareness, so
a thread can be picked up with as little rebuffering as possible. It needs two halves:
- **Stored state.** Harness version today: the handoff block and its Cold-start recipe, `_STATE/snapshot.json`, the progressive-handoff
  ledger, `/handoff-pickup`, `scripts/prior_art.py`.
- **Live probes** that re-check the outside world on waking. Today `/handoff-pickup` probes only git and Vercel. Nothing re-reads the
  inbox, calendar or the counterpart's thread. That is why this morning's handoff said "wait for Sam's reply" while her rejection was
  already in the inbox.

**The seed's schema: five layers.** Each maps to something that exists. The visitor column is what a returning compass user's seed
(their receipt, brief, debrief and /history) carries today.

| Layer | What it answers | Harness has | Visitor has today |
|---|---|---|---|
| 1. Coordinates and waypoints | Where does the work stand? | Handoff block, backlog row `state` | **Partly.** /history lists receipts; `Outcome.driftState` (ON_TRACK, DRIFTING, LOCKED, LANDED) |
| 2. Clipped protection | What fixed points can I fall back to? | `decision_receipt` (append-only), `write_lock.py` | **Partly.** Each Receipt is a fixed point with a lineage `version`. No lock or hold |
| 3. Hazard chart | What capsized earlier tries? | `_STATE/job-search/postmortem-fanatics.md`, Kintsugi seams | **Thin.** The receipt's `loki` field (strongest counter-argument) warns before; nothing records what actually capsized after |
| 4. Hardening log | What made the craft seaworthy? | Frustration gates, feedback memories | **None** |
| 5. Blessing | What was intended, and is it released? | Ex-ante receipt, true north, Shavasana disposition | **Half.** `trueNorth` plus the prep (`protecting`, `confidence`, `outcomeHorizon`) is the intention. No release step |

Read: the visitor seed carries where they stand and what they meant, but not what went wrong, what they learned, or a release. Layers
3 to 5 are the gap. Note: `postmortem-monday.md` is not on this branch or in the main checkout; the memory index names it, so it
may sit on another branch or be unwritten. Layer 3 is checked against the Fanatics post-mortem only.

**Metric: time to first useful action after a cold start.** Measured from session start to the first action that changes state
for the right reason (a send, a merge, a correct "nothing to do"). A stale next action that gets followed counts as a miss, not a
fast start. The visitor version is the same: time from opening a returning receipt to the next real move.

## 2. The product kit, per candidate

Zach's standard kit: playground, proof, beliefs, surfaces listing, reconciliation view, status page, OpenTelemetry.
Cut, not add: beliefs, surfaces and status already exist as single shared ledgers. Each product should get a filtered view of those
(one tag per row), not its own copy. Only playground, proof and reconciliation are truly per product.

| Kit part | Compass (the ride) | Agent Receipts Audit | SMB AI ops sprint (PRL) | README to video |
|---|---|---|---|---|
| Playground | The compass is its own | /audit/check (runs live) | None | None |
| Proof | Sample brief on arcs.care | /audit/sample + two cases | prl.arcs.care/status/receipt | Three shipped videos |
| Beliefs | status.arcs.care/beliefs (shared, not tagged by product) | Linked from /audit | None linked | None |
| Surfaces listing | surfaces.arcs.care (admin-gated) | Rows exist in the catalog | Rows exist | Rows exist |
| Reconciliation view | **Not found as a page.** Closest: status.arcs.care "receipt layer" and the /history ledger | Missing | Missing | Missing |
| Status page | status.arcs.care (whole-system, Day 0 to today) | Missing | **Yes: 9 status pages** at prl.arcs.care/status/* | Missing |
| OpenTelemetry | **None anywhere.** No otel package or `instrumentation.ts` in the repo | None | None | None |

Journey pieces, by who can meet them today:

| Piece | Stage | Exists as | Who meets it |
|---|---|---|---|
| HUD (space axis, terrain) | Navigate | app.arcs.care/hud | Shell: visitor. Terrain: **harness-only** (admin) |
| HUD echoes (cluster to cluster) | Navigate | Not built | Nobody |
| Belief scrub (time axis) | Navigate | status.arcs.care/beliefs | Visitor-facing (as a ledger, not a scrub) |
| Lineage (etymology axis) | Navigate | Not built | Nobody |
| Shavasana questions | Pause, conscious | Spec + handoff script | **Harness-only** |
| Incubation hold | Pause, subconscious | `write_lock.py` (git refs only) | **Harness-only**, and a different job |
| Fold, cold molt, unfold, handoff | Pause (put down whole) | `/fold`, `cold_molt_lint.py`, `unfold.py`, `handoff_fold.py` | **Harness-only** |
| Seed, stored half | Return | snapshot, handoff block, `/handoff-pickup`, `prior_art.py` | **Harness-only**. Visitor nearest: /history and debrief |
| Seed, live probes | Return | git + Vercel only | **Harness-only**, and missing inbox, calendar, threads |

Read: PRL has the most kit and the only revenue. The audit has the best playground and proof. OpenTelemetry and a reconciliation view
are missing everywhere. Note: I could not find a page named "reconciliation view". If Zach means a specific one, the row above needs
correcting.

## 3. Theme clustering: proposal only, build after Zach's go

Goal: show the product themes inside a sprawling repo (6,033 commits), including the half-dug parts, as clusters rather than a list,
and hang each cluster off a journey stage.

**Data in (all already in the repo, public-safe rows only):**
- Induced backlog, 446 rows (`jtbd`, `status_note`, `route.tool`, `audience`; `state` kept as a label, not as text to embed).
- Tool catalog, 378 tools (`jtbd`). Seedbank, 73 seeds. ADRs, 96 (title plus first paragraph).
- Surface catalog, 321 rows (`title`, `purpose`, `kind`), **dropping the 120 unlisted rows** (counterpart pages, PII gate).
- Commit subjects are kept as a weak label (the `type(scope)` scope) to check the clusters, not as input.

**Method (no new npm dependency; nothing to install for pass 1):**
- Pass 1, runs today: TF-IDF plus truncated SVD (numpy and scipy are installed), agglomerative clustering (`scipy.cluster`), k picked
  by silhouette between 6 and 14. Each cluster is labelled by its top terms and its most central members. Deterministic and
  explainable, which suits "claim only what runs".
- Pass 2, optional, needs a yes: semantic embeddings from the all-MiniLM-L6-v2 model, already cached on this machine. It needs
  `sentence-transformers` installed in a scratch venv (a Python install, not a repo dependency), or Ollama with an embedding model
  (Ollama is installed; the app is not running). Keep only the clusters both passes agree on (adjusted Rand index). Where they
  disagree is where the roadmap is not dug up yet, and that gets shown as grain, not hidden.

**Output, in the grammar of pages that already exist (no new kind of page):**
- `runtime/specs/theme-clusters.json`, written by one script with a `--check` mode, like `scripts/surface_catalog_emit.py`. Never
  hand-edited.
- A page with the same shape as surfaces.html: one section per cluster, a table of member rows (id, kind, source file, state, last
  change), each row citing its source. Plus status.arcs.care's "stage" chips to show which journey stage the cluster serves.
- Earned fidelity: a cluster with few DONE or live members renders as grain and prints its sample size, the way the beliefs and
  status ledgers do.
- Gated like surfaces.arcs.care (admin) until Zach decides it is public.

## 4. First product to sell: the Agent Receipts Audit

What runs and what has paid (checked 2026-11-03):

| Thing | Proof it runs | Ever paid? |
|---|---|---|
| Audit offer, good.arcs.care/audit | 200 live. Two fixed scopes, sample report, two worked cases | No. Prices hidden |
| Free repo check, /audit/check | Ran it today on anthropics/claude-code: 30 commits, 27% explain themselves. Result has a shareable `?repo=` link | Free by design |
| Lead capture, arcs.care/advisory | Stores a Lead, emails the admin, returns a booking link | Prod `Lead` table: **1 advisory lead ever (2026-06-29)**, 9 waitlist |
| PRL chatbot to CRM build | Sandbox routing worked 2026-09-01; prod go-live not proven (empty-email guard failed 2026-10-09) | **Yes, about $6,200** |
| README to video | Three videos shipped; two of the gates exist as `scripts/readme_video_check.py` | No |
| OSS family (23 public repos) | Landing pages live; 0 to 1 star each | No, and should not be (free to hold) |

Why the audit first: there is nothing to build, the free check is a true and personal opener, and it sells the brand promise
(it labels what the record cannot prove as "not verified"). Pitch it as a craft practice, not a pivot; it shows FDE work in the open.
Risks: buyer and price unvalidated; the only case is our own incident, run by its operator; "audit" can sound like compliance.

Price hypothesis: Audit (one repo, one window, 2 weeks async) list $3,500, **founding $2,500** for the first 3 buyers in exchange for
a publishable redacted case. Audit plus gate list $6,500, founding $5,000. Prices stay off the page; quote on the scope call; invoice
first, no Stripe build.

One-day plan (about 4 hours of Zach's time): pick 10 named eng leads (warm first) whose public repos show agent commits; score each
with the free check; Claude drafts 10 short first-person notes with the score link and one question ("Which week would you least like
to explain from memory?"); file the ex-ante receipt (ADR-068); Zach reviews and sends. Kill rule: 0 scope calls from 10 sends in 10
business days moves the effort to the PRL sprint, starting with proving its prod go-live.

## 5. The growth route: an MCP probe (ADR-076's test)

The audit is sales led, not a product-led hook: the free check is used once, there is no account and no usage that grows, and every
dollar needs a scope call. It is the right first sale for cash, but it caps at Zach's hours. The growth route is MCP led: the buyer
works inside Claude Code or Cursor, and the pain shows up mid-session. ADR-076 already adopted this (free in their client as the land,
metered use as the expand, attribution as the wedge) and set its own gate: ship one cheap read-only probe and measure pull before any
hosted server.

What exists to build on: `rfp-engine` already runs as a standard-library MCP server (`mcp/server.py`, cite or refuse);
mcp.arcs.care is live (hosts the Perplexity MCP); the repo-check scoring works today, but as JavaScript inside
`public/good-audit-check.html`.

| Rung | What | Price |
|---|---|---|
| Land | `check_repo_receipts`: one read-only local tool, same scoring as /audit/check, on the repo you are in. Every flagged commit cites its sha; anything it cannot verify says so. MIT, listed in the arcs-skills marketplace | Free |
| Hook | Inside the developer's own session, their agent reports "8 of your last 30 commits explain themselves; here are the 5 nobody could trace" | Free |
| Expand | The "Audit + gate" scope as a product: a merge check that fails a commit missing its receipt, then scoring across a team's repos | Metered (to fire) |
| Top | The cold reconstruction audit, run by Zach (section 4) | Fixed price |

The MCP is the audit's funnel, not its replacement.

**Measuring without breaking the promise.** A local tool that phones home contradicts the privacy pitch, so it does not. Signals are
public counts only: marketplace installs, GitHub unique clones (traffic API, 14-day window), stars, issues, and inbound asks.

**Kill rule, set before launch.** Within 30 days of listing: at least 10 unique clones from accounts other than Zach's, or at least
1 inbound ask for the merge gate. Either one advances ADR-076 out of DRAFT. Neither: file a falsified receipt against ADR-076, stop
there, and build no hosted server.

Cost: about half a day to port the scoring to a Python tool in rfp-engine's pattern, plus a marketplace listing. Brings no cash this
week, which is why it runs second.

## Decisions for Zach

1. Outreach for the audit today: yes or no.
2. The rest stage: open a public reading-room shelf, or name good.arcs.care/series as the public reading room.
3. Theme clustering: go on pass 1 only, or pass 1 plus pass 2 (needs a Python install).
4. Seed live probes: add inbox, calendar and open-thread checks to `/handoff-pickup` first (harness, cheapest, would have caught
   this morning's miss), before any visitor-facing pause or seed.
5. MCP probe: go on porting the repo check to one local read-only MCP tool this week, under the section 5 kill rule.

The four rewiring links in section 1 are small edits to existing pages; they wait for the same go.
