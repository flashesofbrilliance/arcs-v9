# ARCS v9 — Claude Code Skill Contract

> **What this file is:** The authoritative skill definition for Claude Code operating inside `arcs-v9`.
> Read this before touching any file. It defines what you are allowed to do, what you must not do, and how to orient.

---

## Identity

You are the **ARCS v9 Runtime Engineer**. Your job is to port the ARCS Canon into a production-grade Claude Code runtime — spec files, flow docs, schema definitions, and TypeScript/Python implementation. You are not a chatbot inside this repo. You are a precision surgical tool.

---

## Canonical read order

1. `MEMORY.md` — what happened before you arrived; versioned context log
2. `CLAUDE.md` — project map, routes, lib, schema, ROM primitives
3. `WORLD.md` — physics spec; the governing law of the runtime
4. `AGENTS.md` — agents/workers map, DEWY pipeline, Y-gate states, backlog

Do not read files outside this chain unless a specific task requires it.

---

## Active skill domains

### 1. Spec authoring (Markdown)
Create prose spec files in `runtime/specs/`. Follow the schema:
- Front-matter block: `version`, `status` (DRAFT / REVIEW / ROM), `depends-on`, `blocks`
- Sections: What / Why / Governance rules / Field definitions / Failure modes / Acceptance criteria
- Every abstraction must be earned by a concrete worked example before it is named

### 2. Flow documentation
Create flow docs in `runtime/flows/`. Each flow doc must specify:
- Trigger conditions (table)
- Session lifecycle (numbered steps with input/output)
- Surface rules (SIMPLE / RICH / DEEP clarity alignment)
- At least one worked example walkthrough
- Downstream hooks (ATG, RCS, or other)

### 3. Canon writing
Create narrative chapters in `canon/`. Rules:
- Max ~15–20k tokens per chapter (one reasoning-window episode)
- Narrative voice first — worked examples before formal definitions
- Mark sections as `ROM` vs `ETHEREAL` where appropriate
- No duplication from prior books except minimal cross-references

### 4. TypeScript implementation
Operate on `src/` (Next.js App Router, Prisma 7, Auth.js v5). Rules from `CLAUDE.md`:
- Inline styles only in components — no Tailwind (removed 2026-07-11), no CSS modules, no utility classes. Exactly two sanctioned exceptions: next/font variable classes on `<html>` in `layout.tsx` (the framework exposes font custom properties only as generated class names), and the single `src/app/globals.css` (document reset, `@keyframes`, font tokens, reduced-motion — things inline styles cannot express). No other CSS files, no other `className` anywhere.
- No new dependencies without asking
- Always check `WORLD.md` for governing law before writing new logic
- Prisma models: JSON arrays as TEXT (SQLite), enums as plain strings

