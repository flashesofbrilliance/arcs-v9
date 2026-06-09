import { PrismaClient } from "@prisma/client"
import { PrismaPg } from "@prisma/adapter-pg"
import { Pool } from "pg"

// Prisma 7: url no longer goes in schema.prisma — pass adapter to PrismaClient.
// prisma.config.ts owns DATABASE_URL for Migrate (db push / migrate deploy).
// Runtime client gets it via adapter here.
// Both use the Supabase pooler URL (port 6543) — set DATABASE_URL in .env.local.
// IMPORTANT: PrismaPg requires an explicit pg.Pool instance (not a config object)
// so that SSL options are applied — { connectionString } form silently fails SSL
// on the Supabase pooler and every query throws at runtime.
function makePrisma() {
  const connectionString = process.env.DATABASE_URL
  if (!connectionString) throw new Error("DATABASE_URL is not set")
  const pool = new Pool({ connectionString, ssl: { rejectUnauthorized: false } })
  const adapter = new PrismaPg(pool)
  return new PrismaClient({ adapter })
}

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient }

// Lazy getter — defers DATABASE_URL validation to first request, not build time.
// This allows `next build` to succeed without DATABASE_URL in the build environment.
function getPrisma(): PrismaClient {
  if (!globalForPrisma.prisma) {
    globalForPrisma.prisma = makePrisma()
  }
  return globalForPrisma.prisma
}

export const prisma: PrismaClient = new Proxy({} as PrismaClient, {
  get(_target, prop) {
    return (getPrisma() as unknown as Record<string | symbol, unknown>)[prop]
  },
})
