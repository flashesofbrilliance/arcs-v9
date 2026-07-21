# Teleport Brief — open-source track + PII cleanup (2026-07-21)

Self-contained pickup for a fresh terminal/CLI session. Read this, skip re-exploration.
Durable anchors: auto-memory `project-open-source-skills-queue.md` + `_STATE/snapshot.json → open_source`.

## Branch / state
- Worktree branch: `claude/code-skills-open-source-36bde4` (PR #122 open to main).
- Main worktree: `.claude/worktrees/frosty-kepler-b69f51` (on `main`, HEAD `5cce9f6`). Find via
  `git worktree list`; do PII scrub there, not on this branch.

## DONE this arc (do not redo)
- Shipped 3 public skill repos (skill at repo root; MIT; gauntlet-passed; em-dash→en-dash each time):
  - github.com/flashesofbrilliance/rca-skill
  - github.com/flashesofbrilliance/fix-toolbar-comments-skill
  - github.com/flashesofbrilliance/state-sync-skill
  - Local clones: `/Users/zharris/<name>-skill`. Staging copies: `open-source/<name>/`.
- Varun PII fully scrubbed from public arcs-v9: all 21 branches rewritten in ONE mirror
  filter-repo pass, `main` unchanged at `5cce9f6`, PRs healed. Gist (73e5b445…) DELETED.
  Lesson saved: memory `filter-repo-rewrite-all-refs-one-pass.md` (never single-branch rewrite).

## PENDING TASK 1 — own-data PII scrub (plain single-branch edit on main; NO history rewrite)
User's own aggregate data hardcoded in the public repo. Scrub to placeholders. Exact targets:
- `scripts/score_me.py:19` → `SUBJECT_NAME = "Zach Harris"` → placeholder
- `scripts/score_me.py:21` → `NETWORK_SIZE = 11177` → e.g. `10000` or param
- `scripts/forensic_scan.py:4` and `:364` → "11,177-contact network" + date → generic
- `scripts/archetype_scan.py:556` → "Builder → Navigator → Chartist | Total: 11,177" → generic
- `scripts/network_scan.py:22` → `CSV_PATH = "/Users/zharris/Downloads/Basic_LinkedInDataExport_05-20-2026.zip/..."` → relative/arg path
Commit on main worktree, `[NCI:SKIP]`. Current-state edit only — old commits already carry this
(user's own data, low stakes; history rewrite NOT warranted unless user asks).

## PENDING TASK 2 — open-source queue (all AUTHORED-FRESH, not extract-and-redact)
Finding: the LinkedIn personal-data-mining suite is the HIGHEST-sauce code in the repo (16 scripts
embed the archetype taxonomy / 5-lens forensic / NCI / Double-Helix kernel). Redaction can't
genericize it — the method IS the sauce. Queue, in order:
1. `tokenmining` / budget-mode skill (assessed, not built) — model-tier switch on signal, batching,
   inline-over-subagent, explicit checkpoint. Zero sauce, no extraction.
2. `linkedin-connections-toolkit` (new) — author clean: generic `Connections.csv` ETL (the useful
   reusable bit is the header-skip parser at network_scan.py:185) + plain non-ARCS analysis
   (recency/company/seniority/staleness). Keep ARCS scoring private. Build, not extract.

## HOLD (sauce risk — do not publish)
NCI trio (nci-scoring/nci-commit/drift-check = the ADR-035 rubric itself); teardown/precall-brief/
recoil-report (client data + gauntlet operators); arcs-research/dewy-stub/receipt-book-curator
(DEWY receipt shape); arcs-brand-manager (fork of Anthropic's skill); the whole scanner suite.

## Ship recipe (per skill)
extract/author → scrub (grep: arcs|nci|dewy|adr-|_patterns|_decisions|real names|/Users paths) →
em-dash check (`grep -c $'—'`, swap → en-dash) → LICENSE(MIT) + README(use-cases/how-to) →
git init + commit → `gh repo create flashesofbrilliance/<name> --public --source=. --push` →
copy to `open-source/<name>/` → commit staging.
