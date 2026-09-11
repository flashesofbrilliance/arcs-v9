#!/usr/bin/env node
// provision_studio_tenant.mjs — one-command, no-HITL runtime provisioning for a
// Receipt Studio tenant. Removes the psql / SQL-editor / clipboard dance: it
// applies the RLS role+policies, sets the role's login password, and writes
// <TENANT>_DATABASE_URL to Vercel (Production + Preview) — all locally. The
// password is generated here and NEVER leaves this machine or gets logged.
//
// It does NOT touch the code artifacts (registry row in src/lib/receipt-studio.ts,
// the studio block in the receipt SSOT, the next.config /api rewrite). Those are
// version-controlled edits; add them + deploy as usual. This script is only the
// runtime credential half — the part that used to need a human in the loop.
//
// Usage:
//   node scripts/provision_studio_tenant.mjs <tenant> <brand> [options]
//   e.g.  node scripts/provision_studio_tenant.mjs robin zensai
//         node scripts/provision_studio_tenant.mjs acme acmecorp --redeploy
//
// Options:
//   --no-preview     set only Production (default sets Production + Preview)
//   --redeploy       trigger a prod redeploy so the running deployment picks it up
//   --write-migration  also write prisma/migrations/<ts>_<tenant>_studio_role/migration.sql
//   --dry-run        print the plan; do not connect, ALTER, or touch Vercel
//
// Required env (never committed):
//   STUDIO_ADMIN_DATABASE_URL   a superuser/admin Postgres conn string that can
//                               ALTER ROLE + CREATE POLICY. Use Supabase's
//                               "Direct connection" or "Session mode" string
//                               (NOT the transaction pooler on :6543).
// Optional env (sane defaults for this project):
//   STUDIO_PROJECT_REF   default xbbpiryokswwvcrcutge
//   STUDIO_POOLER_HOST   default aws-1-us-east-1.pooler.supabase.com
//   STUDIO_POOLER_PORT   default 6543
//   STUDIO_VERCEL_SCOPE  default arcs-care  (Vercel team slug for redeploy)

import { randomBytes } from 'node:crypto'
import { spawnSync } from 'node:child_process'
import { writeFileSync, mkdirSync, readdirSync, existsSync } from 'node:fs'
import pg from 'pg'

const args = process.argv.slice(2)
const flags = new Set(args.filter(a => a.startsWith('--')))
const [tenant, brand] = args.filter(a => !a.startsWith('--'))
const DRY = flags.has('--dry-run')

function die(msg) { console.error('✗ ' + msg); process.exit(1) }
if (!tenant || !brand) die('usage: node scripts/provision_studio_tenant.mjs <tenant> <brand> [--no-preview] [--redeploy] [--write-migration] [--dry-run]')
if (!/^[a-z][a-z0-9]{1,30}$/.test(tenant)) die(`tenant must be lowercase alnum: got "${tenant}"`)
if (!/^[a-z][a-z0-9]{1,40}$/.test(brand)) die(`brand must be lowercase alnum: got "${brand}"`)

const role = `${tenant}_app`
const ref = process.env.STUDIO_PROJECT_REF || 'xbbpiryokswwvcrcutge'
const host = process.env.STUDIO_POOLER_HOST || 'aws-1-us-east-1.pooler.supabase.com'
const port = process.env.STUDIO_POOLER_PORT || '6543'
const scope = process.env.STUDIO_VERCEL_SCOPE || 'arcs-care'
const envName = `${tenant.toUpperCase()}_DATABASE_URL`
const envs = flags.has('--no-preview') ? ['production'] : ['production', 'preview']

// Role + policies SQL — identical posture to the robin_app/louisville_app roles:
// SELECT+INSERT + column-scoped UPDATE, tenant/brand pinned in USING + WITH CHECK.
// Idempotent (IF NOT EXISTS / DROP POLICY IF EXISTS), safe to re-run.
const roleSQL = `
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${role}') THEN CREATE ROLE ${role} NOLOGIN; END IF;
END $$;
GRANT USAGE ON SCHEMA "public" TO ${role};
GRANT SELECT, INSERT ON TABLE "SessionReceipt" TO ${role};
GRANT UPDATE (status, outcome, variance, lesson, payload) ON TABLE "SessionReceipt" TO ${role};
DROP POLICY IF EXISTS "${role}_select" ON "SessionReceipt";
CREATE POLICY "${role}_select" ON "SessionReceipt" FOR SELECT TO ${role} USING (tenant = '${tenant}' AND brand = '${brand}');
DROP POLICY IF EXISTS "${role}_insert" ON "SessionReceipt";
CREATE POLICY "${role}_insert" ON "SessionReceipt" FOR INSERT TO ${role} WITH CHECK (tenant = '${tenant}' AND brand = '${brand}');
DROP POLICY IF EXISTS "${role}_update" ON "SessionReceipt";
CREATE POLICY "${role}_update" ON "SessionReceipt" FOR UPDATE TO ${role} USING (tenant = '${tenant}' AND brand = '${brand}') WITH CHECK (tenant = '${tenant}' AND brand = '${brand}');
`

