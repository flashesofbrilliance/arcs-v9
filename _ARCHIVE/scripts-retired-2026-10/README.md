# Retired scripts, October 2026

Scripts moved here by `git mv`, so their history is intact. Restore one with `git mv _ARCHIVE/scripts-retired-2026-10/<name> scripts/<name>`.

| Script | Retired | Why | Evidence |
|---|---|---|---|
| `backlog_status_migrate.py` | 2026-10-18 | One-shot migration of backlog `status` prose to the `state` enum plus `status_note`. The migration is complete and `scripts/backlog_status_check.py --check` gates the result. | Its docstring says one-shot; the only mention elsewhere is the 2026-10-10 night-moves log. |
| `release_notes.py` | 2026-10-18 | Archived on Zach's instruction. Not verified finished: it is a reusable tool (`--since <date>` lists what landed on main from git), and a handoff block in `_ARCHIVE/handoffs.md` still tells readers to run it. | No code, hook, command or CI step references it. Its one output is `_RELEASES/2026-10-06.md`. |
| `receipt_efficacy_probe.py` | 2026-10-18 | Archived on Zach's instruction. Not verified finished: a re-runnable dry-run proof of predictions to closes to Accountant scoring, with zero DB access; its real-DB step needed an explicit yes that was never recorded here. | No code, hook, command or CI step references it. Built for #1029 (receipt provenance). |
| `tributary_backfill_probe.py` | 2026-10-18 | Archived on Zach's instruction. Not verified finished: a read-only probe of whether `Receipt.parentTributaryIndex` can be inferred for older children. No record was found that the backfill itself was ever done. | No code, hook, command or CI step references it. |

The first row was checked as a finished one-shot. The last three were archived by decision, not by proof of completion; restore any of them if the work they serve comes back.
