# Arc: canon (reconstructed 2026-10-06)

> The canon domain started in May 2026 as hand-committed book chapters and ADRs (Book II Parts I to V, ADR-009, ADR-014) and grew into the governance machinery that keeps a many-session, many-harness repo honest: an oracle that allocates every ADR, seed and handoff number (git non-fast-forward is the lock), an integrity gate that fails any record citing a SHA, path or ADR not on origin/main, a generated operator registry plus MCP bridge (no hand-written operator map), the Librarian (Operator 21) as a retrieval policy, the induced backlog with freshness checks, and finally the handoff pipeline itself: CLAUDE.md append-only (retired 2026-07-19), then per-session fragments, then `handoff_fold.py molt` (one arc, oracle-versioned, bookends refused). The trajectory is one lesson repeated: anything typed by hand drifts, so every count, number and citation is now stamped or checked by a script.

## Goal
Every durable fact (decision, number, citation, open loop) has exactly one machine-checkable home, so a cold session can resume any domain from git alone without re-deriving or trusting prose.

## What changed
- v0.5.0 to v1.8.0 (May to June 2026): Book II Part V (Accumulation Protocol) drafted and committed under `_CANON/book-ii/`; ADR-009 (design system), ADR-014 (CI/CD governance) landed.
- v3.8.0 to v3.10.0 (2026-07-19): token-efficiency audit; CLAUDE.md became a lean working file holding only the latest 1 to 2 handoffs, history relocated to `_ARCHIVE/handoffs.md`.
- v3.34.0 to v3.46.0 (August): ADR citation audits; oracle (`scripts/oracle.py`) made the only way to number ADRs, seeds, receipts (AGENTS.md gotcha #12) after ADR-033 and ADR-067 collisions.
- v3.53.0 (2026-09-04): ADR-075 Metabolic Router; drift sweep (ADR-074 indexed, oracle 73 to 74); operators census reconciled (52 top-level .py, 22,171 LOC).
- v3.54.0 (2026-09-06): `scripts/integrity_gate.py` (ADR-075 GATE organ) checks every ADR, SHA, path a record cites against origin/main.
- v3.56.0 to v3.58.0 (2026-09-07/08): ADR-076 renumbered via oracle; `cache_manifest.py` per-slice grading; memory `look-out-before-look-in`.
- v3.61.0 (2026-09-13): 74 worktrees swept by patch-id; seed bank cleaned; wrap memories consolidated.
- v3.64.0 (2026-09-17): induced backlog + completeness audit (#470, #471, #473, #476); seeds #474.
- v3.68.0 (2026-09-27): operator registry + MCP bridge (#559, `1ffed09e`); periodic table locked as the only operator numbering (gotcha #16); Librarian retrieval seed (#560).
- v3.69.0 (2026-09-27): echo detector embedding signature; shared-template control showed 0 real echoes (memory `template-aliasing-shared-boilerplate-fakes-cross-domain-echo`).
- v3.70.0 (2026-09-28): `belief_log_emit.py` stamps the public falsified-beliefs count on good.arcs.care/audit.
- v3.71.0 (2026-09-28): `operators/arcs_librarian.py` `Librarian.recommend()` (`aaf81d33`, #613); registry row 21 rebound to `recommend`.
- v3.72.0 (2026-09-30): Chronicle five books by git epoch, SSOT `runtime/specs/chronicle-books.json`.
- v3.73.0 / v3.75.0 (2026-10-04): oracle argv fix (`4583555`) so `--dry-run` no longer allocates; session-start hook arms `core.hooksPath` when unset.
- v3.81.0 / v3.81.1 (2026-10-05): seeds 5 to 16 from job-tracker-pro; `scripts/backlog_freshness.py` (#713) lists backlog rows past `review_by`.
- v3.84.0 (2026-10-05): open PRs 74 to about 25 (21 closed with comments, branches kept).
- v3.104.0 to v3.110.0 (2026-10-06): #884 write-lock + leases (ADR-085 PROPOSED, opt-in); #882 `claude-models.ts` single model registry (#715 closed as superseded); #897 `purpose_guard.py` hard gate; fragments path for `/handoff`; `unfold.py handoff_open()` reads Open items from unfolded fragments.
- v3.113.0 (2026-10-06): fold PR #921 (`78c6e949`); receipts `2026-10-06--handoff-fragment-pr914--ZH`, `2026-10-06--handoff-fold-pr921--ZH`.
- v3.114.0 (2026-10-06): #936 (`986daa56`) replaced an unmerged-SHA citation with branch + PR state; receipt `2026-10-06--qualify-abb6aedb-pr936--ZH`.
- 2026-10-06: #951 `handoff_fold.py molt` merged (`a8980fa9`); #960 molted key-audit + compass-lint fragments into v3.115.0.

## State
- origin/main head `89264922` (2026-10-06). `scripts/handoff_fold.py` carries `new`, `list`, `molt` (oracle-versioned, refuses bookends); `fold` is a deprecated alias.
- Oracle ADR audit: 80 numbers, high-water 85, next free 86, gaps 21, 42, 43, 47, 82 (verified live).
- Only one ADR-032 file exists now (`ADR-032-zero-trust-posture.md`); the duplicate is resolved.
- `integrity_gate.py _ARCHIVE/handoffs.md` still FAILS (verified: e.g. vapor citation to a Vercel TS config that does not exist). Backlog row `adr-index-drift-repair` covers the ADR index part only.
- `_DECISIONS/ADR-026-debrief-delivery-fix.md` and `ADR-059` still cite the old .js name of scripts/sage_efficacy.mjs (verified by grep).
- ADR-009 still says Stability STABLE; the 2026-06 ultrareview asked for REVISIT.
- Induced backlog has 93 rows; `unfold-uses-librarian`, `orphan-seeds-curation`, `tao-backfill-066-067`, `adr-index-drift-repair` are live rows.
- AGENTS.md `RECOIL_PASSWORD` row and operators census are already fixed.
- No per-domain arc home existed in the molt design; arcs written to `_HANDOFFS/arcs/<domain>.md` (proposed in the reconstruction PR).

## Decisions
- Never infer a number: `python3 scripts/oracle.py next <ns>` and commit `_SEEDS/_oracle.json`; a non-ff rejection means re-allocate.
- Never cite a SHA not on origin/main; cite the branch and PR state instead (integrity_gate enforces).
- Sessions never edit CLAUDE.md to hand off: write a fragment, then `molt` synthesizes one arc; overflow goes to `_ARCHIVE/handoffs.md` by version. History is relocated, never deleted.
- A fold/molt PR goes stale fast: re-molt on fresh origin/main rather than hand-resolving CLAUDE.md conflicts.
- `/handoff` can load a stale command copy: confirm it says "fragment" before following it.
- Operator numbering is the periodic table; the registry is generated and greps every binding.
- A number a script can compute is stamped by that script and gate-covered, never typed.
- A preview flag a tool does not recognize turns a look into a touch: tools must reject unknown args.
- A git bundle does not carry gitignored handoff trails: archive the session before pruning a worktree.
- Merge with `gh pr merge --merge` only; every merge/deploy/publish ends with one decision receipt.

## Open
1. `_ARCHIVE/handoffs.md` fails integrity_gate on pre-existing citations (needs qualify sweep or an archive exemption decision).
2. ADR-026 and ADR-059 cite sage_efficacy.js; repoint to `.mjs`.
3. ADR-009 stability should read REVISIT, not STABLE (cosmetic).
4. Oracle-backed citation linter: nothing flags a bare `ADR-0NN` pointing at the wrong file (flight-manual cites ADR-032 for Brief rendering).
5. `unfold-uses-librarian` (backlog row) and `librarian-recommend-needle` follow-ups: Supabase sync of the operator ledger, Op 28 Auditor binding.
6. Zach: orphan seeds curation, tao proverbs for ADR-066/067, lattice `--regenerate` (human-owned).
7. Zach: ratify or reject the `_HANDOFFS/arcs/` per-domain home in the reconstruction PR.

## Next action
Run `python3 scripts/integrity_gate.py _ARCHIVE/handoffs.md`, and for each failing citation either qualify it (branch + PR state, as #936 did) or propose an archive exemption, in one PR merged with `--merge` plus a receipt.

## Cold-start
- Files: `scripts/handoff_fold.py` (docstring = molt schema), `scripts/oracle.py`, `scripts/integrity_gate.py`, `scripts/unfold.py`, `scripts/backlog_freshness.py`, `scripts/operator_registry_emit.py`, `operators/OPERATOR-REGISTRY.json`, `operators/arcs_librarian.py`, `_QUEUE/induced-backlog.jsonl`, `_SEEDS/index.jsonl`, `_DECISIONS/index.json`, `_ARCHIVE/handoffs.md`, `_HANDOFFS/fragments/`.
- Commands: `python3 scripts/handoff_fold.py list`; `python3 scripts/oracle.py audit adr`; `python3 scripts/backlog_freshness.py`; `python3 scripts/operator_registry_emit.py --check`; `operators/mcp-bridge.sh --self-test`; `python3 scripts/open_loops.py`.
- Tracker: artifact AvE1T5TMQD164GPFGetHvm, `debt` collection.
- Memory slugs: `operator-numbering-locked-periodic-table-registry-generated`, `progressive-handoff-global-hooks`, `verify-handoff-prose-against-live-backlog-not-just-doc`, `shared-anchor-append-refetch-before-write`, `worktree-prune-archive-first-incremental-bundles`, `memory-index-load-cap-observed`, `keep-a-tidy-house-consolidate-dont-accumulate`.
