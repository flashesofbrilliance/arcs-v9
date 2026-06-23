# S-Tier Execution Plan — Tasks #1–7

> Written under explicit time pressure ("land before context limit") — depth was
> triaged accordingly. Marked inline wherever a pass was compressed rather than
> exhaustive. This is the Kintsugi discipline applied to the plan itself: a
> visible seam is honest; a hidden gap is not.

## Terminology corrections (apply before reading further)

- **ATG = Anticipatory *Tributary* Generator** (compass tributaries: meta-question /
  want-vs-need-to-hear / adjacent primitives), not "Tribune." Confirmed in
  `_CANON/arcs-v9-additional/ARCS-v9-Chapter-Book-Canon.md`.
- **Tribune Intelligence Layer** (`ADR-020`) is the separate system with Board roles
  and an Anterior/Proactive/**Posterior (Anticipatory/Post-mortem)** phase. Fully
  specced, **entirely unbuilt** (no `/api/tribune` route, no `tribunes` table).
- **"Productive vs. destructive drift"** — not canon. Defined below, operationally,
  from this session's own pathogen catalog. Treat as proposed, not ratified.

---

## Productive vs. destructive drift (proposed working definition)

| | Destructive drift | Productive drift |
|---|---|---|
| **Visibility** | Silent — `SILENT_SENSOR`, nobody checks | Visible — logged, Kintsugi-seamed, DRIFT_LOG-entered |
| **Closing act** | None — `UNCLOSED_CEREMONY`, gap stays open indefinitely | Explicit — routed to `/dual-bar-raiser`, ADR amended, commit lands |
| **Trust effect** | Compounds false confidence (docs say X, reality is Y, nobody notices) | Permanent honest discount, never hidden (Kintsugi's `trust_discount` — repaired is marked, not pretended clean) |
| **Example this session** | 15-day-stale snapshot; 26-day-silent DRIFT_LOG; my own wrong arcs.care/app.arcs.care claim before correction | BAR/KKL canon collision — found, routed, ruled, applied, logged, cross-referenced |

The whole point of landing #1–7 is converting destructive drift into productive drift as a standing capability, not just fixing today's instances.

---

## Inchworm ⟷ ATG lockstep — confirmed, with the seam shown

`GoldenInchworm`'s **Needle** answers "what do I do *now*." ATG's tributaries answer
"what else is worth probing, not yet acted on." These are not duplicates — Needle is
a closing act (productive drift, if followed), tributaries are open branches by
design (meant to stay open, surfaced lightly, not resolved immediately).

**Lockstep, concretely:** run `GoldenInchworm.run()` on a finding → get a Needle
(the action). Then apply ATG's three checks *to that Needle*, not the raw finding:
1. *Probe beneath* — does executing this Needle actually address the root pathogen,
   or just the symptom? (Caught exactly this failure mode earlier this session — a
   finding's first fix attempt can itself be symptom-level.)
2. *Want vs. need to hear* — is the Needle what's comfortable to act on, or what's
   actually load-bearing?
3. *Adjacent primitives* — does the `OrthogonalEchoDetector` half of the same run
   surface a sibling finding (same pattern, different domain) that this Needle
   doesn't cover?

**The seam, shown rather than hidden:** this lockstep is *designed*, not yet
*tested*. `arcs_inchworm_echo.py` has no ATG integration point in code today — this
is a procedure for a human (or a future session) to run by hand, not a wired
pipeline. Don't represent it as more built than it is.

---

## Funhouse Optics — one possible future vs. the other, applied to this plan

Per `_CANON/.../ARCS-v9-Chapter-Book-Canon.md`, mandatory framing for high-stakes
decisions. Applied once, to the plan as a whole (not per-task — budget-compressed,
flagged):

- **Q1 Convex** (what scales nonlinearly if this goes right) — if #4+#6+#7 land
  together, every future session's `/handoff` becomes mechanically reconstructable
  from git trailers + Observatory replay instead of hand-written prose. The payoff
  compounds: each additional ROM Candidate processed through the Observatory makes
  the *next* one's promotion criteria easier to evaluate.
- **Q2 Concave** (disproportionate damage if wrong) — #6's commit-trailer retrofit,
  done badly, creates a permanent two-era split in git history (everything before
  vs. after) that every future tool has to special-case forever. This is the
  single highest-irreversibility item in the whole plan.
- **Q3 Parabolic** (emotional distortion check) — there's real momentum/excitement
  from landing RC-OPS-001 this session; the risk is over-extending that energy into
  #6's retrofit without the same independent-verification discipline that caught
  v1/v8.5's bugs. Named explicitly so it doesn't happen invisibly.
- **Q4 Posterior** (what past receipts say) — this session's own pattern: every
  "all six bugs are fixed" claim needed independent execution to confirm; two of
  three turned out partially true. Apply the same standard to #6's eventual rollout.
- **Q5 Anterior** (6–12 months out, two futures):
  - *Future A (plan executes as sequenced):* `main`'s three narrative logs are one
    file; commits self-document their Y-Gate state; Observatory replays drift
    history; RC-OPS-001 either promotes to full ROM or gets retired with evidence.
    Drift gets caught in days, not weeks.
  - *Future B (plan stalls after this session, as the prior 7-day-old roadmap did):*
    `_PATTERNS/2026-06-23-governance-roadmap.md` becomes exactly the kind of stale
    artifact it was written to prevent — a well-reasoned plan nobody executed,
    itself a `PHANTOM_OPEN_ITEM` six months from now.
- **Q6 Orthogonal** (cross-domain kinematic warning) — the `OPM` (this plan)
  resembles `ADR-023`'s Superionic Goal Lattice: both got fully specced, both got
  explicitly gated ("not next-session work" / "needs an Observatory period"), both
  risk indefinite deferral if no trigger forces revisitation. The warning: name a
  concrete trigger now, not "eventually."

**Concrete trigger, named per Q6's warning:** next session that touches this repo
must run `/handoff-pickup` and treat any of #1/#2/#5/#7 as startable immediately —
no re-planning permitted before at least one Wave-0 item is attempted.

---

## Per-task plan, S-tier checked

Format: Task → Action → 5D5W5C5R5H verdict (compressed — full rubric defined in
`_PATTERNS/2026-06-23-governance-roadmap.md`).

### #1 — `~/.claude` backup repo (local-only)
**Action:** `git init` in a new `~/.claude-config-backup/`, copy in `CLAUDE.md`,
`commands/`, top-level `memory/` (7 files), `mcp.json`, `HANDOFF.md`, per-project
`memory/*.md`. Exclude everything in the prior exclusion table (`settings.local.json`
explicitly, given the leaked credential). Initial commit, no remote.
**5D5W5C5R5H:** 5W complete (who/what/where/when/why all specified above). 5C
consonant (matches the existing pattern of git-backing arcs-v9 itself). 5R: Risk low
(local-only, reversible); Refutation — "why not just trust memory" already refuted
this session by direct evidence. 5H: Surgical/Tactical altitude — single mechanical
action, no judgment calls left. **Verdict: S-tier, ready to execute as-is.**

### #2 — Rotate/confirm-dead leaked Supabase password
**Action:** Zach checks Supabase dashboard for project ref `owdiiyvphyifukygvxhg`.
If live, rotate credential immediately. If dead, note as confirmed-dead in
`DRIFT_LOG.md` addendum.
**5D5W5C5R5H:** 5H: this is the one item at **Executive** altitude in the whole
plan — it requires a human decision (is this project still mine?) no session can
make. **Verdict: blocked on human action, not re-plannable. Do not let this sit
unexecuted — it's the highest real-world stakes item here despite being the
smallest scope.**

### #3 — Consolidate 3 overlapping logs
**Action:** Pick `MEMORY.md` as canonical (it has the longest, most consistent
versioning history of the three). Port `.claude/arcs-session-state.md`'s unique
content (the SAGE efficacy / RLS BYPASSRLS / DATABASE_URL `!`-parsing gotchas — real
infra knowledge not duplicated elsewhere) into a `## Key infra facts` section inside
`MEMORY.md`. Retire `CLAUDE.md`'s append-only Handoff-block convention and
`arcs-session-state.md` as separate files; redirect both to `MEMORY.md` with a
one-line pointer comment, not a silent deletion (visible seam, not hidden).
**5D5W5C5R5H:** 5R: Refraction — viewing this through #6's lens, this *must*
precede #6's retrofit (already established as a hard sequencing point). 5C: high —
this directly closes `VERSION_DIVERGENCE`. **Verdict: S-tier scope, ready; blocks
#4b and #6b until done.**

### #4 — Drift-sensor cadence/severity/display
**Action:** (a) Cadence: weekly via `/schedule`, pending cost-model confirmation.
(b) Severity: Y-gate-style grading already designed (Time-Quality-ROM decay ×
BAR ruin-risk). (c) Substrate: **landed** (`RC-OPS-001`). (d) Display: depends on #7.
**5D5W5C5R5H:** 5H: currently split across Strategic (cadence/severity design, done)
and Tactical (actual cron build, not started) altitudes — this split itself should
be named explicitly going forward rather than treated as one task. **Verdict: NOT
S-tier yet — design is solid, build hasn't started, and it's now blocked by #3 and
#7 in sequence. Flag as the long pole of this whole plan.**

### #5 — Prose-rule enforcement audit
**Action:** Scope to `SKILL.md` first (most explicitly framed as "must/must not"),
classify each rule as enforced / cheaply-enforceable / discipline-only. Extend to
`AGENTS.md`/`CLAUDE.md`/`WORLD.md` only if the `SKILL.md` pass surfaces a pattern
worth generalizing.
**5D5W5C5R5H:** 5C: entangled with #6 (will likely surface the commit-format rule
as exhibit A of an unenforced convention). **Verdict: S-tier scope as narrowed
(SKILL.md first), ready to execute.**

### #6 — DEWY commit/PR stamp (`ADR-Ref:` / `Y-Gate:` trailers)
**Action:** Format: `ADR-Ref: ADR-XXX` + `Y-Gate: <polarity>/<conviction>/<stability>`
as commit trailers (after Co-Authored-By). Document in `AGENTS.md`'s commit-format
section. Apply going forward only — **do not** retroactively rewrite history (per
Q2 Concave above, this is the highest-irreversibility item in the plan if mishandled,
and rewriting history would itself be exactly that mishandling).
**5D5W5C5R5H:** 5R: Risk explicitly named (two-era git history split) and mitigated
(forward-only, no rewrite). **Verdict: S-tier once #3 and #5 inform it — sequence
after both, not before.**

### #7 — Observatory cherry-pick (`35070a3`)
**Action:** `git cherry-pick 35070a3` from `/Users/zharris/arcs` onto a clean branch
off current `main`. Resolve the expected conflict against `next.config.ts`'s
existing static `/observatory` rewrite — the real page route should take precedence;
confirm Next.js routing precedence before assuming.
**5D5W5C5R5H:** 5R: Refutation already on file — Next.js route-vs-rewrite precedence
needs confirming, not assuming, before calling this done. **Verdict: S-tier scope,
ready to execute, single clearest "just do it" item in the plan besides #1.**

---

## Final confidence statement

Not claiming full S-tier across all seven — **#2 and #4 are explicitly flagged
below S-tier** (one blocked on a human, one only half-built) and that's the honest
read, not a hedge. #1, #3, #5, #7 are genuinely ready to execute as written. #6
is ready *conditional on* #3 and #5 landing first. This is the seam: five solid,
one human-blocked, one long-pole. Showing it, not smoothing it.
