# Tech-Debt Batch — backgroundable cleanup
**Date:** 2026-07-19 · **Purpose:** items cheap to fix and safe to run as isolated background subagents
(the messy edits happen in *their* context, not the main session — that's the token saving). Grounded in
an actual repo sweep, not guesses.

## Tier A — GREEN: safe to run autonomously in a background batch
Mechanical, independent, build-verifiable. Each is one subagent; they don't touch each other's files.

| # | Item | Evidence | Fix | Verify |
|---|------|----------|-----|--------|
| A1 | **Debug `console.*` shipping to prod** (7 hot ones of 18) — `[COMPASS DATA SAMPLE]`, `[COMPASS PROFILE]` timing, `[logStage]`, cron sweep logs | `src/app/api/compass/route.ts:408,430,434`, `cron/debrief/route.ts:135`, `guide/[receiptId]/page.tsx:706` | Gate behind `NODE_ENV !== 'production'` (or a `DEBUG` flag), or delete pure timing probes | `npx next build` |
| A2 | **Circular/redundant `@`-imports** | `AGENTS.md:7-8` back-imports `@WORLD.md` + `@CLAUDE.md`, but CLAUDE.md is the root that already imports AGENTS.md | Drop the two back-imports from AGENTS.md (loader dedupes, but they're noise + a load-order trap) | grep confirms; session still loads |
| A3 | **`_STATE/` sprawl** | `meta-audit-roadmap-v1.md` (23.8k), `cold-start-v3.1.0.md`, `compass-kit-phase2-handoff.md`, `pickup-*.md` — stale by their own version stamps | Move stale docs to `_ARCHIVE/state/` (on-demand); keep `snapshot.json` + current branch state live | `ls`; snapshot untouched |
| A4 | **Permission-list rot** | `.claude/settings.json` `allow` has 60+ entries incl. opaque `mcp__<uuid>__*` tools | De-dup, drop dead UUID entries, group by server | JSON validates |
| A5 | **Prose-rule audit mis-flag** | `2026-06-23-prose-rule-enforcement-audit.md` headline says `layout.tsx` violates "no className"; but `layout.tsx:60` is the **sanctioned next/font exception** (AGENTS.md Gotcha #2) | Correct the audit doc: that finding is a false positive; the one real `className` in `src/` is allowed | grep: 1 className, sanctioned |
| A6 | **ADR numbering/index debt** | Two files both numbered `ADR-025`; no `ADR-021` exists (gap) | Document the 021 gap in index.json; disambiguate the two 025s (025a/025b as PENDING.md already does) | JSON validates |

## Tier B — YELLOW: needs a decision or review first (NOT autonomous)
Real risk or a product call — do not hand to an unattended agent.

| # | Item | Why not autonomous |
|---|------|--------------------|
| B1 | **3 `eslint-disable` react-hooks** (`dashboard/page.tsx:92,102` exhaustive-deps; `PointerTypeProbe.tsx:24` set-state-in-effect) | Each suppresses a real hook rule — could be a genuine stale-closure/effect bug or a justified escape. Needs per-site judgment; a blind "fix" can introduce render loops. |
| B2 | **`nci_score` impl ≠ spec** | `runtime/flows/question-compass-to-dewy.md:223`: impl collapses NCI to a single int; the DEWY spec (`dewy-receipt-schema-v1.md`) defines a 5-lens object w/ per-lens breakdown. Product decision: build the 5-lens or amend the spec. |
| B3 | **`SageTrace` RLS disabled** | Security, but **out-of-band**: Supabase project is invisible to the MCP (wrong org) — needs the `supabase` CLI. Lives in `_PATTERNS/2026-07-19-out-of-band-actions.md` §D, not this batch. |

## How to run Tier A cheaply
Fan out A1–A6 as **parallel background subagents**, one per item, each: make the edit → `npx next build`
(where it touches code) → commit to `claude/token-efficiency-audit-ip3l3x` with `[NCI:SKIP <reason>]`
(all six are docs/chore/mechanical per ADR-033, so SKIP is correct). Isolated contexts = the file-dump
noise never enters the main session. Estimated: 6 small agents, one build each.
