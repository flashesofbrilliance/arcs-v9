# PRL Plan — Pre-mortem Gauntlet (high burden of proof) + refinements
_2026-08-05 · adversarial FM simulation on the current engagement plan. Each FM must survive: is it REAL_
_(evidence, not speculation) · likelihood × impact · de-risk. Only survivors listed. Refinements at the end._

## FM1 — Sandbox never lands → the whole plan deadlocks. [CONFIRMED · High × High]
**Proof:** sandbox has been "pending" since Jul; no committed date; it gates 1.1 go-live, 1.2 audit, and the
OEM↔molder model. AND Zach's own rule is "sandbox-first, no blind prod writes" → if sandbox never comes, the
safety rule itself blocks go-live forever. This is the single point of failure.
**De-risk (NEW):** define an **escape hatch** — if sandbox stalls past a set date, go-live proceeds on ONE
Todd-approved, clearly-labelled prod test lead (created + deleted, with sign-off), which the go-live recap
already contemplates. Escalate the sandbox ask as its own item, not buried in the recap. Name a date.

## FM2 — Feature-drift while the blocker sits. [CONFIRMED · High × High] (the meta-FM)
**Proof:** this session alone added presentation mode, receipts, calendar links, Stripe-per-phase, cascade
Gantt, discovery list, CRM-audit orchestration, KB PDFs, OCR, competitor gating — none of which ships 1.1.
Memory already flags Zach's expansion instinct as the thing to manage; Todd is the discipline anchor. Risk:
budget + energy pour into polish while the actual unlock (sandbox) sits, and 1.1 never crosses the line.
**De-risk:** the budget hold (just set) is the right instrument. **Refinement: hard re-anchor** — no new
build until 1.1 ships OR the sandbox lands. Everything past the KB is parked. Treat new feature ideas as
backlog entries, not this-week work.

## FM3 — The bot hallucinates a certification (the $30K/safety error). [CONFIRMED · Med × Extreme]
**Proof:** LLMs hallucinate; the KB has NO UL-yellow-card/cert data; refusal is currently a prompt guardrail
(soft). A single invented "yes, that grade is UL-listed / FDA-compliant" is a $30K or safety/liability error.
**De-risk (HARDEN):** make cert/spec statements a **deterministic hard block**, not a prompt hope — Lyro must
be structurally unable to assert a cert value; it recognizes the question and hands off. The 1.3 eval's
**refusal test is a go-live gate**, not a nice-to-have. No cert claim without a source row, enforced.

## FM4 — Competitor cross-reference leaks. [CONFIRMED · Med × High]
**Proof:** it's PRL's competitive positioning; if uploaded open to Tidio (against the gating rec) or if the
gating isn't built before the data touches the live bot, a competitor scrapes it anonymously.
**De-risk:** already flagged (don't open-upload; gate behind capture). **Refinement: gating must be BUILT and
verified before the competitor data goes anywhere near the live bot** — add as a hard prerequisite in 1.3,
not a post-launch layer. Until then the competitor PDF stays out of Tidio entirely.

## FM5 — Wrong material recommendation from G/B/B. [CONFIRMED · Med × High]
**Proof:** the G/B/B matrix is family-level, not grade+application-level suitability. A confident "use PBT"
that's wrong for the specific part = a failed part and a liability trail.
**De-risk:** G/B/B answers are framed as **"options to confirm with a specialist," never "use this."** The bot
narrows and routes; it never certifies suitability. Encode in the prompt + eval.

## FM6 — Vendor cost bubble. [CONFIRMED · Med × Med]
**Proof:** the Tidio AI-conversation cap (51/mo → hard-stop vs overage) is UNconfirmed (pending the support
review); ZoomInfo per-lookup is uncapped; Mailgun deliverability unproven.
**De-risk:** **the pending Tidio support review is a hard gate before Lyro is enabled** (confirm cap behavior);
ZoomInfo enrichment gets a spend cap as a config prerequisite; Mailgun on a verified subdomain. Vendor costs
stay PRL's line, surfaced, never buried.

## FM7 — Coordination overrun eaten under fixed-per-phase pricing. [CONFIRMED · Med × Med]
**Proof:** 1.1 overran ~6x on coordination (client-controlled latency), and the pricing is fixed-per-phase =
Zach absorbs overrun within a phase. If coordination keeps overrunning, margin erodes.
**De-risk:** the receipt-calibration re-prices the NEXT phase from the ACTUAL of the last (catches systematic
overrun); the pre-flight checklist + defaults-on-no-response caps client-latency drag. **Refinement:** the
receipt's "wrong if actual outside range" is the tripwire — if a phase blows its hour band on coordination,
that's a documented signal to re-price 1.3+ up, not silently eat it.

## FM8 — Present mode fails on Todd's iPhone. [PLAUSIBLE · Med × Low]
**Proof:** iOS Safari does not support `requestFullscreen` on non-video elements. Todd reads on iOS.
**De-risk:** graceful fallback was coded (the `.catch()` + CSS-overlay present mode works without true
fullscreen). **Refinement: verify** the CSS-overlay present mode + auto-fit actually render on iOS Safari
(the one untested surface); if not, it degrades to normal scroll, which is fine. Low stakes.

## FM9 — Full pricing on a forwardable URL seen by the SM prematurely. [PLAUSIBLE · Low × Med]
**Proof:** prl.arcs.care now carries the full $18k phased pricing and is a link Todd may forward; we stripped
pricing from the Artifact earlier for this exact reason. Zach chose full pricing knowingly.
**De-risk:** **confirm the link stays Todd-controlled** (not broadly link-shared); pricing is framed boring/
predictable so it reads as transparency, not a number to negotiate. Accept if Zach stands by the choice.

## FMs considered and DISMISSED (burden of proof failed)
- "The KB specs are wrong" → **dismissed**: audited, 100% verified vs source.
- "The deck routing breaks (saga)" → **low**: it uses the proven single-wildcard rule + backup exists.
- "Repo leaks the proprietary data" → **low**: private repo, git-only, gating flagged; not speculative-enough to rank.

---

## PLAN REFINEMENTS (what changes)
1. **Sandbox escape hatch + escalation** — name a date; if it stalls, go-live on one Todd-signed labelled test
   lead. Make the sandbox ask its own escalated item (FM1).
2. **Hard re-anchor / no new build until 1.1 ships or sandbox lands** — feature ideas → backlog, not this week (FM2).
3. **Cert/spec = deterministic hard block + the refusal eval is a go-live gate** (FM3).
4. **Competitor gating built + verified BEFORE the data touches the live bot; competitor PDF out of Tidio till then** (FM4).
5. **G/B/B = "options to confirm with a specialist," never a directive** (FM5).
6. **Tidio support review = hard gate before Lyro; ZoomInfo spend cap as prerequisite** (FM6).
7. **Receipt tripwire on coordination overrun → re-price next phase, don't eat it** (FM7).
8. **Verify iOS Safari present-mode fallback** (FM8).
9. **Confirm prl.arcs.care link audience with Todd** (FM9).

**Net read:** the plan is sound; its two structural risks are both about *the same thing* — the sandbox
gate (FM1) and the temptation to build around it instead of pushing on it (FM2). The budget hold + the
re-anchor are the highest-leverage de-risks. The 0%-hallucination bar is only met if refusal is a hard,
eval-gated block, not a prompt. Everything else is bounded.
