-- ADR-020 Tribune Intelligence Layer: three-phase annotation rows that wrap a Receipt.
-- Additive only. Receipt gains a nullable batonId (forward chain link); no existing
-- column changes. Tribune rows cascade-delete with their receipt.

ALTER TABLE "Receipt" ADD COLUMN IF NOT EXISTS "batonId" TEXT;

CREATE TABLE "Tribune" (
  "id"           TEXT NOT NULL,
  "receiptId"    TEXT NOT NULL,
  "phase"        TEXT NOT NULL,
  "riskTier"     TEXT,
  "labResult"    TEXT,
  "courtInvoked" BOOLEAN NOT NULL DEFAULT false,
  "driftState"   TEXT,
  "nciDelta"     DOUBLE PRECISION,
  "clarityMode"  TEXT NOT NULL DEFAULT 'SIMPLE',
  "batonId"      TEXT,
  "boardVotes"   TEXT,
  "content"      TEXT NOT NULL,
  "model"        TEXT,
  "createdAt"    TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT "Tribune_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "Tribune_phase_check" CHECK ("phase" IN ('anterior', 'proactive', 'posterior')),
  CONSTRAINT "Tribune_riskTier_check" CHECK ("riskTier" IS NULL OR "riskTier" IN ('baseline', 'asymmetric', 'ruin'))
);

CREATE UNIQUE INDEX "Tribune_receiptId_phase_key" ON "Tribune"("receiptId", "phase");
CREATE INDEX "Tribune_receiptId_idx" ON "Tribune"("receiptId");
CREATE INDEX "Tribune_batonId_idx" ON "Tribune"("batonId");

ALTER TABLE "Tribune" ADD CONSTRAINT "Tribune_receiptId_fkey"
  FOREIGN KEY ("receiptId") REFERENCES "Receipt"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Tribune" ADD CONSTRAINT "Tribune_batonId_fkey"
  FOREIGN KEY ("batonId") REFERENCES "Receipt"("id") ON DELETE SET NULL ON UPDATE CASCADE;
