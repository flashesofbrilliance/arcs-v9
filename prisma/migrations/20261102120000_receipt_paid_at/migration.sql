-- Receipt.paidAt: set by the Stripe webhook when a brief is bought. Additive, nullable,
-- no backfill. Apply with `prisma migrate deploy`, never `db push`.
ALTER TABLE "Receipt" ADD COLUMN "paidAt" TIMESTAMP(3);
