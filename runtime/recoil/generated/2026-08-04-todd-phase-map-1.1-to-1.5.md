# PRL Resins Chatbot — Phase Map 1.1 → 1.5 + 1.1 Go-Live Gate
_2026-08-04 · scoping doc from the Aug-4 meeting (Todd down to extend scope)_
_New assets in hand: Unbounce access · ZoomInfo · Mailgun_

Grounded against: Jul-20 / Jul-31 Granola transcripts (verbatim), the Jul-30 MASTER-HANDOFF,
the Aug-3 vision-serialization + Lyro-v2 docs, and the live SugarCRM Leads schema audit.
Where this doc corrects a prior status, it is called out as **[STALE→]**.

---

## Current external dependencies (parked as of 2026-08-04)

Work is gated on three inbound items, none internal. Do not burn cycles trying to route around them;
the parallel-path work that does NOT need them is called out under each.

| Dep | Gates | Parallel work available now |
|---|---|---|
| **SugarCRM sandbox access** (awaiting) | 1.1 Create-Lead test + the CRM Data Reality session + baseline | Draft the CRM Data Reality agenda; finalize the field mapping on paper against the known schema. |
| **Tidio support email — account review** (awaiting) | 1.5 Lyro (webhook tier, handoff mechanism) | Nothing to force; keep Lyro OFF (correct for 1.1 anyway). |
| **Machine-readable competitor/resin cross-reference DB from Todd** (requested) | 1.5 Lyro resin recognition + the deterministic eval harness | **Define the exact schema to request** so it comes back usable in one pass; scaffold the eval that cross-references Lyro output against this deterministic ground-truth. |

**On the competitor DB:** today's source is the Product Selection Guide 2025, whose cross-reference
tables are page-IMAGES (OCR fast-follow). A machine-readable version from Todd retires the OCR risk
and becomes the **ground truth** for a deterministic eval: Lyro (non-deterministic) is graded against
a fixed competitor-grade → PRL-equivalent table, so we can prove recognition/mapping correctness
before go-live rather than trusting the model. Ask Todd for a defined shape (see the schema note we
send him), not "the data," so it lands usable the first time.

---

## 0. Framing (do not lose this)

Todd accepted the chatbot **because it avoids the reps** — the reps are where the pain is, and
Phase 2 is rep-facing. The 1.x sub-phases below complete the *demand-capture instrument* without
touching a single 58-year-old rep. The one business number Todd has ever volunteered, unprompted,
is **four hours** (time-to-first-touch on a lead). Every 1.x phase is scored against: does it get
a clean lead in front of a rep, faster, inside that window — and can we show him that number.

---

## PHASE 1.1 — MVP lead capture, live (THE GO-LIVE GATE)

### Final JTBD
> When a qualified visitor lands on the PRL site or a paid lander, capture a clean, correctly-routed
> lead into SugarCRM within seconds — so a rep can follow up inside the four-hour window — **without
> asking any rep to learn or touch new tooling.**

### Definition of done = "ready for internal testing"
A test conversation down **each** branch produces a Sugar lead that a rep would accept as real.

### Acceptance criteria (all must pass before internal testing)
1. **All 6 Sugar-required fields populate** on every created lead: `account_name` (company),
   `first_name`, `last_name`, `lead_source`, `location_c` (state), `phone_work`.
2. **Name splits correctly** — Zapier Split-Text `name` → first/last, with a single-word fallback
   (no lead fails because someone typed just "Dave").
