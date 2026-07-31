-- CreateTable
CREATE TABLE "SessionReceipt" (
    "id" TEXT NOT NULL,
    "tenant" TEXT NOT NULL,
    "brand" TEXT NOT NULL,
    "sessionId" TEXT NOT NULL,
    "author" TEXT NOT NULL,
    "bet" TEXT NOT NULL,
    "assumptions" TEXT,
    "falsifier" TEXT NOT NULL,
    "killScale" TEXT,
    "atRisk" TEXT,
    "scoreBackDate" TIMESTAMP(3) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'OPEN',
    "outcome" TEXT,
    "variance" TEXT,
    "lesson" TEXT,
    "parentId" TEXT,
    "seedsSessionId" TEXT,
    "payload" JSONB,
    "userId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "sealedAt" TIMESTAMP(3),

    CONSTRAINT "SessionReceipt_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "SessionReceipt_tenant_brand_sessionId_idx" ON "SessionReceipt"("tenant", "brand", "sessionId");

-- CreateIndex
CREATE INDEX "SessionReceipt_scoreBackDate_idx" ON "SessionReceipt"("scoreBackDate");

-- AddForeignKey
ALTER TABLE "SessionReceipt" ADD CONSTRAINT "SessionReceipt_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "SessionReceipt"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- RLS: deny-all for anon/authenticated (ADR-008). Prisma connects as the
-- postgres superuser and bypasses RLS, so the app keeps full access.
ALTER TABLE "SessionReceipt" ENABLE ROW LEVEL SECURITY;
