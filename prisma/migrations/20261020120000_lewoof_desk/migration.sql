-- Le Woof Desk (lewoof.arcs.care/desk): accounts Hila works and the results she logs.
-- Deny-all RLS (on, no policies) like every other public table: the anon key reads and
-- writes nothing over PostgREST, and the app connects as postgres (BYPASSRLS).
-- NOT APPLIED by this PR. Zach applies it (migrate deploy) after review.
CREATE TABLE "lewoof_accounts" (
    "id" TEXT NOT NULL,
    "section" TEXT NOT NULL,
    "rank" INTEGER NOT NULL DEFAULT 0,
    "name" TEXT NOT NULL,
    "website" TEXT,
    "contactPage" TEXT,
    "flags" TEXT,
    "score" INTEGER NOT NULL DEFAULT 0,
    "contactName" TEXT,
    "contactTitle" TEXT,
    "email" TEXT,
    "emailSource" TEXT,
    "phone" TEXT,
    "phoneNote" TEXT,
    "hook" TEXT,
    "notes" TEXT,
    "stage" TEXT NOT NULL DEFAULT 'new',
    "touches" INTEGER NOT NULL DEFAULT 0,
    "lastResult" TEXT,
    "nextTouch" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "lewoof_accounts_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "lewoof_touches" (
    "id" TEXT NOT NULL,
    "accountId" TEXT NOT NULL,
    "kind" TEXT NOT NULL,
    "result" TEXT NOT NULL,
    "note" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "lewoof_touches_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "lewoof_accounts_section_idx" ON "lewoof_accounts"("section");
CREATE INDEX "lewoof_accounts_stage_nextTouch_idx" ON "lewoof_accounts"("stage", "nextTouch");
CREATE INDEX "lewoof_touches_accountId_idx" ON "lewoof_touches"("accountId");
CREATE INDEX "lewoof_touches_createdAt_idx" ON "lewoof_touches"("createdAt");

ALTER TABLE "lewoof_accounts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "lewoof_touches" ENABLE ROW LEVEL SECURITY;