// 48 hex chars = 192 bits, alphanumeric only → URL-safe and no SQL-literal
// escaping needed (no quotes/specials can appear).
const pw = randomBytes(24).toString('hex')
const url = `postgresql://${role}.${ref}:${pw}@${host}:${port}/postgres`

if (flags.has('--write-migration')) {
  const already = existsSync('prisma/migrations') && readdirSync('prisma/migrations').some(d => d.endsWith(`_${tenant}_studio_role`))
  if (already) {
    console.log(`• migration for ${tenant} already exists, skipping --write-migration`)
  } else {
    // Timestamp must sort after existing migrations; derived from Date is fine here (user-run, not a workflow).
    const ts = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)
    const dir = `prisma/migrations/${ts}_${tenant}_studio_role`
    if (!DRY) { mkdirSync(dir, { recursive: true }); writeFileSync(`${dir}/migration.sql`, roleSQL.trim() + '\n') }
    console.log(`• ${DRY ? '[dry-run] would write' : 'wrote'} ${dir}/migration.sql (commit it for prisma tracking)`)
  }
}

function vercel(argv, opts = {}) {
  return spawnSync('vercel', [...argv, '--scope', scope], { stdio: ['pipe', 'inherit', 'inherit'], ...opts })
}

async function main() {
  console.log(`Provisioning Studio tenant "${tenant}" (brand "${brand}") → role ${role}, env ${envName}${DRY ? '  [DRY RUN]' : ''}`)

  const admin = process.env.STUDIO_ADMIN_DATABASE_URL
  if (!DRY && !admin) die('STUDIO_ADMIN_DATABASE_URL is not set (Supabase Direct/Session connection string with ALTER ROLE privilege)')

  if (DRY) {
    console.log('• [dry-run] would apply role+policies SQL (idempotent) as admin')
    console.log(`• [dry-run] would ALTER ROLE ${role} WITH LOGIN PASSWORD '<generated, 48 hex>'`)
    console.log(`• [dry-run] would set ${envName} for: ${envs.join(', ')}  (value: postgresql://${role}.${ref}:***@${host}:${port}/postgres)`)
    if (flags.has('--redeploy')) console.log('• [dry-run] would redeploy latest production')
    console.log('✓ dry run complete — set STUDIO_ADMIN_DATABASE_URL and re-run for real.')
    return
  }

  // 1) apply role + policies, 2) set the login password — one admin session.
  const client = new pg.Client({ connectionString: admin, ssl: { rejectUnauthorized: false } })
  await client.connect()
  try {
    await client.query(roleSQL)
    console.log(`✓ role + RLS policies applied (${role}, pinned ${tenant}/${brand})`)
    await client.query(`ALTER ROLE ${role} WITH LOGIN PASSWORD '${pw}'`)
    console.log(`✓ ${role} password set (generated locally, not logged)`)
  } finally {
    await client.end()
  }

  // 3) write the Vercel env(s). rm-then-add so a re-run cleanly overwrites.
  for (const env of envs) {
    vercel(['env', 'rm', envName, env, '-y'], { stdio: ['ignore', 'ignore', 'ignore'] })
    const r = vercel(['env', 'add', envName, env], { input: url })
    if (r.status !== 0) die(`vercel env add ${envName} ${env} failed`)
    console.log(`✓ ${envName} set for ${env}`)
  }

  // 4) optional redeploy so the running deployment picks up the new env.
  if (flags.has('--redeploy')) {
    console.log('• redeploying latest production…')
    const ls = spawnSync('vercel', ['ls', 'arcs-v9', '--scope', scope], { encoding: 'utf8' })
    const dep = (ls.stdout.match(/https:\/\/arcs-v9-[a-z0-9]+-[a-z-]+\.vercel\.app/) || [])[0]
    if (dep) { vercel(['redeploy', dep]); console.log('✓ redeploy triggered') }
    else console.log('! could not find a deployment to redeploy — push to main or redeploy manually')
  } else {
    console.log('\nNext: redeploy production so the running deployment picks up the env')
    console.log('  (env changes do not reach an already-running deployment). Re-run with --redeploy,')
    console.log('  or it activates on the next push to main.')
  }
  console.log(`\n✓ ${tenant} provisioned. Remaining code bits (once): registry row in src/lib/receipt-studio.ts,`)
  console.log('  studio block in the receipt SSOT, and the /api rewrite in next.config.ts — then deploy.')
}

main().catch(e => die(e.message))
