---
name: meta-audit
description: Run one epoch of the ARCS Meta-Audit (the Drift Sentry) over the full corpus and the live code — Recoil passes, a code-verified parity matrix, the BAR/COURT/LAB/KKL/FUN-HOUSE gauntlets, Chi/Ma/Wuwei, a stack-ranked next-move list, and an append-only Golden Inchworm log entry. Use to check where ARCS stands against its promised done-state and surface the highest-conviction next move; run when a new handoff, ROM candidate, or serializability epoch lands, or on the weekly cadence.
user-invocable: true
---

# /meta-audit — one epoch of the Drift Sentry

> **SSOT:** `_STATE/meta-audit-roadmap-v1.md` (the living document; §8 is append-only, newest
> first). Rendered artifact: `_ARTIFACTS/arcs-meta-audit-roadmap.html`. CI-side subset:
> `scripts/state_sync_check.py` (canon-vs-code drift, runs on every PR). This skill is the
> full manual epoch that the CI check only samples.

## What this is

A reflective, code-grounded audit of the whole ARCS corpus. It does **not** add features — it
measures the gap between what the canon promises and what the code actually does, then names
the one move most worth making next. Governed by the **Golden Inchworm update law**: every new
handoff / ROM candidate / serializability epoch appends a §8 entry and re-grades §3 (parity)
and §6 (next moves).

## Non-negotiables (learned the hard way — do not skip)

- **Honesty gauge overrides any confidence request.** ARCS doctrine: never inflate NCI or
  conviction. Gauges are *earned*, not asserted. A requested "100% confident" is answered with
  the real number. ([[confidence-conviction-nci-operational-definitions]])
- **Anchor the epoch to a main-reachable commit.** Stamp the epoch hash from `git log main`,
  never an unmerged worktree/branch hash (a prior epoch stamped a never-merged hash and the
  audit lost its own lineage — v2.11.0 correction). Verify: `git merge-base --is-ancestor <hash> main`.
- **Verify parity against code, not handoffs.** §3 rows flip only on `git`/`grep` evidence in
  `src/` / `operators/` / `prisma/`, never on what a handoff claims. Canon that contradicts
  shipped code is a **drift finding**, not a parity update. ([[verify-domain-topology-live-not-from-memory]])
- **Weekly and small, not nightly and elaborate.** Scheduled runs carry no token discount; the
  economy is the batching. One focused epoch per real trigger. ([[cost-efficiency-global-goal]])
- **Real data only.** Every claim traces to a commit, a file:line, or a report. No fabrication.

## The protocol (eight sections, matching the SSOT)

**Step 0 — Set the epoch.** Find the last §8 entry's epoch hash. Compute what changed since:
`git log --first-parent <last>..main` (commits), plus new handoffs, `_DECISIONS/`, `_PATTERNS/`,
memory, and ROM candidates. Stamp the new epoch hash (main-reachable) and the date (verify with
`date` — [[dont-confabulate-timestamps-verify-with-date]]).

**Step 1 — True North.** State the audit's own receipt: the sharp question ("Where is ARCS vs
its promised done-state, and what's the highest-conviction next move?"), the bearing, earned
Conviction/Coherence gauges, weighted done-state %, mode, door.

**Step 2 — Recoil passes.** (a) *Reverse Listening* (end→start): where did the corpus actually
land vs. what the canon narrates? Name the divergences. (b) *Deep Recall* (start→end): slow-read
the founding promise (WORLD.md/canon) and grade what's real / embryonic / correctly-gated.

**Step 3 — Parity matrix (code-verified).** Re-grade each capability row: Backend built?
Frontend built? Verdict (PARITY / PARTIAL / EMBRYO / ORPHAN / GAP / GATED / MISSING). Flag
`canon STALE` where code ships but canon says backlog. Cite files. Rows flip on code only.

**Step 4 — Gauntlets.** Run the five lenses and record each verdict: **BAR** (ruin/exposure) ·
**COURT** (NOTOMATION, honesty, consistency) · **LAB** (Loki — strongest objection) · **KKL**
(Kairos — which windows are open/closed) · **FUN HOUSE** (mirror — the unnamed thing / standing
kryptonite). Note immune-system catches.

**Step 5 — Chi · Ma · Wuwei.** Chi = where energy lives (feed it). Ma = deliberate emptiness
(do not fill early). Wuwei = do not force (let evidence accumulate).

**Step 6 — Stack-ranked next moves.** Table: move · size (S/M/L) · Y-gate · why-now. Carry
prior ranks forward with status (OPEN / PARTIAL / DONE) so persistence is visible.

**Step 7 — Drift flags (the three classes).** (a) canon claims contradicted by code (cross-check
`state_sync_check.py`); (b) commits without `[NCI:xx]` tags; (c) open recoil `riskFlags` never
closed (`--sweep`). Report counts and trend vs. last epoch.

**Step 8 — Append the Golden Inchworm entry.** Prepend to §8 (newest first): date · version ·
epoch hash · what changed · §3 re-grade · §6 re-grade · drift (a)/(b)/(c) · the single **Next
move**. Never edit prior entries (append-only history). Bump the doc version.

## Output

1. A new §8 entry prepended in `_STATE/meta-audit-roadmap-v1.md`, with §3/§6 re-graded in place.
2. The single highest-conviction **Next move**, surfaced to the user in one line.
3. Optionally re-render `_ARTIFACTS/arcs-meta-audit-roadmap.html` from the doc when a surface is
   wanted (the deck already has a print/silkscreen stylesheet).

Commit docs-only (the audit touches `_STATE/` + `_ARTIFACTS/`, both build-skipped): `[NCI:SKIP]`.

## Anti-goals

- Adding features mid-audit. The audit measures; it does not build. A found move goes to §6, not
  into a diff in the same pass.
- Grading parity from handoffs instead of code (the recurring self-deception this audit exists to catch).
- Inflating gauges to a requested confidence. Earned, or it is noise.
- Editing prior §8 entries. History is append-only; corrections are new entries that supersede.
- Turning it into a nightly elaborate cron. Weekly, small, per real trigger.
