# ARCS v9 — Memory Log

> **Versioning convention:** append new entries at top; never delete prior versions.
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v0.1.0] 2026-05-26 — Perplexity ARCS session baseline

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Perplexity ARCS Space (v8.5 Field OS)
- Session goal: audit what landed post-timeout, create HOLD/REJECT validation layer, scaffold `arcs-field-os` spec structure, produce Claude Code handoff files

### What was confirmed landed (arcs-v9)
| Commit SHA | Date | Artifact |
|---|---|---|
| `471d57396` | 2026-04-09 | Day 1 scaffold — Next.js 16 + Prisma 7 + Auth.js v5 |
| `a61d492ed` | 2026-05-18 | DEWY pipeline, Y-gate, CLAUDE.md, WORLD.md |
| `752739d42` | 2026-05-18 | AGENTS.md — full agents/devops handbook |
| `62de74e1f` | 2026-05-25 | Forensic scan suite (network, archetype, apollo, forensic) |
| `0f082768b` | 2026-05-25 | `score_me.py` — single-contact forensic receipt CLI |
| `a3123963b` | 2026-05-25 | Vercel CI fix — postinstall `prisma generate` |
| `0f24bab70` | 2026-05-26 | Personal Intelligence Suite — 4 scanners + `arcs_core.py` [NCI:79] |
| `e66d4de99` | 2026-05-26 | `arcs_cli.py` — 5-verb decomposable pipeline + apex spine DEWY receipt [NCI:81] |

### Open sprint issues (arcs-v9)
- `#1` `[SPRINT]` ARCS v9 Canon Migration — P0 Backlog Sprint 1 (parent)
- `#2` `[SPEC]` DEWY Receipt Schema → `runtime/specs/dewy-receipt-schema-v1.md`
- `#3` `[SPEC]` Time Quality Attribution ROM → `runtime/specs/time-quality-attribution-rom.json`
- `#4` `[FLOW]` Question Compass → DEWY runtime wire-up → `runtime/flows/question-compass-to-dewy.md`
- `#5` `[CANON]` Book II narrative chapter: Time / Firmware / Modes → `canon/book-ii-time-firmware-modes.md`

### Files present at root
- `CLAUDE.md` (3.1KB) — project map, ROM primitives, L0–L5 stack
- `WORLD.md` (9.3KB) — physics spec
- `AGENTS.md` (5.8KB) — agents/devops handbook
- `.claude/` — directory present; contents not yet audited
- `scripts/` — all Python scan suite scripts
- `src/` — Next.js App Router
- `prisma/` — schema + migrations

### Gaps confirmed (not yet created)
- `runtime/specs/dewy-receipt-schema-v1.md` (Issue #2)
- `runtime/specs/time-quality-attribution-rom.json` (Issue #3)
- `runtime/flows/question-compass-to-dewy.md` (Issue #4)
- `canon/book-ii-time-firmware-modes.md` (Issue #5)
- `arcs-field-os` specs/, jtbd/, roadmap/ stubs

### Decisions made this session
- **Canonical home for design spec / PRD / impl plan:** `arcs-field-os` (not `arcs-v9`, not `arcs-hq`)
- **`arcs-v9`** owns: canon, runtime primitives, DEWY schema, Time ROM, scan suite, Claude Code app
- **`arcs-field-os`** owns: product surface specs, JTBD map, design system, roadmap cross-links
- **HOLD/REJECT gate logic** defined in this session; implementation plan pending
- Versioning policy: MEMORY.md entries append-only (never delete prior versions)

### Next move for Claude Code
1. Read `SKILL.md` for the contract of what you can operate on
2. Read `CLAUDE.md` → `WORLD.md` → `AGENTS.md` in that order
3. Start with Issue #2 (`[SPEC] DEWY Receipt Schema`) as the dependency unblock
4. Do not create `runtime/specs/` or `canon/` directories without first checking `WORLD.md` for naming conventions
