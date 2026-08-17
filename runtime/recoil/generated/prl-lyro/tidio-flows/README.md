# PRL Tidio Flows — importable variants + how to test each

_2026-08-09 · Each `.json` here imports straight into Tidio (Automation → Flows → Import). Generated
from the version-controlled generator `prl_tidio_flow_gen.py` (repo: `runtime/recoil/generated/`), so
never hand-edit the JSON — change the generator and re-export. Importing is safe; a flow does nothing
until you activate it._

## What's in here

```
main/
  prl-main-capture-first-REQUIRED.json   <- RECOMMENDED. Capture up front, required, incl. company.
  prl-main-capture-at-end.json           <- Original. Answers first, captures at the end.
  prl-main-ai-forward.json               <- Hands "Help me choose" to Lyro AI; rigid path for the rest.
ai-bridge/
  prl-ai-handoff-bridge.json             <- Delivers a lead AFTER a Lyro-only conversation (see notes).
sem-onramps/
  prl-sem-{sabic,lexan,ultem,noryl,valox}.json  <- Paid-search landing-page onramps (URL-triggered).
```

## Import — universal steps (all variants)

1. Tidio → **Automation → Flows → Import** → pick the `.json`. It arrives as a **Draft**.
2. **Test before activating** (see per-variant below). Test as a **fresh visitor**: incognito window,
   or clear cookies + localStorage — the main flows trigger on **first visit** only.
3. **Collision rule:** only ONE flow may use the **onFirstVisit** trigger at a time. Before activating a
   new `main/` flow, **deactivate the currently-live one** (`PRL Resins - Lead Capture`). Two on-first-visit
   flows will fight.
4. Verify capture without any CRM: Tidio emails the captured lead to the connected inbox on submit, AND
   you can **Export CSV** of leads. Both prove capture before Zapier/Sugar is wired.

## Deterministic pre-check (run once, no Tidio needed)

Before trusting any flow's routing/recognition, from `runtime/recoil/generated/prl-lyro/`:
```
python3 full_grid_sweep.py     # 150 grades x 50 states x 3 branches = 22,500, must all pass
python3 coverage_sweep.py      # competitors/grades/states/fields
```
These test the recognizer + field mapping the delivery step relies on. Green here = the data layer is sound.

---

## main/prl-main-capture-first-REQUIRED.json  ⭐ recommended

**What it is.** Greeting → **required capture gate**: Name → Company → Phone → Email → State (phone & email
validated) → THEN "What brings you in?" + qualifying questions → close. Contact is secured before anything
else; company is included (the gap found on staging 2026-08-09); capture runs as a quota-free flow step
before Lyro.

**How to test.** Import → deactivate the old flow → activate → incognito → open the widget.

**What to test / acceptance (all must hold):**
- The bot asks, in order, **Name, Company, Phone, Email, State — before any product question.**
- **Phone and email reject junk** (type `asdf` for email → it re-asks with the error).
- You cannot advance to the questions without answering each field (only escape = closing the widget).
- After capture, "What brings you in?" appears with the 5 options; each option leads to its questions and
  ends on the "specialist will reach out" close.
- The captured lead (Tidio email / CSV export) contains **name, company, phone, email, state** — all five.
- No path states a spec, cert, or price (spot-check "I know what I need" → a grade).

---

## main/prl-main-capture-at-end.json  (original, for comparison / A-B)

**What it is.** Greeting → "What brings you in?" → qualifying questions per branch → capture at the END.
Lower up-front friction, but a mid-conversation bail loses the lead, and it can under-capture.

**How to test.** Same import/activate/incognito. **Acceptance:** every branch still reaches the capture
block and collects name/email/phone/company/state; the difference to measure vs the recommended variant is
**completion rate** (how many finish vs drop) — that is the A/B in `experience-consistency-and-ab-plan.md`.

---

## main/prl-main-ai-forward.json  (Lyro-forward)

**What it is.** Rigid path for "I know what I need" and "Have someone call me"; **hands "Help me choose"
and "Something else" to Lyro AI** (the flow ends on an open invitation and Lyro picks up).

**How to test.** Requires **Lyro enabled**. Import/activate/incognito. **Acceptance:**
- "I know what I need" runs the rigid capture path (as above).
- "Help me choose" ends the flow and Lyro takes over the conversation.
- CRITICAL: an AI-only conversation must still deliver a lead — it does NOT pass the capture form, so it
  reaches Sugar only via **ai-bridge** below. Do not rely on this variant until the bridge is verified, or
  "Help me choose" is a lead-loss path. Run the live-model eval (`prl_lyro_eval.py`) before trusting Lyro.

---

## ai-bridge/prl-ai-handoff-bridge.json

**What it is.** A short capture chain a Lyro conversation steers into, so an AI-qualified visitor still
produces a delivered lead (name/company/phone/email/state).

**How to test.** ⚠ **Trigger must be set manually after import** — it ships as `onFirstVisit` as a
placeholder and WILL collide with the main flow if activated as-is. Confirm with Tidio support whether Lyro
can hand to a flow directly or must steer the visitor to a quick reply, set that trigger, THEN test.
**Acceptance:** after a Lyro chat, the visitor is steered here, gives the fields, and a complete lead lands.

---

## sem-onramps/prl-sem-*.json  (paid-search landing pages)

**What they are.** URL-triggered onramps (fire on a page whose URL contains the slug, e.g. `sabic-alternatives`,
`lexan`, `ultem`, `noryl`, `valox`). Open with a competitor-specific greeting, capture a high-intent
replacement lead. They **never state a match** — they capture the grade + conditions and route to a specialist.

**How to test.** These live on the **live prlresins.com Unbounce landers**, so adding the Tidio snippet there
is a **production change needing Todd's go-ahead** — import + leave inactive until then. To test in isolation:
import, temporarily set the trigger to a test URL you control, visit that URL. **Acceptance:** the
competitor-specific greeting fires; it asks the grade + conditions; it captures name/company/phone/email/state;
it never asserts an equivalent grade or a spec.

---

## After capture works: wiring delivery to SugarCRM (the sandbox-gated step)

None of these write to your CRM yet. Delivery = the flow's webhook / API-call node → Zapier Catch Hook →
Sugar Create-Record, tested against the **SugarCRM sandbox** (not production). That is the last go-live step
and the one thing still waiting on sandbox access. Full plan: `prl-lyro/TEST-PLAN-go-live.md` (Layer 3).
