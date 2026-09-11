import { PrismaClient } from "@prisma/client"
import { PrismaPg } from "@prisma/adapter-pg"
import { Pool } from "pg"

// Least-privilege client for the anonymous /api/louisville/* routes.
// Connects as the louisville_app role: SELECT+INSERT on "SessionReceipt" only,
// RLS ENFORCED and tenant-pinned to jeben/louisvillebrands (unlike the main
// prisma client, which connects as postgres and bypasses RLS).
// Fail-closed: if LOUISVILLE_DATABASE_URL is unset the routes error rather
// than silently falling back to the superuser connection.
function makeLouisvillePrisma() {
  const connectionString = process.env.LOUISVILLE_DATABASE_URL
  if (!connectionString) throw new Error("LOUISVILLE_DATABASE_URL is not set")

  // Same manual URL parse as db.ts — pg's parser mishandles special chars,
  // and PrismaPg needs an explicit Pool for SSL to apply on the pooler.
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
  const adapter = new PrismaPg(pool)
  return new PrismaClient({ adapter })
}

const globalForLouisville = globalThis as unknown as { louisvillePrisma?: PrismaClient }

function getLouisvillePrisma(): PrismaClient {
  if (!globalForLouisville.louisvillePrisma) {
    globalForLouisville.louisvillePrisma = makeLouisvillePrisma()
  }
  return globalForLouisville.louisvillePrisma
}

export const louisvillePrisma: PrismaClient = new Proxy({} as PrismaClient, {
  get(_target, prop) {
    return (getLouisvillePrisma() as unknown as Record<string | symbol, unknown>)[prop]
  },
})
