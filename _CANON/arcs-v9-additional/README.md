---
name: canon-arcs-v9-additional-documents
description: Additional ARCS canonical documents — whitepapers, case studies, phenomenology
version: 1.0.0
category: canon/reference
---

# ARCS v9 — Additional Canon Documents

Supplementary world-building documents that frame ARCS philosophy, design decisions, and applied case studies. These are **reference materials**, not operational specifications (see `runtime/specs/` for those).

## Document Index

### Foundational Whitepapers & Theory

**`ARCS-WhitePaper-v2-1.md`**
- Core positioning and architecture summary
- Suitable for external sharing / investor / stakeholder communication
- Explains the four zones, Y-gate model, and decision manifold metaphor
- Status: **CANONICAL** (v2.1, latest stable)

**`ARCS-YellowPaper-v1-2.md`**
- Deep technical dive into the DEWY pipeline and operator architecture
- For engineering audience; explains L0–L5 layer system
- Includes pseudo-code examples and decision flow diagrams
- Status: **CANONICAL** (v1.2, latest stable)

### Design & Implementation

**`ARCS-v9-Chapter-Book-Canon.md`**
- Unified narrative framing ARCS as a world (Myst / Hitchhiker's Guide register)
- Explains the **Leisure Suit Larry** mechanic (world remembers your choices)
- Describes the tonal design principles (calm, precise, serious play)
- Used to brief designers and copywriters on brand voice
- Status: **REFERENCE**

**`ARCS-DNA-Omakase-Deck.md`**
- High-level strategic narrative and positioning
- DNA = core identity + values + market niche
- Omakase = "I'll trust your judgment" — the app's ethos toward decision-makers
- Status: **REFERENCE** (internal strategy)

### Archive & Superseded

Older versions of whitepapers and yellowpapers are archived in `archive/specs/deprecated-versions/` and not referenced by active documents.

## Integration with Product

These documents inform:
- **Copy & UX voice** — the "Myst" register and calm design principles from the worldbuilding
- **Brand positioning** — how ARCS is communicated to users and stakeholders
- **Architectural decisions** — the four zones, phase states, Y-gate model ratified in whitepapers
- **Design tokens** — fog-density rendering, earned fidelity principles

## How to Update

1. **If updating a whitepaper or yellowpaper:**
   - Increment minor version (v2.1 → v2.2) for clarifications
   - Increment major version (v2 → v3) only for architectural changes
   - Commit with message: `docs(canon): WhitePaper v2.2 clarification on phase states [NCI:XX]`

2. **If adding a new canonical document:**
   - Write in the **Myst/Hitchhiker's register** — world-building tone, not documentation tone
   - Add to this README with status
   - Link from relevant ADRs if it validates architectural decisions
   - Commit with message: `feat(canon): [Title] [NCI:XX]`

3. **If deprecating a document:**
   - Move file to `archive/` with explanation comment
   - Update this README status to 🟢 ARCHIVED
   - Leave a pointer in the `archive/` so readers know where to find superseded versions

## Version Reference

| Document | Latest Version | Status |
|----------|---|---|
| WhitePaper | v2.1 | CANONICAL |
| YellowPaper | v1.2 | CANONICAL |
| Chapter Canon | v1 | REFERENCE |
| DNA Omakase Deck | v1 | REFERENCE |

## For Readers

**New to ARCS?**
1. Start with `ARCS-v9-Chapter-Book-Canon.md` (world-building context)
2. Then `ARCS-WhitePaper-v2-1.md` (architecture overview)

**Implementing ARCS?**
1. Read `ARCS-YellowPaper-v1-2.md` (technical deep dive)
2. Reference `ARCS-v9-Chapter-Book-Canon.md` for design principles
3. Consult `runtime/specs/` for machine-readable specifications

**Pitching ARCS?**
- Use `ARCS-WhitePaper-v2-1.md` + `ARCS-DNA-Omakase-Deck.md`
- Reference the four zones and earned-fidelity rendering model
