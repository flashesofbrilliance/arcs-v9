-- Compass Lane surfaces (additive). No rename of JobOpportunity/JobSwipe/ForgeRun:
-- those stay so the live board, its API routes, and the pipeline token keep working.
-- Adds the tables the Sources and Debrief surfaces read, plus a copy-backfilled Score.

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
CREATE INDEX "IngestRequest_sourceKey_requestedAt_idx" ON "IngestRequest"("sourceKey", "requestedAt");

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
CREATE UNIQUE INDEX "Score_jobid_targetVersion_key" ON "Score"("jobid", "targetVersion");
CREATE INDEX "Score_jobid_idx" ON "Score"("jobid");
ALTER TABLE "Score" ADD CONSTRAINT "Score_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

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
ALTER TABLE "Correction" ADD CONSTRAINT "Correction_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

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
ALTER TABLE "LaneOutcome" ADD CONSTRAINT "LaneOutcome_jobid_fkey" FOREIGN KEY ("jobid") REFERENCES "JobOpportunity"("jobid") ON DELETE CASCADE ON UPDATE CASCADE;

-- RLS: same fail-closed posture as the jobs board (deny anon + authenticated;
-- server routes use the service role / pipeline token, never the anon key).
ALTER TABLE "Source" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "IngestRequest" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Score" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Correction" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "LaneOutcome" ENABLE ROW LEVEL SECURITY;
