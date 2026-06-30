-- AddColumn: parentTributaryIndex
-- Tracks which tributary (0|1|2) spawned this receipt from parent
-- Enables hypercube explorer to show decision tree hierarchy by depth and lineage

ALTER TABLE "Receipt" ADD COLUMN "parentTributaryIndex" INTEGER;

-- Create index for efficient tree queries
CREATE INDEX "Receipt_parentId_parentTributaryIndex_idx" ON "Receipt"("parentId", "parentTributaryIndex");
