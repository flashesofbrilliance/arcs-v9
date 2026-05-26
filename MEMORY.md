# ARCS v9 — Memory Log

> **Versioning convention:** append new entries at top; never delete prior versions.
> Format: `## [vX.Y.Z] YYYY-MM-DD — <what changed>`

---

## [v0.2.0] 2026-05-26 — Perplexity session: Orient PRD, DEWY schema, handoff v0.2.0 + post-handoff Claude Code commits

### Session context
- Operator: Zach Harris (`flashesofbrilliance`)
- Working environment: Perplexity ARCS Space (v8.5 Field OS)
- Session goal: push Orient PRD (Kairos Lock), DEWY receipt JSON schema, updated handoff file, MEMORY v0.2.0
- Kairos Lock declared on `arcs-field-os/specs/orient-prd.md` — breaking changes require v0.2.0 + PR

### Artifacts pushed this session

#### arcs-field-os
| Commit SHA | File | What it is |
|---|---|---|
| `618022004033d72b` | `specs/orient-prd.md` v0.1.0 | Governing authority for Orient surface. Kairos Lock active. L0–L5 pipeline fully specced with worked examples. NULL/OM/UNDEFINED coverage at every stage gate. |
| `79b7261` (prior) | `jtbd/jtbd-master-map.md` v0.1.0 | Canonical four-surface architecture (Calibrate → Orient → Chart Course → Detect) |
| (prior) | `specs/index.md` | Spec registry with authoring priority queue |

#### arcs-v9
| Commit SHA | File | What it is |
|---|---|---|
| `20916740` | `runtime/specs/dewy-receipt-schema-v1.json` | Machine-readable JSON Schema Draft 07. Full field coverage from orient-prd.md §3 L5. Source of truth for Receipt model. Prisma schema must conform. |
| `20916740` | `CLAUDE.md` (appended) | Handoff v0.2.0 section appended. v0.1.0 preserved verbatim above it. |
| `35d32da6` (prior) | `MEMORY.md` v0.1.0 | Initial memory log — baseline audit |
| `35d32da6` (prior) | `SKILL.md` v0.1.0 | Skill contract, priority queue, ROM primitives |
| `55009d62` (prior) | `CLAUDE.md` (appended) | Handoff v0.1.0 section appended |

### Post-handoff Claude Code commits (landed after our last push)
| Commit SHA | Date | What it does |
|---|---|---|
| [`a38d7f2`](https://github.com/flashesofbrilliance/arcs-v9/commit/a38d7f2acf29133732a2eae4a266eb8e06059631) | 2026-05-26 17:11 | Versioned output tree — `exports/{domain}/YYYY-MM-DD/` + `exports/receipts/` auto-write on `arcs_cli.py run`. `arcs_core.py` gains `versioned_out_dir(domain)` + `receipts_dir()` helpers. [NCI:75] |
| [`fa8c54d`](https://github.com/flashesofbrilliance/arcs-v9/commit/fa8c54df9d1676bfd27155dbc1adae916bba103a) | 2026-05-26 17:32 | `.gitignore` updated — `exports/` and local scan outputs excluded (personal data, not source) |

### Cross-repo dependency state
- `arcs-field-os/specs/orient-prd.md` is the governing authority for arcs-v9 Issues #2, #3, #4
- `arcs-v9/runtime/specs/dewy-receipt-schema-v1.json` is the source of truth for the Receipt Prisma model
- Any Prisma schema changes to `Receipt` must be validated against the JSON schema before commit
- `arcs-field-os` spec changes require a `MEMORY.md` entry in arcs-v9

### Open gaps (updated status)
```
runtime/specs/dewy-receipt-schema-v1.json   ✅ EXISTS — wire into Prisma (Issue #2 active)
runtime/specs/dewy-receipt-schema-v1.md     🔴 CREATE — human-readable companion (Issue #2)
runtime/specs/time-quality-attribution-rom.json  🔴 CREATE (Issue #3)
runtime/flows/question-compass-to-dewy.md   🔴 CREATE (Issue #4)
canon/book-ii-time-firmware-modes.md        🔴 CREATE — after #3 (Issue #5)
arcs-field-os/specs/hold-reject-gate.md     🔴 NOT YET WRITTEN — HOLD/REJECT logic lives in orient-prd.md §2.2 for now
```

### Next move for next session
1. Read `CLAUDE.md` → Handoff v0.2.0 section (active pickup point)
2. Read `arcs-field-os/specs/orient-prd.md` before touching Issues #2–4
3. Start Issue #2: validate `prisma/schema.prisma` Receipt model against `runtime/specs/dewy-receipt-schema-v1.json`
4. Note: `exports/` directory now exists locally (gitignored) — do not recreate or commit scan output files

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
