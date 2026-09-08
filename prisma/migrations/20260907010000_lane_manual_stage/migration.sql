-- Manual kanban stage: let a row be advanced by hand (mark applied, move to
-- interview loop) instead of only by derived state. laneStage overrides the
-- derived bucket when set; laneStatus is the fate within a stage.
ALTER TABLE "JobOpportunity"
  ADD COLUMN "laneStage" TEXT,
  ADD COLUMN "laneStatus" TEXT,
  ADD COLUMN "laneMovedAt" TIMESTAMP(3);
