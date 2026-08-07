-- Least-privilege role for the anonymous Robin Receipt Studio route (CISO review).
-- Mirrors louisville_app (20260731140000) but for the robin/zensai tenant, and
-- adds UPDATE — the Robin Studio can CLOSE/SCORE a receipt (OPEN -> SCORED), which
-- Louisville's file-only flow never needed. Still no DELETE, still one table.
--   * table access: SELECT + INSERT + UPDATE on "SessionReceipt" ONLY (no DELETE,
--     no other tables) — a compromised route cannot touch User/Receipt/Lead/etc.
--   * policies pin tenant='robin' AND brand='zensai' on read, write, AND update
--     (both USING and WITH CHECK), so a close can never move a row across tenants.
-- LOGIN + password are granted out-of-band (never committed): after this migration
-- applies, provision the credential and set ROBIN_DATABASE_URL, e.g.
--     ALTER ROLE robin_app WITH LOGIN PASSWORD '<generated>';
-- Until then this is a harmless NOLOGIN shell role and the route fail-closes
-- (db-robin.ts throws if ROBIN_DATABASE_URL is unset).

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'robin_app') THEN
    CREATE ROLE robin_app NOLOGIN;
  END IF;
END
$$;

GRANT USAGE ON SCHEMA "public" TO robin_app;
GRANT SELECT, INSERT, UPDATE ON TABLE "SessionReceipt" TO robin_app;

-- Tenant-pinned policies, scoped to this role only (anon/authenticated stay deny-all).
DROP POLICY IF EXISTS "robin_app_select" ON "SessionReceipt";
CREATE POLICY "robin_app_select" ON "SessionReceipt"
  FOR SELECT TO robin_app
  USING (tenant = 'robin' AND brand = 'zensai');

DROP POLICY IF EXISTS "robin_app_insert" ON "SessionReceipt";
CREATE POLICY "robin_app_insert" ON "SessionReceipt"
  FOR INSERT TO robin_app
  WITH CHECK (tenant = 'robin' AND brand = 'zensai');

DROP POLICY IF EXISTS "robin_app_update" ON "SessionReceipt";
CREATE POLICY "robin_app_update" ON "SessionReceipt"
  FOR UPDATE TO robin_app
  USING (tenant = 'robin' AND brand = 'zensai')
  WITH CHECK (tenant = 'robin' AND brand = 'zensai');
