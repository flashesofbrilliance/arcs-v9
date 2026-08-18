@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
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

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). A full interactive Next.js page exists but was never pushed — recoverable via cherry-pick
from a stale local clone, see `_STATE/snapshot.json` → `observatory.status`.

# Token-saving rules
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.


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

# Handoff — v3.38.0 (2026-08-18)

> **Active pickup point.** The self-cataloging arc, end to end in one thread:
> inchworm → catalog → atlas → dolls → doctrine. The corpus now indexes itself,
> renders itself, polices itself, and travels.

## Headline: the memory corpus became a self-cataloging, navigable, portable system — and canonized how it stores itself

- **Self-cataloging index** — `scripts/memory_index_sync.py` (session-start hook, `--append`):
  orphan memory files auto-catalog into an "Uncurated (auto)" band rendered from their own
  frontmatter `description` (the SSOT inversion). Fixed the old inline check's regex bug
  (dotted filenames false-positived ORPHAN forever). Dead links + byte budget stay
  receipt-only. Index consolidated 20.9→17.4KB, 0 dropped, 0 dead links.
- **Catalog emitter** — `scripts/memory_catalog_emit.py`: mechanical, declared-edges-only
  backfill (183 nodes, 590 `[[wiki-link]]` edges, 22 dangling counted honestly).
- **Terrain Atlas** — `_ARTIFACTS/terrain-atlas.html`: 2.5D ziggurat where **stratum = echo
  weight** (base uncited → apex canon 10+), fog = staleness, district = azimuth; arrow-key
  traversal climbs the strongest declared edge; full camera (orbit/tilt/track, presets);
  per-node **russian-doll nested-ticket export** (cycles = `@ref`, never invented hierarchy).
  The apex self-identified: `cut-not-add-provable-architecture`, cited ×21.
- **Dolls (User0 → UserN+1)** — `scripts/doll_export.py` + `doll_sprout.py`: epoch-stamped
  declared-closure bundles, `--bodies` for true tenant bootstrap, **fail-closed air-gap gate**
  (`audience:` absent = internal; external cuts name what they held). Sprout never overwrites;
  the tenant's inchworm self-catalogs. Round-trip tested (96 shells w/ bodies).
