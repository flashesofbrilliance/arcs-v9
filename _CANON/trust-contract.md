# ARCS Trust Contract

> **Version:** 1.3
> **Date:** 2026-07-19
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
If you are signed in, your decision receipt is stored in your account and accessible via your history. It is yours. If you are not signed in, the receipt is generated and displayed in your browser only — nothing is written server-side. If you want to keep an anonymous bearing, you can sign in and save it; the write happens only after you authenticate.

**Sharing an anonymous bearing:** If you create a one-time share link for an anonymous bearing, the bearing is encoded inside the link itself — in the URL fragment, which browsers never transmit to a server. Nothing is written server-side; the content travels only in the link you send. The link renders once on the recipient's device (a per-device flag then flips it to a sign-in page), and because the content rides in the link, anyone you send it to can read it — treat it like any message. See ADR-037.

> **Disclosure (2026-07-13 — repair seam, kept visible on purpose):** From launch until
> 2026-07-13, a defect stored anonymous receipts server-side, contrary to this section —
> 48 such receipts existed when it was found. The write path was fixed the same day
> (commit `8b486e8`; the repository is public, so this is verifiable, not just claimed).
> The pre-fix receipts were deliberately retained rather than deleted: receipt links are
> made to be shared, and some are referenced in the wild — deleting them would break
> those references. They carry no account identity. If you ran an anonymous session
> before 2026-07-13: signing in from the same browser claims your receipts automatically,
> and a deletion request (via the inquiry link on arcs.care) will be honored.

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

## 8. How ARCS catches you at the fork

**Honest answer: it doesn't, yet — you have to recognize it and bring it.**

§5 above defines what kinds of decisions ARCS is designed for. It does not address a different question: how do you know you're standing at one of those forks *before* you ever open the compass? Today, the answer is that ARCS does not proactively detect this. There is no background system watching your calendar, your messages, or your behavior for a decision forming and tapping you on the shoulder. You have to notice the fork yourself and bring it to the instrument.

This is a real limitation, not a hidden one. Two things are true at once:

- **It's partly a deliberate boundary, not just a gap.** A system that silently watches your data for "decision-shaped moments" and surfaces itself uninvited is closer to the black box ARCS is explicitly trying not to be (see §7). Discovery without consent is its own trust problem — solving "how do you find the fork" by adding ambient surveillance would trade one trust gap for a worse one.
- **It's also genuinely unbuilt, not fully resolved by that boundary.** A consent-based version of fork-detection — something that helps you notice a decision is forming from signals you've explicitly opted into, rather than ambient monitoring — is a real, not-yet-built direction (`Kairos detection`, tracked as backlog in this repo's `AGENTS.md`, gated behind having enough real outcome data to calibrate it responsibly). It is not shipped. This document will be updated when that changes.

**What exists today instead:** product copy is the current, honest mechanism — surfaces like the homepage's "name the real fork" framing exist to prompt *you* to recognize the moment, not to detect it for you. That's a discovery aid, not a disclosure claim, and it lives in product copy rather than this contract for that reason: it's a UX nudge, not a guarantee about what the system does on your behalf.

---

## Amendment log

| Version | Date | Change |
|---|---|---|
| 1.3 | 2026-07-19 | §1 amended: "Sharing an anonymous bearing" added — one-time share links encode the bearing in the URL fragment (never sent server-side), render once per recipient device, and are readable by anyone holding the link. No server write; ADR-032's no-anonymous-storage invariant is preserved, not reversed. See ADR-037. |
| 1.2 | 2026-07-13 | §1 amended: (a) anonymous receipts clarified — browser-only, nothing written server-side, opt-in save happens strictly post-auth; (b) dated repair-seam disclosure added — pre-fix defect stored 48 anonymous receipts, fixed in `8b486e8`, rows retained (operator decision: shared links reference them), deletion honored on request. See ADR-032. |
| 1.1 | 2026-06-23 | Added §8 — answers Zak's "how will you catch people at the fork" question (previously unaddressed; verified against the full June 16–22 feedback checklist, all six original items were already covered §1–§6) |
| 1.0 | 2026-06-22 | Initial canonical version |