3. **Phone handling is decided and enforced** — required in-bot, or a placeholder written so the
   record still creates (client decision #1 below).
4. **`lead_source` carries a value** — either a new "Chatbot" picklist value or ride "Web Site"
   (client decision #2).
5. **`location_c` is normalized to what the live schema actually accepts** — the Create-Record
   picklist keys read as **abbreviations** (MI/CA), which contradicts earlier "full state name"
   guidance. **Verify against one real live lead before go-live.** [open]
6. **Notification email arrives within seconds** — sent via **Mailgun** (authenticated domain,
   bypasses the `info@prlresins.com` DNS block that was stuck on PRL IT). [STALE→ was "blocked on IT"]
7. **No lead-loss path exists** — **Lyro stays OFF for 1.1** (AI-level delivery needs Tidio+, and
   an AI-only conversation would qualify a visitor and deliver nothing). AI is 1.5, gated on a
   verified handoff.
8. **Widget renders branded on the WP dev site** — maroon/gold, single logo image (double-avatar
   fixed), greets on the real PRL Divi theme, Incognito-verified.

### Blockers to 1.1 (current, de-duplicated)
| # | Blocker | Owner | Status |
|---|---------|-------|--------|
| B1 | Wire Tidio **flow-level** webhook node → Zapier Catch Hook | Claude | **UNBLOCKED** — flow webhook works on current plan [STALE→ was "plan-gated"] |
| B2 | Zapier Create-Lead step: name-split + phone + company fallback + lead_source + state normalize | Claude + Zach | Staged, not built |
| B3 | 3 client decisions from Todd (see below) | Todd | Open |
| B4 | Notification delivery — switch from DNS-blocked Gmail/`info@` path to **Mailgun** | Zach + Claude | New path, unblocks B; needs Mailgun domain verify |
| B5 | Upload hexagon logo in Tidio Welcome image | Zach (manual) | Open |
| B6 | Reimport + activate the 5-button (resources) flow | Zach (manual) | Open |

### Client decisions — RESOLVED in the Aug-4 meeting
1. **Phone: REQUIRED.** ✓ Confirmed by Todd Aug-4; implemented in `prl_tidio_flow_gen.py` (phone +
   email now captured on every lead path).
2. **lead_source: ADD "Chatbot" value.** ✓ Todd will add it in the CRM — but **sandbox-first**: add +
   verify the value + Create-Lead in the copy-down instance BEFORE replicating to live production. See
   `2026-08-04-todd-safeguards-killswitch-rollback.md`.
3. **Test lead → use the SANDBOX** (not a labelled prod test lead). Zach's call Aug-4: prove everything
   in a lower/copy-down environment first; nothing blind on the live production instance. This makes
   **SugarCRM sandbox access the gating dependency** for the CRM-write test (already the parked item).

**New requirement (Aug-4): safeguards / kill-switch / rollback plan** — the in-flight DR layer, now at
`2026-08-04-todd-safeguards-killswitch-rollback.md`. Sandbox-first everywhere; one-toggle kill switches
per surface; additive-only CRM changes; canary monitoring; tell Todd immediately on any real-lead impact.

### Blindspots (things that will bite if unwatched)
- **GTM go-live hits prod.** The dev site loads the shared prod GTM container (GTM-WLP9C76). Never
  flip go-live via GTM on dev — it publishes to LIVE. GTM is the eventual single go-live switch
  (covers WP + Unbounce), not a dev tool.
- **The 4-hour metric is not instrumented.** Not a 1.1 blocker, but it's the number Todd repeats to
  his owner. Stamp `date_entered` → first-touch on the lead the moment delivery is live (1.2).
- **ZoomInfo is not wired into capture yet** — 1.1 ships without it; the email gap it fixes is 1.3.

---

## PHASE 1.2 — Reliable delivery + instrument the 4-hour metric
**JTBD:** "When a lead lands, prove it moved fast." Attack the one number Todd measures.
- Harden the flow → Mailgun → Sugar path (retries, visible task history in Zapier).
- **Instant autoresponder to the visitor via Mailgun** — acknowledges within seconds, which is
  itself a partial answer to the four-hour gap (the *prospect* hears back instantly even if the rep
  is slow).
- **Stamp time-to-first-touch** on the Sugar lead; simple report: time-to-touch vs close-won /
  close-lost, using data Todd already owns. Nearly free, highest-trust deliverable.
- **New asset used:** Mailgun (delivery + autoresponder).

### ⚠ 1.2 has a discovery prerequisite (do this BEFORE promising the metric)
The JTBD above assumes Sugar already captures the *fielding* event. It may not. This must be a
conversation (SM + whoever runs the reports), not an assumption:

1. **What timestamps/flags exist today?** Lead arrival (`date_entered` we control), assignment,
   first activity/call log, status-change history. If there is no captured "first touch," we cannot
   measure time-to-first-touch out of the box.
2. **Do NOT solve a missing first-touch by making reps log calls** — that is the exact toe-stepping
   we are avoiding. Find an **auto-capturable proxy** instead: lead status change (New → Working),
   an outbound email logged, or worst case measure only "arrival → first *system* event." Better a
   partial number nobody had to work for than a perfect number that imposes rep behavior.
3. **The retro-analysis win (potentially the biggest artifact in the whole engagement):** if
   historical leads carry *both* a response-time signal *and* an outcome (closed-won realized
   revenue vs closed-lost, in Opportunities, linked back to source), we can show
   *"leads fielded inside 4 hours close at X% / $Y vs beyond 4 hours"* — built entirely from data
   PRL already owns, before we ship anything. This is the number Todd takes to the owner. Gated
   entirely on whether the data exists, which is why the discovery call comes first.
4. **Map the shadow layer** — info used *outside* Sugar (spreadsheets, email, tribal knowledge), and
   verbal/phone touchpoints (calls to the plant, sample requests, updates never keyed in) that are
   real business-process steps invisible to the CRM. These matter twice: they distort any
   response-time reading built only on CRM data, and they are the future rep-facing capture surface
   (Phase 2). Inventory them now; do not try to capture them yet.

**Action:** a **CRM Data Reality** discovery session (SM + reports owner) that unlocks both this
metric AND the baseline (punchlist B2). It is the long pole. Schedule it early.

## PHASE 1.3 — Fix the email gap via ZoomInfo enrichment
**JTBD:** "Every lead arrives with a real business email + firmographics, so routing and follow-up
don't depend on what the visitor bothered to type." Directly fixes the **95%-of-Sugar-leads-have-
no-email** finding.
- Enrich at capture (or on-create) via ZoomInfo: company → verified contact email, title, size,
  location → improves both routing and the qualification signal.
- Resolves the "emails aren't populating in CRM" root cause with the tool that was missing.
- **New asset used:** ZoomInfo. **Decision to surface:** enrich at capture vs nightly batch; per-
  lookup cost/quota.

## PHASE 1.4 — SEM / Unbounce onramp
**JTBD:** "Paid-search demand converts on the lander it arrived on, not just organic site traffic."
- Per-campaign dedicated flows on Unbounce landers (e.g. /sabic-alternatives, Covestro, Ventilator)
  matched to the **existing live Unbounce→SugarCRM zaps** (SugarCRM already connected there — that's
  the Create-Lead mapping we've been copying).
- `build_sem_onramp` flow already exists (11 nodes) — wire triggers to the SEM URLs.
- **New asset used:** Unbounce access (edit landers + own the flow/zap wiring end to end).

## PHASE 1.5 — AI qualification layer (Lyro) + resin recognition
**JTBD:** "Where the visitor needs judgment, not a form, let the AI improvise — but never let it
qualify-and-drop." The upgrade already bought; the reason to buy it was improvisation, not the tree.
- Turn on Lyro with the **guardrailed prompt** (never recommend a grade/spec/cert/price; hand off) +
  public knowledge sources only (keep proprietary forms off Tidio's servers).
- Route **"Help me choose" + "Something else" → AI**; keep "I know what I need" + "call me" rigid.
- **Load-bearing gate:** `build_ai_handoff` must be verified delivering to Sugar *before* Lyro goes
  live, or "Help me choose" becomes a silent lead-loss path. Confirm with Tidio how Lyro triggers a
  flow (open question from the Daniel call).
- Competitor-grade recognition (Lexan/Makrolon/Ultem/Noryl/Lustran/Valox/Zytel) as buying signal.

---

## PHASE 2 (log, do not scope yet) — rep-facing
The real pain, and the real change-management. Test before proposing anything here:
**does it reduce work for a 58-year-old rep who doesn't want to use technology?** If not, it's our
roadmap, not Todd's. Candidates he actually voiced: voice-to-text field notes → Sugar, Mon/Fri lead
digest to reps, per-rep SDR sub-agent, ElevenLabs voice agent, multilingual transcription, resin
recommendation engine (the one he pulled toward twice — needs an NDA-optional data conversation).

---

## Open questions for Todd (in his language, not ours)
1. "Once leads start landing, do you want to see how fast they get picked up? You mentioned four hours."
2. "For the email gap — want me to auto-fill the business email from ZoomInfo so every lead is
   complete, or keep it to what they type?"
3. Confirm the 3 decisions above (phone / lead_source / test lead).