- **ADR-065 minted via oracle** (+ **tao-249**, aspect C): corpus = SSOT, storage = induced
  projection, 4 serialization invariants, namespace isolation, **Infra Compass = ROM CANDIDATE**
  ("Induced Projection"; Y-map evidenced by this session's own FORK/PARADOX/DRIFT).
- **Merge reconcile**: 27 commits behind main resolved; three-way v3.35.0 handoff collision
  renumbered honestly (ours → v3.37.0); PII repos (`arcs-memory-pipeline`, `arcs-career-fit`)
  **re-privatized** per their own "pending review" descriptions (a live PARADOX, closed).
  30-day sweep ran; gauntlet-sampling-engine + dollar-compression minted to memory.
- **The system ratified itself**: the pre-push tripwire rejected the ADR-065 push because
  build.html still said 59 ADRs — the drift the mint itself created. Fixed the surface
  (never `--no-verify`), pushed clean. The Infra Compass worked before it was built.

## Wisdom receipt (the durable lessons, distilled)

1. **Invert the index**: when a file's frontmatter IS the SSOT for its index line, cataloging
   becomes mechanical and new knowledge can never silently fall out of the index.
2. **Declared-only edges are the honesty floor for provenance**: absent ancestry stays absent;
   a guessed edge is the propaganda version of lineage. (Held everywhere: catalog, atlas,
   tickets, dolls, ADR-065 invariant 3.)
3. **The NOTOMATION split scales every inchworm**: mechanical countables automate
   (append, emit, count); judgment (curation, canon, RED response) stays human. The same
   cut worked for the index, the seedbank, the snapshot, and the compass design.
4. **Let the data make the shape**: the ziggurat's pyramid wasn't designed — it emerged from
   the citation distribution, and its apex independently surfaced the corpus's own governing
   goal (`cut-not-add`, ×21). Render the structure; don't impose it.
5. **Fail closed at every boundary**: `audience:` absent = internal; PARADOX resolves to the
   restrictive assertion + a receipt (the ROM RC). The air-gap gate refused 100% on first
   run — that's the gate working, not failing.
6. **Dollar compression in practice**: ~350 lines of stdlib authored once, zero LLM in any
   runtime path — export/sprout/emit/check run free forever.
7. **A gate that catches its own minting commit is the proof the gate is real** (tripwire vs
   ADR-065's own drift).

## Next / open flags
- Roll `audience:` frontmatter onto any memory that would ever be cut externally (gate is
  fail-closed until then — correct but total).
- pg/pgvector migration (**ask-first** per ADR-065); `--emit-sql` on the emitter is the seam.
- ROM ratification of "Induced Projection" when earned; Infra Compass L1–L5 synthesis unbuilt.
- Origin-session / cross-session echo enrichment (`Activation` rows) — designed, not built.
- lattice-drift still fires (ADR count 57 vs 60; epoch stale) — regenerate is human-owned.
- Sweep leftovers unminted: CWO pattern, status-URL gotcha, F33 panel-as-plan-breaker,
  family token-SSOT, marketplace-as-channel, release runbook.
- **Apex Spine → Alexandria**: `_ARTIFACTS/apex-spine.html` (the S4 canon stratum as a print
  spine, 14 vertebrae) is a candidate resident for the **center reading room of the Library
  of Alexandria** performer (`_ARTIFACTS/arcs-alexandria.html`) — the corpus's load-bearing
  canon displayed at the library's heart. Placement idea, not yet integrated.

## Blocking
NONE this track. (PRL remains blocked on Todd — see snapshot `blocking_v3350_prl`.)

## Deploy note
All work pushed to `claude/plugin-marketplace-arcs-skills-9622bd` (head `b12349f` pre-handoff);
one public-surface content change (build.html ADR stat 59→60) rode the tripwire-gated push.
No product deploy. Comet application: SENT (see v3.37.0).

---

# Handoff — v3.37.0 (2026-08-17)

> Minted in-session as v3.35.0; renumbered at merge — main had already minted its own v3.35.0 (PRL)
> and v3.36.0 (family surfaces) in parallel. Same collision class ADR-057's oracle governs.

> **Active pickup point.** A resume-tailoring session for Zach that became a live demonstration of
> **ATG (Adjacent Tributary Generation)**: a bounded deliverable threw off reusable offshoots. No
> arcs-v9 code touched; the skill work pushed to a separate public repo.

## Headline: tailored the Comet Technical PMM application end-to-end, and the method became a shipped skill

Built Zach's application for **Comet — Technical Product Marketing Manager** (reports to VP Marketing
Hannah Klemme) in `_ARTIFACTS/resume-comet/`: a print-safe designed résumé (2pp), an ATS-plain
companion, a matching cover letter, and the honesty-graded `competency-model.json` SSOT. Voice tuned
from Zach's LinkedIn export (Shares/Comments/Recommendations). Centerpiece: an **orthogonal echo** —
his open-source `token-savings-bank` independently works the same problem as Opik's AI Spend Tracker,
reframed honestly to *reduction-side vs observability-side* after the gauntlet caught the category
error. Framing locked as **builder-who-markets**, not engineer-applying-to-marketing.

**Pre-send gauntlet — 4-facet adversarial panel (subagents):** recruiter/ATS · hiring-manager (Hannah)
· technical-peer · reference-check. Verdicts: **TAKE THE CALL / PASS-WITH-FIXES / CREDIBLE-WITH-FIXES
/ DEFENSIBLE-WITH-FIXES.** Survivors applied (all subtractive): echo landed ONCE + reframed;
"evaluation workflows"→"structured decision scoring" (Opik term-of-art); arcs-field-scan honestly
labeled (mock); titles reconciled to the LinkedIn export (**Grayscale = Product Lead**, **Squat =
Head of Product Innovation & Tech Lead**); "nearly two decades." ATS synced.

## ATG offshoots (the reusable surplus)
- **resume-tailor skill → v0.2, PUSHED** to `flashesofbrilliance/resume-tailor-skill` main
  (`e8e87d1..e41d30a`): Parameters + Components (voice-extract, orthogonal-echo, proof-link,
  term-of-art gate, social-proof restraint, layout/print discipline) + Greenhouse JD fast-path +
  Comet exemplar + `evals/evals.json` + `references/rubric.md`. `resume-tailor@arcs` now installs it.
- **4-facet pre-send gauntlet** as a reusable adversarial-verification harness.
- **Blog concept** "NOTOMATION powering gradient ascent" — forked to its own running session.
- Memories: [[atg-offshoot-artifacts-comet-resume-session]], [[resume-tailor-skill-v0.2-field-tested]],
  [[resume-tailor-voice-from-linkedin-export]], [[orthogonal-echo-proof-point]].

## Open / candidate-side flags (before the app SENDS)
- **ARCS not on Zach's LinkedIn** (current listed present-role = "Mañana — Product Partner"). The
  résumé leads with ARCS Founder — biggest reference-check gap; add to LinkedIn or be ready to explain.
- Squat "$350M ARR" / "seven-figure" — self-reported, not in export; kept, decide soften/cut.
- ARCS 60% / 3–5× — labeled internal estimates; Hannah says they invite an audit of the hard numbers.
- Contact = **github-only** ("Contact via recruiter") — fine if recruiter-routed; add a real email if
  applying direct (recruiter called it the single biggest odds-mover).
- Confirm VP name (Hannah Klemme) is the current hiring manager.

## Also flagged (infra, not this task)
- **build.arcs.care ↔ status 1:1 pulse sync not pushed** — build pulse lags the repo (~55 vs ~58 ADRs).
  Not a blocker; candidate for its own task.

## Blocking
NONE.

## Deploy note
No arcs-v9 code touched — no deploy. Skill push went to `flashesofbrilliance/resume-tailor-skill`
(separate repo). Résumé artifacts are untracked deliverables in `_ARTIFACTS/resume-comet/`.

---

> _v3.36.0 (family surfaces) + v3.35.0 (PRL) relocated to `_ARCHIVE/handoffs.md` on 2026-08-18; v3.34.0 and earlier on 2026-08-17._
