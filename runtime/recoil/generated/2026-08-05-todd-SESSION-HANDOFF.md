# PRL Chatbot — Session Handoff + Discovery Insights (pickup here)
_2026-08-05 · supersedes 2026-07-30-MASTER-HANDOFF as the top-level pickup. Machine-local detail:_
_`~/.claude/projects/-Users-zharris-arcs-v9/memory/project_todd_hotes_prl_resins.md`._

## THE ONE UNLOCK
**Todd's SugarCRM sandbox access.** It gates 1.1 go-live, the 1.2 CRM Data Reality audit, and the whole
OEM↔molder data-model question. Todd has already opened prl.arcs.care (good signal). **Budget is on HOLD
until the sandbox lands** (per Zach) — everything below is either done or deliberately parked.

## STATE (what's live / done)
- **Live client deck at prl.arcs.care** (+ app.arcs.care/prl-chatbot.html): now/next/later, best/base/worst,
  payment schedule ($4.5k/4k/6k/3.5k = $18k, phased), receipt-calibrated pricing, presentation mode
  (auto-fit, fullscreen, keyboard nav), ex-ante receipts with Google + Outlook reminders. 0 em-dashes,
  impeccable-polished. Source: `_ARTIFACTS/prl-roadmap-deck.html`. Deploy from MAIN worktree only.
- **1.1 go-live recap sent to Todd** (Aug-4). Decisions resolved: phone REQUIRED, add "Chatbot" lead_source
  (sandbox-first), test via sandbox. Bot built + tested on dev; delivery blocked only on sandbox.
- **1.3 knowledge base = built + verified** (Todd delivered the machine-readable data): 150 grades (specs
  100% verified vs source), competitor cross-ref, nomenclature, G/B/B recommender. Git: `runtime/recoil/
  generated/prl-kb/`.

