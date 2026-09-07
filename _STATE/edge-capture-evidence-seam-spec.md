# Edge-Capture Evidence Seam — spec (v0.2)

**Reach: grounded design.** The outcome handler *exists* (verified from source this session); the
constitutional postures are read from source. Persisted from RAM before compaction (the "say the word"
move). The capture *mechanism* is an enhancement to the built handler; the *no-derivation firewall* is
the genuinely-new nucleus (see §Ante-disciplinary gate). Drafted 2026-09-04. **§Surgical-first
implementation appended 2026-09-06** — the first honest cut of the capture-RATE nudge is built.

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

---

## §Surgical-first implementation — the ripe-to-close nudge (v0.2, 2026-09-06)

**Reach: GREEN on the mechanism-inventory + the build; YELLOW on whether it moves the number.**
Verified this session by source read: the capture *mechanism* is **fully built, end to end** — not
just the handler. What ships on this branch already: `POST/GET /api/receipts/[id]/outcome` ·
`src/emails/debriefEmail.ts` · `src/app/api/cron/debrief/route.ts` (long-horizon sweep, progressive
opt-in via `User.firstDebriefSentAt`/`debriefOptIn`) · `src/molecules/DebriefCard.tsx` ·
`src/app/debrief/[receiptId]/page.tsx` · `src/app/api/account/reminders` (opt-in/opt-out).

### The actual gap (revised, GREEN)
Not "no mechanism" and not "no email." The email path **reaches ~0 opted-in users** and, worse,
`DebriefCard` — the only in-app close affordance — renders **only on `/brief/[id]`**, a page a
returning user has no reason to revisit. So **nothing PULLS a returning user toward the receipts most
likely to have landed.** The behavioral root (real-user-def §8) is *forgetting the fitting*; the missing
piece is the pull that fights the forgetting *at the moment the user is already in the app* — independent
of email deliverability. That pull is the smallest honest cut.

### First cut (built + `npm run build` green + endpoint smoke `200 {"ripe":[]}`)
1. **`GET /api/receipts/ripe`** — read-only, auth-gated, over the **caller's own** rows only. Selects
   `status:OPEN`, `parentId:null` (seed), `outcome:null`, on a **short window**
   (`TODAY|THIS_WEEK|THIS_QUARTER` — a years-out horizon has not landed, nudging it would be dishonest),
   then a **conservative past-window proxy**: past `reminderDate` if set, else an age floor per window
   (TODAY 2d · WEEK 10d · QUARTER 100d). Returns ≤3. **NOTOMATION-clean: surfaces CANDIDATES, never
   asserts an outcome; touches no derivation plane** — this is the firewall as a deployment boundary in
   the smallest form (a plain read).
2. **Dashboard nudge** (`src/app/dashboard/page.tsx`) — a compact banner mirroring the existing
   `onboardingNudge`, linking the top ripe receipt to its existing `/debrief/[id]`. Reuses tokens +
   `Button`; no new molecule, no new dep.
3. **Governor = a dark flag.** Mounts only when `NEXT_PUBLIC_OUTCOME_NUDGE === "true"` (mirror server
   flag `outcomeNudge`/`OUTCOME_NUDGE` in `src/lib/flags.ts`). **Default OFF → the draft copy reaches
   no real user.** This is the write-lock-paradox governor *in code*: narrow default, widen only on
   evidence. Dogfood-first is the honest first population — the founder's own 247 is the only real data
   that exists; validate that the pull *moves rate* before widening to strangers.

### Gates still owed (do NOT skip before widening the flag)
- **Draft-first copy bless.** The banner wording ("The shoe may have dropped on … Did it land where the
  compass pointed?") is DRAFT. Zach blesses before `NEXT_PUBLIC_OUTCOME_NUDGE` is flipped for any real
  user. Marked with an inline `DRAFT COPY` comment at the mount.
- **`privacy-review` + `ciso-review`** on the ripe route (it's a read of the caller's own rows — low
  risk — but the seam is new-surface; run the pass before prod-widening, per the constitutional check).
- **The realness firewall still stands.** This nudge raises *capture* (self-graded matched/regret). It
  does **not** manufacture an **externally-validated** outcome — that remains ~0/247 and is the separate
  `2026-09-05-receipt-outcome-resolver-spec.md` track (externalVerdict / adjudicatedBy). Capture-rate and
  external-adjudication are two different keels; this cut moves only the first.

### Widen-on-evidence ladder (surgical governor, do not pre-build)
- **Now:** flag OFF, dogfood the founder's 247 locally → does the pull produce closes the email didn't?
- **If yes:** bless copy → flag ON for the founder in prod → measure closes over a week.
- **Then, only then:** widen to real users; consider the edge-function reliability layer (§seam step 2)
  *only if* latency/reliability of the Next route proves to be the binding constraint (it is not, yet —
  capture is behavioral, not plumbing).

**Reach recap:** the 247/2 numbers are GREEN (Supabase-MCP-verified 2026-09-05). The mechanism-inventory
and the build are GREEN (source-read + built + build-green + endpoint smoke this session). That the pull
*moves the number* is YELLOW — the honest thing the dogfood epoch exists to test.
