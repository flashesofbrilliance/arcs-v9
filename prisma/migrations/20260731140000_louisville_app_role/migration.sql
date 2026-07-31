-- Least-privilege role for the anonymous Louisville routes (CISO review follow-up).
-- The main app connects as postgres (BYPASSRLS); these two public routes instead
-- connect as louisville_app, for which RLS is ENFORCED and tenant-pinned:
--   * table access: SELECT + INSERT on "SessionReceipt" ONLY (no UPDATE/DELETE,
--     no other tables) — a compromised route cannot touch User/Receipt/Lead/etc.
--   * policies pin tenant='jeben' AND brand='louisvillebrands' on read AND write.
-- LOGIN + password are granted out-of-band (never committed); on a fresh DB this
-- migration leaves a NOLOGIN shell role that is harmless until credentials are set.

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'louisville_app') THEN
    CREATE ROLE louisville_app NOLOGIN;
  END IF;
END
$$;

GRANT USAGE ON SCHEMA "public" TO louisville_app;
GRANT SELECT, INSERT ON TABLE "SessionReceipt" TO louisville_app;

-- Tenant-pinned policies, scoped to this role only (anon/authenticated stay deny-all).
DROP POLICY IF EXISTS "louisville_app_select" ON "SessionReceipt";
CREATE POLICY "louisville_app_select" ON "SessionReceipt"
  FOR SELECT TO louisville_app
  USING (tenant = 'jeben' AND brand = 'louisvillebrands');

DROP POLICY IF EXISTS "louisville_app_insert" ON "SessionReceipt";
CREATE POLICY "louisville_app_insert" ON "SessionReceipt"
  FOR INSERT TO louisville_app
  WITH CHECK (tenant = 'jeben' AND brand = 'louisvillebrands');
