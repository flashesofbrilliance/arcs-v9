# ARCS Invariants — ROM A/B/C (proposed, NOT yet enforced in code)

> Source: `~/.claude/plans/phase-1-2-1-sage-integration-week-1.md` (2026-06-19, dual-bar-raiser
> validated). **Status check (2026-06-22):** the SAGE integration this plan was written for
> already shipped via a different path (Vercel Services `/svc/sage`, `SageTrace` table,
> `SAGE_URL` flag — see `CLAUDE.md` Handoff v2.1.0) and none of these three gates were wired
> into it. This file records the research-grounded rules as a design proposal to retrofit,
> not as something already running. Do not treat any of the below as currently enforced —
> `compass/route.ts` does not call a coherence audit, does not run a pre-synthesis adversarial
> wave, and does not fork goal-threat from hedonic noise in the energy scan today.

## ROM A — Coherence Audit (no receipt exits ungraded)

No receipt exits the Mastering layer (Layer 5) without a coherence audit. Survivability
scores (nciScore, court verdicts, signal classifications) must form an internally coherent
probability space — a de Finetti Dutch-book check: if any combination of the receipt's own
sub-scores implies a contradiction (e.g. "strong_signal" classification paired with a
nci_score in the noise range), that is itself a failure, independent of whether either score
looks individually reasonable. Grounding: Karvetski & Mandel (2020) — coherentization, not
structured analytic technique alone, produces accuracy gains; ACH-style SATs without it do
not.

## ROM B — Dual-Wave Adversarial (pre-synthesis, not post-synthesis)

Adversarial review (Loki, Skeptic, Red Team, Cynic) must include a **Wave 1 pass before
synthesis**, not only a Wave 2 pass after. Wave 1 receives the raw JTBD only — zero
synthesized context, zero access to whatever the pipeline has already concluded — so it
cannot anchor on an answer that doesn't exist yet. Wave 0 gate: before L0 fires, check
whether the question itself already smuggled in an anchor or false premise; reframe before
proceeding if so. Grounding: Fariña et al. (2003) / Pre-Dicta (2026) / PNAS (2023) — bias
cascades across decision stages and compounds; reviewing an already-anchored output (Wave 2
only) catches less than challenging the premise before synthesis exists.

## ROM C — Eudaimonistic Probe (goal-threat vs. hedonic noise)

The energy/discomfort scan must distinguish two signals that are otherwise conflated:
1. **Goal-threat (B-grade signal):** "Does this threaten something I've declared core?"
2. **Hedonic/unfamiliarity (C-grade noise):** "Is this discomfort about real goal-threat, or
   just unfamiliarity?"
Treating discomfort as uniformly meaningful (or uniformly dismissable) loses information; the
fork is what makes the signal usable. Grounding: Nussbaum (2001) — emotions are eudaimonistic
appraisals tracking goal-threat/flourishing, not mere hedonic reaction; conflating the two
degrades the Visceral Translator's actual utility.

## Structural enforcement

- **Write-lock sentinel:** once a receipt has completed Mastering (Layer 5), it is locked —
  no modification. The decision cascade is immutable once committed.
- **Anti-hallucination tripwire:** n<5 observed instances = NO PATTERN. Never declare a
  pattern, trend, or coherence where the sample doesn't support it.
- **Anti-sycophancy trigger:** >80% operator consensus on a non-trivial question fires the
  Immune System (additional adversarial pass). Productive discord is a structural
  requirement, not a failure mode — unanimous agreement above that threshold is itself
  suspicious.
- **Loki trigger condition:** pre-synthesis injection point, runs before L0. Loki's output
  feeds the Orchestrator as a constraint vector, not as commentary appended after the fact.
- **NOTOMATION (carried from CLAUDE.md/AGENTS.md):** never compress, replace, or overrule
  revealed preference. These invariants scaffold and sequence cognition; they do not decide
  on the user's behalf.
- **Client-of-record invariant:** Zach is the only agent authorized to commit an irreversible
  decision. Operators (SAGE, LAB, BAR, etc.) advise; they do not commit on their own
  authority.

## Fallback contract — already true today, independent of ROM A/B/C

If `SAGE_URL` is unset or the fetch fails/times out, the pipeline degrades to Claude-only —
never to an error (`compass/route.ts:189-216`, confirmed live). If ROM A/B/C are ever wired
in, they should preserve this: the Coherence Audit must still run on Claude-only receipts,
not only on SAGE-assisted ones, so a skipped operator never becomes a silently
falsely-confident score.
