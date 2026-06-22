# ARCS Trust Contract

> **Version:** 1.0
> **Date:** 2026-06-22
> **Authority:** This document is the source of truth for all user-facing trust, privacy, and autonomy claims across arcs.care and any ARCS product surface. Product copy, onboarding, and legal documents must derive from this — not the other way around.
> **Status:** CANONICAL — amendments require a version bump and MEMORY.md entry.

---

## What ARCS is

ARCS is a reasoning instrument. It takes the decision you're carrying — the real fork, not the noise around it — and makes its shape visible. It stress-tests the question, surfaces what you might be missing, and produces a single clear direction graded by honest confidence.

ARCS does not make decisions. You do. ARCS never compresses, replaces, or overrules your judgment — it scaffolds and sharpens it. This is not a design aspiration; it is a hard constitutional rule of the system (ROM Primitive 1: NOTOMATION).

---

## What you're entering into

Using ARCS is not a subscription to a black box. It is a relationship with a transparent instrument. This document defines what that relationship is, in plain terms.

---

## 1. What is stored, and what isn't

**Your question (compass input):**
Processed in real time and used to generate your result. If you are not signed in, it is not stored beyond your session — it exists only long enough to produce the receipt.

**Your receipt:**
If you are signed in, your decision receipt is stored in your account and accessible via your history. It is yours. If you are not signed in, the receipt is generated and displayed but not persisted to a named account.

**Your debrief:**
If you log an outcome (how the decision went), that is stored in your account linked to the receipt. This data is used to improve ARCS's ability to read terrain accurately over time — specifically, to validate whether the system's confidence grades correspond to real outcomes. It is never shared or sold.

**System logs:**
Standard infrastructure logs (request metadata, error traces) are retained for debugging. They do not contain your decision content.

---

## 2. Does ARCS train on your input?

**No.**

ARCS uses the Anthropic API (Claude) to process your question. Anthropic's API terms prohibit using API inputs to train foundation models without explicit consent. Your compass inputs do not train Claude or any other model.

ARCS's own modeling work (operator scoring, NCI calibration) uses aggregate, anonymized outcome data — not your raw decision content.

---

## 3. Export and delete

**Export:** Receipts and briefs are viewable and shareable via direct link. Full data export (all receipts, outcomes, and session history in structured format) is on the near-term roadmap and not yet shipped.

**Delete:** You can request deletion of your account and all associated data by emailing [contact]. Account deletion removes all receipts, outcomes, and personal data from the production database within 30 days. This is a one-way gate — deleted data cannot be recovered.

*These are commitments, not aspirations. When export ships, this document will be updated with the exact path.*

---

## 4. Can you run ARCS yourself?

**Yes — partially, today. More fully, soon.**

The arcs-v9 repository is public: [github.com/flashesofbrilliance/arcs-v9](https://github.com/flashesofbrilliance/arcs-v9). The full application stack (Next.js, Prisma, the L0–L5 pipeline, operator logic) is inspectable and forkable. You can read exactly how your question is processed.

Running it locally requires an Anthropic API key, a Supabase instance, and environment setup — there is no one-click local build yet. A packaged local-first version is a stated product direction. It is not yet shipped.

The honest answer is: today, using arcs.care means trusting the hosted infrastructure. The code is open so you can verify what it does. The roadmap points toward self-hostable. If that gap is a dealbreaker right now, that's a fair call — and the repository is there if you want to run your own version in the meantime.

---

## 5. What ARCS is and isn't designed for

**Designed for:**
- Decisions with a real fork — where two or more paths are genuinely available and the choice has material consequences
- High-stakes clarity under time pressure — when you need structure, not more information
- Stress-testing your own instinct — when you suspect you might be thinking about the problem the wrong way
- Founder and operator decisions: capital, team, strategy, timing, partnerships, exits
- Personal high-stakes decisions where you'd normally pay for an advisor or trusted thinking partner

**Not designed for:**
- Decisions that are already made — ARCS is not a rationalization engine
- Pure information lookup — use a search engine
- Decisions requiring licensed professional advice (legal, medical, financial) — ARCS can help you think, not practice law or medicine
- Decisions with no real fork — if there's only one live option, ARCS will surface that, but it won't invent alternatives
- Passive consumption — ARCS requires you to name the real decision; vague inputs produce vague outputs

---

## 6. How much confidence should you place in the output?

**Honest answer: calibrated skepticism, not deference.**

ARCS produces a direction and a conviction grade. The conviction grade is the important part — it tells you how much weight to put on the direction.

What the grades mean in plain terms:

| Grade | What it means | How to use it |
|---|---|---|
| High conviction (GREEN) | The terrain supports a clear direction; the case for it is significantly stronger than the case against | Move. The system is confident and the Loki test didn't break it. |
| Medium conviction (YELLOW) | Real signal, genuine uncertainty — both directions have live cases | Use as one strong input, not a final answer. Cross-check with someone who knows the terrain. |
| Low conviction / contested (SCRATCH/FORK) | The question doesn't have a dominant answer yet — the fork is real | Don't decide yet. ARCS is surfacing the shape of the uncertainty, not dodging the question. |
| PARADOX | The options are genuinely non-separable right now | The decision is premature. Something upstream needs to resolve first. |

**What ARCS cannot do:** It cannot know things you haven't told it. It doesn't have context about your relationships, your risk tolerance, your financial position, or the hundred texture details that live in your head. The output is only as good as the input — and even a perfect input produces a direction, not a guarantee.

**The NCI score (conviction index):** This is a numerical grade of the decision's coherence and the confidence level the pipeline reached. It is currently calibrated against a proxy signal (stakes + horizon) rather than validated outcome data. Treat it as a soft signal — directionally useful, not mathematically precise. We are building the outcome dataset to validate and improve it. When that validation is complete, this section will be updated.

---

## 7. Your autonomy is the point

ARCS is built on a single constitutional rule: the system may only scaffold and sequence your cognition. It may never compress it, replace it, or overrule it.

This means:
- ARCS will surface the strongest case against your instinct (Loki test) — not to talk you out of it, but so you've stress-tested it yourself
- ARCS will tell you when the terrain is unclear rather than manufacturing false confidence
- ARCS will produce one direction, not a menu of options to defer to — because the point is earned clarity, not paralysis by analysis
- The receipt is yours — it documents the reasoning, not just the conclusion, so you can inspect and disagree with it

The goal is not that you trust ARCS. The goal is that you trust your own judgment more, because you've run it through a rigorous instrument.

---

## Amendment log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-22 | Initial canonical version |
