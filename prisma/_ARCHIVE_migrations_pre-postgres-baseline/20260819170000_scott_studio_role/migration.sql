-- Scott tenant role (draft, pattern-matched from robin_studio_role / 20260807170000).
-- NOT verified byte-for-byte against the live robin_app/yuri_app migrations -- diff-review
-- this against those two before applying to production. Same least-privilege posture:
-- SELECT + INSERT + column-scoped UPDATE (status,outcome,variance,lesson,payload) on
-- "SessionReceipt" ONLY. No DELETE, no other tables. Tenant/brand pinned in USING + WITH CHECK
-- on every policy so a compromised route for one tenant cannot read or write another's rows.

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'scott_app') THEN
    CREATE ROLE scott_app LOGIN PASSWORD :'scott_app_password';
  END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO scott_app;
GRANT SELECT, INSERT, UPDATE (status, outcome, variance, lesson, payload) ON "SessionReceipt" TO scott_app;

ALTER TABLE "SessionReceipt" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "scott_app_select" ON "SessionReceipt";
CREATE POLICY "scott_app_select" ON "SessionReceipt"
  FOR SELECT TO scott_app
  USING (tenant = 'scott' AND brand = 'parlance');

DROP POLICY IF EXISTS "scott_app_insert" ON "SessionReceipt";
CREATE POLICY "scott_app_insert" ON "SessionReceipt"
  FOR INSERT TO scott_app
  WITH CHECK (tenant = 'scott' AND brand = 'parlance');

DROP POLICY IF EXISTS "scott_app_update" ON "SessionReceipt"
  ;
CREATE POLICY "scott_app_update" ON "SessionReceipt"
  FOR UPDATE TO scott_app
  USING (tenant = 'scott' AND brand = 'parlance')
  WITH CHECK (tenant = 'scott' AND brand = 'parlance');

-- No DELETE grant, ever. A receipt is filed and scored, never removed.
