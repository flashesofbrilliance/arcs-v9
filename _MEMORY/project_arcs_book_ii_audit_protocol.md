---
name: project_arcs_book_ii_audit_protocol
description: "Upstream ARCS audit format for Book II — annotation types, lens shift between Parts IV and V+, and how to translate raw audit packets"
metadata: 
  node_type: memory
  type: project
  originSessionId: 647bf9ab-683a-43f0-8609-916dc754067b
---

## Book II upstream audit protocol

**Format (all Parts):** Section-keyed, sentence-anchored annotations. Each note: section heading → numbered note → quoted sentence → annotation type tag → comment.

**Annotation types:**
- `IMPL_GAP` — spec doesn't match existing implementation (primary for Parts I–IV where RC exists)
- `CONSISTENCY` — internal logical/structural contradiction within the Part itself
- `CANON_COLLISION` — conflict with Parts II–IV (ROM axioms, constitutional court, sessions API, lineage model)
- `STYLE` / `CLARITY` — phrasing that materially affects precision or implementability (use sparingly)

**Lens shift starting Part V:**
- Parts I–IV: primary question = "does this match what RC actually does?" → heavy `IMPL_GAP`
- Part V onward (forward spec): primary questions = internal consistency + canon collision; `IMPL_GAP` mostly irrelevant
- Audit prompt amendment for forward-spec Parts: *"Part V is forward spec only; weight CONSISTENCY and CANON_COLLISION over IMPL_GAP."*

**Part V specific consistency checks to flag if missed:**
- Do gate types / kairos conditions / accumulation steps / modes compose without contradiction?
- Is ordering explicit: gate → kairos → prior update → lineage append?
- Multi-gate edge case (multiple gates fire on same receipt in short window) — named?
- "No silent overwrite" rule (§5.4) compatible with Part IV receipt/lineage/Kintsugi model?

**Translation workflow:**
When upstream audit returns raw CONDITIONAL CLEAR packet → paste raw into session → translate to section-keyed annotation set → accept/reject per item → produce "apply these edits" list for Claude Code.

**Status:**
- Parts I–III: CANONICAL (upstream patches applied)
- Part IV: DRAFT held — CONDITIONAL CLEAR received
- Part V: DRAFT held — audit pending; file at `_CANON/book-ii/part-v-the-accumulation-protocol.md` v0.1.0
