#!/usr/bin/env python3
"""Fail when a Prisma migration CREATEs a table without enabling RLS on it.

Why: prod Postgres (Supabase) serves the public schema over PostgREST with default
grants to anon/authenticated. A table created without ENABLE ROW LEVEL SECURITY is
readable AND writable with the public key. Tribune shipped that way (2026-09-06) and
sat open for three weeks. Checks the whole migration history: a CREATE TABLE passes if
ANY migration (same or later) enables RLS on it. Stdlib only.

Usage: python3 scripts/migration_rls_lint.py [migrations_dir]
"""
import re
import sys
from pathlib import Path

CREATE = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:"?public"?\.)?"?(\w+)"?', re.I)
ENABLE = re.compile(r'ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:ONLY\s+)?(?:"?public"?\.)?"?(\w+)"?\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY', re.I)

# Tables whose RLS was enabled out-of-band (scripts/rls-policies.sql / the Supabase-side
# rls_deny_all migration), not in a Prisma migration. Verified live 2026-09-28: every public
# table has relrowsecurity=true. Frozen: a NEW table must enable RLS in its own migration.
BASELINE_OUT_OF_BAND = {
    "Account", "Brief", "DemandSignal", "Outcome", "PrepGuide", "PrepSession",
    "ProfileUpload", "Receipt", "Session", "User", "VerificationToken",
    "new_Receipt",  # SQLite table-rebuild temp name, renamed to Receipt in the same migration
}


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "prisma/migrations")
    created: dict[str, str] = {}
    enabled: set[str] = set()
    for f in sorted(root.glob("*/migration.sql")):
        sql = re.sub(r"--[^\n]*", "", f.read_text())
        for t in CREATE.findall(sql):
            created.setdefault(t, f.parent.name)
        enabled.update(ENABLE.findall(sql))
    missing = {t: m for t, m in created.items() if t not in enabled and t not in BASELINE_OUT_OF_BAND}
    for t, m in sorted(missing.items()):
        print(f"✖ {t} (created in {m}) never gets ENABLE ROW LEVEL SECURITY", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
