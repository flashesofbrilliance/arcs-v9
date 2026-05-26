# ARCS Repo Map

> **What this is:** Canonical directory ownership, file rules, and cross-repo
> dependency governance for the ARCS v9 project.
> Read this before creating any new file or directory in either repo.

---

## Repos

| Repo | URL | Purpose |
|---|---|---|
| `arcs-v9` | https://github.com/flashesofbrilliance/arcs-v9 | Runtime, canon, scan suite, Next.js app, Prisma schema, Claude Code working repo |
| `arcs-field-os` | https://github.com/flashesofbrilliance/arcs-field-os | Product surface specs, JTBD map, design system, roadmap, orient PRD |

---

## arcs-v9 Directory Ownership

| Directory / File | Owns | Do not put here |
|---|---|---|
| `MEMORY.md` | Versioned session log — append only | Implementation notes, specs |
| `SKILL.md` | Claude Code operating contract | Canon content, product specs |
| `CLAUDE.md` | Project map + handoff chain — append only | World physics, agent definitions |
| `WORLD.md` | Physics spec — governing law | Working state, session logs |
| `AGENTS.md` | Agents/workers map, DEWY pipeline | Canon narrative |
| `.claude/` | Agent definitions, skill refs, repo map | Source code, specs |
| `runtime/specs/` | Machine-readable and human-readable runtime specs | Flow docs, canon chapters |
| `runtime/flows/` | Flow documentation (trigger → lifecycle → hooks) | Specs, schema files |
| `canon/` | Narrative canon chapters (Book I, II, etc.) | Implementation specs |
| `scripts/` | Python scan suite (zero external deps) | TypeScript, Next.js code |
| `src/` | Next.js App Router, components, API routes | Python, specs, canon |
| `prisma/` | Prisma schema + migrations | Application logic |
| `exports/` | **Gitignored** — personal scan output data | Anything committed |

---

## arcs-field-os Directory Ownership

| Directory | Owns | Do not put here |
|---|---|---|
| `specs/` | Product surface specs (PRDs, gate specs, surface contracts) | Runtime JSON schemas, canon chapters |
| `jtbd/` | JTBD master map, surface architecture | Implementation flows |
| `artifacts/` | Session artifacts, diagrams, exported docs | Source specs |
| `origins/` | Origin documents, founding context | Working session files |

---

## Cross-Repo Dependency Rules

1. **`arcs-field-os/specs/orient-prd.md` governs `arcs-v9` Issues #2, #3, #4.**
   Read it before touching any of those issues. It is Kairos Locked at v0.1.0.

2. **`arcs-v9/runtime/specs/dewy-receipt-schema-v1.json` governs the Prisma Receipt model.**
   Any change to `prisma/schema.prisma` Receipt must validate against the JSON schema first.

3. **Breaking changes to `arcs-field-os/specs/orient-prd.md` require:**
   - A PR (not a direct push)
   - Version bump to v0.2.0
   - New MEMORY.md entry in `arcs-v9`

4. **`arcs-v9` MEMORY.md must be updated any time `arcs-field-os` specs change.**
   The cross-repo dependency state section tracks what each repo currently relies on.

5. **`exports/` is always gitignored in `arcs-v9`.** Personal scan output data.
   Never recreate, never commit.

---

## File Creation Rules

| Action | Rule |
|---|---|---|
| New spec in `arcs-v9` | Use front-matter: `version`, `status` (DRAFT/REVIEW/ROM), `depends-on`, `blocks` |
| New flow in `arcs-v9` | Must include trigger table, session lifecycle, surface rules, worked example |
| New canon chapter | Max ~15–20k tokens; narrative voice first; mark ROM vs ETHEREAL sections |
| New Python scanner | Must implement full gauntlet interface; no inter-scanner dependencies |
| New TypeScript file | Inline styles only; no CSS files; no new dependencies without asking |
| New directory | Check this file first — it may already have a canonical home |

---

## Versioning Policy

| File | Policy |
|---|---|
| `MEMORY.md` | Append-only; prepend new `## [vX.Y.Z]` entry at top; never delete prior versions |
| `SKILL.md` | Update in place; increment version; add changelog row at bottom |
| `CLAUDE.md` | Append-only; new `## Handoff — vX.Y.Z` section at bottom; never overwrite |
| Spec files | `version` front-matter; rename to `*-v2.md` only on breaking schema change |
| Python scripts | Never overwrite; create `*_v2.py` for breaking changes |
| Kairos Locked files | No in-place edits; version bump + PR required; log in MEMORY.md |

---

## Quick Orientation Sequence

For any new session, run in this order:

```
1. arcs-v9/MEMORY.md      → what happened; current gap status
2. arcs-v9/CLAUDE.md      → latest Handoff section; active pickup point
3. arcs-v9/SKILL.md       → operating contract; priority queue
4. arcs-field-os/specs/orient-prd.md  → if touching Issues #2-4
5. arcs-v9/WORLD.md       → before writing any logic, schema, or route
```

Do not skip steps. Do not reorder.
