# PRL Lyro Configuration Plan — v2 (post-gauntlet, de-risked)
_2026-08-06 · Rewritten after a 3-lens ARCS gauntlet (scope-fidelity, Todd-preference, technical FM).
v1 (03e8f50) was a "configure 80% of Lyro now" bundle; the gauntlet proved that unfaithful to the sold
phase-gates and quietly spec-fabrication-prone. This version is scoped to **Phase 1.5 only**, gated, capped._

## What the gauntlet changed (read this first)
The v1 plan failed three hard tests. All three fixes are now baked in below:
1. **Scope:** v1 folded 1.3 (competitor recognition), 1.4 (OEM/molder persona), and 1.1/1.2 (webhook/baseline)
   into the last, optional, $3,500 phase — collapsing the phase-gated ladder Todd is paying predictability for.
   → v2 is **Lyro-only**; everything else is tagged "deferred to its sold phase."
2. **Fabrication:** loading grade tech-sheet PDFs + the UL explainer as free KB *licenses* Lyro to answer
   spec/cert questions — the exact opposite of the never-fabricate requirement, with a fabricated-cert path.
   → v2 keeps **all specs/certs/prices/lead-times OUT of the KB**, so they route to a human by construction.
3. **Architecture:** the Lyro→capture-Flow→webhook handoff is unproven (enabling Lyro auto-disables Flows).
   → v2 makes that the **first in-account verification gate**; no build starts until it's confirmed.

---

