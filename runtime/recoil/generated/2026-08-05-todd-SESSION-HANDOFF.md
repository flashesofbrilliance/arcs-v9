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

## SESSION 2026-08-10 — kickoff call + artifact family + the parallel 1.1-UAT / 1.2-kickoff plan

**Where we landed (Aug 10 walk-through call · recoil `2026-08-10-todd-recoil-close.md`):** 1.2 PAID + kicked off.
Warm, high-trust call. **Go-live is now gated only on two Todd-owned unblocks:** (1) **written sandbox approval**
(verbal to Long on the Aug 11 3:00pm call, then in writing), and (2) the **info@ email fix — IN MOTION** (Zach
looped **Jorge/IT** in with Tidio support). **Bill** (not Nicole) runs Sugar = the lead verifier + territory owner.

**Artifact family (all committed / published):**
- **4 shareable claude.ai artifacts** (private → Zach shares from each menu): Go-live evidence
  `1daae3aa`, 1.2 kickoff+doc-tracker `1ea25934`, UAT sign-off `9713ddbb`, Sugar call agenda `b98f7dfc`
  (**SENT to Long** + support, cc Todd).
- **prl.arcs.care deck** — live + current (sandbox = in-progress / prod copy-down pending Todd).
- **Repo (branch `claude/chatbot-1-1-jtbd-blockers`):** recoil-close, `SPRINT-2-1.2-kickoff.md` (SSOT),
  `SUGAR-call-prep-2026-08-11.md`, `PREMORTEM-user-experience.md`, `TEST-PLAN-go-live.md`, `ADR-PRL-001`
  (governed answering), `ADR-043` + DEWY receipt (adaptive rhetorical resonance); the recognizer + 3 sweeps
  (self-test 34/34, coverage, 22,500-grid) + `prl_lyro_eval.py` (84 cases) + the **capture-first flow**
  (name→email→phone→company→state, validated) + the `~/Downloads/prl-tidio-flows` bundle.

**Recap email:** **SENT to Todd (Aug 10)** — the four artifact links + two asks (written sandbox approval +
negative keywords/anti-ICP). Now awaiting Todd's replies on those two.

**THE PARALLEL PLAN — 1.1 UAT and 1.2 kickoff run together:**
- **1.1 critical path (UAT):** info email fixed (Tidio/Jorge) → sandbox access (Todd approval + prod copy-down)
  → wire delivery (Zapier) → **lead lands in CRM** → **routing logic** (territory assignment via Bill's map) →
  notification (rep + prospect autoresponder + the new **4-hour escalation nudge**) → **verify received
  (UAT: Todd + Bill sign off)** → flip live. Both gates Todd-owned; our work is days once either lands.
- **1.2 kickoff (parallel):** baseline prep, ZoomInfo enrichment (needs a Zoom contact), Mailgun, the **4-hour
  escalation nudge** build, the **anti-ICP / negative-keyword** filter (garbage "sheet" leads) + Gravity Forms
  spam fix (Zach cleared, staging→live), CRM data-reality session (Bill), net-new/dedup clarification.

**Todd owes:** written sandbox approval · negative keywords + garbage-lead examples · territory map (Bill) ·
ZoomInfo contact · (optional) 30-min with Bill. [George/Jorge's email = DONE, looped with Tidio.]

**Anti-ICP / spam engine BUILT (Aug 10):** `prl-lyro/normalization/exclusions.json` (extensible SSOT, seeded
with Todd's "sheet" signal + form spam) + `exclusions.py` (self-test 8/8) + `gravity_forms_blocklist()`
generator + `prl-gravity-forms-cleanup.md` spec. ONE source shared by chatbot + form; Todd's list drops into
`todd_provided` with no code change. **Applying in WP staging** (honeypot + form-factor field via clicks;
Turnstile needs the add-on+keys; keyword blocklist needs a snippet — noted in the spec).

**Stripe decision (Aug 10):** **skip Connect** for the engagement — it's for platforms onboarding other
merchants; Zach just invoices clients → standard account + instant payout is correct. Connect only fits IF ARCS
productizes as a platform (e.g. Receipt Studio tenants selling, ARCS taking a fee). Instant payout: check
Available vs Pending in the Dashboard; new-account holds may keep today's $4.5k pending.

**Meta minted:** ADR-043 + memory `[[adaptive-rhetorical-resonance]]`. **Parked (Zach to greenlight):** a
calendar-auto-prep routine (run `recoil-prep` ahead of counterpart calls) + an ADR/DEWY candidate watcher hook.

## NEXT SESSION STARTS AT
Send the recap email (Zach) → run the **Aug 11 3pm Long/SugarAI call** (sandbox approval + the tech-question
agenda) → on unblock (sandbox creds + info@ receiving): **import the capture-first flow to staging, wire
delivery to Sugar, run the 1.1 UAT** (lead lands → routing → verify received → sign off), while starting 1.2
(enrichment, 4-hr nudge, anti-ICP filter, baseline). Chase Todd's: keywords/examples, territory map, Zoom contact.
