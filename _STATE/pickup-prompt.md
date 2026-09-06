# Pickup prompt — the keel (outcome-capture rate)

**The fold:** *external = apply-with-governor.* An external directive (spec these, dogfood these) is
not refused and not maximally built — it is **applied through the write-lock-paradox governor**: the
smallest honest cut first, widened only on evidence. This session applied that governor to the P1 keel.

## The keel — capture RATE (not build)
- The outcome-capture **mechanism is fully built** (handler · debrief email · long-horizon cron ·
  DebriefCard · reminders opt-in). Verified by source read 2026-09-06.
- The gap is **rate**: 247 receipts, **2 outcomes**, ~0 externally-validated (Supabase-MCP-verified
  2026-09-05). Root cause is behavioral (forget-the-fitting, real-user-def §8) **and** a surfacing gap:
  `DebriefCard` renders only on `/brief/[id]`, so nothing pulls a returning user to close.

## Built this session (surgical first cut — governor-gated dark)
- `GET /api/receipts/ripe` — auth-gated read of the caller's own OPEN short-window seed receipts with
  no outcome, past their window (reminderDate or conservative age floor). NOTOMATION-clean: candidates
  only, no derivation. `build` green; smoke `200 {"ripe":[]}` unauth.
- Dashboard banner (`src/app/dashboard/page.tsx`) → top ripe receipt's `/debrief/[id]`. Mirrors the
  `onboardingNudge` pattern; no new dep, inline styles.
- Governor = dark flag `NEXT_PUBLIC_OUTCOME_NUDGE` (+ server mirror `OUTCOME_NUDGE` in `src/lib/flags.ts`).
  **Default OFF → draft copy reaches no real user.**

## Next (in order — do not skip)
1. **Dogfood locally:** flip `NEXT_PUBLIC_OUTCOME_NUDGE=true` against a dev.db with the founder's
   receipts. Does the pull produce closes the email didn't? That is the whole test.
2. **Bless the DRAFT copy** (banner wording) before any real-user exposure. Marked `DRAFT COPY` at the mount.
3. **`privacy-review` + `ciso-review`** on the ripe route before prod-widening.
4. Widen the flag only on evidence (founder-in-prod → real users). Edge-function reliability layer
   (seam step 2) only if plumbing proves the binding constraint — it is not yet (capture is behavioral).

## Two keels, don't conflate
- **This cut** moves *capture* (self-graded matched/regret).
- **External adjudication** (~0/247) is the separate `2026-09-05-receipt-outcome-resolver-spec.md`
  track (externalVerdict/adjudicatedBy). Different keel.

SSOT: `_STATE/edge-capture-evidence-seam-spec.md` §Surgical-first implementation (v0.2).
