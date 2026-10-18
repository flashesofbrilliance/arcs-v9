# Retired scripts, October 2026

Scripts moved here by `git mv`, so their history is intact. Restore one with `git mv _ARCHIVE/scripts-retired-2026-10/<name> scripts/<name>`.

| Script | Retired | Why | Evidence |
|---|---|---|---|
| `backlog_status_migrate.py` | 2026-10-18 | One-shot migration of backlog `status` prose to the `state` enum plus `status_note`. The migration is complete and `scripts/backlog_status_check.py --check` gates the result. | Its docstring says one-shot; the only mention elsewhere is the 2026-10-10 night-moves log. |
