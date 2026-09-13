# Cross-Harness Handoff — 2026-09-11 · Hermes / Claude Code / Perplexity

> Paste as the first message in a fresh thread in ANY of the three harnesses. Self-contained.
> Verified against live git + Vercel + repo state at 2026-09-11 ~23:30 ET. Parent handoffs:
> `_STATE/handoff-2026-09-11-forge-queue-runbook.md`, `_STATE/handoff-2026-09-10.md`,
> `_QUEUE/PENDING.md` (master ADR queue — READ THIS for the aggregate roadmap, not this file's summary of it).

---

## 0. Altitude check — where we actually are

**Ship status:** Nothing from the last ~5 days of forge/job-search/perplexity work is deployed.
`fresh-starts` (35 commits ahead of `origin/main`, now pushed to origin as of this session —
commit `268c14aa`) is **not merged to main** and **not what Vercel Production serves**.
Production (`arcs-v9-git-main-arcs-care.vercel.app`) is on `origin/main`, 14 commits behind
`fresh-starts`. This is a normal, intentional state (working branch discipline) — flagging it
because "did we ship yesterday's work" was the literal question and the answer is **committed
+ pushed to origin, not merged, not deployed.**

**Repo fragmentation is the top structural risk right now, not any single feature gap.**
`git worktree list` returns **71 worktrees** under `.claude/worktrees/` (mostly Claude Code
session artifacts), most parked on branches with unmerged, uninvestigated commits. This is the
real cross-harness collision surface: work is scattered across dozens of branches that no
single session has audited end-to-end. Nobody currently has an aggregate picture of what's
actually unmerged vs. dead vs. duplicate across all 71.

---

## 1. Master plan / aggregate roadmap — where it lives (there is no single doc, use these three)

There is **no single master roadmap doc** synthesizing all three harnesses. The closest things:

1. **`_QUEUE/PENDING.md`** — the real ADR-level implementation queue (26 ADRs + non-ADR backlog +
   worktree-hold-branch collisions). This is the authoritative "what's decided, what's blocked,
   what's gapped" table. **Read this in full before planning any new work** — I'm not
   reproducing all 26 rows here, only the ones that are live blockers or cross-harness conflicts
   (§2–§4 below).
2. **`AGENTS.md`** "Agents & workers map" — Live/Backlog/Foundation component inventory (this
   repo's CLAUDE.md-adjacent file, already in your context if you're in Hermes/Claude Code).
3. **`_STATE/snapshot.json`** — machine-readable current-state pointer (git head, dirty files,
   Vercel deploy state). **Was stale (2026-09-10) as of session start; not yet refreshed in this
   handoff** — refresh it before trusting it (`git log -1`, `vercel ls`, dump into the JSON).

**Recommendation (not yet actioned):** the recurring pain across handoffs — I read 3+ of them
tonight and each says "snapshot.json is stale, refresh it" — suggests `_STATE/snapshot.json`
refresh should be a pre-commit hook or a 1-line `npm run` script, not a manual step every
session forgets. Nobody has built this. Candidate seed (§6).

---

## 2. Duplicative / conflicting work across harnesses (found tonight, not yet reconciled)

- **Worktree-hold ADR collisions (confirmed, from PENDING.md, unresolved since 2026-08-03):**
  three Claude Code worktrees (`token-consumption-improvement-6ba854`, `elastic-rubin-f22a6e`,
  `decision-geometry-logo-81fb56`) each independently claimed ADR numbers 038–041 that main has
  since reused for different content. 34 total commits sit unmergeable until renumbered. No
  harness has done the renumbering. **This is a live, actionable blocker** — the fix is
  mechanical (renumber + rebase), not a design decision, but it needs someone to actually do it.
- **`operators-harness-integration` skill exists with a resolved recommendation** (engine-only
  `operators/`, harness in a separate root dir, composition-contract-only README) but the
  **placeholder section is only committed on branch `feat/resume-pwa-theming`** (commit
  `b0d8b5c1`), not on main. If Claude Code or Hermes starts a new agentic-harness build without
  first landing that placeholder on main, you'll re-derive (or contradict) a decision that's
  already made. **Land `b0d8b5c1`'s README section on main before any new harness work starts.**
- **Two ADRs both numbered 025** (go-live-provisional-logic vs. sage-signal-validation-path) —
  disambiguated informally as 025a/025b in PENDING.md but never renumbered in the filesystem.
  Low urgency, but any harness that does `ls _DECISIONS/025*` will get confused.
- **No `ADR-021` exists** — unexplained gap. Nobody has investigated whether this is a lost
  commit or an intentional skip. Low priority but flagged per "log what's still missing."
- **Perplexity's role in the pipeline is under-specified relative to how much work references
  it.** ADR-018 (`/helpful` raw-context input model) is explicitly **HELD pending an "Architect
  packet from Perplexity Space session"** — that packet, if it exists, isn't in this repo. If
  yesterday's Perplexity work produced anything like that packet, it needs to land in
  `_DECISIONS/` or `_QUEUE/PENDING.md` gets it wrong indefinitely.

---

## 3. JTBD / risks / blindspots / honest caveats (explicit, not softened)

**JTBD trunk right now (per the most recent working handoff, 09-11 forge-queue-runbook):**
drain the 34-row forge queue (13 t1 auto, 10 t2 auto, 11 t3 needs-confirm) on `jobs.arcs.care`.
This is the active, in-flight job — not blocked, but **not yet reconciled with the ADR/roadmap
layer above**. It's running on its own local rhythm (`resume-tailors` thread → folded into
`fresh-starts`) somewhat disconnected from the PENDING.md ADR trunk. That's fine operationally
but means the "aggregate view across all three coding environments" the user asked for doesn't
actually exist as one artifact — it's two parallel tracks (product/ADR trunk vs. job-search
forge trunk) that get manually cross-referenced by whoever's in the seat.