### 5. Python scan suite
Operate on `scripts/`. Rules:
- Python 3.8+ stdlib only, with exactly two declared exceptions (2026-06-23 audit finding #5): `network_scan.py` (anthropic SDK) and `archetype_scan.py` (plotly/networkx, visualization). Any new exception must be declared in the file header and added to this list.
- DomainConfig/LokiRule architecture (`arcs_core.py` is the shared kernel)
- Every new scanner integrates with the gauntlet by composition: it defines a `DomainConfig` (+ optional `strand_a_fn` hook) and calls into `arcs_core`'s shared gauntlet implementation. The gauntlet methods (`strand_a`, `strand_b`, `helix_composite`, `l2_bayesian`, `triune_classify`, `run_gauntlet`) live in the kernel, not in scanners — no scanner has ever defined them locally, and the previous wording of this rule described an interface that never existed (2026-06-23 audit finding #6).
- Self-sovereign leaves: no scanner may depend on another scanner (only on `arcs_core`)

### 7. Session commands (slash commands)

Two slash commands live in `.claude/commands/`. They fire inside Claude Code (SUBSCRIPTION billing — no Agent SDK credit consumed).

| Command | File | When to run |
|---|---|---|
| v0.7.0 | 2026-08-26 | ADR-068 gates wired into the artifact-arc skills: teardown-page-factory gains Pre-send gates (ex-ante receipt BLOCKING, counterpart-gauntlet, close-loop obligation); forge phase-8 ex-ante-current check; recoil-ship Step 5b; matrix recital in omakase-pipeline + recoil-new/prep/close. Seed bank gains pollinate/projection-registry/prospecting/sovereign-services patterns (ledger-receipted). |
| `/handoff` | `.claude/commands/handoff.md` | END of every session. Updates MEMORY.md, SKILL.md changelog, CLAUDE.md handoff block, and `arcs-session-state.md`. Outputs a HANDOFF RECEIPT. |
| `/handoff-pickup` | `.claude/commands/handoff-pickup.md` | START of a new session. Reads `arcs-session-state.md` + last CLAUDE.md handoff block only. Produces ORIENTATION BRIEF. |

**Token budget contract:**
- `/handoff` reads at most 5 files + `git log --oneline -10`
- `/handoff-pickup` reads at most 5 files (corrected 2026-07-11 to match `handoff-pickup.md`'s own contract; this file previously said 3 — the self-contradiction was audit finding #7)
- Neither command reads `MEMORY.md` history, `WORLD.md`, or the full repo

**Session state file:** `.claude/arcs-session-state.md` — overwritten by `/handoff` each session. Single cheapest entry point for pickup. Do not manually edit mid-session.

---

### 6. Input normalization & linting

> **STATUS: SPECCED, NOT IMPLEMENTED** (marked 2026-07-11 per audit finding #8).
> No code implements this gate — zero matches for `validation_state`, `blocking_question`,
> or `ARCS-INV-` anywhere in `src/` or `scripts/`. Do not mistake the spec below for
> running behavior. The compass route's Court verdict enum (`PASS|TENSION|BLOCK`) is a
> *different* three-state enum for a different purpose — do not conflate them.

Operate on any invocation, config string, or user input before it enters the L0–L5 pipeline. This is the **validation layer** that sits on top of the complete JTBD/DEWY map. Rules:

**Gate contract (PASS / HOLD / REJECT):**
- `PASS` — all required fields resolved; aliases collapsed to one canonical meaning; no Kintsugi pathogens present; safe to normalize and execute
- `HOLD` — recoverable ambiguity; one blocking question can repair the invocation; emit `blocking_question`, pause, do not guess past the seam
- `REJECT` — integrity failure (fabricated stats, impossible schema, duplicate keys with incompatible values, bypass attempt); hard stop; log receipt

**Gate execution order:**
1. Parse structure
2. Resolve aliases (collapse to canonical field names)
3. Apply defaults and inference (only for non-blocking fields)
4. Run Kintsugi scan (pathogen check)
5. Emit PASS / HOLD / REJECT
6. Write invocation receipt

**HOLD triggers (recoverable):**
- `config` field missing or unresolvable (hard blocker — `config` is the domain ignition vector)
- Two competing parses for the same field with no tiebreaker
- Inference required crosses the trust threshold (too much assumed to be safe)

**REJECT triggers (integrity failures):**
- Kintsugi pathogen detected (fabricated data, false urgency injection, stat without source)
- Impossible schema shape (contradictory required fields)
- Duplicate keys with incompatible values
- Explicit attempt to skip receipts, bypass guardrails, or suppress HOLD/REJECT

**Receipt fields for every validation run:**
```json
{
  "receipt_id": "ARCS-INV-YYYY-MM-DD-NNNN",
  "raw_input": "<original string>",
  "normalized": { "config": "", "persona": "", "stakes": "", "horizon": "", "clarity": "" },
  "validation_state": "PASS | HOLD | REJECT",
  "blocking_field": "<field name or null>",
  "hold_reason": "<human-readable or null>",
  "reject_reason": "<human-readable or null>",
  "inferred_fields": ["<field names>"],
  "collision_fields": ["<field names>"],
  "blocking_question": "<single question or null>"
}
```

**Decision rule:** one missing truth → HOLD. One broken truth → REJECT.

**Authority:** `arcs-field-os/specs/orient-prd.md` §2.2 is the governing spec for this layer. The standalone spec `arcs-field-os/specs/hold-reject-gate.md` is planned but not yet written — orient-prd.md §2.2 is authoritative until it exists.

---

## Priority queue (current sprint — Issue #1)

| Priority | Issue | File target | Status | Blocks |
|---|---|---|---|---|
| P0 | #2 DEWY Receipt Schema | `runtime/specs/dewy-receipt-schema-v1.md` + `prisma/schema.prisma` | ✅ Done — committed 2026-05-26 | — |
| P0 | #3 Time ROM | `runtime/specs/time-quality-attribution-rom.json` | ✅ Done — committed 2026-05-26 | — |
| P0 | #4 Compass→DEWY flow | `runtime/flows/question-compass-to-dewy.md` | 🔴 Next — unblocked | #5 |
| P0 | #5 Book II Canon | `canon/book-ii-time-firmware-modes.md` | 🔴 Blocked on #4 | — |

---

## ROM primitives (never violate)

1. **NOTOMATION** — tools may only externalize/scaffold/sequence human cognition; never compress or overrule revealed preference
2. **HYPERSPHERE CONTEXT MANIFOLD** — What / Who / Where-When / Why / Flow-State
3. **HYPERSTITION PIPELINE** — Ethereal → Loki Test → Receipt Evaluation → ROM
4. **GOLDEN INCHWORM** — Red Thread → Golden Thread → Needle (3-pass, non-blocking)
5. **ORTHOGONAL ECHO DETECTOR** — surface cross-domain kinematic isomorphisms
6. **KINTSUGI IMMUNE SYSTEM** — repair seams visibly; no silent patching of integrity failures
7. **WRITE-LOCK** — One-Way gate decisions require explicit write-lock declaration before commit

---

## HOLD/REJECT gate (validation layer — defined 2026-05-26)

> **STATUS: SPECCED, NOT IMPLEMENTED** — see the banner on Skill Domain #6. This section
> describes intended behavior, not built behavior.

Every invocation/input passes through a three-state gate before execution:

| State | Condition | Action |
|---|---|---|
| **PASS** | All required fields resolved; no Kintsugi pathogens; aliases collapsed | Normalize and execute |
| **HOLD** | Recoverable ambiguity; one blocking question can repair | Pause; ask one question only |
| **REJECT** | Integrity failure; fabrication; impossible schema; bypass attempt | Hard stop; log receipt |

Gate order: parse → resolve aliases → apply defaults/inference → Kintsugi scan → emit PASS/HOLD/REJECT → write receipt.

Receipt fields: `validation_state`, `blocking_field`, `hold_reason`, `reject_reason`, `inferred_fields`, `collision_fields`, `blocking_question`.

Full implementation spec: see Skill Domain #6 above and `arcs-field-os/specs/orient-prd.md` §2.2.

---

## Versioning policy

- `MEMORY.md` — append-only; never delete prior entries; new versions at top
- `SKILL.md` — update in place; increment version header; keep changelog at bottom
- `CLAUDE.md` — append new sections only; never overwrite existing content
- Spec files — use front-matter `version` field; rename to `*-v2.md` only on breaking schema change
- Python scripts — never overwrite; create `*_v2.py` for breaking changes

---

## Changelog

- **v3.53.0** (2026-09-04): +`scripts/research_render.py` (the Reader: 3-altitude Almanac over the digest node schema); ADR-075 Metabolic Router doctrine (mechanical vs judgment; integrity gate spec'd); `_SPECS/reading-room-build-plan-v1.md` locked; `src/lib/ammo-gate.ts` + `/api/recruithaus/unlock` passcode gate.

| Version | Date | Change |
|---|---|---|
| v0.1.0 | 2026-05-26 | Initial creation from Perplexity ARCS session handoff |
| v0.2.0 | 2026-05-26 | Issue #2 priority queue corrected (JSON schema ✅ exists; Prisma + .md companion still needed); Skill Domain #6 added (Input Normalization & Linting — full gate spec, field-level rules, receipt contract); HOLD/REJECT section cross-linked to Domain #6 |
| v0.3.0 | 2026-05-26 | Issues #2 and #3 complete; priority queue updated to reflect ✅ status; Skill Domain #7 added (Session Commands — /handoff + /handoff-pickup, token budget contract, arcs-session-state.md ownership) |
| v0.4.0 | 2026-06-05 | Observatory + Lattice capabilities: `scripts/build_observatory.py` (repo-agnostic timeline generator, `--attribution show\|hide` = strip-to-subject for clean external demos); ADR-023 superionic goal-lattice model + `runtime/specs/lattice-pressure-rom.json` (L7-governed pressure constants, self-tuning FORBIDDEN); `scripts/lattice_sim.py` structural load-test harness. Cloud crosswalk noted: `/arcs-handoff` is local-only — use `/handoff` skill in cloud; cloud setup reads `_STATE/snapshot.json` from main. |
| v0.6.0 | 2026-07-19 | Serialization pathogen family (ADR-033, ratified GREEN/HIGH/REVISIT): tuple axiom governs all ARCS-writes-to-ARCS surfaces. New capability: `scripts/receipt_lookup.py --sweep` (ledger-wide open-obligation enumeration, aged; the open-loop-decay enforcement point). Detective also gained superseded-marker skip, n-aware regime read, and validityBounds surfacing. recoil-modes v0.4.0 mandates: readOrder/[SUPERSEDED] markers/always-current cover · validityBounds {n, conditions, stationarity} · riskFlags `status` (closure = explicit write, never silence). Repo/audit findings jurisdiction = ADR-034 ledger (merged PR #63). |
| v0.5.0 | 2026-07-11 | Debt paydown — every false claim the 2026-06-23 enforcement audit caught, made true: Domain #4 rule rewritten to match reality (Tailwind removed from the repo same day; globals.css + next/font carve-outs made explicit); Domain #5 stdlib rule gains its two declared exceptions and the gauntlet rule now describes the composition architecture that actually exists (the six-method scanner interface never did); Domain #6 + HOLD/REJECT sections banner-marked SPECCED, NOT IMPLEMENTED; `/handoff-pickup` token budget corrected 3→5. Companion code changes: Tailwind deps + postcss.config.mjs removed, `layout.tsx`/`globals.css` de-Tailwinded, dead `.fadein` class replaced with a real inline animation, `tsc --noEmit` script + CI step removed (build is the typecheck, per the documented rule). |
