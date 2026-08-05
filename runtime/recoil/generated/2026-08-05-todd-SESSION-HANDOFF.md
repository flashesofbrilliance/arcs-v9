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
backlog); (3) **cert/spec = deterministic hard block + refusal eval is a go-live gate** (0% hallucination
is only real if refusal is enforced, not prompted); (4) **competitor gating built + verified BEFORE the
data touches the live bot**; (5) **G/B/B = options-to-confirm, never a directive**; (6) **Tidio support
review = hard gate before Lyro; ZoomInfo spend cap prerequisite**; (7) receipt tripwire on coordination
overrun (re-price, don't eat); (8) verify iOS present-mode fallback; (9) confirm prl.arcs.care link audience.

## NEXT SESSION STARTS AT
Send Todd the UL yellow-card ask (draft ready) if batching a note to him. Otherwise: wait on sandbox; when it
lands, run the 1.2 CRM Data Reality audit (resolve OEM↔molder model + territory) and build 1.3 recognition + eval.
