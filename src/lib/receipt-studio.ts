import { PrismaClient } from "@prisma/client"
import { PrismaPg } from "@prisma/adapter-pg"
import { Pool } from "pg"

// Receipt Studio — the tenant registry + per-tenant least-privilege DB clients.
//
// This is the ONLY place a Studio tenant is defined. tenant + brand are
// server-side truth here, keyed by the [tenant] path segment; the client body
// never sets them (same doctrine as the louisville route). Each tenant has its
// OWN RLS-pinned DB role and connection secret, so a compromised route for one
// tenant cannot read or write another's rows:
//   jeben  -> louisville_app (SELECT+INSERT, pinned jeben/louisvillebrands)
//   robin  -> robin_app      (SELECT+INSERT+UPDATE, pinned robin/zensai)
//
// db-louisville.ts stays as-is (the live /api/louisville/* routes keep using it);
// this module is additive. Fail-closed: a tenant whose <dbEnvVar> is unset throws,
// so the route errors rather than silently using the superuser connection.

// `close` = the role has UPDATE and may score/close a receipt. jeben's
// louisville_app is INSERT-only, so PATCH is rejected up front with a 405
// (CISO finding D) rather than failing deep at the DB grant layer.
export const STUDIO_TENANTS = {
  jeben: { brand: "louisvillebrands", dbEnvVar: "LOUISVILLE_DATABASE_URL", viewerEnvVar: "LOUISVILLE_VIEWER_EMAILS", close: false },
  robin: { brand: "zensai", dbEnvVar: "ROBIN_DATABASE_URL", viewerEnvVar: "ROBIN_VIEWER_EMAILS", close: true },
} as const

export type StudioTenant = keyof typeof STUDIO_TENANTS

export function isStudioTenant(t: string): t is StudioTenant {
  return Object.prototype.hasOwnProperty.call(STUDIO_TENANTS, t)
}

// Per-tenant Prisma client, lazily built and cached on globalThis (serverless
// reuse). Same manual URL parse + explicit Pool as db.ts/db-louisville.ts —
// pg's parser mishandles special chars and PrismaPg needs the Pool for SSL.
//
// Connection ceiling (SRE finding F4): each tenant opens its own Pool (max:3),
// so this registry scales as 3 x N tenants per serverless instance against the
// Supabase pooler, on top of the main + louisville clients. Fine at N=2; keep
// this bound conscious before onboarding many tenants. Also: a set-but-WRONG
// connection string is cached after buildClient() succeeds (Pool connects
// lazily), so fixing the env var needs an instance recycle / redeploy, not just
// a var change — same caveat as the louisville proxy client.
const globalForStudio = globalThis as unknown as { studioClients?: Record<string, PrismaClient> }

function buildClient(dbEnvVar: string): PrismaClient {
  const connectionString = process.env[dbEnvVar]
  if (!connectionString) throw new Error(`${dbEnvVar} is not set`)
  const url = new URL(connectionString)
  const pool = new Pool({
    host: url.hostname,
    port: Number(url.port) || 6543,
    database: url.pathname.slice(1),
    user: decodeURIComponent(url.username),
    password: decodeURIComponent(url.password),
    ssl: { rejectUnauthorized: false },
    max: 3,
  })
  return new PrismaClient({ adapter: new PrismaPg(pool) })
}

export function studioPrisma(tenant: StudioTenant): PrismaClient {
  const cfg = STUDIO_TENANTS[tenant]
  if (!globalForStudio.studioClients) globalForStudio.studioClients = {}
  const cache = globalForStudio.studioClients
  if (!cache[tenant]) cache[tenant] = buildClient(cfg.dbEnvVar)
  return cache[tenant]
}

// Fields the Studio consumes — never the raw row (strips userId). Same allowlist
// as the louisville route, plus the close/score fields the Robin Studio writes.
export const PUBLIC_SELECT = {
  id: true,
  sessionId: true,
  author: true,
  bet: true,
  assumptions: true,
  falsifier: true,
  killScale: true,
  atRisk: true,
  scoreBackDate: true,
  status: true,
  outcome: true,
  variance: true,
  lesson: true,
  parentId: true,
  payload: true,
  createdAt: true,
  sealedAt: true,
} as const

export const STUDIO_LIMITS = {
  MAX_BODY_BYTES: 32_768,
  MAX_ROWS_PER_SESSION: 100,
  THROTTLE_WINDOW_MS: 60_000,
  THROTTLE_MAX: 30,
} as const
