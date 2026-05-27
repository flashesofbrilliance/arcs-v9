import { PrismaClient } from "@prisma/client"
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3"

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient }

function createPrismaClient() {
  const url = process.env.DATABASE_URL ?? "file:./dev.db"
  if (url.startsWith("postgresql://") || url.startsWith("postgres://")) {
    // Production: Postgres (Supabase) — no adapter, Prisma uses native driver
    return new PrismaClient()
  }
  // Local dev: SQLite via better-sqlite3 driver adapter
  const adapter = new PrismaBetterSqlite3({ url })
  return new PrismaClient({ adapter })
}

export const prisma = globalForPrisma.prisma ?? createPrismaClient()

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma
