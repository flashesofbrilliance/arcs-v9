-- Share tokens for briefs: /brief/[receiptId] became owner-only, and a brief is
-- shared through an owner-minted, revocable token instead of the raw receipt id.
-- Only the SHA-256 of the token is stored. RLS on with no policies (deny-all over
-- PostgREST), matching every other public table; the app connects with BYPASSRLS.
-- Apply with `prisma migrate deploy`, never `db push`.
CREATE TABLE "BriefShare" (
  "id" TEXT NOT NULL,
  "briefId" TEXT NOT NULL,
  "tokenHash" TEXT NOT NULL,
  "createdBy" TEXT NOT NULL,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "revokedAt" TIMESTAMP(3),
  CONSTRAINT "BriefShare_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "BriefShare_tokenHash_key" ON "BriefShare"("tokenHash");
CREATE INDEX "BriefShare_briefId_idx" ON "BriefShare"("briefId");
ALTER TABLE "BriefShare" ADD CONSTRAINT "BriefShare_briefId_fkey" FOREIGN KEY ("briefId") REFERENCES "Brief"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "BriefShare" ENABLE ROW LEVEL SECURITY;
