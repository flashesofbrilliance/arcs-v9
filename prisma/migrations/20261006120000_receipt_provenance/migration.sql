-- Receipt.provenance ("test" | "real" | NULL legacy) and Outcome.synthetic. Additive, nullable /
-- defaulted, no backfill here: tagging existing rows is a separate, explicitly approved write.
-- Apply with `prisma migrate deploy`, never `db push`.
ALTER TABLE "Receipt" ADD COLUMN "provenance" TEXT;
ALTER TABLE "Outcome" ADD COLUMN "synthetic" BOOLEAN NOT NULL DEFAULT false;
