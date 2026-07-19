# Durable environment gotchas (on-demand ledger)

> Banked 2026-07-19 from a scan of the handoff/memory archives (`_ARCHIVE/`). These are the
> non-obvious, still-true lessons that recurred across sessions and cost real time to re-learn.
> **On-demand only** — deliberately NOT in the auto-loaded path (CLAUDE/AGENTS/WORLD), to avoid
> re-creating the per-session token tax that fix #1 removed. Open this when a task touches the area.
> The basics (inline styles, JSON-as-TEXT, `npx next build` for typecheck, `git worktree list`,
> commit style) already live in AGENTS.md → Gotchas and are not repeated here.

## Supabase / DB
- Project `xbbpiryokswwvcrcutge` is **invisible to the Supabase MCP** (wrong org) — use the
  `supabase` **CLI** for its DDL/RLS ops.
- Prisma connects as the `postgres` **superuser → bypasses RLS**; Auth.js v5 ≠ Supabase Auth, so
  `auth.uid()` is always NULL. User isolation lives at the **app layer**; RLS is **deny-all only**.
  (New tables like `SageTrace` need the deny-all policy applied explicitly — RLS is off by default.)
- **Prisma 7:** no `url` in `schema.prisma`; wire the `PrismaPg` adapter in `db.ts`;
  `prisma.config.ts` loads `.env.local` (no `override`).

## Vercel / deploy / domains
- `vercel env add` **cannot target "all preview branches"** (CLI v53 bug) — set preview vars via
  the Vercel **dashboard**.
- **Verify domain→project mapping LIVE** via `get_deployment`, never from memory. `arcs.care` /
  `app` / `www` / `resume` all alias **this** repo; the standalone `arcs-care` project is `live:false`.
- **Subdomain HTML hosting:** use `beforeFiles` in `next.config.ts` — `vercel.json` rewrites are
  overridden by `src/app/page.tsx`. Commit on **`main`**, not a worktree branch; a new subdomain may
  need explicit assignment to the project in the Vercel dashboard/API first.
- `vercel.json` on `main` carries `experimentalServices` (sage Python microservice) + `crons` —
  **don't drop them** if/when migrating to `vercel.ts`.
- **Verify fixes against the LIVE production domain** (curl-grep the specific CSS rule / string that
  changed), not just "deploy succeeded."

## Git / concurrency
- Concurrent sessions push between your fetch and merge: `git fetch origin main && git rebase
  origin/main` **before** any fast-forward merge. **Never force-push** over another session's commits.
- Merges can land on the wrong branch when a worktree is active — confirm the target before merging.

## State / handoff
- Feature branches own `_STATE/branch-<slug>.json`; **never overwrite the shared `snapshot.json`**.
  The cloud setup script fetches `snapshot.json` from the **main** raw URL, so feature-branch
  snapshots don't reach the next cloud session until merged.

## Tooling
- **HEIC screenshots:** the Read tool can't render them — convert via `sips -s format png` first.
- `smoke.sh`: use `curl -s`, **not `-sf`** — `-f` exits nonzero on expected 400s and kills the
  script under `set -euo pipefail`.
