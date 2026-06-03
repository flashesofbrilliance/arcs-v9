# Session Post-Mortem — 2026-06-03
### ADR-016 Execution + Infrastructure Recovery

> *ARCS-grade debrief. Evidence-tagged. Lessons extracted as reusable primitives.*
> *Duration: ~6 hours. Scope: arcs-v9 prod unblock.*

---

## What we set out to do

Unblock arcs-v9 production so anonymous users can run the compass (ADR-016 Option C).
Estimated: 45–90 min once gates passed.
Actual: ~6 hours.

The gap was entirely infrastructure — not code complexity. Every line of ADR-016 code
was correct on first write. The hours were spent diagnosing and fixing four silent failures
that had existed since day one of the prod deployment.

---

## The four silent failures (and why they were silent)

### 1. PrismaPg SSL — the deepest one

**Symptom:** Production builds green. All routes return 200. But every DB write silently fails.

**Root cause:** `db.ts` used `new PrismaPg({ connectionString })` — the config-object form.
This creates the adapter but the underlying `pg.Pool` never negotiates SSL against the
Supabase pooler. Every `prisma.receipt.create()` threw at runtime. The error never surfaced
in builds because `prisma generate` doesn't connect to the database.

**Why silent:** Next.js build succeeds even when runtime DB calls fail. The 401 auth guard
meant no real traffic ever hit the routes. Zero runtime errors logged because zero real
requests reached the DB layer.

**Fix:**
```typescript
// WRONG — silently breaks SSL on Supabase pooler
const adapter = new PrismaPg({ connectionString })

// CORRECT — explicit Pool with SSL
const pool = new Pool({ connectionString, ssl: { rejectUnauthorized: false } })
const adapter = new PrismaPg(pool)
```

**Lesson:** Any Prisma 7 + Supabase pooler setup needs the explicit Pool form. Verify by
running a real `prisma.$queryRaw` against prod before calling the DB layer "working."

---

### 2. `emailVerified` + `image` missing from User schema

**Symptom:** Magic link submitted → page shows "Check your email" → no email arrives →
`VerificationToken` table stays empty.

**Root cause:** `PrismaAdapter` (Auth.js v5) requires `emailVerified TIMESTAMP` on the
`User` table to upsert users on sign-in. The `0_init` Postgres baseline was written
before these columns were added in a later SQLite-only migration (`d732dad`). The Postgres
schema had a gap the SQLite dev schema didn't.

**Why silent:** Auth.js swallows the DB error and redirects to the sign-in page without
surfacing the Postgres `column User.emailVerified does not exist` error to the user.
The only way to find it was Supabase postgres logs.

**Fix:** `ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "emailVerified" TIMESTAMP(3)`
applied live via Supabase MCP. `0_init` migration patched retroactively (ADR-022).

**Lesson:** When Auth.js sign-in silently fails (form submits, page resets, no email),
check Supabase postgres logs immediately — it's almost always a schema gap in the
PrismaAdapter's expected columns.

---

### 3. Stale CLI-upload deploy (Prisma 6 in prod)

**Symptom:** Production deployment fails with `P1012: Argument "url" is missing` and
`Prisma CLI Version: 6.19.3` — but `package.json` pins `^7.7.0`.

**Root cause:** Someone ran `vercel deploy` from a local working tree that had a stale
`package-lock.json` with Prisma 6 pinned. The Vercel CLI uploaded that local snapshot
instead of building from the connected GitHub repo.

**Why silent:** The Vercel project was git-connected, but git-integration auto-deploy
had never fired (the connection was established after the last push). The CLI upload
bypassed the lockfile entirely.

**Diagnosis tell:** Build log shows `Downloading 106 deployment files...` instead of
`Cloning github.com/... (Commit: sha)`. The upload signature vs the clone signature
is immediately distinguishable.

**Fix:** `git commit --allow-empty && git push` → triggers a real git-integration build
from HEAD. `npm ci` vs `npm install` was a red herring — the source files themselves
were wrong.

**Lesson:** Check the build log's first line. `Cloning` = git build (correct).
`Downloading N deployment files` = CLI upload (potentially stale). Never use
`vercel deploy --prod` from a local working tree — always use git push.

---

### 4. DATABASE_URL credential failures (Marketplace-provisioned project)

**Symptom:** Three password resets on `xbbpiryokswwvcrcutge`, all fail auth at the
Supabase pooler. `vercel env pull` returns empty for `DATABASE_URL`.

**Root cause (compound):**
- The project was provisioned via Vercel Marketplace — its DB credentials are
  integration-managed, not accessible via the standard Supabase "postgres" role reset UI
