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

# Handoff — v3.77.0 (2026-10-04)

> **"Tribes, Vibes, Lies" went from a doc to a gated preview page.** PR #691 (the v3.73.0 handoff) merged to
> main at `ac92aaed` on Zach's "merge it once smoke is green"; receipt
> `2026-10-04--handoff-v3.73.0-essay-tribes-vibes-lies-pr691--ZH`. Draft PR #700 holds the preview page
> `public/blog-nftt-tribes-vibes-lies.html` (head `056a417`, 9/9 checks green, mergeable, unrouted,
> not merged, no receipt owed yet). The essay's source of truth is still the Claude Doc:
> https://claude.ai/code/artifact/a2b5bb76-183c-4f0d-95f8-dc9f8a19e08f.

### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script reads 0 commits, 0 merges (it filters by `git config user.name`, the known blind spot). By hand: 3 session commits (`637a33d`, `6d4598d`, `056a417`), 1 merge to main (`ac92aaed`, PR #691), 1 receipt.
- **Inhale** (what came in): 0 falsification rows today, 2 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: mirror on the script's count; breathing (both directions) on the hand count.
- **Sycophancy check**: agreement 10 / dissent 2 (ratio 3.33) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff-2.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): every claim carries a sha, a PR number, a path, a URL, or a receipt id. Downgraded: the real-font render of the preview is stated as not checked, not as checked. The 2/247 figure stays unconfirmed.
- **Somatic read**: `somatic: not asked`. No sends today; the page is unrouted and the doc is private.
- **Disposition**: RELEASED on Zach's `/handoff`.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- PR #691 (`ac92aaed`): the v3.73.0 handoff block, MEMORY entry, backlog row `essay-tribes-vibes-lies`,
  session-state file. `fe-smoke` was still running at merge time; it later passed on PR #700's head.

## Open on a branch (not on main)
- **Draft PR #700**, branch `claude/essay-tribes-vibes-lies-preview`, commits `6d4598d` (page) and
  `056a417` (merge of main to clear a stale-base `generated-views` failure; `public/good.html` drift was
  fixed on main by `c9bb397`, not by this PR). One file, 426 lines: the NFTT literary template chrome cloned
  from `public/blog-nftt-confirmed-not-my-bug.html`, nine sections, a short-version panel, two pull quotes,
  six inline-SVG figures (prosthetic vs exoskeleton; the Tribes/Vibes/Lies ladder; three dials + one
  tripwire; the decide/act/receipt/measure loop from tao-041 and tao-222; the four zones from WORLD.md;
  a 2x2 of tao-227/220/194/045 quoted as minted), two gold dashed placeholder boxes in section VI, and a
  `<!-- tao-waiver: preview draft ... -->` marker that the `tao-coverage` pre-commit gate required.
- Vercel preview (noindex): https://arcs-v9-git-claude-essay-tribes-vibes-lies-preview-arcs-care.vercel.app/blog-nftt-tribes-vibes-lies.html
- Gates run on the page: `scripts/page_gate.py` at 375/790/1280, wrap-lint, div-balance, token-source,
  component-source, tao-coverage; em-dashes 0; every figure screenshot-checked at 1280, one at 390. Three
  label collisions under the fallback font were fixed before push. The real-font render was not
  screenshot-checked (the preview host is not reachable from the container); Zach has the URL.
- The doc gained, after v3.73.0: three tributaries, the short-version block, two pull quotes, and three
  canon-sourced widgets (loop, zones, proverb 2x2) in addition to the first three.

## Open (next session)
1. Zach still owes the two worked examples (one pass with the tripwire moment, one yes that went as
   expected) and the 2/247 confirmation (doc comment open; re-measure `Outcome` rows).
2. Leave-draft gates on #700, in order: fill placeholders in the doc and the page; re-measure 2/247;
   `/tao-mint` a proverb citing `nftt/tribes-vibes-lies` and remove the waiver; route in `src/proxy.ts`;
   add to `scripts/nftt_index_build.mjs` POSTS + `scripts/nftt_index_layout.json` and rebuild the index;
   `python3 scripts/nftt_published.py derive --now tribes-vibes-lies` then `stamp`; page-gate; Zach's
   publish bless; merge with `--merge`; one `decision_receipt` row.
3. The paid tier the essay promises (COURT/DEEP mode for a 30-person cohort, a per-user 30-outcome
   calibration curve) is not purchasable; decide the mechanics before the post routes.
4. Phone-width figures scale to about half size; legible but small. Option: stacked phone layouts for the
   instrument and proverb figures.
5. PR #700 watch: subscribed; safety-net check-ins at 04:06Z, 09:02Z, 13:04Z found nothing; a final
   one is armed for 17:06Z, after which check-ins stop and only a GitHub event or Zach resumes them.

## Lessons (in the record)
- `tao-coverage` is a pre-commit gate: a new NFTT page needs a proverb citing it or a declared waiver.
  The first commit attempt was refused; the waiver is honest for a preview and wrong for the real post.
- A branch cut before a generated-page fix lands reproduces that failure in CI even when the diff is one
  unrelated file. Reproduce the check on `origin/main` first; if it passes there, merge main in.
