◇ injected env (0) from .env.local // tip: ⌘ suppress logs { quiet: true }
◇ injected env (0) from .env // tip: ◈ encrypted .env [www.dotenvx.com]
-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT,
    "emailVerified" TIMESTAMP(3),
    "name" TEXT,
    "image" TEXT,
    "tier" TEXT NOT NULL DEFAULT 'FREE',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "firstDebriefSentAt" TIMESTAMP(3),
    "debriefOptIn" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ProfileUpload" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "pdfUrl" TEXT,
    "exportUrl" TEXT,
    "skipped" BOOLEAN NOT NULL DEFAULT false,
    "uploadedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ProfileUpload_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PrepSession" (
    "id" TEXT NOT NULL,
    "stakes" TEXT,
    "horizon" TEXT,
    "protecting" TEXT NOT NULL DEFAULT '[]',
    "confidence" INTEGER,
    "entity" TEXT,
    "adversarialInput" TEXT,
    "outcomeHorizon" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "PrepSession_pkey" PRIMARY KEY ("id")
);

-- CreateTable
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
    "nciSelfGrade" TEXT,
    "mode" TEXT NOT NULL,
    "doorClass" TEXT,
    "macroTags" TEXT NOT NULL DEFAULT '[]',
    "atgTributaries" TEXT,
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
    "parentTributaryIndex" INTEGER,
    "version" INTEGER NOT NULL DEFAULT 0,
    "forkPath" TEXT,
    "mergedFrom" TEXT NOT NULL DEFAULT '[]',
    "prepId" TEXT,
    "batonId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewDate" TIMESTAMP(3),
    "status" TEXT NOT NULL DEFAULT 'OPEN',
    "reminderDate" TEXT,
    "debriefSentAt" TIMESTAMP(3),

    CONSTRAINT "Receipt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Brief" (
    "id" TEXT NOT NULL,
    "receiptId" TEXT NOT NULL,
    "situationFraming" TEXT NOT NULL,
    "entityAnalysis" TEXT,
    "generatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Brief_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SageTrace" (
    "id" TEXT NOT NULL,
    "receiptId" TEXT NOT NULL,
    "fired" BOOLEAN NOT NULL,
    "signal" TEXT,
    "failureReason" TEXT,
    "latencyMs" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "SageTrace_pkey" PRIMARY KEY ("id")
);

-- CreateTable
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

-- CreateTable
CREATE TABLE "JobOpportunity" (
    "jobid" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "company" TEXT NOT NULL,
    "location" TEXT,
    "url" TEXT NOT NULL,
    "alertQuery" TEXT,
    "alertLocation" TEXT,
    "source" TEXT NOT NULL DEFAULT 'linkedin_alert_digest',
    "firstSeen" TIMESTAMP(3) NOT NULL,
    "seenCount" INTEGER NOT NULL DEFAULT 1,
    "salary" TEXT,
    "composite" DOUBLE PRECISION,
    "band" TEXT NOT NULL DEFAULT 'UNSCORED',
    "dims" TEXT,
    "gates" TEXT,
    "assessment" TEXT,
    "atsClass" TEXT,
    "atsName" TEXT,
    "companyType" TEXT,
    "compBand" TEXT,
    "workLocation" TEXT,
    "hmKind" TEXT,
    "hmText" TEXT,
    "contactType" TEXT,
    "contactDetail" TEXT,
    "contactUrl" TEXT,
    "nextStep" TEXT,
    "jdHits" TEXT,
    "unscoredWhy" TEXT,
    "scoredAt" TIMESTAMP(3),
    "laneStage" TEXT,
    "laneStatus" TEXT,
    "laneMovedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "JobOpportunity_pkey" PRIMARY KEY ("jobid")
);

-- CreateTable
CREATE TABLE "JobSwipe" (
    "jobid" TEXT NOT NULL,
    "direction" TEXT NOT NULL,
    "why" TEXT,
    "at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "userId" TEXT,

    CONSTRAINT "JobSwipe_pkey" PRIMARY KEY ("jobid")
);

-- CreateTable
CREATE TABLE "ForgeRun" (
    "jobid" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "url" TEXT,
    "resumeUrl" TEXT,
    "hmKind" TEXT,
    "hmText" TEXT,
    "contactType" TEXT,
    "contactDetail" TEXT,
    "contactUrl" TEXT,
    "notes" TEXT,
    "requestedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ForgeRun_pkey" PRIMARY KEY ("jobid")
);

-- CreateTable
CREATE TABLE "JobBoardSetting" (
    "key" TEXT NOT NULL,
    "value" TEXT NOT NULL,

    CONSTRAINT "JobBoardSetting_pkey" PRIMARY KEY ("key")
);

-- CreateTable
CREATE TABLE "Source" (
    "key" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "adapter" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'proposed',
    "lastRunAt" TIMESTAMP(3),
    "lastError" TEXT,
    "watermark" TIMESTAMP(3),
    "pollWindow" TEXT,
    "note" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Source_pkey" PRIMARY KEY ("key")
);

-- CreateTable
CREATE TABLE "IngestRequest" (
    "id" TEXT NOT NULL,
    "sourceKey" TEXT NOT NULL,
    "fromDate" TEXT,
    "toDate" TEXT,
    "query" TEXT,
    "status" TEXT NOT NULL DEFAULT 'queued',
    "rowsAdded" INTEGER,
    "note" TEXT,
    "requestedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completedAt" TIMESTAMP(3),
    "requestedBy" TEXT,

    CONSTRAINT "IngestRequest_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Score" (
    "id" TEXT NOT NULL,
    "jobid" TEXT NOT NULL,
    "targetVersion" TEXT NOT NULL,
    "composite" DOUBLE PRECISION,
    "band" TEXT NOT NULL,
    "dims" TEXT,
    "gates" TEXT,
    "assessment" TEXT,
    "scoredAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Score_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Correction" (
    "jobid" TEXT NOT NULL,
    "learned" TEXT NOT NULL,
    "pattern" TEXT,
    "avoid" TEXT,
    "logic" TEXT,
    "links" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Correction_pkey" PRIMARY KEY ("jobid")
);

-- CreateTable
CREATE TABLE "LaneOutcome" (
    "jobid" TEXT NOT NULL,
    "fate" TEXT NOT NULL,
    "predictedComposite" DOUBLE PRECISION,
    "actualDims" TEXT,
    "actualNote" TEXT,
    "honestyLabel" TEXT,
    "closedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "LaneOutcome_pkey" PRIMARY KEY ("jobid")
);

-- CreateTable
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

-- CreateTable
CREATE TABLE "Tribune" (
    "id" TEXT NOT NULL,
    "receiptId" TEXT NOT NULL,
    "phase" TEXT NOT NULL,
    "riskTier" TEXT,
    "labResult" TEXT,
    "courtInvoked" BOOLEAN NOT NULL DEFAULT false,
    "driftState" TEXT,
    "nciDelta" DOUBLE PRECISION,
    "clarityMode" TEXT NOT NULL DEFAULT 'SIMPLE',
    "batonId" TEXT,
    "boardVotes" TEXT,
    "content" TEXT NOT NULL,
    "model" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Tribune_pkey" PRIMARY KEY ("id")
);

-- CreateTable
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

-- CreateTable
CREATE TABLE "Session" (
    "id" TEXT NOT NULL,
    "sessionToken" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Session_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "VerificationToken" (
    "identifier" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL
);

-- CreateTable
CREATE TABLE "Annotation" (
    "id" TEXT NOT NULL,
    "userId" TEXT,
    "receiptId" TEXT NOT NULL,
    "surface" TEXT NOT NULL DEFAULT 'BRIEF',
    "anchorText" TEXT NOT NULL,
    "preContext" TEXT NOT NULL DEFAULT '',
    "postContext" TEXT NOT NULL DEFAULT '',
    "type" TEXT NOT NULL,
    "body" TEXT NOT NULL,
    "linkedRef" TEXT,
    "kernel" TEXT,
    "hardened" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Annotation_pkey" PRIMARY KEY ("id")
);

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

-- CreateTable
CREATE TABLE "ScanSignal" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "version" INTEGER NOT NULL DEFAULT 1,
    "parentSignalId" TEXT,
    "signalType" TEXT NOT NULL DEFAULT 'profile',
    "calibrationBasis" TEXT NOT NULL DEFAULT 'cold_read',
    "sourceBlobUrls" TEXT,
    "outputBlobUrl" TEXT,
    "archetypeStack" TEXT NOT NULL DEFAULT '[]',
    "genomeThreads" TEXT NOT NULL DEFAULT '{}',
    "signalContrast" TEXT NOT NULL DEFAULT '{}',
    "loadBearingPoint" TEXT NOT NULL DEFAULT '',
    "packagingGap" TEXT NOT NULL DEFAULT '',
    "evidenceLedger" TEXT NOT NULL DEFAULT '[]',
    "platformInferences" TEXT,
    "networkResonance" TEXT,
    "driftState" TEXT NOT NULL DEFAULT 'CLEAR',
    "receiptsSince" INTEGER NOT NULL DEFAULT 0,
    "deltaThreshold" INTEGER NOT NULL DEFAULT 5,
    "signalEmbedding" TEXT,
    "metadata" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ScanSignal_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ScanFeedback" (
    "id" TEXT NOT NULL,
    "signalId" TEXT NOT NULL,
    "feedbackVersion" INTEGER NOT NULL DEFAULT 1,
    "payload" TEXT NOT NULL DEFAULT '{}',
    "overallIntensity" TEXT,
    "deltaGateDecision" TEXT,
    "annotationBlobUrls" TEXT,
    "feedbackEmbedding" TEXT,
    "metadata" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ScanFeedback_pkey" PRIMARY KEY ("id")
);

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
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "ProfileUpload_userId_key" ON "ProfileUpload"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "Receipt_receiptId_key" ON "Receipt"("receiptId");

-- CreateIndex
CREATE INDEX "Receipt_userId_idx" ON "Receipt"("userId");

-- CreateIndex
CREATE INDEX "Receipt_sessionId_idx" ON "Receipt"("sessionId");

-- CreateIndex
CREATE INDEX "Receipt_parentId_idx" ON "Receipt"("parentId");

-- CreateIndex
CREATE INDEX "Receipt_createdAt_idx" ON "Receipt"("createdAt");

-- CreateIndex
CREATE INDEX "Receipt_receiptId_idx" ON "Receipt"("receiptId");

-- CreateIndex
CREATE INDEX "Receipt_validationState_idx" ON "Receipt"("validationState");

-- CreateIndex
CREATE INDEX "Receipt_horizon_idx" ON "Receipt"("horizon");

-- CreateIndex
CREATE UNIQUE INDEX "Brief_receiptId_key" ON "Brief"("receiptId");

-- CreateIndex
CREATE UNIQUE INDEX "SageTrace_receiptId_key" ON "SageTrace"("receiptId");

-- CreateIndex
CREATE INDEX "SageTrace_fired_idx" ON "SageTrace"("fired");

-- CreateIndex
CREATE UNIQUE INDEX "PrepGuide_receiptId_key" ON "PrepGuide"("receiptId");

-- CreateIndex
CREATE INDEX "JobOpportunity_band_composite_idx" ON "JobOpportunity"("band", "composite");

-- CreateIndex
CREATE INDEX "JobOpportunity_firstSeen_idx" ON "JobOpportunity"("firstSeen");

-- CreateIndex
CREATE INDEX "IngestRequest_sourceKey_requestedAt_idx" ON "IngestRequest"("sourceKey", "requestedAt");

-- CreateIndex
CREATE INDEX "Score_jobid_idx" ON "Score"("jobid");

-- CreateIndex
CREATE UNIQUE INDEX "Score_jobid_targetVersion_key" ON "Score"("jobid", "targetVersion");

-- CreateIndex
CREATE UNIQUE INDEX "Outcome_receiptId_key" ON "Outcome"("receiptId");

-- CreateIndex
CREATE INDEX "Tribune_receiptId_idx" ON "Tribune"("receiptId");

-- CreateIndex
CREATE INDEX "Tribune_batonId_idx" ON "Tribune"("batonId");

-- CreateIndex
CREATE UNIQUE INDEX "Tribune_receiptId_phase_key" ON "Tribune"("receiptId", "phase");

-- CreateIndex
CREATE UNIQUE INDEX "Account_provider_providerAccountId_key" ON "Account"("provider", "providerAccountId");

-- CreateIndex
CREATE UNIQUE INDEX "Session_sessionToken_key" ON "Session"("sessionToken");

-- CreateIndex
CREATE UNIQUE INDEX "VerificationToken_token_key" ON "VerificationToken"("token");

-- CreateIndex
CREATE UNIQUE INDEX "VerificationToken_identifier_token_key" ON "VerificationToken"("identifier", "token");

-- CreateIndex
CREATE INDEX "Annotation_receiptId_idx" ON "Annotation"("receiptId");

-- CreateIndex
CREATE INDEX "Annotation_userId_idx" ON "Annotation"("userId");

-- CreateIndex
CREATE INDEX "Lead_source_idx" ON "Lead"("source");

-- CreateIndex
CREATE INDEX "Lead_createdAt_idx" ON "Lead"("createdAt");

-- CreateIndex
CREATE INDEX "ScanSignal_userId_idx" ON "ScanSignal"("userId");

-- CreateIndex
CREATE INDEX "ScanSignal_parentSignalId_idx" ON "ScanSignal"("parentSignalId");

-- CreateIndex
CREATE INDEX "ScanSignal_signalType_idx" ON "ScanSignal"("signalType");

-- CreateIndex
CREATE INDEX "ScanSignal_driftState_idx" ON "ScanSignal"("driftState");

-- CreateIndex
CREATE INDEX "ScanSignal_createdAt_idx" ON "ScanSignal"("createdAt");

-- CreateIndex
CREATE INDEX "ScanFeedback_signalId_idx" ON "ScanFeedback"("signalId");

-- CreateIndex
CREATE INDEX "ScanFeedback_deltaGateDecision_idx" ON "ScanFeedback"("deltaGateDecision");

-- CreateIndex
CREATE INDEX "ScanFeedback_createdAt_idx" ON "ScanFeedback"("createdAt");

-- CreateIndex
CREATE INDEX "SessionReceipt_tenant_brand_sessionId_idx" ON "SessionReceipt"("tenant", "brand", "sessionId");

-- CreateIndex
CREATE INDEX "SessionReceipt_scoreBackDate_idx" ON "SessionReceipt"("scoreBackDate");

-- AddForeignKey
ALTER TABLE "ProfileUpload" ADD CONSTRAINT "ProfileUpload_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Receipt" ADD CONSTRAINT "Receipt_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Receipt" ADD CONSTRAINT "Receipt_prepId_fkey" FOREIGN KEY ("prepId") REFERENCES "PrepSession"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Receipt" ADD CONSTRAINT "Receipt_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "Receipt"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Brief" ADD CONSTRAINT "Brief_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SageTrace" ADD CONSTRAINT "SageTrace_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PrepGuide" ADD CONSTRAINT "PrepGuide_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "JobSwipe" ADD CONSTRAINT "JobSwipe_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ForgeRun" ADD CONSTRAINT "ForgeRun_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Score" ADD CONSTRAINT "Score_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Correction" ADD CONSTRAINT "Correction_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LaneOutcome" ADD CONSTRAINT "LaneOutcome_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Outcome" ADD CONSTRAINT "Outcome_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Tribune" ADD CONSTRAINT "Tribune_receiptId_fkey" FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Tribune" ADD CONSTRAINT "Tribune_batonId_fkey" FOREIGN KEY ("batonId") REFERENCES "Receipt"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Account" ADD CONSTRAINT "Account_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Session" ADD CONSTRAINT "Session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ScanSignal" ADD CONSTRAINT "ScanSignal_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ScanSignal" ADD CONSTRAINT "ScanSignal_parentSignalId_fkey" FOREIGN KEY ("parentSignalId") REFERENCES "ScanSignal"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ScanFeedback" ADD CONSTRAINT "ScanFeedback_signalId_fkey" FOREIGN KEY ("signalId") REFERENCES "ScanSignal"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SessionReceipt" ADD CONSTRAINT "SessionReceipt_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "SessionReceipt"("id") ON DELETE SET NULL ON UPDATE CASCADE;

