import { PrismaClient } from "@prisma/client"

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient }

// Schema datasource is postgresql — both local dev and prod use Supabase.
// Set DATABASE_URL in .env.local to the Supabase pooler URL (port 6543).
export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma
