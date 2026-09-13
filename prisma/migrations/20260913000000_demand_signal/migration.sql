-- Owned record of demand-probe interactions (ADR-076 Stage 0). Companion to the
-- Vercel custom events mcp_probe_view / mcp_probe_interest, which we do not own
-- and which ad blockers drop. No IP, no user agent stored.
CREATE TABLE "DemandSignal" (
  "id" TEXT NOT NULL,
  "probe" TEXT NOT NULL,
  "action" TEXT NOT NULL,
  "surface" TEXT NOT NULL DEFAULT 'nftt',
  "vid" TEXT,
  "path" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "DemandSignal_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "DemandSignal_probe_action_idx" ON "DemandSignal"("probe", "action");
CREATE INDEX "DemandSignal_createdAt_idx" ON "DemandSignal"("createdAt");
