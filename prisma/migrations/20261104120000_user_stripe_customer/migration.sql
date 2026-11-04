-- User.stripeCustomerId: set by the Stripe webhook when someone subscribes to ARCS Pro,
-- so later subscription events (cancel, lapse) find the user. Additive, nullable,
-- no backfill. Apply with `prisma migrate deploy`, never `db push`.
ALTER TABLE "User" ADD COLUMN "stripeCustomerId" TEXT;
CREATE UNIQUE INDEX "User_stripeCustomerId_key" ON "User"("stripeCustomerId");
