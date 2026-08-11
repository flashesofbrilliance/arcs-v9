# ARCS Session State — v3.32.0 (2026-08-11)

## Just shipped
- **Model-tier router (ADR-047)** — `scripts/model_tier_router.py`. Stdlib heuristic classifier that
  RECOMMENDS Haiku/Sonnet/Opus by reversibility × value. Same shape as the watcher family.
  Ruin-floor guardrail (never downgrade irreversible work); NOTOMATION (recommend, never switch).
  10/10 self-test. Commits `efcb386` (router+ADR) + `c61d948` (index), pushed.
- Locked the operating principle to memory: `[[model-tier-routing-locked-principle]]`.
- Full `/consolidate-memory` pass — index re-filed + trimmed to 136 lines, reconciles clean.

## Branch / deploy
- Branch: `claude/kind-grothendieck-fd2df4`, in sync with origin.
- No product code / no `next.config.ts` touched → no build triggered.
- Optional: open a PR from this branch.

## Carrying forward (not this session's work)
- Yuri's reply pending — nothing on our side (`[[project_yuri_kleban_google]]`).
- Todd Sugar sandbox call — gate pending Todd's approval.

## Blocking
NONE.

## Next session
`/handoff-pickup` — reads `_STATE/snapshot.json` + the latest `# Handoff` block in CLAUDE.md.
