# Assumptions ledger — premises held before they were tested

> GENERATED from `_STATE/assumptions.jsonl` by `scripts/assumptions.py render` — do not hand-edit.
> The ethereal stage of the hyperstition pipeline, given a book. A row is registered while it is
> still an assumption, with the test that would decide it. When the test runs it closes to `held`
> or `falsified` and points at its F-row / receipt; the row is never edited, a successor is added.

Rows: 10 · falsified: 4 · held: 2 · open: 4

| id | status | assumption | held by | since | test that would decide | decided |
|---|---|---|---|---|---|---|
| asm-001 | **open** | Everything in the corpus can be orchestrated or choreographed (sequenced by a conductor, or moved by dancers reading shared cues). | both | 2026-09-27 | Name one artifact class that can only be cultivated (scaffolded, measured, waited on) and show a cron or hook that tried to trigger it and failed or lied; if none exists after 30 days of unfold runs, hold. | open |
| asm-002 | **open** | Source trust decays on a 90-day half-life with confirmations weighing one tenth of falsifications. | claude-fable | 2026-09-27 | On 2026-12-27 compare each source's tier to its falsification count in the intervening quarter; a source tiered LOW that falsified twice, or ELEVATED that never did, falsifies the constants. | open |
| asm-003 | **open** | A cold session's first tool call reveals whether a chip leaked: an action means lossless, a re-derivation means the chip carried an inclusion. | claude-fable | 2026-09-27 | Spawn five FLAWLESS stones through the bench and classify each child's first tool call; if a FLAWLESS stone's child re-derives, the lint is missing a check. | open |
| asm-004 | **held** | The two red CI jobs on main (smoke ledger delinquency, leak-check) are inherited and harmless to merge behind, as long as each run's failing steps are verified by name. | both | 2026-09-27 | Any merge whose post-merge main shows a third failing step, or a regression traced to a merge made behind the guard, falsifies it. | 2026-09-27 · `2026-09-27--operator-mcp-bridge-registry-pr559-merge--ZH` |
| asm-005 | **held** | The Claude Code harness loads only the first ~24KB of the memory index. | both | 2026-09-27 | Spawn a session against an over-cap index and read the injected context before any tool call; measure the cutoff. | 2026-09-27 · `memory-index-load-cap-observed` |
| asm-006 | **falsified** | The memory index sync script parses both the bare-slug and legacy link forms. | claude-fable | 2026-09-26 | Run --append against a bare-slug index and count appended rows; any duplicate appended falsifies it. | 2026-09-27 · `PR #574; MEMORY.md consolidation stamp 2026-09-27` |
| asm-007 | **falsified** | Operators 1-19 are implemented by the repo files named in the external audit. | perplexity | 2026-09-27 | grep each named file for the operator it is claimed to implement. | 2026-09-27 · `F40` |
| asm-008 | **falsified** | The Tao has one source of truth. | both | 2026-08-01 | Set-diff the ids of the two files. | 2026-09-27 · `_DECISIONS/CANON-COLLISION-tao-two-books.md` |
| asm-009 | **open** | A session that produces exactly as much as it consumes is at rest. | both | 2026-09-27 | Maekawa: a flat-foldable interior vertex needs mountain and valley folds to differ by exactly two; read the breath audit for a small net direction rather than balance, across ten handoffs, and see whether balanced sessions leave more open loops than directed ones. | open |
| asm-010 | **falsified** | Old window glass is thicker at the bottom because glass flows under gravity. | zach | 2026-09-27 | Compute the relaxation time from measured viscosity (Zanotto 1998); check for panes thicker at the top. | 2026-09-27 · `runtime/specs/LORE.md#lore-001` |
