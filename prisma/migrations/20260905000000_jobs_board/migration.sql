-- Job-search board (jobs.arcs.care): opportunities, swipes, forge runs, settings.
-- Moves the loop's state off the claude.ai artifact store (2026-09-05).

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
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "JobOpportunity_pkey" PRIMARY KEY ("jobid")
);

CREATE INDEX "JobOpportunity_band_composite_idx" ON "JobOpportunity"("band", "composite");
CREATE INDEX "JobOpportunity_firstSeen_idx" ON "JobOpportunity"("firstSeen");

CREATE TABLE "JobSwipe" (
  "jobid" TEXT NOT NULL,
  "direction" TEXT NOT NULL,
  "why" TEXT,
  "at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "userId" TEXT,
  CONSTRAINT "JobSwipe_pkey" PRIMARY KEY ("jobid"),
  CONSTRAINT "JobSwipe_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE
);

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
  CONSTRAINT "ForgeRun_pkey" PRIMARY KEY ("jobid"),
  CONSTRAINT "ForgeRun_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "JobBoardSetting" (
  "key" TEXT NOT NULL,
  "value" TEXT NOT NULL,
  CONSTRAINT "JobBoardSetting_pkey" PRIMARY KEY ("key")
);
