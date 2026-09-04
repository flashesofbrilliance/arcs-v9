# Edge-Capture Evidence Seam — spec (v0.1)

**Reach: grounded design.** The outcome handler *exists* (verified from source this session); the
constitutional postures are read from source. Persisted from RAM before compaction (the "say the word"
move). The capture *mechanism* is an enhancement to the built handler; the *no-derivation firewall* is
the genuinely-new nucleus (see §Ante-disciplinary gate). Drafted 2026-09-04.

## Context / the keel
- Outcome-capture is the keel — **not** "build the handler." The handler ships:
  `POST /api/receipts/[receiptId]/outcome` + `Outcome` model + debrief email + daily cron. The gap is
  capture **rate** (2/247, and by the realness gate ~0 *externally-validated* — both logged outcomes
  are the founder self-grading his own receipts, which §5.1 exists to exclude).
- Behavioral root (YELLOW, real-user-def §8): humans mis-weight stakes ex-ante + forget the fitting
  ex-post, a self-reinforcing loop. The mechanism fights **avoidance + forgetting**, not "no build."

## The seam: elicitation → edge-capture → persist
1. **Elicitation (the consent step).** The debrief nudge fires at `reminderDate` (built; reaches ~0
   opted-in users today — that's the real leak, not a missing path). The user actively supplies
   `matched` / `regretScore` / `learning`. Consent is intrinsic (user-initiated), no inference.
2. **Edge-capture.** A thin Supabase edge function: authenticate → validate → persist. Low-latency,
   reliable, non-blocking. **Crucially: no operator / LLM / derivation-plane access** — the
   "capture, not derivation" line is a **deployment boundary, not a policy.** The function
   *physically cannot* derive, so it can't manufacture an outcome.
3. **Persist.** Write the `Outcome` row + flip `status → LOGGED` + set `driftState`. Auth-gated, deletable.

## Reconciliation depth — surgical-first (the write-lock-paradox governor)
- Start at the shallowest, most **reversible** label: `matched` (binary) + `regretScore`. Do NOT
  auto-extract invariants across outcomes.
- Deepen only with **n + field-verification**. Deep-reconciling on low-n (extracting an "invariant"
  from 2 self-graded dogfood outcomes) is the **write-lock paradox**: a false invariant planted deep,
  self-reinforcing, un-undoable — inception.
- **Never write-lock a YELLOW.** Only GREEN (field-verified) invariants earn irreversibility (ROM #7).
  KINTSUGI: annotate-never-rewrite, so a mislabel stays correctable instead of sealed.

## Constitutional check (against source postures — passed conditionally)
- **Auth-gated writes** — anonymous stays ephemeral (the 2026-07-13 repair-seam precedent).
- **No-derivation firewall** — the deployment boundary above; *deriving* outcomes from behavior would
  trip the never-list (profiling) + §5.1 (a receipt can't close itself).
- **30-day material-change notice** (terms) — a new capture seam *is* a material change; cannot ship silently.
- **Deletable** — falls under the 30-day one-way delete.
- Owed before build: a `privacy-review` + `ciso-review` pass on the actual implementation, not just this read.

## Ante-disciplinary gate (run on this spec itself)
- The capture **mechanism** = enhancement to the built handler (edge function for reliability/latency).
  NOT net-new — it accretes onto the existing outcome route.
- The genuinely-new **nucleus** = *the no-derivation firewall as a deployment boundary, not a policy*
  (control-integrity: **wired**, not described). That is the seed worth its own home.

**Reach:** GREEN — handler exists, postures source-read, surgical-depth grounded. YELLOW — the
behavioral root (§8) and whether an edge function's reliability actually *moves capture-rate* (untested;
capture-rate is behavioral — avoidance/forgetting — not merely plumbing, so faster capture ≠ more capture).