## TIDIO UPLOAD — final artifacts (answer to "what + where")
Upload these to Tidio → Lyro → Knowledge. All at `runtime/recoil/generated/prl-kb/tidio-upload/` (git) and
sent to Zach as files:
1. `PRL-Product-Catalog-2025.pdf` — 150 grades + specs. **Upload (safe, public).**
2. `PRL-Material-Selection-Good-Better-Best.pdf` — the "which material for which need" recommender. **Upload (safe).**
3. `PRL-Competitor-Cross-Reference.pdf` — competitor→PRL grade mappings. **DO NOT upload as an open KB source
   yet.** Pending Todd's approval + a handling decision (approval/disclosure draft: `2026-08-05-todd-competitor-
   data-approval-draft.md`). **Default (pending Todd): gate the competitor match behind lead capture** (contact
   first, then answer) — turns the most valuable answer into a lead magnet + screens anonymous competitor fishing.
   So it lives behind the capture flow, not as an always-open KB doc.
Format note: prose PDFs (index better in Lyro than CSVs). CSV versions also exist in scratchpad if needed.

## PENDING / PARKED (with the sandbox budget)
- **Todd asks:** (1) sandbox access [critical]; (2) UL yellow-card / agency-listing data per grade — the
  ~$30K/6mo differentiator, NOT in any file we have (draft ready: `2026-08-05-todd-ul-yellowcard-ask-draft.md`).
- **1.2:** delivery + enrichment (ZoomInfo/Mailgun) + the 4-hr metric + baseline + the CRM Data Reality audit.
- **1.2 audit must resolve:** the OEM↔molder relationship in Sugar (unmodeled) + territory setup (currently global).
- **1.3 build:** recognition + the deterministic eval (0% hallucination; refusal-on-unsourced-certs is the key test);
  cheap adds: promote FDA/agency to a structured field, add a KB refusal note.
- **Deferred features:** Stripe-payment-per-phase (review→greenlight flag; Zach creates invoices), persisted
  Receipt Studio (louisville reuse), the live cascade/slippage Gantt HUD.

## DISCOVERY INSIGHTS — running list (append after each Granola/recoil call)
The durable strategic facts about PRL/Todd, serialized from the recorded calls. Append, do not rewrite.

**ICP structure (the central complexity):** two entangled personas. **OEM** (Honda, John Deere) sets the
spec (writes resin onto a print → sticky, hard to displace); **injection molder** is a separate business
that buys + consumes it. Pricing flows OEM→molder; molders arbitrage the margin. Can't serve one without
the other. → chatbot needs distinct persona "hats"; route by timeline + certification + spec, not category.
**Sales:** reps by territory (any vertical) + two dedicated OEM reps who coordinate when a molder is
involved (one deal, multiple reps); value-based pricing, every customer unique; high switching cost both ways.
**Key differentiator:** pre-existing UL yellow-card approvals save a customer ~6mo + ~$30K in lab testing.
**The number Todd manages to:** four-hour lead callback (the metric to instrument + take to the owner).
**Attribution blind spot:** ~$26.5M closed-won with no lead source; 231 deals tagged w/ competitor grade
(latent ICP + competitor-displacement signal). 95% of leads have no email.
**Todd himself (handling, machine-local only, never client-facing):** boring/low-variance = smooth flight;
linear/sequential (pilot) + polyrhythmic (drummer); System-2, wants shown reasoning; scope-discipline anchor
(chatbot-first, pulls back expansion); budget discretion, moves fast; friends-not-foes with his people; apex
objective = Zach as lowest-threat/highest-force-multiplier. Full profile in the machine-local tracker.

**Recommendation on this list:** keep it as the single running discovery SSOT; after each recorded call, run
recoil-close / a Granola deep-recall and append the new durable facts here. It compounds the ICP model and
feeds the persona routing + the 1.2 CRM data-model design.

## PRE-MORTEM REFINEMENTS (must-carry) — `2026-08-05-todd-plan-premortem-gauntlet.md`
The plan's two structural risks are the SAME thing: the sandbox gate, and building around it instead of
pushing on it. Carry these: (1) **sandbox escape hatch + escalation** — name a date, else go-live on one
Todd-signed labelled test lead; (2) **no new build until 1.1 ships or sandbox lands** (feature ideas →
backlog); (3) **anti-fabrication = deterministic hard block (unsourced categories) + confidence-threshold off-ramp
that defers to a human/delegated specialist rather than making something up; the eval gates BOTH** (0%
hallucination = when not grounded + confident, hand off, never invent); (4) **competitor gating built + verified BEFORE the
data touches the live bot**; (5) **G/B/B = options-to-confirm, never a directive**; (6) **Tidio support
review = hard gate before Lyro; ZoomInfo spend cap prerequisite**; (7) receipt tripwire on coordination
overrun (re-price, don't eat); (8) verify iOS present-mode fallback; (9) confirm prl.arcs.care link audience.

## SESSION 2026-08-09 — moves + corrections (anti-amnesia; append)

Ran the /handoff-pickup on Todd, attempted Build A, ran a serialized recoil, and banked an ADR. Moves:

1. **Build A step 1 attempted live, then HELD (Zach's call).** Tidio has **no bulk/source-level Lyro↔Copilot
   "Used by" toggle** — it's **per-Q&A-entry only** (verified in-app; parent checkmarks read-only, Manage =
   Download/Set-audience/Delete, multi-select = Set-audience/Delete). So "5 PDFs → Copilot-only" = hundreds of
   manual toggles, OR delete the source. Zach chose HOLD; **Lyro account untouched, matches the 2026-08-09 backup**
   (`prl-lyro/backups/`). Detail: `prl-lyro/tidio-capabilities-research.md` §5 + `CHECKPOINT-...md` step 1.
2. **Serialized recoil on the last 4 calls** → `2026-08-09-todd-serialized-recoil.md`. Kairos locks (launch=the
   close · family-office succession · year-end $15K displacement · "tomorrow"=intent) + field-level ambition read
   (Todd's win = a clean, defensible, narratable modernization to carry *upward* into the family-office CEO seat;
   near-zero drama; single-inbox simple).
3. **ADR-PRL-001 (governed answering, not silence)** → `prl-lyro/ADR-PRL-001-governed-answering.md`. Promotes the
   Aug-5 pre-mortem pt(3) to an explicit per-category posture, eval-gated. The bot MAY state a spec when
   grounded+eval-passed+fresh; HARD-routes cert/yellow-card until sourced; competitor = gate-behind-capture; price
   = never. Reconciles the stale 1.3 DoD ("no path where the bot states a spec as fact" → "…an UNGROUNDED spec").

**Corrections banked (the amnesia this session caught):**
- **IDES** (not "IDS"; catalog.ides.com, company I=73811, e.g. `Datasheet.aspx?I=73811&E=32892`) crawl +
  reverse-lookup are **already built** (Aug 7): 28 datasheets scraped + `normalize.py` (895 competitor keys,
  self-test 10/10). **IDES bulk-export is a freshness upgrade, NOT a launch gate** (earlier session-notes wrongly
  called it the gate).
- **Eval harness already built** — `prl_lyro_eval.py`, 74 cases. Needs live responses scored, not building.
- **1.3 ground truth already delivered + verified** (150-grade catalog, specs 100% vs source).
- The one real Todd-sourced data gap = **UL yellow-cards** (~$30K/6mo differentiator, in no file).
- **Launch centerpiece reframed:** governed spec/data-sheet answering + capture, NOT spec-silence.
- **Sandbox unblocked** (Aug-9 email, case 589806): free, one already exists, Sugar Sell Advanced allows 2. Ball
  with SugarAI support / Todd for access to the existing one.

**FRAGMENTATION / amnesia risk (flag):** all Todd work lives on branch `claude/chatbot-1-1-jtbd-blockers` (this
session ran from the `yuri-ahmed-communication` worktree). The **main `CLAUDE.md` handoff is Yuri/forge-focused
and does not point here** — a pickup from the main chain gets Todd amnesia. THIS file is the Todd pickup; the
machine-local memory (`project_todd_hotes_prl_resins.md`) + `_STATE/snapshot.json` should point at it.

**Recognizer VERIFICATION (2026-08-09, committed on branch):** built + ran a staged end-to-end lead sim
(`prl-lyro/simulate_lead_e2e.py`) + two exhaustive deterministic sweeps — `coverage_sweep.py`
(895/895 competitors, 150/150 grades, 50/50 states, 64/64 field-gate perms, 297/297 punctuation) and
`full_grid_sweep.py` (**150 grades × 50 states × 3 branches = 22,500, all invariants hold**). These caught +
fixed two recognizer bugs the 15-case self-test hid (trailing punctuation killed the competitor cross-ref;
parenthesized grade codes + sentence punct). No fuzzy/typo correction by design (exact-or-route). Net-new:
`prl_lyro_eval.py` gained an `input_hygiene` category (74→80 cases, for live scoring). The three sweeps are
the recognizer regression suite — re-run after any dictionary/normalize change.

**PARKED for prl.arcs.care (client-facing):** update the "74 safety checks pass clean" line → 80 + the
22,500-combination recognizer verification (proposed wording pending Zach; deploy from MAIN worktree only).

**Uncommitted as of 2026-08-09:** this handoff append, ADR-PRL-001, the serialized recoil, `todd-always-sometimes-
never.md` (Todd decision aid, NOT sent), and the tidio-capabilities/checkpoint annotations.

## NEXT SESSION STARTS AT
Todd decision aid (`prl-lyro/todd-always-sometimes-never.md`, reframed to governed-not-silenced) is drafted, NOT
sent — decide send vs hold for Todd's Friday reply. Then: (1) get sandbox access (unblocked, ball with support/
Todd); (2) collect+score live eval responses to flip governed categories; (3) when sandbox lands, run the 1.2 CRM
Data Reality audit (OEM↔molder model + territory). Build A step 1 still pending Zach's delete-vs-per-entry call.
