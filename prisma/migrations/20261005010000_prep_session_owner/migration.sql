-- Owner on PrepSession: /api/compass loaded a prep row by a client-supplied
-- prepId with no ownership check (IDOR). Additive and nullable: pre-existing
-- rows stay unowned and are no longer loadable by compass. No FK, so account
-- deletion order is unchanged (delete route removes owned rows explicitly).
-- Apply with `prisma migrate deploy`, never `db push`.
ALTER TABLE "PrepSession" ADD COLUMN "userId" TEXT;
CREATE INDEX "PrepSession_userId_idx" ON "PrepSession"("userId");
