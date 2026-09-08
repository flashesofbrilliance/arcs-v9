-- Second Studio tenant (registry generalization proof): yuri_app, mirroring
-- robin_app (20260807170000). Same least-privilege posture, pinned to a
-- different tenant/brand, proving the pattern is not robin-specific.
--   * SELECT + INSERT + column-scoped UPDATE (status,outcome,variance,lesson,
--     payload) on "SessionReceipt" ONLY. No DELETE, no other tables.
--   * policies pin tenant='yuri' AND brand='google' on read, write, AND update
--     (USING + WITH CHECK), so a close can never cross tenants.
-- LOGIN + password are granted out-of-band (never committed): after this
-- migration applies, provision the credential and set YURI_DATABASE_URL, e.g.
--     ALTER ROLE yuri_app WITH LOGIN PASSWORD '<generated>';
-- Until then this is a harmless NOLOGIN shell role and the route fail-closes
-- (src/lib/receipt-studio.ts throws if YURI_DATABASE_URL is unset).

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'yuri_app') THEN
    CREATE ROLE yuri_app NOLOGIN;
  END IF;
END
$$;

GRANT USAGE ON SCHEMA "public" TO yuri_app;
GRANT SELECT, INSERT ON TABLE "SessionReceipt" TO yuri_app;
GRANT UPDATE (status, outcome, variance, lesson, payload) ON TABLE "SessionReceipt" TO yuri_app;

DROP POLICY IF EXISTS "yuri_app_select" ON "SessionReceipt";
CREATE POLICY "yuri_app_select" ON "SessionReceipt"
  FOR SELECT TO yuri_app
  USING (tenant = 'yuri' AND brand = 'google');

DROP POLICY IF EXISTS "yuri_app_insert" ON "SessionReceipt";
CREATE POLICY "yuri_app_insert" ON "SessionReceipt"
  FOR INSERT TO yuri_app
  WITH CHECK (tenant = 'yuri' AND brand = 'google');

DROP POLICY IF EXISTS "yuri_app_update" ON "SessionReceipt";
CREATE POLICY "yuri_app_update" ON "SessionReceipt"
  FOR UPDATE TO yuri_app
  USING (tenant = 'yuri' AND brand = 'google')
  WITH CHECK (tenant = 'yuri' AND brand = 'google');
