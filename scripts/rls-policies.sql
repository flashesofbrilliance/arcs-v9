-- ─────────────────────────────────────────────────────────────────────────────
-- RLS Policies for arcs-v9 / Supabase project owdiiyvphyifukygvxhg
--
-- Architecture note:
--   Prisma connects as the `postgres` superuser role via DATABASE_URL (pooler
--   port 6543). Superusers bypass RLS unconditionally — app-level user scoping
--   is enforced at the API route layer (ADR-001).
--
--   Auth.js v5 manages sessions in the DB, NOT via Supabase Auth. Therefore
--   auth.uid() is always NULL for Prisma queries and cannot be used in policies.
--
--   RLS here protects against:
--     - anon-key access (Supabase dashboard → anon role, supabase-js clients)
--     - authenticated-role access (if Supabase Auth is ever added later)
--     - Any non-superuser direct DB access
--
--   Enabling RLS with no permissive policies = implicit DENY ALL for anon +
--   authenticated roles. Superuser (Prisma) is unaffected.
--
-- To apply: Supabase dashboard → SQL Editor → paste and run.
-- ─────────────────────────────────────────────────────────────────────────────

-- ── 1. Enable RLS on all 9 tables ────────────────────────────────────────────

ALTER TABLE "User"              ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Account"           ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Session"           ENABLE ROW LEVEL SECURITY;
ALTER TABLE "VerificationToken" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Receipt"           ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Brief"             ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PrepGuide"         ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PrepSession"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "Outcome"           ENABLE ROW LEVEL SECURITY;

-- ── 2. Explicit DENY ALL for anon and authenticated roles ─────────────────────
--
-- Supabase automatically denies when no policies exist, but explicit policies
-- make intent clear and survive future policy additions that might open access.

-- User table
CREATE POLICY "deny_anon_user"
  ON "User" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_user"
  ON "User" FOR ALL TO authenticated USING (false);

-- Account table (Auth.js internal — OAuth account links)
CREATE POLICY "deny_anon_account"
  ON "Account" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_account"
  ON "Account" FOR ALL TO authenticated USING (false);

-- Session table (Auth.js internal — active sessions)
CREATE POLICY "deny_anon_session"
  ON "Session" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_session"
  ON "Session" FOR ALL TO authenticated USING (false);

-- VerificationToken table (Auth.js internal — magic link tokens)
-- NOTE: No userId — tokens are ephemeral and keyed by identifier+token.
--       Deny all non-superuser access; app manages these exclusively.
CREATE POLICY "deny_anon_verification_token"
  ON "VerificationToken" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_verification_token"
  ON "VerificationToken" FOR ALL TO authenticated USING (false);

-- Receipt table (core DEWY receipt — user's decision history)
CREATE POLICY "deny_anon_receipt"
  ON "Receipt" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_receipt"
  ON "Receipt" FOR ALL TO authenticated USING (false);

-- Brief table (cartography output — linked to Receipt → User)
CREATE POLICY "deny_anon_brief"
  ON "Brief" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_brief"
  ON "Brief" FOR ALL TO authenticated USING (false);

-- PrepGuide table (step-by-step prep guide — linked to Receipt → User)
CREATE POLICY "deny_anon_prep_guide"
  ON "PrepGuide" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_prep_guide"
  ON "PrepGuide" FOR ALL TO authenticated USING (false);

-- PrepSession table (calibration instrument — linked to Receipt via Receipt.prepId)
-- NOTE: PrepSession has no direct userId. Row isolation is enforced at the
--       API layer: users only see PrepSessions via their own Receipts.
CREATE POLICY "deny_anon_prep_session"
  ON "PrepSession" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_prep_session"
  ON "PrepSession" FOR ALL TO authenticated USING (false);

-- Outcome table (decision outcome log — linked to Receipt → User)
CREATE POLICY "deny_anon_outcome"
  ON "Outcome" FOR ALL TO anon USING (false);
CREATE POLICY "deny_authenticated_outcome"
  ON "Outcome" FOR ALL TO authenticated USING (false);

-- ── 3. Verification query ─────────────────────────────────────────────────────
-- Run after applying to confirm all tables have RLS enabled and policies wired.

SELECT
  c.relname AS table_name,
  c.relrowsecurity AS rls_enabled,
  c.relforcerowsecurity AS rls_forced,
  count(p.policyname) AS policy_count
FROM pg_class c
LEFT JOIN pg_policies p ON p.tablename = c.relname
WHERE c.relname IN (
  'User','Account','Session','VerificationToken',
  'Receipt','Brief','PrepGuide','PrepSession','Outcome'
)
GROUP BY c.relname, c.relrowsecurity, c.relforcerowsecurity
ORDER BY c.relname;
