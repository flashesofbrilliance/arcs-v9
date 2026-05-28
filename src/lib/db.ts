import { PrismaClient } from "@prisma/client"
import { PrismaPg } from "@prisma/adapter-pg"

// Prisma 7: url no longer goes in schema.prisma — pass adapter to PrismaClient.
// prisma.config.ts owns DATABASE_URL for Migrate (db push / migrate deploy).
// Runtime client gets it via adapter here.
// Both use the Supabase pooler URL (port 6543) — set DATABASE_URL in .env.local.
function makePrisma() {
  const connectionString = process.env.DATABASE_URL
  if (!connectionString) throw new Error("DATABASE_URL is not set")
  const adapter = new PrismaPg({ connectionString })
  return new PrismaClient({ adapter })
}

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient }

export const prisma = globalForPrisma.prisma ?? makePrisma()

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma
