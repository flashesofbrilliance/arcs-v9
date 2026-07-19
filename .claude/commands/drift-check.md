# /drift-check

> Run the ARCS drift audit on demand (instead of waiting for the 04:00 UTC sentinel). Read-only:
> reports, does not commit. Billing tier: SUBSCRIPTION (interactive).

> **Rubric + thresholds source of truth:** `_DECISIONS/ADR-035-commit-nci-rubric.md`.

## Steps

1. **Git audit:** `git log --oneline --since='48 hours ago'`. Extract every `[NCI:XX]` score; list commits
   missing a tag entirely (SKIP is a valid tag, absence is not).
2. **NCI trend:** average of the last 5 *scored* (non-SKIP) commits; direction (up/flat/down); and whether
   any commit in the last 48h dropped **>10 pts** from the previous scored one (ADR-035 drift rule).
3. **SKIP ratio:** what fraction of recent commits are `[NCI:SKIP]`. A high ratio is fine if they're genuinely
   docs/chore (ADR-035), but flag it if runtime-behavior commits (`src/`/`prisma/`/`operators/`/`runtime/`)
   are skipping the score.
4. **Verdict — output one:**
   - ✅ ON TRACK — recent commits present, scored ones ≥50, no drift.
   - ⚠️ IDLE — no commits in 48h (note it; not necessarily bad).
   - 🔴 DRIFT — scored NCI dropping >10pts, or runtime commits skipping the score.
5. **Summary table:**

   | Metric | Value |
   |--------|-------|
   | Commits (48h) | N |
   | Scored / SKIP / untagged | a / b / c |
   | Avg NCI (last 5 scored) | XX/100 |
   | Trend | up/flat/down |
   | Drift | none / ⚠️ −N pts |
   | Verdict | ✅/⚠️/🔴 |

Do not commit or modify files — this command only reports. (The scheduled sentinel is the one that writes
drift warnings; see `_PATTERNS/2026-07-19-out-of-band-actions.md` §A.)