- Fallback fonts run wider than the self-hosted ones; size SVG label boxes for the fallback and the real
  render only gains margin.

# Handoff — v3.76.0 (2026-10-04)

> **NFTT bylines date the LinkedIn originals each essay was written from; main's red generated-views
> check fixed on the way.** PR #697 merged at `cb0d8772` and PR #703 at `348ae373`, both on Zach's
> explicit asks; receipts `2026-10-04--nftt-linkedin-originals-pr697--ZH` and
> `2026-10-04--nftt-method-byline-dedup-pr703--ZH`. PR #706 (Four Dates + The Pre-Mortem originals)
> carries this handoff; merged by Zach at `07d580ae`, both bylines live-verified, receipt
> `2026-10-04--nftt-originals-fourdates-premortem-handoff-v3.76-pr706--ZH`.

### Shavasana — handoff pause, 2026-10-04 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): script reported 0 commits, 0 merges (the author-filter blind spot, Open item 4). Recount from git: 4 session commits (`01a5ddb1`, `c9bb3975`, `fef1912a`, `2930d83a`), 2 merges to main (#697 `cb0d8772`, #703 `348ae373`) with #706 pending, 2 receipts. `febc68b4` and `c9247f18` in the same range are other sessions'.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 5 / dissent 0 (ratio 5.0) → RETURN: agreement with no dissent on record.
- **Cold re-read (canary on the draft draft-handoff-v376.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (Claude, cold re-read): the RETURN counts keyword markers; the stretch carries dissent the vocabulary missed, each in the record: Zach's "first published on LinkedIn" was declined as false (PR #697 body); a zero-step local sweep's PASS was caught and re-run (11/11); the generator fix was narrowed after it touched the resume-tailor card; The Pre-Mortem's undated source was not stamped. Every other claim carries a sha, PR, deployment or receipt id. Nothing downgraded.
- **Somatic read**: not re-asked; Zach's read earlier this session (v3.74.0): "Feeling more certain than at the start, no sends today."
- **Disposition**: RELEASED on Zach's "run the handoff" despite the RETURN verdict, for the reasons above.

_This block asserts nothing new. Counts, paths, and questions only._

## Shipped + on main
- **Originals line** (`01a5ddb1`, #697): bylines read "From the LinkedIn original(s), <dates>" after the
  publish `<time>`, each date in its own `<time datetime>`. Deliberately not "first published": every
  NFTT post is a new essay. SSOT `runtime/specs/nftt-originals.json` (platform, ISO dates, evidence);
  `scripts/nftt_published.py` stamps it, `--check` fails a missing or orphan segment, `--self-test` 21/21.
  Live-verified on Closing the Loop and The Instinct via Vercel `web_fetch_vercel_url`.
- **generated-views fix** (`c9bb3975`, #697): main went red at `febc68b4` (#695 hand-edited `good.html`).
  `connector_render.py` looked the honest card's distribution row up by page key `honest`; the row is
  keyed `check-it-before-you-say-it`. `EXTERNAL_PAGES` entries may now name their row (`"repo"`); output
  byte-identical to #695's edit. Shipped inside #697 (session limited to one branch), disclosed on the PR.
- **The Method byline** (`fef1912a`, #703): the hand-written "Source: a LinkedIn article published Jan 30,
  2026" dropped as a duplicate of the generated segment; live-verified.
- **Four Dates + The Pre-Mortem** (`2930d83a`, #706): originals added on Zach's confirmation of the
  platform (PR #411 records the LinkedIn corpus). The Pre-Mortem's fifth source stays out (undated in its
  export). Six of seven series posts now carry the line; Tuning has none (it cites, not adapts).
- v3.74.0 open items 1 (wording approved by Zach) and 2 (originals) resolved.

## Open (next session)
1. ~~Live check + receipt for PR #706~~ RESOLVED 2026-10-04: merged by Zach at `07d580ae`; deploy
   `dpl_FDWpWLdVVHHs85FfCBrFcwBZsPsw` aliased to good.arcs.care; both bylines live via Vercel
   `web_fetch_vercel_url`; receipt `2026-10-04--nftt-originals-fourdates-premortem-handoff-v3.76-pr706--ZH`.
2. `post-1-brief` / `post-1-exec` (unrouted) still fail wrap-lint on main.
3. The impeccable contrast ratchet did not run in the cloud container (detector absent).
4. `scripts/shavasana_handoff.py` exhale counts commits by `git config user.name` ("Claude" in cloud
   sessions, commits authored "Zach Harris"), so it reads 0. Count by repo/branch, or match both names.

## Lessons (in the record)
- A label that sounds right can be false: "first published on LinkedIn" read naturally, but each post's
  own footer showed a new essay written from LinkedIn originals. Read the provenance before naming it.
- A check that ran zero steps reported PASS: the first local generated-views sweep parsed 0 steps from
  ci.yml. Count what ran before trusting a pass.
- A hand edit to a generated page reddens every PR, not only its own: #695's two-line `good.html` change
  failed generated-views on main until the generator learned the row key.
