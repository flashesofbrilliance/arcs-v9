---
name: honest-proposals-zach
description: Zach's PRIVATE overlay on the honest-proposals method (never publish). Use whenever Zach writes a client proposal, reply, services agreement or Exhibit A from an engagement record. Layers his terms, voice, Connecticut agreement habits, counterpart gauntlet and decision receipts on top of the public method.
---

# honest-proposals-zach (private)

Method: `_ARTIFACTS/honest-proposals-skill/SKILL.md` (staging copy of the public skill). Read it, then apply these
overrides. Never copy anything from a real engagement folder into the public method or its example.

## Overrides

1. **Start from a real instance for wording, the fictional one for shape.** The record shape and rules come from
   `_ARTIFACTS/engagements/example-fictional/`. Agreement wording that a lawyer has read lives in the most recent
   real engagement (today `_ARTIFACTS/engagements/myally-ld/`, v0 schema, rev 27 in a Claude Doc supersedes its
   rendered v2 text). New engagements use schema `engagement-record-v1`.
2. **Payment terms** (memory `payment-terms-new-vs-existing-clients`): a first step under about $2K is 100% at
   signing; a larger fixed fee is 50/50; monthly work bills in advance. These are fields with `source.kind:
   decision`.
3. **Proposal bar** (memory `proposals-narrow-specific-no-pressure-value-first`): narrow, specific, no pressure,
   value from the pains the client named. Box discovery; ship a working slice early
   (memory `avoid-front-loaded-unpaid-discovery`).
3a. **Sanity check, every polish round:** before applying any multi-part copy plan, run the `sanity-check` agent
   with the counterpart's verbatim ask (from the engagement SSOT) and the plan or current draft. On DRIFTED, fix the
   offer first, then polish. Cause: the Louisville proposal drifted into one flavor decision over many rounds that each
   passed every gate (PR 2069).
4. **Gauntlet:** run the `counterpart-gauntlet` workflow with the proposal seats (founder, finance, counsel,
   skeptic, busy reader), passing the transcript and every client output. Record the run in `gauntlet`.
5. **Counsel:** a Connecticut lawyer reads each new agreement template version once; record it in `counsel_review`
   with `by_role: "Connecticut counsel"`, never the lawyer's name.
6. **Receipts:** `ex_ante` before the send; after the reply, `close` plus one `decision_receipt` row
   (AGENTS.md, "Receipts or it didn't happen"). Send only on Zach's explicit yes
   (memory `confirm-before-outbound-send-even-when-authorized`).
7. **Client pages:** a client page tab renders from the record (`scripts/myally_hub_sync.py` pattern); the leak
   ceiling keeps full-build pricing off it until the paid step. Run `page_gate.py --counterpart` on it.
8. **Before any public use**, run the pre-call qualification gate on unverified inbound
   (memory `unverified-inbound-starts-at-bad-faith-reference-class`).

## Checks

```
python3 scripts/engagement_render.py --dir _ARTIFACTS/engagements/<slug>
python3 scripts/proposal_lint.py --dir _ARTIFACTS/engagements/<slug>
python3 scripts/proposal_lint.py --send-ready --dir _ARTIFACTS/engagements/<slug>
```
