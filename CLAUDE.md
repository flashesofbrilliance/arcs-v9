@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  `_STATE/handoff-progress.jsonl` every turn-with-change, and asks for a `## Delta` in
  `_STATE/handoff-progress.md` at each compaction. Both are gitignored. `/handoff` folds them
  into the CLAUDE.md block and marks the ledger claimed; the global SessionStart hook flags any
  worktree whose trail was never claimed. Compaction never writes CLAUDE.md anymore.
- **Open work lives in `_QUEUE/induced-backlog.jsonl`** — items carry route/gates/trigger; execute
  from there without replanning. Dense multi-domain sessions: run `/fold` to spawn composed sessions.
- **On-demand only** (do NOT read to orient — open only when the task actually needs them):
  `MEMORY.md`, `SKILL.md`, `_ARCHIVE/handoffs.md`, `_ARCHIVE/memory-archive.md`, `_STATE/*`.
- There is no "read MEMORY→SKILL→WORLD→AGENTS in order" chain anymore. That mandate cost ~40k
  tokens per session and was retired 2026-07-19; open a specific file only when a task points to it.

# Project Map (read this before exploring)

## Stack
- Next.js 16 App Router · Prisma 7 + SQLite (`dev.db`) · Auth.js v5 magic link · Anthropic SDK

## Routes
| Path | File | Purpose |
|------|------|---------| 
| `/` | `src/app/page.tsx` | Home / entry |
| `/dashboard` | `src/app/dashboard/page.tsx` | **Main compass UI** — question input, prep form, result |
| `/compass` | `src/app/compass/page.tsx` | Magic-link login form |
| `/brief/[receiptId]` | `src/app/brief/[receiptId]/page.tsx` | Cartography brief (two-column) |

## API Routes
| Endpoint | File | Purpose |
|----------|------|---------| 
| `POST /api/compass` | `src/app/api/compass/route.ts` | L0–L5 Claude pipeline → Receipt |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession |
| `GET /api/brief/[receiptId]` | `src/app/api/brief/[receiptId]/route.ts` | Generate/fetch Brief |

## Lib
- `src/lib/db.ts` — Prisma client singleton
- `src/lib/auth.ts` — Auth.js v5 config (Resend magic link)
- `src/lib/ygate.ts` — Y gate computation (GREEN/YELLOW/RED/FORK/SCRATCH/DELTA/PARADOX/DRIFT)
- `src/lib/env.ts` — env validation

## Schema (prisma/schema.prisma)
Core models: `User` · `PrepSession` · `Receipt` (DEWY + Y gate + kinematic + lineage) · `Brief` · `Outcome`
All JSON arrays stored as TEXT (SQLite). Enums as plain strings.

## Design tokens (inline style objects, no CSS framework)
```
bg: #020408 | surface: #0d1117 | border: #1e293b
text: #e2e8f0 | muted: #475569 | dimmed: #64748b
cyan: #00F0FF | green: #00FF9D | gold: #FFD700 | red: #FF4D6D
```

## Y states → render resolution
GREEN=SHARP · YELLOW/FORK=DEGRADED · SCRATCH/DELTA/DRIFT=GRAIN · PARADOX=MOIRE · RED=GRAIN

# ARCS v9 Architecture (governing law)

## ROM Primitives — constitutional, never violate
1. **NOTOMATION** — scaffold/sequence cognition only; never compress/replace/overrule revealed preference
2. **HYPERSPHERE CONTEXT MANIFOLD** — What / Who / Where-When / Why / Flow-State
3. **HYPERSTITION PIPELINE** — Ethereal → Loki Test → Receipt Evaluation → ROM
4. **GOLDEN INCHWORM** — Red Thread → Golden Thread → Needle (3-pass, non-blocking)
5. **ORTHOGONAL ECHO DETECTOR** — surface cross-domain kinematic isomorphisms
6. **KINTSUGI IMMUNE SYSTEM** — repair seams visibly; no silent patching of integrity failures; show the break and the gold
7. **WRITE-LOCK** — one-way-door decisions require explicit write-lock declaration before commit; irreversibility is declared, not assumed

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). The full interactive Next.js page IS committed on main at `src/app/observatory/page.tsx`
(landed 2026-06-23, ~1.2k LOC); the old "never pushed" note was stale (Atlas audit 2026-09-03).
Confirm the `/observatory` route vs the static-demo rewrite before relying on either.

