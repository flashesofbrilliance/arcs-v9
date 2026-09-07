---
title: Gauntlet CBA — is the counterpart-gauntlet worth its tokens?
version: v1
status: draft
created: 2026-09-07
owner: Zach
tool: scripts/gauntlet_cba.py
doctrine: ADR-075 (metabolic router — mechanical/judgment split), token-savings-bank (open-source/)
---

# Gauntlet CBA v1

Turns "is burning ~3M tokens on this gauntlet worth it?" from a gut call into a
number you can read. Companion tool: `scripts/gauntlet_cba.py` (stdlib, pure
arithmetic — the mechanical half of ADR-075; the judgment half is which facets
are safe to route cheaper, which stays a human decision).

## What the gauntlet actually is

`.claude/workflows/counterpart-gauntlet.js` — the pre-send honesty gate on a
counterpart artifact family. Two phases, **7 agents**:

- **Phase 1 · "Counterpart reads it"** — 6 persona facets run *in parallel*,
  each reading the **whole corpus** (transcript + full comms thread + every
  surface's rendered HTML + register/situational memory) from scratch and
  hunting for pathogens/cracks/breaks grounded in a real quote or memory fact.
- **Phase 2 · "Verify + synthesize"** — 1 adversarial verifier (`effort:high`)
  re-reads the corpus + all 6 findings, rejects over-flags, dedups, ranks by
  relationship-cost, prescribes fixes in-register.

**The cost driver is structural, not per-finding:** the same source material is
ingested **7 times** (6 facets + synth), and parallel fan-out agents each carry
their own context, so they cannot share a prompt-cache prefix. That 7× re-read
— not the model tier — is where the tokens go.

## The numbers (defaults: C=400k tokens/agent → ~2.9M/run; Opus $5/$25, Sonnet 5 $2/$10, cache read 0.1×)

| Scenario | Per run | 4-pass heal cycle |
|---|---|---|
| **Baseline** (all-Opus, full 6-facet re-read) | **$15.81** | **$63.26** |
| Lever 1 — tier-route mechanical facets to Sonnet | $13.18 (−17%) | — |
| Lever 2 — mechanical pre-pass + cached register card (facets read ~10% of C) | $2.74 (−83%) | — |
| **Combined** — pass 1 full+routed, passes 2–N incremental delta | $13.18 (pass 1) | **$18.14 (−71%)** |

**Read this:** one run is already cheap. The scary "3M tokens" is ~$16. The real
spend is re-running the full 6-facet corpus re-read on **every heal iteration**.
That is the thing to optimize — and the fix raises catch-rate, not lowers it.

## Per-agent mechanical/judgment split (the routing decision)

Correctness outranks budget (token-savings-bank, rule 0): a **judgment facet
never drops tier**, because the gauntlet is an honesty gate and a missed
trust-breaker costs a relationship, not a dollar. Only the mechanically-scorable
classes move.

| Agent | Class | Detectable how? | Lever |
|---|---|---|---|
| `skeptic` | **mechanical** | oversell / banned-lexicon / "words they'd never say" → grep against a register wordlist | route → Sonnet; pre-pass catches most |
| `bitesize` | **mechanical** | density, cross-surface repetition → diff/dedup over the HTML surfaces | route → Sonnet; pre-pass catches most |
| `builder` | **mixed** | false precision + copy-vs-data contradiction (mechanical) / mechanism read (judgment) | keep Opus; pre-pass removes the mechanical part |
| `practitioner` | **judgment** | "does it respect what they already solved" — meaning | **stays Opus** |
| `connector` | **judgment** | "does it feel managed / sized as a lead" — tone | **stays Opus** |
| `situational` | **judgment** | "does it read their situation right / project a narrative" — deep judgment | **stays Opus** |

Plus two air-gap / integrity checks that are **pure grep** and should never cost
an agent token at all: employer named more than once, off-page referrer leak,
retired-surface links. These belong in the pre-pass regardless.

## The three levers (in build order)

1. **Mechanical pre-pass** (`scripts/gauntlet_prepass.py`, a script ≈ $0) —
   **SHIPPED 2026-09-07.** Before spawning agents, sweep the deterministic
   defect classes ONCE — banned lexicon, cross-surface duplicate spans, false
   precision, employer over-exposure — and compose `scripts/leak_check.sh` for
   the air-gap verdict. Emits a baseline JSON that `counterpart-gauntlet.js`
   injects (via `args.mechanical_baseline`) into every facet + the synth.
   - **What shipped is ADDITIVE**: facets stop re-hunting these classes and the
     synth dedupes against them; **no facet is removed and no judgment read is
     shrunk**, so catch-rate strictly rises. The immediate return is
     *correctness* (these defects are now caught every run, deterministically,
     not probabilistically by whichever agent looked) plus a modest token drop
     from eliminated re-hunting — NOT yet the full Lever-2 model number.
   - The **83%/run** figure in the table above assumes the *aggressive* form
     (facets read a distilled register card ≈10% of C instead of the raw
     corpus). That read-shrink is the measured follow-up below, not what shipped.
2. **Read-shrink + incremental delta passes** — **NEXT, needs a real family
   measured first.** Distill a cached register card once; have facets read the
   card + only the *changed* surface on heal passes 2–N (and only the facets
   whose class the change touched). This is where the modeled **71% cycle**
   saving lives. Gated on measuring C on a real family (surfaces can be large
   HTML) to confirm the ≈10%-of-C assumption before trusting the number.
3. **Tier-route** the two mechanical facets (`skeptic`, `bitesize`) to Sonnet 5.
   Smallest lever (~17%); do it, but it is not the main event.

**Guardrail:** none of these touch the judgment facets or the `effort:high`
synth. The gauntlet's catch-rate on trust-breakers is sacred; these levers cut
redundant *reads*, not *scrutiny*. The pre-pass only ADDS deterministic catches.

## CBA learning ledger (fill actuals on the next real gauntlet run)

| Run | Est tokens | Actual tokens | Est $ | Actual $ | Lever applied | What we learned → next estimate |
|---|---|---|---|---|---|---|
| (model baseline @ C=400k) | ~2.9M/run | — | ~$15.81/run | — | none | Structural: 7× corpus re-read dominates; caching can't help parallel fan-out. Optimize the re-read, not the tier. |
| **Yuri family MEASURED, 2026-09-07** | ~0.6M/run @ C≈70k | surfaces **40,127 raw / 12,849 visible** tok (7 surfaces) | ~$4.26/run · $17.06/4-pass cycle | not yet run through agents | prepass (shipped) | **C=400k was 10× too big for a Yuri-class family.** Real surface corpus ~40k raw / ~13k visible; with transcript+comms+memory C≈70k. So one run ≈ **$4**, a heal cycle ≈ **$17** — at this scale the pre-pass's return is **correctness, not dollars**. The cost lever only bites at large C (big families / long transcripts / many iterations = the original "3M-token" case). Prepass found **3 real candidate defects** (1 banned lexicon + 2 cross-surface dups) and the injected baseline is **1.4 KB** — negligible cost, strictly-additive catch. Next: run the agent phase once with the baseline injected to measure the actual token delta vs. baseline. |

Rule (from the reading-room build plan §6): a run is not "done" until its row is
filled. The ledger routes the next estimate (mechanical) and, when a lever lesson
generalizes, a wisdom memory (judgment).

## Provenance

- Tool: `scripts/gauntlet_cba.py` (this session).
- Pricing: claude-api skill, cached 2026-06-24 (Opus 5 / 4.8 $5/$25, Sonnet 5
  $2/$10, Haiku 4.5 $1/$5; cache read ~0.1× input).
- Gauntlet under analysis: `.claude/workflows/counterpart-gauntlet.js`.
- Doctrine: ADR-075 (mechanical/judgment split), `open-source/token-savings-bank/`.
