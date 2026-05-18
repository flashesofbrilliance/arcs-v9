-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "email" TEXT,
    "name" TEXT,
    "tier" TEXT NOT NULL DEFAULT 'FREE',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "PrepSession" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "stakes" TEXT,
    "horizon" TEXT,
    "protecting" TEXT NOT NULL DEFAULT '[]',
    "confidence" INTEGER,
    "entity" TEXT,
    "adversarialInput" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "Receipt" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT,
    "decision" TEXT NOT NULL,
    "trueNorth" TEXT NOT NULL,
    "whyBullets" TEXT NOT NULL,
    "nciScore" INTEGER NOT NULL,
    "fated" TEXT,
    "paths" TEXT,
    "court" TEXT,
    "courtVerdict" TEXT,
    "mode" TEXT NOT NULL,
    "doorClass" TEXT,
    "macroTags" TEXT NOT NULL DEFAULT '[]',
    "rawResponse" TEXT,
    "entity" TEXT,
    "stakeholders" TEXT,
    "window" TEXT NOT NULL,
    "stakes" TEXT,
    "protecting" TEXT NOT NULL DEFAULT '[]',
    "horizonLocked" BOOLEAN NOT NULL DEFAULT false,
    "yPolarity" TEXT NOT NULL DEFAULT 'BINARY',
    "yConviction" TEXT NOT NULL DEFAULT 'HIGH',
    "yStability" TEXT NOT NULL DEFAULT 'LOCKED',
    "yState" TEXT NOT NULL DEFAULT 'GREEN',
    "yConvictionPrev" TEXT,
    "yDeltaTrigger" TEXT,
    "yConditions" TEXT NOT NULL DEFAULT '[]',
    "yOverride" BOOLEAN NOT NULL DEFAULT false,
    "yOverrideAt" DATETIME,
    "yOverrideNote" TEXT,
    "promotedTo" TEXT,
    "gradientMagnitude" REAL NOT NULL DEFAULT 0.5,
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
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewDate" DATETIME,
    "status" TEXT NOT NULL DEFAULT 'OPEN',
    CONSTRAINT "Receipt_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "Receipt_prepId_fkey" FOREIGN KEY ("prepId") REFERENCES "PrepSession" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "Receipt_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "Receipt" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Brief" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "receiptId" TEXT NOT NULL,
    "situationFraming" TEXT NOT NULL,
    "generatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Brief_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Outcome" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "receiptId" TEXT NOT NULL,
    "what" TEXT NOT NULL,
    "matched" BOOLEAN NOT NULL,
    "regretScore" INTEGER NOT NULL,
    "learning" TEXT,
    "loggedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Outcome_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Account" (
    "id" TEXT NOT NULL PRIMARY KEY,
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
    CONSTRAINT "Account_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Session" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "sessionToken" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "expires" DATETIME NOT NULL,
    CONSTRAINT "Session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "VerificationToken" (
    "identifier" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expires" DATETIME NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE INDEX "Receipt_userId_idx" ON "Receipt"("userId");

-- CreateIndex
CREATE INDEX "Receipt_sessionId_idx" ON "Receipt"("sessionId");

-- CreateIndex
CREATE INDEX "Receipt_parentId_idx" ON "Receipt"("parentId");

-- CreateIndex
CREATE INDEX "Receipt_createdAt_idx" ON "Receipt"("createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "Brief_receiptId_key" ON "Brief"("receiptId");

-- CreateIndex
CREATE UNIQUE INDEX "Outcome_receiptId_key" ON "Outcome"("receiptId");

-- CreateIndex
CREATE UNIQUE INDEX "Account_provider_providerAccountId_key" ON "Account"("provider", "providerAccountId");

-- CreateIndex
CREATE UNIQUE INDEX "Session_sessionToken_key" ON "Session"("sessionToken");

-- CreateIndex
CREATE UNIQUE INDEX "VerificationToken_token_key" ON "VerificationToken"("token");

-- CreateIndex
CREATE UNIQUE INDEX "VerificationToken_identifier_token_key" ON "VerificationToken"("identifier", "token");
