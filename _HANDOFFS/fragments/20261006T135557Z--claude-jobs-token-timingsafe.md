<!--
branch: claude/jobs-token-timingsafe
head: d7963b38
created_at: 2026-10-06T13:55:57Z
-->
> **Jobs pipeline token is compared in constant time (#906, merged `0fbcc9e3`, all checks green).**
> Receipts `2026-10-06--jobs-token-timingsafe-pr906--ZH` (PR) and `--jobs-token-timingsafe-merge-pr906--ZH` (merge).

## Done
- `src/lib/jobs.ts` `callerFor()`: `token === expected` replaced by `tokensMatch()` (node:crypto `timingSafeEqual`
  on equal-length Buffers, false on length mismatch). No new deps; `npm run build` passed.
- Prod verified: `dpl_G6cRZvix...` READY at `f74642f3` (#907), which contains `0fbcc9e3`; serves arcs.care + jobs.arcs.care.
  Live `GET jobs.arcs.care/api/jobs` with empty / short / long wrong tokens all return 401 (no 500 on length mismatch).

## Open (next session)
1. Valid-token path not exercised live (token not in hand); confirm on the next scheduled pipeline run.

## Lessons
- `timingSafeEqual` throws on unequal lengths: guard length first, then probe prod with a wrong-length token to prove no 500.
