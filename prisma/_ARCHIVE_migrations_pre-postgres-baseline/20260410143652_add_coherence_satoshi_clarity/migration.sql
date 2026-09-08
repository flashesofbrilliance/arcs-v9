-- RedefineTables
PRAGMA defer_foreign_keys=ON;
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Receipt" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT,
    "decision" TEXT NOT NULL,
    "trueNorth" TEXT NOT NULL,
    "whyBullets" TEXT NOT NULL,
    "nciScore" INTEGER NOT NULL,
    "coherencePct" INTEGER,
    "isSatoshi" BOOLEAN NOT NULL DEFAULT false,
    "clarityMode" TEXT NOT NULL DEFAULT 'SIMPLE',
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
INSERT INTO "new_Receipt" ("court", "courtVerdict", "createdAt", "decision", "doorClass", "entity", "fated", "flowTopology", "forkPath", "gradientDirection", "gradientMagnitude", "horizonLocked", "id", "macroTags", "manifoldCurvature", "mergedFrom", "mode", "nciScore", "parentId", "paths", "prepId", "promotedTo", "protecting", "rawResponse", "renderResolution", "reviewDate", "sessionId", "stakeholders", "stakes", "status", "trueNorth", "userId", "version", "whyBullets", "window", "yConditions", "yConviction", "yConvictionPrev", "yDeltaTrigger", "yOverride", "yOverrideAt", "yOverrideNote", "yPolarity", "yStability", "yState") SELECT "court", "courtVerdict", "createdAt", "decision", "doorClass", "entity", "fated", "flowTopology", "forkPath", "gradientDirection", "gradientMagnitude", "horizonLocked", "id", "macroTags", "manifoldCurvature", "mergedFrom", "mode", "nciScore", "parentId", "paths", "prepId", "promotedTo", "protecting", "rawResponse", "renderResolution", "reviewDate", "sessionId", "stakeholders", "stakes", "status", "trueNorth", "userId", "version", "whyBullets", "window", "yConditions", "yConviction", "yConvictionPrev", "yDeltaTrigger", "yOverride", "yOverrideAt", "yOverrideNote", "yPolarity", "yStability", "yState" FROM "Receipt";
DROP TABLE "Receipt";
ALTER TABLE "new_Receipt" RENAME TO "Receipt";
CREATE INDEX "Receipt_userId_idx" ON "Receipt"("userId");
CREATE INDEX "Receipt_sessionId_idx" ON "Receipt"("sessionId");
CREATE INDEX "Receipt_parentId_idx" ON "Receipt"("parentId");
CREATE INDEX "Receipt_createdAt_idx" ON "Receipt"("createdAt");
PRAGMA foreign_keys=ON;
PRAGMA defer_foreign_keys=OFF;
