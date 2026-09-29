-- Close a public-API exposure: 20260906000000_tribune created "Tribune" without the
-- ENABLE ROW LEVEL SECURITY line its sibling migrations carry, and _prisma_migrations was
-- never covered. With RLS off and default grants, the anon key could read and write both
-- over PostgREST. Deny-all (RLS on, no policies) matches every other public table; the app
-- connects as postgres (BYPASSRLS), so it is unaffected. Applied live 2026-09-28; idempotent.
ALTER TABLE "Tribune" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "_prisma_migrations" ENABLE ROW LEVEL SECURITY;
