-- ARCS v9 DEWY Schema — baseline migration
-- Applied via Supabase MCP on 2026-05-28 (all prior tables dropped, schema was empty)
-- This migration is the canonical starting state for arcs-v9 on Supabase.

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT,
    "emailVerified" TIMESTAMP(3),
    "image" TEXT,
    "name" TEXT,
    "tier" TEXT NOT NULL DEFAULT 'FREE',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "PrepSession" (
    "id" TEXT NOT NULL,
    "stakes" TEXT,
    "horizon" TEXT,
    "protecting" TEXT NOT NULL DEFAULT '[]',
    "confidence" INTEGER,
    "entity" TEXT,
    "adversarialInput" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "PrepSession_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Receipt" (
    "id" TEXT NOT NULL,
    "userId" TEXT,
    "receiptId" TEXT,
    "schemaVersion" TEXT NOT NULL DEFAULT '0.1.0',
    "surface" TEXT NOT NULL DEFAULT 'ORIENT',
    "validationState" TEXT NOT NULL DEFAULT 'PASS',
    "sessionTs" TIMESTAMP(3),
    "decision" TEXT NOT NULL,
    "sharpQuestion" TEXT,
    "dewyVector" TEXT,
    "trueNorth" TEXT NOT NULL,
    "whyBullets" TEXT NOT NULL,
    "loki" TEXT,
    "bar" TEXT,
    "nciScore" INTEGER NOT NULL,
    "nciGrade" TEXT,
    "nciByLens" TEXT,
    "coherencePct" INTEGER,
    "isSatoshi" BOOLEAN NOT NULL DEFAULT false,
    "clarityMode" TEXT NOT NULL DEFAULT 'SIMPLE',
    "fidelityHeader" TEXT,
    "fated" TEXT,
    "paths" TEXT,
    "court" TEXT,
    "courtVerdict" TEXT,
    "mode" TEXT NOT NULL,
    "doorClass" TEXT,
    "macroTags" TEXT NOT NULL DEFAULT '[]',
    "rawResponse" TEXT,
    "inferredFields" TEXT NOT NULL DEFAULT '[]',
    "collisionFields" TEXT NOT NULL DEFAULT '[]',
    "entity" TEXT,
    "stakeholders" TEXT,
    "window" TEXT NOT NULL,
    "horizon" TEXT,
    "stakes" TEXT,
    "protecting" TEXT NOT NULL DEFAULT '[]',
    "horizonLocked" BOOLEAN NOT NULL DEFAULT false,
    "driftState" TEXT,
    "yPolarity" TEXT NOT NULL DEFAULT 'SCRATCH',
    "yConviction" TEXT NOT NULL DEFAULT 'LOW',
    "yStability" TEXT NOT NULL DEFAULT 'SHIFTING',
    "yState" TEXT NOT NULL DEFAULT 'SCRATCH',
    "yGateScore" TEXT,
    "yConvictionPrev" TEXT,
    "yDeltaTrigger" TEXT,
    "yConditions" TEXT NOT NULL DEFAULT '[]',
    "yOverride" BOOLEAN NOT NULL DEFAULT false,
    "yOverrideAt" TIMESTAMP(3),
    "yOverrideNote" TEXT,
    "promotedTo" TEXT,
    "gradientMagnitude" DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    "gradientDirection" TEXT NOT NULL DEFAULT '{}',
    "flowTopology" TEXT NOT NULL DEFAULT 'CONVERGENT',
    "manifoldCurvature" TEXT NOT NULL DEFAULT 'MODERATE',
    "renderResolution" TEXT NOT NULL DEFAULT 'SHARP',
    "sessionId" TEXT NOT NULL,
    "parentId" TEXT,
    "version" INTEGER NOT NULL DEFAULT 0,
    "forkPath" TEXT,
    "mergedFrom" TEXT NOT NULL DEFAULT '[]',
    "prepId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewDate" TIMESTAMP(3),
    "status" TEXT NOT NULL DEFAULT 'OPEN',
    CONSTRAINT "Receipt_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Brief" (
    "id" TEXT NOT NULL,
    "receiptId" TEXT NOT NULL,
    "situationFraming" TEXT NOT NULL,
    "entityAnalysis" TEXT,
    "generatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Brief_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "PrepGuide" (
    "id" TEXT NOT NULL,
    "receiptId" TEXT NOT NULL,
    "mode" TEXT NOT NULL,
    "guideTitle" TEXT NOT NULL DEFAULT '',
    "betLabel" TEXT NOT NULL DEFAULT '',
    "totalPrepHours" TEXT NOT NULL DEFAULT '',
    "stages" TEXT NOT NULL,
    "stageLog" TEXT NOT NULL DEFAULT '[]',
    "outcomeStatement" TEXT NOT NULL DEFAULT '',
    "leadingIndicator" TEXT NOT NULL DEFAULT '',
    "kpiLabel" TEXT NOT NULL DEFAULT '',
    "failureSignal" TEXT NOT NULL DEFAULT '',
    "generatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "PrepGuide_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Outcome" (
    "id" TEXT NOT NULL,
    "receiptId" TEXT NOT NULL,
    "what" TEXT NOT NULL,
    "matched" BOOLEAN NOT NULL,
    "regretScore" INTEGER NOT NULL,
    "learning" TEXT,
    "loggedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Outcome_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Account" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "provider" TEXT NOT NULL,
    "providerAccountId" TEXT NOT NULL,
    "refresh_token" TEXT,
    "access_token" TEXT,
    "expires_at" INTEGER,
    "token_type" TEXT,
    "scope" TEXT,
    "id_token" TEXT,
    "session_state" TEXT,
    CONSTRAINT "Account_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "Session" (
    "id" TEXT NOT NULL,
    "sessionToken" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "Session_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "VerificationToken" (
    "identifier" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");
CREATE UNIQUE INDEX "Receipt_receiptId_key" ON "Receipt"("receiptId");
CREATE INDEX "Receipt_userId_idx" ON "Receipt"("userId");
CREATE INDEX "Receipt_sessionId_idx" ON "Receipt"("sessionId");
CREATE INDEX "Receipt_parentId_idx" ON "Receipt"("parentId");
CREATE INDEX "Receipt_createdAt_idx" ON "Receipt"("createdAt");
CREATE INDEX "Receipt_receiptId_idx" ON "Receipt"("receiptId");
CREATE INDEX "Receipt_validationState_idx" ON "Receipt"("validationState");
CREATE INDEX "Receipt_horizon_idx" ON "Receipt"("horizon");
CREATE UNIQUE INDEX "Brief_receiptId_key" ON "Brief"("receiptId");
CREATE UNIQUE INDEX "PrepGuide_receiptId_key" ON "PrepGuide"("receiptId");
CREATE UNIQUE INDEX "Outcome_receiptId_key" ON "Outcome"("receiptId");
CREATE UNIQUE INDEX "Account_provider_providerAccountId_key" ON "Account"("provider", "providerAccountId");
CREATE UNIQUE INDEX "Session_sessionToken_key" ON "Session"("sessionToken");
CREATE UNIQUE INDEX "VerificationToken_token_key" ON "VerificationToken"("token");
CREATE UNIQUE INDEX "VerificationToken_identifier_token_key" ON "VerificationToken"("identifier", "token");

-- Foreign Keys
ALTER TABLE "Receipt" ADD CONSTRAINT "Receipt_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "Receipt" ADD CONSTRAINT "Receipt_prepId_fkey" FOREIGN KEY ("prepId") REFERENCES "PrepSession"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "Receipt" ADD CONSTRAINT "Receipt_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "Receipt"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "Brief" ADD CONSTRAINT "Brief_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "PrepGuide" ADD CONSTRAINT "PrepGuide_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Outcome" ADD CONSTRAINT "Outcome_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Account" ADD CONSTRAINT "Account_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Session" ADD CONSTRAINT "Session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
