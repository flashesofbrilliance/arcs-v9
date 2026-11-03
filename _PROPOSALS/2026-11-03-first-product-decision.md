# The journey first, then the first product: decision page (2026-11-03)

Status: PROPOSED, waiting on Zach's yes or no on three items (bottom). Nothing was built, sent or published to make this page.

Prior art: `_PATTERNS/2026-07-13-frontend-monetization-queue.md` (July ranking), backlog rows `agent-receipts-audit-offer` (DONE) and
`agent-receipts-audit-first-conversion` (HOLDING, its one dependency is now DONE), memories on free-to-hold / metered-to-fire,
refusal to overclaim, cut not add, and the product-marketing legibility gap.

## 1. The journey, as it runs today

The test is WORLD.md's Myst rule: the world teaches you how to read it, with no tour. Four stages: **arrive** at the compass, **pick
up** instruments, **rest** in the reading room, **return** through receipts. Each link below was read from the live HTML or the source
on 2026-11-03.

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

## Decisions for Zach

1. Outreach for the audit today: yes or no.
2. The rest stage: open a public reading-room shelf, or name good.arcs.care/series as the public reading room.
3. Theme clustering: go on pass 1 only, or pass 1 plus pass 2 (needs a Python install).

The four rewiring links in section 1 are small edits to existing pages; they wait for the same go.