- `vercel env pull` CLI v53.1.0 has a bug: returns empty for encrypted vars
- The `[YOUR-PASSWORD]` placeholder in Supabase's Connect string UI was copied literally

**Resolution:** Created a dedicated `arcs_app` Postgres role via Supabase MCP with a
known alphanumeric password. Updated `DATABASE_URL` to use the new role.

**Lesson:** For Marketplace-provisioned Supabase projects, don't try to reset the
`postgres` role password via the dashboard — it won't work reliably. Create a dedicated
app role with known credentials instead. Upgrade Vercel CLI to 54.7.1+ before trying
to use `vercel env pull` (Homebrew: `brew upgrade vercel-cli`).

---

## What worked well

| Thing | Why it worked |
|---|---|
| Supabase postgres logs | Surfaced the `emailVerified` error instantly — the most direct debugging surface |
| `pg` direct connection test | Validated credentials before setting them in Vercel — saved multiple bad-deploy cycles |
| `vercel curl --deployment` bypass | Let us test auth-protected routes without fighting deployment protection |
| MCP `apply_migration` | Applied schema fixes to prod without needing direct DB access |
| Empty-commit git-push diagnostic | Proved git-integration was working before we had env vars set |
| ARCS gate sequence (G0→G4) | Caught the wrong Supabase project, wrong DB URL, and RLS state before any code was written |

---

## What to do differently next time

**Before declaring a prod deployment "working":**
1. Run `vercel curl /api/health` (or any DB-touching route) — green build ≠ working DB
2. Check Supabase postgres logs for errors immediately after first deploy
3. Confirm `vercel env pull` returns non-empty values (CLI v54.7.1+)
4. For Auth.js: verify `VerificationToken` table gets a row after sign-in attempt

**Credential hygiene:**
- Never paste API keys into a chat transcript — use `printf '%s' 'key' | vercel env add`
- Create alphanumeric-only DB passwords to avoid URL-encoding issues
- Rotate any credential that appeared in a chat transcript before the first external user

**CLI version:**
- Vercel CLI via Homebrew (`brew upgrade vercel-cli`) not npm — npm can't override the Homebrew symlink
- Always check `vercel --version` before diagnosing CLI-related issues

---

## Reusable primitives extracted this session

| Primitive | Location | Description |
|---|---|---|
| Two-surface protocol | `_PATTERNS/two-surface-protocol.md` | Architect/Implementor sync via `_STATE/snapshot.json` |
| `/init-state-sync` skill | `~/.claude/commands/init-state-sync.md` | Scaffolds state sync for any new repo |
| `scripts/smoke.sh` | `scripts/smoke.sh` | 5-assertion prod acceptance gate |
| `scripts/activation-check.sql` | `scripts/activation-check.sql` | Post-deploy DB health check queries |
| Enhanced `/handoff` | `~/.claude/commands/arcs-handoff.md` | Captures machine state before prose |
| Enhanced `/handoff-pickup` | `~/.claude/commands/arcs-handoff-pickup.md` | Reads snapshot, surfaces drift |

---

## Timeline (condensed)

```
Boot          Crosswalk missing → pivoted to ADR-016 as source of truth
G0–G1         vercel env ls returns empty → CLI v53 bug identified
G1            Prod build Error → stale CLI-upload deploy diagnosed + fixed via git push
G2            DATABASE_URL wrong project (xbbpiryokswwvcrcutge vs owdiiyvphyifukygvxhg)
G2            3 password resets fail → Marketplace project credentials inaccessible
G2            arcs_app role created via MCP → first successful pooler connection
G3            Schema applied via MCP (3 migrations)
G4            RLS + BYPASSRLS confirmed
ADR-016 code  401 removal + claim endpoint + localStorage + smoke.sh — ~45 min
Smoke 5/5     Passed via vercel curl bypass
DB fix        PrismaPg SSL — entire DB layer was silently broken since day 1
Schema fix    emailVerified missing — Auth.js silently failing
BS-5          Magic link delivered, User row created, Session established
State sync    _STATE/snapshot.json + /handoff + /handoff-pickup — Architect/Implementor bridge
```

---

## NCI self-assessment

| Dimension | Score | Note |
|---|---|---|
| Execution accuracy | 88 | Code correct on first write; infra failures were pre-existing |
| Diagnostic precision | 82 | PrismaPg SSL took too long — should have checked DB layer earlier |
| Gate discipline | 91 | Stopped at every unexpected result, didn't work around |
| Documentation quality | 85 | ADRs + post-mortem + patterns extracted |
| Credential hygiene | 61 | Keys appeared in transcript — rotation required |

**Overall: NCI 82/100**