**Blindspots / unverified premises (flag explicitly, per user's falsification-first preference):**
- **Capture rate, not SAGE firing, is the real P1 gap** (per AGENTS.md backlog note) — Outcome
  handler is built but only 2/247 receipts have a closed outcome. This is the actual bottleneck
  for any "does this pipeline work" claim, and it is NOT what most recent sessions have been
  spending time on (forge/resume tailoring instead). Worth a deliberate check-in: is job-search
  forge work displacing the receipt-capture work that the roadmap says is the real keel?
- **Integrity gate ran DRIFTED-AT-BIRTH on 5 of the 9 newly committed state files tonight**
  (old handoffs from 08-28/08-29 citing paths/commits never merged to origin/main). Not blocking,
  not fixed here — these are historical documents whose citations were already stale before I
  touched them. Flagging so nobody treats those old handoffs as verified state.
- **71 worktrees is not itself measured** — I don't know how many are genuinely stale vs. still
  needed. No harness has run a sweep. This is a blindspot, not a finding: "safe to prune" has
  not been established for any of them except the 3 explicitly noted as merged-and-removable
  (`nftt-ledger-not-story` in the 09-10 handoff).
- **Receipt ledger discipline (AGENTS.md "Receipts or it didn't happen")** — only 2 ship receipts
  logged ever (rubric v1.3, NFTT PR #394). Tonight's fresh-starts push is a candidate for a third
  receipt but I have not logged one (no merge/deploy happened, so per the rule's own text — "every
  merge, deploy, or publish action" — a bare branch push may not even qualify. Judgment call,
  flagging rather than assuming.)
- **Hypothesis needing falsification:** that the job-search forge pipeline's throughput (34-row
  queue, ~1/3 token cost via edit-from-seed) is actually the highest-leverage use of harness time
  right now vs. closing the Outcome-capture gap. Nobody has run this comparison explicitly — it's
  implicit in where time has gone.

---

## 4. .env / secrets inventory across local + cloud (documented, not synced — per your call)

No new tooling. Current known state, file-by-file, **var names only, no values printed**:

| File | Location | Vars present | Notes |
|---|---|---|---|
| `.env` | repo root, gitignored | `ANTHROPIC_API_KEY` | dev fallback |
| `.env.local` | repo root, gitignored | `ANTHROPIC_API_KEY` | Next.js local override |
| `.env.production.local` | repo root, gitignored | `ANTHROPIC_API_KEY`, `AUTH_RESEND_KEY`, `AUTH_SECRET`, `DATABASE_URL` + Vercel/Turbo system vars | pulled via `vercel env pull`; this is the closest thing to a "real" prod env snapshot locally |
| `.vercel/.env.preview.local` | repo root, gitignored | `ANTHROPIC_API_KEY` + Vercel/Turbo system vars (no `AUTH_*`/`DATABASE_URL`) | preview env is thinner than prod — **gap**: preview builds may not have `AUTH_SECRET`/`DATABASE_URL`/`AUTH_RESEND_KEY` set, worth confirming before trusting a preview deploy's auth flow |
| Vercel dashboard (cloud, not pulled here) | `arcs-care/arcs-v9` project | per AGENTS.md table: `ANTHROPIC_API_KEY`, `AUTH_SECRET`, `AUTH_RESEND_KEY`, `DATABASE_URL`, `ADMIN_EMAILS`, `RECRUITHAUS_AMMO_PASSWORD` | source of truth for prod; `RECOIL_PASSWORD` explicitly retired per AGENTS.md, no code reads it |
| `~/.arcs/jobs-pipeline.env` | outside repo, `chmod 600` | jobs-board API token (64-char) | **the Vercel-side copy of this token is a placeholder that 401s** — known gap, banked to memory 2026-09-11; always source this local file, never `vercel env pull` for this one var |

**Gap explicitly flagged, not fixed:** preview env (`.vercel/.env.preview.local`) is missing
`AUTH_SECRET` / `AUTH_RESEND_KEY` / `DATABASE_URL` compared to production. If any harness spins
up a preview deploy expecting magic-link auth or DB writes to work, it may silently fail or
fall through to dev defaults. Nobody has verified which.

**Shell environment note:** the jobs-pipeline token pattern
(`set -a; . /Users/zharris/.arcs/jobs-pipeline.env; set +a`) is the working convention for
loading secrets into a shell session outside of Next.js's own env loading. If you want true
cross-shell/cross-harness sync later, that's the seam to build on — not attempted here per
your explicit "just document, no new tooling" call.

---

## 5. Local source pointers (so a fresh Claude Code / Perplexity session can orient fast)

- Repo root: `/Users/zharris/arcs-v9` (main checkout, parked on `fresh-starts`)
- Master ADR queue: `_QUEUE/PENDING.md`
- Agent/component map: `AGENTS.md` (this file, "Agents & workers map" + "Operators Library" tables)
- Operator library: `operators/` (52 top-level `.py`, 62 tracked files, 22,171 LOC — see AGENTS.md
  file-census note for the exact recount commands, don't trust round numbers)
- Job-search / forge pipeline: `scripts/forge_edit_from_seed.mjs`, `runtime/specs/forge-bundles.json`,
  `_STATE/job-search/forge-cost-ledger.jsonl`, board SSOT at `jobs.arcs.care` (NOT the repo jsonls —
  those lag, resync from `/api/jobs`)
- Perplexity artifacts from recent work: `_MEMORY/project_perplexity_mcp.md`,
  `_ARTIFACTS/forge-perplexity-ai-strategist-financial-servi/` (resume bundle, already folded
  into listen-labs seed per commit `5038efd5`)
- Handoff chain (newest first): this file → `_STATE/handoff-2026-09-11-forge-queue-runbook.md`
  → `_STATE/handoff-2026-09-10.md`
- Decision receipts (Supabase, not local): `decision_receipt` table, project `xbbpiryokswwvcrcutge`
  (ARCS_v9) — see AGENTS.md "Receipts or it didn't happen"

---

## 6. Banked capabilities / patterns / skills relevant right now

Already built, underused this session — load these before starting fresh work:

- `arcs-handoff` (this doc follows its protocol)
- `operators-harness-integration` — **has an unresolved landing action** (§2 above): its
  recommendation is decided but not merged to main
- `arcs-jobs-board-forge` — the forge queue runbook skill; should be the entry point for
  continuing the drain, not re-deriving the procedure
- `arcs-branch-merge-verification` — use this BEFORE renumbering/merging the 3 ADR-collision
  worktrees (§2)
- `git-commit-verification` — same, for any of the 71-worktree cleanup
- `arcs-decision-receipts` — use when the next actual merge/deploy happens (not tonight's push)

## 7. Additive skill / seed recommendations (proactive, not yet built)

Based on tonight's net-new pain points, ranked by leverage:

1. **`worktree-audit` skill (NEW, doesn't exist).** A mechanical sweep of all 71 worktrees:
   ahead/behind main, last-commit age, merged-or-not, ADR-number-collision detection. This is
   exactly the "teleport to terminal, not agents" case (AGENTS.md gotcha #11) — a deterministic
   scan that currently doesn't exist and is causing real confusion (§0, §2). Highest leverage,
   cheapest to build.
2. **Snapshot auto-refresh (script or pre-commit hook), not a skill** — kills the recurring
   "snapshot.json is stale" note that shows up in nearly every handoff I read tonight.
3. **Cross-harness roadmap synthesis as a living doc**, not this one-off handoff — i.e. promote
   §1–§3 of this file into a maintained `_STATE/roadmap.md` that both the ADR trunk and the
   job-search forge trunk write status into, so the "two parallel tracks" problem (§3) becomes
   visible instead of implicit.
4. **Land the operators-harness-integration placeholder on main** (§2) — not a new skill, but
   the single highest-value unblock for any future agentic-harness work, and it's a 1-commit cherry-pick.
5. **Preview-env parity check** — a smoke script asserting `.vercel/.env.preview.local` has the
   same critical var set as production before trusting a preview deploy (§4 gap).

None of these are built yet. Recommend picking ONE to actually build next session rather than
adding all 5 to the backlog pile — per your "ship minimal" preference, #1 (worktree-audit) has
the best ratio of leverage to build cost and directly answers the "do we have duplicative
work" question mechanically instead of me eyeballing 71 branch names.

---

## Reading sequence for whoever picks this up

1. This file (already self-contained)
2. `_QUEUE/PENDING.md` in full — the real roadmap
3. `_STATE/handoff-2026-09-11-forge-queue-runbook.md` — active JTBD (forge drain)
4. Decide: worktree-audit build, OR continue forge drain, OR land the operators-harness placeholder.
   Don't start new harness/agentic work without doing #3 from §7 first.
