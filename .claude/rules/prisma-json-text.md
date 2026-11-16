---
paths:
  - "src/**"
  - "prisma/**"
---

<!-- Moved from AGENTS.md gotcha 3 on 2026-11-16 (scrum groom, Zach's verdict: move). Loads when Claude reads, writes or edits a matching file. -->

**JSON arrays are TEXT strings.** The Prisma schema stores JSON arrays in TEXT columns (a SQLite-compat choice, kept on Postgres for now). Always `JSON.stringify()` before a write and `JSON.parse()` after a read. Do not switch a column to the Prisma `Json` type without a migration decision.