# Token-saving rules
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (EXCEPTION, 2026-09-29: text INDEX pages such as good.arcs.care/series/* put lede, rows and footer rule on the 680px measure) (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


# Versioning & handoff policy (amended 2026-07-19)

> Supersedes the prior "CLAUDE.md — append new sections only; never overwrite" rule, which had grown
> this file to 28 handoff sections / ~19.8k tokens loaded on **every** session. Rationale + measurements:
> `_PATTERNS/2026-07-19-token-efficiency-audit.md`.

- **CLAUDE.md is a working file, kept lean — not an archive.** It holds durable facts (Project Map,
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. When a new handoff
  lands, move the oldest live one into `_ARCHIVE/handoffs.md`.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.74.0 (2026-10-04)

> **NFTT posts carry their publish time; the seven PR #411 essays are denoted as one serialized thread;
> the NFTT index is reorganized.** PR #688 merged to main at `0bfa5877` on Zach's explicit go; one
> `decision_receipt` row (`2026-10-04--nftt-timestamps-serialized-thread-pr688--ZH`). All 9 PR checks
> green on head `8e8bab71`; production deploy `dpl_7C9ivtd9NHPeWZC99bs4T1bWBGgw` READY and aliased to
> good.arcs.care (Vercel `get_deployment`).

### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script reported 0 commits, 0 merges. Recount by hand from git: 6 commits (`e6b54862`, `d606f62d`, `8923d258`, `53e9c057`, `2cecca39`, `8e8bab71`), 1 merge to main (`0bfa5877`), 1 receipt. The script filters `--author=$(git config user.name)` = "Claude", while this cloud container authors commits as "Zach Harris": a gate blind spot (Open item 5), not a quiet session.
- **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: script read "mirror (inhale, no exhale)" off the miscount; with the recount, breathing (both directions).
- **Sycophancy check**: agreement 3 / dissent 1 (ratio 1.5) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): every claim carries a sha, a path, a PR number, a deployment id, or a receipt id. Nothing downgraded; the one corrected number is the exhale count above, corrected to git.
- **Somatic read** (Zach, 2026-10-04): "Feeling more certain than at the start, no sends today."
- **Disposition**: RELEASED on Zach's "consolidate memory and handoff".

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **Publish timestamps** (`e6b54862`): `scripts/nftt_published.py` derives each routed post's publish time
  from git, stamps `article:published_time` + a byline `<time data-pub>` into the post, `--check` and
  `--self-test` (13/13). Ledger `runtime/specs/nftt-published.json`, 32 rows, committed because CI clones
  shallow. Published = first commit on main's TRUE line containing the route commit (first parents,
  hopping to the second parent at "Merge ... 'origin/main' into ..." sync merges). `a-draft-is-not-a-verb`
  is flagged `git-direct-commit`: a commit-time lower bound.
- **The serialized thread** (`d606f62d`): `runtime/specs/nftt-series.json` + `scripts/nftt_series.py`
  (`--check`, `--self-test` 8/8). Each of the seven parts gets "The serialized thread · Part N of 7" under
  the byline and a series panel before `<footer>`; Tuning's hand map is superseded. Order and roles are
  from Tuning's own map; glosses verbatim from that map or each post's index description.
- **Index** (`8923d258`, `53e9c057`): series in part order 1 to 7; sections now The serialized thread (7),
  The Factory on Itself (8), The Cold Reader (3), The Workshop (7), Field Accounts (7); non-series sections
  newest first. Layout in `scripts/nftt_index_layout.json`; dates and parts read from the two specs.
- **Doctype** on the 9 NFTT pages that rendered in quirks mode (`d606f62d`, `8923d258`); **lede fix**
  `.standfirst{max-width:none}` ported from `6f6544ea` to the nine posts it missed (`2cecca39`).
- Gates: both `--check`s in `.github/workflows/ci.yml` and `scripts/git-hooks/pre-commit`; the
  `nftt-story-factory` skill gains the stamp + series steps.

## Open (next session)
1. Zach has not reviewed the new wording in place: tagline "One method, seven subjects", section names
   The Cold Reader / The Workshop, the three new blurbs.
2. LinkedIn first-published dates for the series parts: offered, not decided (the method post's byline
   already carries Jan 30, 2026).
3. `post-1-brief` / `post-1-exec` (unrouted) still fail wrap-lint on main.
4. The impeccable contrast ratchet did not run in the cloud container (detector absent).
5. `scripts/shavasana_handoff.py` exhale counts commits by `git config user.name`; in cloud sessions
   that is "Claude" while commits are authored "Zach Harris", so it reads 0. Count by repo/branch, or
   match both names.

## Lessons (in the record)
- main's first-parent line is not main's history here: fast-forwarded sync merges put branch commits on
  it. The first derivation misattributed five posts by a day (`d38b764c`) and one by a branch commit
  (`8b047f6f`). Hop at the sync merge; check every derived row against the commit it names.
- The tripwire caught an internal repo path that a CSS comment of this session put into a public page.
  Generator comments that render into the page are public text.
- good.arcs.care is blocked by the cloud network policy (proxy 403); live checks go through Vercel
  `web_fetch_vercel_url` and `get_deployment`.

# Handoff — v3.73.0 (2026-10-04)

> **Essay drafted, not shipped: "Tribes, Vibes, Lies" (subtitle "The Exoskeleton, Not the Oracle"),
> the long-form demand piece for a paid ARCS tier.** The draft lives in a Claude Doc, not in this
> repo: https://claude.ai/code/artifact/a2b5bb76-183c-4f0d-95f8-dc9f8a19e08f. No code changed, no
> PR, no deploy, no `decision_receipt` row (nothing was merged or published). This block records
> the shape of the essay so the next session can carry it to good.arcs.care/blog/nftt/ via
> `/nftt-story-factory` without re-deriving it.

### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main, receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 2 / dissent 0 (ratio 2.0) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): every claim names the doc URL, a canon id, or a file path. The '2 closed' count is carried as unconfirmed (it is AGENTS.md's 2026-09-02 figure, not re-measured). Nothing else downgraded.
- **Somatic read**: `somatic: not asked` (Zach present in chat; question not put). No sends today; the doc is private.
- **Disposition**: RELEASED on Zach's 'consolidate memory and handoff'. Exhale 0 commits is accurate: the session's output is a Claude Doc, and this handoff commit is the only repo write.

_This block asserts nothing new. Counts, paths, and questions only._

## What exists (in the doc)
- Nine sections, Zach's first person: confession (247 receipts logged, 2 closed; the valuable calls
  were passes, which leave no outcome), the shift (answers cheap, compounding judgment scarce),
  prosthetic vs exoskeleton, the prefrontal map (five jobs x five instruments, labelled a functional
  analogy, not neuroscience), Tribes/Vibes/Lies as a descent from the read you cannot prove to the
  read that leaves a receipt, the swipe-left ledger (three dials: good use of time / symmetric value /
  right time; one tripwire: stated-vs-revealed gap), why it compounds (the gut did not improve, the
  record did), the invitation (30 people x 30 closed decisions; 30 is the Accountant's n>=30 calibration
  floor from AGENTS.md, not a scarcity device), and three tributaries.
- A short-version block under the byline, two pull quotes, six drawn widgets, each intended as a
  standalone share card: prosthetic vs exoskeleton; the Tribes/Vibes/Lies ladder; dials + tripwire;
  the decide/act/receipt/measure loop (tao-041, tao-222); the four zones with Y state and render
  resolution (WORLD.md); a 2x2 of proverbs quoted as minted (tao-227, tao-220, tao-194, tao-045 from
  `_CANON/tao-proverbs.jsonl`).
- Two placeholders Zach still owes: the prospect he passed on (what they said, what they did not do,
  which dial the pull was on, when the tripwire fired) and one yes that went as expected.
- One open doc comment from Claude asking Zach to confirm the "2 closed" count against the live DB.

## Open (next session)
1. Zach fills the two placeholders and confirms 2/247 (re-measure `Outcome` rows; the number is from
   AGENTS.md as of 2026-09-02 and may have moved).
2. Port to `/nftt-story-factory` (LITERARY theme), em-dashes 0, lede spans the lane, run `page-gate`.
   Rebuild the three widgets as inline SVG in the post; they are doc widgets today.
3. Decide the paid-tier mechanics the essay promises: COURT/DEEP mode for the cohort, a 30-outcome
   calibration curve per user. Neither exists as a purchasable thing; the essay is ahead of the product.
4. Backlog row `essay-tribes-vibes-lies` added this session carries route/gates.

## Lessons (in the record)
- A no closes against a counterfactual. Any outcome ledger undercounts the passes, so an essay that
  sells the loop has to say so up front or a careful reader finds the hole first.
- "I got better at reading people" is unfalsifiable; "my gut now has a record" is the same claim in a
  form that survives. Prefer the second form everywhere the brand speaks.
