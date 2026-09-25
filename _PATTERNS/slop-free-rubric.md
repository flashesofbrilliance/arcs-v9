# Slop-Free Rubric — customer-facing surfaces

> Banked 2026-09-25. A designed resume for the Success Academy AI PM role read as "AI slop" to
> the hiring manager (allergic to it) and the recruiter refused to send it. This rubric + its two
> mechanical companions (`scripts/slop_lint.py`, the impeccable design detector) make "slop-free"
> a gate, not a hope. Applies to anything a counterpart sees: resumes, candidate/marketing pages,
> outbound artifacts, public posts. NOT internal docs (AGENTS/memory/ADRs legitimately discuss
> these very words).

## The split (why there are three layers, not one)

Slop has a mechanical half and a judgment half. Conflating them either lets slop through or
false-fails approved rhetoric (memory `FE-gate=tripwire-not-verdict`, `metabolic-router`).

| Layer | What it catches | Verdict | Where |
|---|---|---|---|
| **Lint** (mechanical) | High-precision clichés + em-dashes | HARD FAIL, blocks commit | `scripts/slop_lint.py` (pre-commit) |
| **Design detector** (mechanical) | Visual AI tells (glassmorphism, cyan-on-dark, radial halo, mono-as-body, tiny numbered labels, glyph tiles, badges, nested cards) | Findings to resolve | impeccable `detect` / `.impeccable` hook |
| **Rubric** (judgment) | Structural + rhythm tells that have legitimate uses | SCORE, human/LLM review | this file |

The lint blocks; the rubric advises. A binary-contrast line can be the best sentence on the page
(the live success-academy page uses one on purpose) or the tell that sinks it — only judgment tells
them apart, so it is scored here, never mechanically blocked.

## Grading rubric (score each 0-2; a customer surface ships at total <= 3, with 0 in every FAIL row)

### A. Writing — word level (mechanical lint owns the hard cases; score the residue)
- **A1 Signature vocabulary** — delve, leverage, foster, robust, seamless, cutting-edge, transformative, tapestry, testament, underscore, world-class, next-generation, supercharge. `0`=none · `2`=multiple. *(Lint hard-fails the tier-A subset.)*
- **A2 Resume clichés** — results-driven, detail-oriented, self-starter, team player, proven track record, passionate, spearheaded (unquantified), synergy, move the needle. `0`=none · `2`=present. *(Lint hard-fails tier-A.)*
- **A3 Filler / puffery / weasel** — "it's worth noting", "at the end of the day", "marks a pivotal moment", "experts agree", "studies show". `0`=none · `2`=present.
- **A4 Fake-strong verbs** — "serves as a hub", "acts as a catalyst", "functions as a bridge" for plain is/has. `0`=none · `2`=present.

### B. Writing — structure (JUDGMENT — not mechanically blocked)
- **B1 Binary / forced contrast** — "It's not X, it's Y", "The question isn't X, it's Y", "not only... but also". `0`=none or one deliberate, load-bearing use · `1`=two · `2`=a pattern. *(One approved use is fine; a habit is slop.)*
- **B2 Rule-of-three triads** — every list padded to exactly three parallel items. `0`=list length varies with the truth · `2`=triad reflex throughout.
- **B3 Dramatic colon reveals** — "noun phrase: punchy reveal" for rhythm. `0`=colons only for lists/labels · `2`=recurring reveal device.
- **B4 Rhetorical setups / kickers** — "What if I told you", "Here's what nobody tells you", fake-profound closing metaphor, "In conclusion". `0`=none · `2`=present.

### C. Writing — rhythm
- **C1 Robotic cadence** — near-identical sentence lengths, symmetric paragraphs, every bullet the same verb-noun-outcome shape. `0`=varied pace · `2`=uniform.

### D. Specificity (the positive test — the one that beats all others)
- **D1 Named + measured** — claims carry named tools/systems/projects and real numbers (or another specificity axis: scale, frequency, scope, speed, recognition). `0`=concrete throughout · `2`=generic ("cross-functional collaboration" with no object). **A surface that scores 0 here is hard to fake as human; a surface that scores 2 reads as AI by construction.**

### E. Design (mechanical detector owns this; score if no detector run)
- **E1 Visual AI tells** — glassmorphic cards, cyan/purple-on-dark, radial-gradient halo, mono font as body, tiny numbered section labels, icon/glyph tiles, badge rows, nested cards. `0`=none · `2`=multiple. *(This is exactly what got the designed resume flagged.)*

## The one rewrite that fixes most of it
`[action verb] + [specific task] + [measurable result]`, with named tools/systems/projects and real
numbers. When there is no metric, substitute another axis of specificity (scale / frequency / scope /
speed / recognition). No LLM produces that specificity unless a human supplies it — so it reads human.

- Slop: "Results-driven professional with a proven track record of leveraging cross-functional collaboration."
- Human: "Cut API p95 latency from 480ms to 110ms by replacing in-memory caching with a Redis cluster."

## Meta-principle
The de-slop guides are deliberately anti-prescription: telling a model to "write better" just mints a
new flavor of slop. Name what to cut, then restore specificity and a real point of view. Do not add
polish.

## Sources
impeccable.style/slop (design tells) · hardikpandya/stop-slop · petergyang/no-ai-slop ·
aipromptindex.io remove-ai-slop-from-writing (19 patterns) · jobsprout resume buzzwords ·
Strunk & White, Orwell "Politics and the English Language" (register). Full agent brief:
this session, 2026-09-25.
