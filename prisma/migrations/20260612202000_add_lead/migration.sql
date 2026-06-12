-- CreateTable
CREATE TABLE "Lead" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "message" TEXT,
    "source" TEXT NOT NULL DEFAULT 'waitlist',
    "receiptId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Lead_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Lead_source_idx" ON "Lead"("source");

-- CreateIndex
CREATE INDEX "Lead_createdAt_idx" ON "Lead"("createdAt");

-- RLS: deny-all for anon/authenticated (ADR-008). Prisma connects as the
-- postgres superuser and bypasses RLS, so the app keeps full access.
ALTER TABLE "Lead" ENABLE ROW LEVEL SECURITY;
