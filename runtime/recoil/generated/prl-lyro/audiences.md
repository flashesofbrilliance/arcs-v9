# Tidio Audiences — PRL (SSOT)
_2026-08-07 · Audience design for the PRL bot. **Scope discipline:** this defines the audience *structure* +
routing/tagging (build-now, safe). Full persona-conditional *answers/knowledge* (different content per persona)
is a **1.4** deliverable — not built here. For MVP the knowledge base is SHARED; audiences differ only in the
opener, the handoff routing, and a tag. Tidio "Audiences" (Configure → Audiences) scope which guidance/handoff/
knowledge apply to a segment; Lyro will NOT reliably auto-classify buyer-vs-spec-holder, so assignment is by
explicit rule (a qualifying question, or page/source), never inference._

## The two core audiences (+ default)
1. **MOLDER — injection molder / buyer.** Sources and consumes resin; cares about price, availability,
   drop-in equivalence, lead time, processing. Usually already has a spec.
2. **OEM — design engineer / spec-holder.** Sets the material spec; cares about properties, UL/cert fit for
   the part, which family/grade to design in. The "stickiness" owner.
3. **DEFAULT — unknown.** No signal yet. Generic help + the qualifying question. Never guess.

(Entanglement, from the ICP work: an OEM sets the spec, the molder buys it. A single inquiry can be either.
That is exactly why we ASK rather than infer.)

## How a visitor is assigned to an audience (assignment rules, in priority order)
1. **Qualifying question (primary, MVP):** an early Flow question —
   *"Are you specifying a material for a new part, or sourcing one you already spec?"*
   → "specifying" = OEM · "sourcing / already spec" = MOLDER · skip = DEFAULT. Sets a tag/attribute.
2. **Entry page / URL rule (1.4-leaning, cheap to add):** landing on a `/products/<family>` page leans MOLDER
   (grade-shopping); a market/application page (`/markets/*`) leans OEM (designing for an application). Use as a
   soft prior only, confirmed by the question.
3. **Campaign source (1.4):** SEM/Unbounce campaign param carries the intended persona. Deferred to 1.4.

## What differs per audience (MVP — small, safe deltas only)
| Element | MOLDER | OEM | DEFAULT |
|---|---|---|---|
| Opener | "Sourcing a resin you already spec? I can point you to the right person for equivalence + availability." | "Designing a part and choosing a material? I can connect you with a PRL specialist for the right family/grade." | Generic (see `conversation-starters.md`) |
| Handoff routing | sales / sourcing specialist (territory) | technical / applications specialist | sales manager (default) |
| Tag on the lead | `audience=molder` | `audience=oem` | `audience=unknown` |
| Knowledge | **SHARED** (same KB) | **SHARED** | **SHARED** |

**MVP rule:** knowledge stays shared; only opener + handoff routing + tag vary. Different *answers* per persona
= 1.4.

## Tagging → measurement (rep-anonymous)
Carry the audience tag into the lead payload (a custom field, or into `description` for MVP — see the Sugar
integration design). Enables channel-level "molder vs OEM inquiry mix," never per-rep. Confirms tag propagation
across the Lyro→Flow boundary is one of the in-account verification gates.

## Build-now vs 1.4 (explicit)
- **Build now (SSOT):** this audience taxonomy, the qualifying question, the opener/handoff/tag deltas above.
- **1.4 (activation of persona-conditional content):** different KB emphasis or answers per persona, SEM
  campaign-driven assignment, per-persona landing openers. Do not build here.

## Open decisions (for Todd, batch with the others)
- Confirm the two-audience split matches how PRL thinks about buyers vs spec-holders.
- Which specialist each audience routes to (names/territories).
- Whether the qualifying question wording fits PRL's voice.
