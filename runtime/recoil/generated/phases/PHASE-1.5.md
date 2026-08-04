# Phase 1.5 — A smarter assistant (AI), turned on safely
_Todd-safe · LATER · 2026-08-04._

## Where this sits
**LATER.** The last piece, and deliberately last, because it only earns its place once everything under
it is proven safe.

## Scope / what "done" looks like
The bot handles open-ended "help me choose" conversations in its own words, instead of a rigid form,
for the visitors where that fits. It still never states a spec, a certification, or a price. It is
turned on only after its handoff into your CRM is proven, so a good conversation can never fall through
the cracks.

## Best / Base / Worst
| | Effort | Time | What drives it |
|---|---|---|---|
| **Best** | ~8 hrs | ~few days | The AI-to-CRM handoff works as expected on the current plan. |
| **Base** | ~14 hrs | ~1 wk | Normal setup + the safety test set + confirming the plan's limits. |
| **Worst** | ~22 hrs | ~1.5 wks | The AI handoff needs a workaround, or the plan's conversation cap needs a change. |

## Dependencies & what could delay it
- **Blocking:** a short review with the chat vendor's support to confirm two things — how the AI hands a
  lead to the CRM, and what happens at the plan's monthly conversation limit. (Already requested.)
- **Coordination overhead:** scheduling that vendor review.
- **Calendar risk:** dependent on the vendor's response time, not just ours.
- **Out-of-scope:** feeding the AI your proprietary internal forms is deliberately excluded (they stay on
  your servers); revisiting that is a separate decision.

## Payment
- **Base price: $3,500** (fixed for the phase). **Paid before kickoff.**
- **Range:** best case ships sooner at the same price. Worst case stays $3,500 unless a named change
  order applies.
- **Watch item (managed up front):** the chat plan may charge more past a monthly AI-conversation limit.
  We confirm that number **before** turning the AI on, so your tool bill never surprises you. If the cap
  is a hard stop, the AI simply pauses and the rest of the bot keeps working — no lost leads.

## Contingency
- **Min-cost path:** if the AI handoff or the plan economics don't check out, we do not turn it on. The
  rigid bot (Phases 1.1–1.4) stands on its own, so you lose nothing by waiting.
- **Where it could bubble:** a higher chat-tool tier (for higher AI volume) is a PRL tool cost, decided
  by you with the numbers in hand, never assumed.
- **Capital note:** this is the one phase with a real ongoing tool-cost variable; it is surfaced and
  capped before go-live.

## Appendix
- Lyro architecture + the handoff safeguard: `2026-08-03-todd-lyro-ai-layer-v2.md` (internal).
- Guardrails + the eval gate: `2026-08-04-todd-phase-map-1.1-to-1.5.md` (1.5) + safeguards doc.
