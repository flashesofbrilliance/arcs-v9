-- scripts/activation-check.sql
-- Post-deploy activation check for ADR-016 Option C
-- Run against xbbpiryokswwvcrcutge (prod DB) to verify anonymous + auth flows are healthy.
-- Usage: paste into Supabase SQL editor or run via MCP execute_sql

-- 1. Anonymous receipts written (userId=null, sessionId populated)
SELECT
  count(*) AS anon_receipt_count,
  min("createdAt") AS first_anon_receipt,
  max("createdAt") AS latest_anon_receipt
FROM "Receipt"
WHERE "userId" IS NULL;

-- 2. Authenticated users created via magic link
SELECT
  count(*) AS user_count,
  min("createdAt") AS first_user,
  max("createdAt") AS latest_user
FROM "User";

-- 3. Active sessions
SELECT count(*) AS active_session_count
FROM "Session"
WHERE expires > NOW();

-- 4. Pending verification tokens (magic links sent but not yet clicked)
SELECT count(*) AS pending_magic_links
FROM "VerificationToken"
WHERE expires > NOW();

-- 5. Claimed receipts (anonymous → authenticated migration working)
SELECT count(*) AS claimed_receipt_count
FROM "Receipt"
WHERE "userId" IS NOT NULL;

-- 6. NCI distribution on anonymous receipts (compass quality check)
SELECT
  CASE
    WHEN "nciScore" >= 70 THEN 'HIGH (≥70)'
    WHEN "nciScore" >= 45 THEN 'MED (45-69)'
    ELSE 'LOW (<45)'
  END AS nci_band,
  count(*) AS count,
  round(avg("nciScore")::numeric, 1) AS avg_nci
FROM "Receipt"
WHERE "userId" IS NULL
GROUP BY 1
ORDER BY 1;
