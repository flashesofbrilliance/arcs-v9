---
name: dual-bar-raiser
description: >
  Establishes the two-agent workflow for all ARCS canon work.
  Architect/Bar-Raiser = external agent (Perplexity Space / meta reasoning).
  Implementer/Editor = Claude Code (in-repo drafting, edits, commits).
  Defines how to classify tasks and route them to the right agent.
---

# Dual Bar-Raiser Workflow — ARCS

This project runs two cooperating agents. Knowing which agent owns which work
is the first decision at every session start.

---

## The two roles

### Architect / Bar-Raiser (external — Perplexity Space or equivalent)
Holds ARCS as a whole. Does not touch files directly.

Owns:
- Book II architecture: new Parts, new primitives, new signal types
- Audit protocols: annotation taxonomies (IMPL_GAP / CONSISTENCY / CANON_COLLISION / STYLE)
- Cross-Part consistency and CANON_COLLISION detection
- Handoff format design, quorum/role definitions, meta-process
- Upstream audit runs — producing CONDITIONAL CLEAR packets

Does NOT:
- Edit files in `/Users/zharris/arcs/`
- Commit
- Update CLAUDE.md or MEMORY.md directly

### Implementer / Editor (Claude Code — this agent)
Works the repo. Does not invent architecture.

Owns:
- Drafting and editing specific sections (§X.Y prose)
- Translating CONDITIONAL CLEAR audit packets into concrete file edits
- Applying upstream audit annotations — accepting, rejecting, or deferring each
- Updating CLAUDE.md handoff blocks, MEMORY.md, `.claude/arcs-session-state.md`
- Git commits as deliberate canonization acts
- Flow docs, specs, runtime files under `_CANON/` and `runtime/`

Does NOT:
- Invent new canon structure without an upstream audit packet
- Design new annotation taxonomies
- Declare a Part canonical without a CONDITIONAL CLEAR receipt

---

## Task classification at session start

When the user describes a task, classify it before acting:

| Task type | Routes to |
|---|---|
| "Draft Part VII" / new section from scratch | Architect first → bring back packet → Implementer applies |
| "Translate CONDITIONAL CLEAR for Part V" | Implementer (translation is mechanical application) |
| "Part VI §6.3 has a contradiction — fix it" | Implementer if fix is clear; Architect if fix requires new primitives |
| "Should debrief block arbitration or not?" | Architect (structural decision) |
| "Apply these 3 edits to §5.2" | Implementer |
| "Update CLAUDE.md handoff" | Implementer |
| "Design the formal declaration mechanism for §6.5" | Architect |
| "Write the one sentence that closes VI.4.2" | Implementer |

**When in doubt:** if the work requires inventing a new named concept or changing
how two Parts relate, it's Architect work. If the work applies a decision already made
to a specific paragraph, it's Implementer work.

---

## Prompt template for Architect work

When routing to the external agent, give the user a ready-to-paste prompt:

```
Context: ARCS Book II, [Part name], [section].
Status: DRAFT held — audit pending.
Lens: Forward spec. Weight CONSISTENCY and CANON_COLLISION over IMPL_GAP.

Question: [the specific structural/architectural question]

Relevant text:
[paste the paragraph(s) in question]

Produce: [what you need — e.g. "a named resolution to the X edge case" or
"a sentence that closes the gap between §5.1 and §5.2 without adding new primitives"]
```

---

## Session close obligations

Before ending any session where this skill was active:

1. Update `.claude/arcs-session-state.md` with:
   - What was done (Architect vs Implementer)
   - Last commit SHA
   - Any new protocols or rules agreed
   - Next action + which agent owns it

2. Update CLAUDE.md with a new `## Handoff — vX.Y.Z` block if substantive work landed.

3. If an Architect decision was made verbally but not yet committed to a file,
   flag it explicitly as "VERBAL — needs commit before next session."

---

## Voice and commit discipline

All edits to Book II canon must preserve the existing voice:
- Declarative. No hedging. No bullet-list exposition.
- Concepts named once, precisely, then used consistently.
- Section endings close the section's argument; they do not open the next one.

Commit format: `feat(canon): [what] [NCI:DRAFT or NCI:CANONICAL]`
Commits are canonization acts. Don't commit noise.
