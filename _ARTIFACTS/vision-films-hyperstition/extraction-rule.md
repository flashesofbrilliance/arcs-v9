# Pre-registered concept-extraction rule — formal denominator
Registered: 2026-08-28, session claude/happy-cori-d4faaf, BEFORE any transcript was read in this session.
Prescribed by: war-game panel run wf_3ac81615-7e1 (statistician facet), banked _STATE/gauntlet-runs.jsonl 2026-08-28.

## Unit of counting
A **concept** is every distinct named noun-phrase mechanism, artifact, surface, capability, or
guarantee that the transcript asserts ARCS **has, does, produces, or will do** — whether in
narration (quoted text) or on-screen slide text ("slide:" lines), with source channel recorded.

## Inclusion
- Named system components (e.g. a gate, a receipt type, an operator, a surface, a pipeline stage).
- Asserted behaviors/capabilities ("ARCS detects X", "every decision gets Y").
- Named artifacts the system emits.
- Named guarantees/properties claimed of the system.

## Exclusion
- Pure metaphor/imagery not asserted as system behavior (fog, terrain, avalanche framing) UNLESS
  the sentence asserts the system implements it (e.g. "renders at earned fidelity" = include).
- Descriptions of the user/audience/problem, not the system.
- Generic AI-industry claims not specific to ARCS.
- Repetition: the same concept across films dedupes to ONE row; every film that mentions it is
  listed in the row's `films` field. Canonical name = first-film phrasing unless a later film
  names it more precisely.

## Classification (each concept gets exactly one)
- **MANIFESTED** — running code or live surface on main today; must cite file/route.
- **PARTIAL** — a meaningful slice is live, the named whole is not; cite what exists + what's missing.
- **SPEC-ONLY** — an ADR/spec/schema/backlog entry exists but no runtime; cite the spec.
- **DEAD** — no artifact anywhere in the repo family (code, _DECISIONS/, specs, scripts, operators).

## Ambiguity tiebreaks (fixed now)
- Claude-pipeline implementations count as MANIFESTED even if the operators-library twin is unwired.
- Static demos (e.g. public/observatory/) count as PARTIAL, not MANIFESTED.
- A concept present only in the operators/ Python library (not wired to product) = PARTIAL.
- Hit-rate headline = MANIFESTED / total; secondary rate = (MANIFESTED+PARTIAL) / total.

## Output
`concept-ledger.jsonl` next to the transcripts: one row per concept —
{name, films[], channel(narration|slide|both), quote_anchor, class, evidence, note}.