## Gauntlet ledger (ranked, cross-lens)
| # | class | finding | sev | mitigation (now in plan) | gate/owner |
|---|---|---|---|---|---|
| 1 | fabrication | KB loading spec sheets + UL explainer licenses spec/cert answers; UL+grade → fabricated cert | **Crit** | Specs/certs/UL/price/lead-time never in KB; hard-route to human; test the adversarial prompt in staging | Go-live gate |
| 2 | architecture | Lyro front door auto-disables Flows; the handoff that fires the webhook is unverified | **Crit** | Verify Lyro→Flow handoff + tag propagation in-account before any build | Build gate (in-account) |
| 3 | scope | Plan bundled 1.3+1.4+1.1/1.2 into the 1.5 envelope, undercutting the phase ladder | **Crit** | Re-scoped to 1.5-only; xref→1.3, persona→1.4, webhook/baseline→1.1/1.2 | Zach (re-scope) |
| 4 | cost-bubble | Per-conversation billing, quota 50, "burns fast"; v1 offered only a soft routing heuristic | High | Hard cap: disable overage auto-buy; fall back to Flow/handoff at quota; alert Todd first | Config gate |
| 5 | friend-not-foe | Lyro scoped to answer the exact Qs reps own + channel attribution reads as rep-scoreboard | High | Reposition as after-hours/overflow catcher that hands the lead TO a named rep; attribution channel-level + rep-anonymous, in writing | Positioning (hard) |
| 6 | dependency | File-import (PDF) tier gating unverified; whole KB approach assumes it's available | High | Confirm file-import tier in-account before build (go/no-go) | Build gate (Tidio review) |
| 7 | dependency | phone_work required in Sugar but bot treats it optional → silent CRM-write failure | High | Make phone required in the Flow form OR approved placeholder; no live write until sandbox/test-lead | Todd decision + sandbox |
| 8 | sequencing | 1.5 sold as LAST + kill-switch ("if AI economics don't check out, we don't turn it on") — absent in v1 | High | Restated as the go-live gate header below | — |
| 9 | staleness | 2021-dated sheets / "Jun16" UL doc presented as current if loaded | Med | Excluded from KB (see fix #1); manifest is a dated ledger | — |
| 10 | tempo | Scattered "waiting-on-Todd" gates = off-tempo stress for a linear pilot | Med | All Todd inputs batched into ONE checklist (bottom) | Zach |
| 11 | guardrail-integrity | Guidance char limit undocumented; never-fabricate clause could be truncated | Med | Put never-fabricate clause FIRST; verify saved prompt reads back complete | Config gate |
| 12 | failure-net | Webhook "success" shown to user even if Sugar write fails | Low | Zapier retry/task-history + email-the-lead fallback on error | 1.2 build |
| 13 | perception | Jargon (wedge/SSOT/attribution) leaks and raises Zach's perceived threat | Low | File stays internal; translate to Todd's words (boring/after-hours/nobody-replaced/capped) | Comms |

---

## Scope boundary (what 1.5 IS and is NOT)
**1.5 "A smarter assistant" ($3,500, ~14h) = Lyro Q&A on non-sensitive, application-level content, plus its
guardrails, handoff, and cost cap.** It runs **only after the 1.2 receipt closes** (delivery + handoff proven),
and it is **gated by the AI-economics kill-switch: if the numbers don't check out, we don't turn it on.**

Deferred to their sold phases (do NOT build under 1.5):
- **Competitor cross-reference recognition** → **1.3** ($4,000).
- **OEM vs molder persona branching/tagging** → **1.4** ($6,000).
- **Lead-delivery webhook + business-email enrichment + the 4-hour baseline** → **1.1 / 1.2**.

## First-principles: why this order, not out of order
The one law under the whole sequence, in Todd's language: **each phase kills a variance source before the
next phase is allowed to depend on it.** Building out of order means standing on ground you haven't proven —
which is turbulence, the exact thing he is paying for predictability to avoid. The order is not
project-management taste; it is the order in which uncertainty actually collapses.

- **1.1 / 1.2 must be first — prove the pipe, and set the baseline.** Every later phase only produces *leads*.
  A lead that cannot reliably reach the CRM is a lead lost, so a smarter bot or better recognition built on an
  unproven pipe is a more sophisticated machine feeding a broken pipe: more capability, zero captured value,
  and an *invisible* failure that looks like it is working (the exact failure mode the gauntlet flagged). And
  1.2 sets the **before-number**. You cannot measure what any later phase *adds* (net-new attributable
  revenue) without it — so measure-first is a hard precondition, not a nicety.
- **1.3 (knowledge) before 1.5 (the voice that speaks it).** Lyro answers *from* the knowledge base. Turn the
  AI on before that KB is curated and verified and it fabricates or mis-answers from thin, unvetted content —
  the one true ruin risk here: a wrong spec or cert handed to a customer. Knowledge must be built and proven
  before the assistant that speaks from it is switched on. Knowledge before voice.
- **1.4 (who arrives + what they see) before/with 1.5.** 1.4 shapes traffic quality and the OEM-vs-molder
  split. Driving *paid* traffic (real money per click) into an unproven funnel burns spend on a leaky system;
  and the persona structure built in 1.4 is what lets 1.5's assistant tailor answers at all. Funnel before
  traffic; persona structure before persona-aware AI.
- **1.5 last, and optional (kill-switch).** Lyro is the highest-variance, highest-cost-risk, most-dependent,
  lowest-floor piece: per-conversation billing (cost variance), and it needs delivery + KB + personas all
  already true. Put the most uncertain and most cost-variable bet **last** and three things fall out: (a)
  every input it relies on is already proven, (b) there is real traffic to measure its economics against
  before committing, and (c) if the economics do not check out, you kill it and *everything below still
  stands*. Last = maximum information before the least-certain bet, minimum blast radius if it fails.

There is also a mechanical reason the order is load-bearing: the **receipt-calibrated pricing chain** re-prices
each phase from the *actual* of the one before it. Run them out of order and the calibration breaks — you would
be pricing 1.5 against a 1.2 that has not happened yet. The sequence is what makes "no number ever lands
outside a range you already saw" true.

---

## The 1.5 build (scoped, in-account-gated)

### A. Knowledge base — application-level only (the guardrail is what's ABSENT)
- **Load:** what PRL makes at the family/market level (the resin families, the markets they serve), the
  application **sell sheets** (EE, Medical, Transportation, Building, Consumer, Sustainability, Structural
  Foam), general company/process info. Site crawl capped at 60 pages → point it at the market/capability pages.
- **Never load (routes to human by construction):** per-grade **property values / datasheets**, **UL /
  certification status or file numbers**, **prices**, **lead times**. This is what makes never-fabricate
  structural, not a prompt promise. The 11 grade tech-sheet PDFs and the UL explainer stay in the repo for
  human reference, **out of Lyro's KB.**
- Staleness: nothing dated/superseded goes in; the KB manifest is a dated ledger.

### B. Guidance prompt (never-fabricate clause FIRST, in case of truncation)
> Never state a specific property value, UL or certification status, file number, price, or lead time. If
> asked for any of these, say you'll connect them to a PRL specialist and capture their contact. [then tone:]
> You are the after-hours assistant for Polymer Resources. Be concise, plain, friendly; no emoji. Answer only
> from PRL's knowledge base. You catch questions when the team is unavailable and hand every real lead to a
> PRL rep — you do not replace them.

### C. Flow ↔ Lyro architecture (VERIFY IN-ACCOUNT BEFORE BUILDING)
- Confirm the exact primitive by which a Lyro conversation hands off to capture + fires the webhook, given
  Lyro auto-disables "Visitor says" Flows. Confirm a tag set in Lyro reaches the webhook payload.
- If no clean handoff exists: capture lives in Lyro's **native handoff/contact form**, or the qualifying
  question + capture sit in a **Flow in front of Lyro**. Decide from what the account actually supports —
  do not assume.
- The irreversible **CRM write stays in the deterministic/Zapier path** (retry + visible task history), never
  a Lyro Action.

### D. Handoff / off-ramp
- Online vs offline behavior set separately so off-hours leads are still captured. Every specs/cert/price/
  lead-time question, and every low-confidence answer, routes to a human with contact capture. Hand the lead
  to a **named rep** (friend-not-foe), not an anonymous queue.

### E. Cost cap (hard, not a heuristic)
- Disable Lyro overage auto-purchase. Set Lyro to fall back to Flow/handoff when the quota is hit. Alert Todd
  **before** any spend. Gate Lyro activation behind the qualifying step so bots/tire-kickers never open a
  billable Lyro conversation. Confirm the plan's real quota in-account.

### F. Measurement (rep-anonymous, channel-level)
- Track resolution rate, handoff rate, leads captured **at the channel level only**. Never per-rep. Framed to
  Todd as "what the after-hours channel adds," never "bot vs rep." (Baseline/4-hour attribution is a **1.2**
  deliverable, not 1.5.)

---

## Config as versioned artifact (extensible)
```
runtime/recoil/generated/prl-lyro/
  guidance-prompt.md     # §B verbatim, never-fabricate clause first
  kb-manifest.md         # loaded vs held-out + WHY (the guardrail ledger; dated)
  handoff-policy.md      # online/offline + escalation + rep-anonymous attribution rule
  costcap-policy.md      # overage off, quota fallback, alert threshold
```
(No qualifying-flow.md here — persona branching is 1.4.)

---

## In-account verification gates (all must pass before 1.5 build; most need the pending Tidio review)
1. Lyro→Flow handoff primitive + tag propagation exist (#2). 2. File-import (PDF) tier available (#6).
3. Guidance char limit ≥ the prompt, never-fabricate clause survives (#11). 4. Real Lyro quota + overage
controls (#4).

## Blocked-until (dependencies)
- **SugarCRM sandbox / one approved labelled test lead** — no live CRM write before this.
- **Tidio account/support review** — gates 1-4 above.
- **phone_work decision** (required-in-form vs placeholder) — Todd's call (#7).

## Single batched Todd checklist (one predictable ask, not scattered gates)
1. Phone: require it in the form, or approve a placeholder value? 2. Confirm after-hours-catcher positioning
(bot hands leads to a named rep, nobody replaced). 3. Sandbox or one labelled test lead to prove delivery.
(UL/cert source is a **1.3+** ask, not needed for 1.5 — kept off this list on purpose.)

---
## Research basis
Sourced Tidio/Lyro pass (2025-26). Native guardrail (answer-from-KB + auto-forward-to-human) is well-sourced
and load-bearing. Unverified, now promoted to in-account gates: language count, Guidance char limit, per-plan
quotas, file-import tier. Key sources: help.tidio.com Data-sources / Lyro Guidance / flows-Lyro-agents / Lyro
Actions; tidio.com/blog/lyro-ai-training; chatimize review.
