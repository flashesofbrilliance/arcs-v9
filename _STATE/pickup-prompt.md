# Pickup — after v3.61.0 (2026-09-13)

Repo: https://github.com/flashesofbrilliance/arcs-v9 · main HEAD `ad4f084f` · everything from the
bridge-index/Triune session is merged and receipted. Orient: `@CLAUDE.md` → Handoff v3.61.0 only.

START HERE → score the bridge lane:
- 578 rows on jobs.arcs.care with `source=bridge_scan`, `band=UNSCORED` (`unscoredWhy: "bridge index scan"`).
- Rubric v1.0 + spec selector live on branch `claude/bridge-scan-rubric` (Thread 2); receipt
  `2026-09-11--bridge-scan-rubric-v1.0--ZH`. Run it over the lane, then update
  `_STATE/job-search/hypothesis-ledger.md` (amendment block, never edit pre-registered text).
- Re-pull is cheap and idempotent: `python3 scripts/bridge_index_scan.py pull _STATE/job-search/employer-index/index.json /tmp/reqs.jsonl && set -a; . ~/.arcs/jobs-pipeline.env; set +a; python3 scripts/bridge_index_scan.py ingest /tmp/reqs.jsonl`.

Then (human call): prune worktrees per `_STATE/worktree-audit-2026-09-11.md` — bundle first.

Rules: oracle-first ADR numbers · receipts on every merge (enums in AGENTS.md) · no new deps ·
inline styles only · run tools from YOUR worktree, not `/Users/zharris/arcs-v9/...`.
