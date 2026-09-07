# Reading Room build plan — v1 (LOCKED 2026-09-04)

> The reticulated construction: the private reading room (Desk + Reader + cache backend +
> reference works) and the metabolic router that keeps it fresh. Sequence locked by Zach
> 2026-09-04 on the cost argument below. Cost discipline runs on the `token-savings-bank`
> skill (`open-source/token-savings-bank/SKILL.md`): four levers, correctness outranks budget.
> Every phase logs est vs actual into the CBA ledger (§6) so the next estimate is cheaper and
> sharper than the last.

## 1. The lock

**Infrastructure spine first, then cheap tenants.** Nine things looked like nine builds; they
are three pieces of infrastructure plus views over them. Once the Reader (instrument), the Desk
(grammar + gate), and the cache (backend) exist, each reference work is ~1–2 hrs, because
Concordance / Chronicle / Lexicon are just views over cached slices through one grammar.

```
Phase 0  integrity gate          (pulled forward: ~1 hr, zero judgment, protects every later write)
Phase 1  the spine               Desk + Reader + cache        (~10 hrs, the expensive part)
Phase 2  the tenants             Concordance -> Chronicle -> Babelfish   (~1–2 hrs each)
Phase 3  the router (full)       routing manifest + triggers + judgment queue
Phase 4  federated design pass + public-projection pipeline
```

The one deliberate pull-forward is the **integrity gate** (router v1 step 1): it is tiny,
has no judgment in it, is reusable by the pre-commit hook, and it stops "described but never
merged" records from entering the corpus while everything else is being built. Everything else
in the router waits for the spine.

**The Desk does not get built until its design plan clears the gauntlet:** impeccable `shape`
→ polish/refine/distill → `/dual-bar-raiser` → persona brand-manager gauntlet → kintsugi. No
build before the final document is kintsugi'd. (Zach, 2026-09-04.)

## 2. Standing token discipline (applies to every phase)

| Lever | Rule for this plan |
|---|---|
| **Route** | Mechanical steps (render, index, cache stamp, epoch tagging, grep-grade) → cheaper-tier subagents or plain scripts. Judgment (curation, canon, copy, design direction) → strong tier, inline. Re-escalate the moment mechanical work surprises (a failing render, an ambiguous cluster). |
| **Batch** | Read together what is certainly needed (all four digests in one pass). Gate exploratory reads on one cheap probe first. Never parallelize writes to the same file. Confirm a class-wide edit's match set before applying. |
| **Inline vs subagent** | Delegate wide sweeps whose intermediate output we only need a conclusion from (corpus audits, gauntlets). Keep inline anything whose details we need afterward (a render we will iterate on). No nested one-line subagents. |
| **Checkpoint** | Checkpoint only across a boundary (session end, compaction, handoff): `_STATE/` receipts, the CBA ledger, the handoff. Never checkpoint secrets — reference env var *names*. Verification of a landed change is a check, never skipped to save tokens. |

Correctness outranks budget at every row. A cheaper tier never touches auth, money, migrations, or an irreversible deploy.

## 3. Phase plan (est · human-equiv · ~Nx · levers · gate)

| Phase | Scope | Est agent-hrs | Human-equiv | ~Nx | Route / Batch / Delegate | Gate (done means) |
|---|---|---|---|---|---|---|
| **0 Integrity gate** | `scripts/integrity_gate.py <file>`: cited ADRs / commits / scripts exist on `origin/main`; wire into pre-commit as a warn-then-block | 1 | ~1 day | ~8× | script + inline; batch the git checks | catches a planted cite to an unmerged commit; zero false positives on the 5 known-bad memories' *fixed* versions |
| **1a Reader** | `research_render.py` hardened: epoch axis, two-shelf Skim (done), per-row export (done), a freshness badge per slice from the manifest | 2 | ~1 wk | ~15× | inline (we iterate on it); mechanical render on a cheap tier | all 3 altitudes verified at 4 widths; export round-trips |
| **1b Cache** ✓ | `cache-manifest.json` emitted by the render; freshness = `git diff --name-only <sha> HEAD` ∩ scope-globs; lazy back-prop as a targeted Curator run on one `(domain, epoch)` via `scripts/cache_backprop.py` (plan → packet → apply, per-slice grade preserved) | 2–3 | ~1 wk | ~12× | script; back-prop delegated per slice to a cheaper-tier Curator | **MET.** A dirty slice re-grades on read (proved: product/2026-04 dirty → re-graded → fresh, 19 siblings stay dirty); a fresh one does not re-audit (per-slice `graded_at_sha` survives a full re-stamp *and* 11 commits of base advance) |
| **1c Desk** | admin-gated `app.arcs.care/reading-room` route (decided 2026-09-06) (reuse the `/recoil` Auth.js + `ADMIN_EMAILS` fail-closed gate), the intent router ("what are you here to do?"), the federated grammar, Almanac wired as tenant #1 | 3–5 | ~2 wk | ~14× | design judgment inline at strong tier; gauntlet + persona runs delegated | passes the full design gauntlet (§1) *before* build; gated route resolves only for admin email |
| **2a Concordance** | concept → every node/ADR/memory/handoff that references it; a view over the existing in-degree graph through the Reader grammar | 1–2 | ~3 days | ~12× | inline; data already computed | pick any concept, see all references, click-through |
| **2b Chronicle** | the temporal arc Day-0 → now: epoch-tagged nodes + git-history epochs (status.arcs.care's raw material) as a library citizen | 2–3 | ~1 wk | ~12× | inline render; git-epoch extraction mechanical | scrub Apr → Sep; per-epoch health |
| **2c Babelfish** (was Lexicon; renamed 2026-09-06) | the controlled vocabulary (DEWY, Y-gate, ROM, Tao, status ladder) as a browsable glossary; a term-harvester (NET-NEW, small) + the Reader for display | 2–4 | ~1 wk | ~10× | harvester delegated; definitions judgment inline | a newcomer can look up any canon term |
| **3 Router (full)** | routing manifest as data + `metabolize` script (mechanical column auto, judgment column → queue) + triggers (post-commit cheap path, night-moves batch, /witness, /handoff) + queue folded into `/canon-review` | 4–8 | ~2 wk | ~10× | script; judgment queue stays human | one record routes to every organ with zero carrying; nothing auto-promotes to canon |
| **4 Federate + project** | unify the sibling surfaces under the Desk grammar; NFTT/brief as lawful air-gapped projections of private originals | 4–7 | ~2 wk | ~10× | gauntlets delegated; copy inline | every public surface has a named private twin; leak-check 0 |

**Totals:** ~20–30 agent-hrs over 4–6 sittings · ~6–10 solo-dev weeks equivalent · **~12–16×**. Token cost dominated by the multi-agent audit/curation runs (~500–600k subagent tokens per full re-curation); order of a few-to-ten million tokens for the whole plan. Wide error bars; the router's iteration count is the biggest swing.

## 4. Sequencing rules

1. Phase 0 ships first and alone (small PR, its own gate).
2. Phases 1a/1b can run in parallel (disjoint files); 1c starts its *design gauntlet* in parallel but does not *build* until 1a/1b land and the gauntlet clears.
3. No tenant (Phase 2) starts before the spine is verified end-to-end (a slice renders through the Desk from the cache).
4. Phase 3's full router waits for Phase 2 to exist, so the manifest routes to real organs, not planned ones.
5. Every phase ends with a CBA ledger row (§6) *before* the next phase is estimated.

## 5. What stays local vs gated

Everything in the private reading room stays **local or admin-gated** (the Desk gate). Never a
public host. The public reading room (NFTT, briefs, the goods) is produced only through the
projection pipeline with the air-gap leak-check at 0.

## 6. CBA learning ledger (append one row per phase; this is how the estimates compound)

| Phase | Est hrs | Actual hrs | Est tokens | Actual tokens | Lever that mattered most | What we learned → next estimate adjusts how |
|---|---|---|---|---|---|---|
| (baseline) Almanac v1→v2 + full-temporal re-curation, 2026-09-04 | ~4 | ~5 | ~600k | ~1.0M | Route: two claims-skeptic agents *refused* an authoring job (correctly) and we re-ran as general-purpose Curators → paid twice | **Match agent role to job class before spawning** (verify ≠ author). Delegated corpus sweeps were the right call (Lever 3); the waste was the role mismatch, not delegation. Future: Curator for augment/grade, Skeptic only for verify. |
| 0 | 1 | ~0.5 | ~40k | ~35k | Route: pure script, zero agents; Batch: one ls-tree + one cat-file --batch-check for all cites | First run against the real corpus found live drift (ADR-042 gap, `routing-manifest.json` vapor, 9 retired `public/*.html` still cited by `_STATE/snapshot.json`), so the gate earns its keep on day one. Rolled out warn-then-block (`INTEGRITY_GATE_BLOCK=1`). Estimates for mechanical scripts hold at ~1 hr; next: trust the ~8× figure. |
| 1a | 2 | ~1.5 | ~150k | ~400k | Delegate: builder + skeptic + runner + per-finding refuters in one graph; 12 of 13 raw findings confirmed real (two contradictory "graded" stamps, undated row dropped, malformed epoch crash) | **Reviewers earn their cost on renderers**: the builder's self-report undercounted em-dashes and mislabeled the render date as "graded". Gate note: **CLOSED — PASS** (visual gate, worktree `priceless-hopper-fbdd55`, ~0.4 hr / ~55k tokens): headless Playwright/Chromium at 4 widths (1280/790/768/375) × 3 altitudes = 0 px overflow in all 12; per-row export round-trips a 3180-byte self-contained bundle; two-shelf Skim, freshness badge, epoch axis, dataviz palette all legible; `.fresh{overflow-x:auto}` keeps the wide slice-table body-overflow-free at 375. **Lever that mattered: teleport to terminal** — a scriptable overflow probe (`scrollW−clientW`) turned "eyeball 12 renders" into one deterministic pass/fail; agents only for the final visual peer-review. Two cosmetic non-blockers logged in `_ARTIFACTS/atlas/1a-visual-gate-findings.md` (375px long-token epoch wrap; mobile slice-table scroll affordance) — flagged for 1b, neither blocks closure. **Made permanent (2026-09-07):** the one-off probe is now a committed regression spec `tests/almanac.spec.ts` (`npm run test:almanac`) — renders the Almanac fresh, loads `file://`, asserts 0-px overflow across 3 altitudes × 4 widths (375/768/790/1280) + a smoke on the `rendered · graded` header, epoch axis, and per-slice freshness, and writes 12 screenshots to `test-results/`. Hermetic (no host); pins the pre-installed Chromium via `executablePath` when Playwright's bundled build is absent. Re-run green. |
| 1b | 2–3 | ~1.5 | ~150k | ~450k | Delegate: same graph; 10 of 13 confirmed incl. one blocker (HEAD fallback made every slice read fresh) | **Scope globs must be derived from provenance, not assumed**: the spec's memories/recoil globs could never fire. Fixed: graded_at_sha = digest file's last commit, unknown-domain/untracked/missing/orphan are dirty markers, one JSON shape, usage errors exit 1. Back-prop (Curator) still the open seam; gate "a dirty slice re-grades on read" NOT met. |
| 1c | 3–5 | ~2.4 (build ~2 + re-run ~0.4) | ~300k | ~850k (build ~600k + re-run ~250k) | Delegate: 3 parallel adversarial lenses (ciso / sre / brand-design) for the killed refute+recheck, then one skeptic peer-recheck of the applied fixes | **Gauntlet COMPLETE (PR "1c gauntlet refute+recheck").** All 4 conservatively-applied ciso findings adjudicated REAL-AND-FIXED-CORRECTLY (iframe sandbox no-same-origin, frame-ancestors 'self' CSP, dev pass-through fully fail-closed with no NODE_ENV bypass, frame src allowlist). Re-run surfaced 2 residual fixes, both applied to the almanac route: (a) Content-Length TOCTOU (statSync-size vs separate stream → truncated 200) closed by single UTF-8 read + Buffer.byteLength; (b) a stale comment claiming a dev pass-through that the code never had. Brand lens: 6/6 HOLD (2 author-blessable drifts: h1 unbuilt lines hand-roll GRAIN vs resStyle token; readout labels the 3rd measure "stale slices" vs brief §6 "drift"). SRE: fail-closed in prod + graceful degrade (missing/malformed manifest→empty shelf, missing render→404) all PASS. Peer-recheck: NO-REGRESSION. `npm run build` green; all 3 routes register dynamic. Out-of-scope flags (not this diff): admin.ts:8-11 stale dev-pass-through prose; verify `/compass` `next=` is `/`-relative before post-auth redirect. **Learned: three parallel specialized lenses + one skeptic recheck reproduce a killed refute-graph at ~0.4 hr / ~250k — cheaper than re-running the full 28-refuter fan-out; match lens to finding-class, don't fan a refuter per raw finding.** |
||||||| 229b9e8b
| 1b back-prop | (in 2–3) | ~1 | ~90k | ~250k | Route: script inline (`cache_backprop.py`); Delegate: runner + skeptic gauntlet with a refuter per finding before commit | **Preserve per-slice grades, or re-stamping one slice frees its siblings that share a digest file.** `stamp`/`check` now carry a prior slice's `graded_at_sha` forward instead of recomputing from the shared file's last commit; only a *complete* re-grade advances it (a `--partial` leaves the slice dirty — WITNESS honesty). Skeptic found 3 real defects, all fixed: write-before-validate left a half-graded digest (KINTSUGI), `--partial` falsely stamped fresh, a cleared note outlived its status. 5 stdlib tests green. **Gate MET.** |
| 2a | 1–2 | | | | | |
| 2b | 2–3 | | | | | |
| 2c | 2–4 | | | | | |
| 3 | 4–8 | | | | | |
| 4 | 4–7 | | | | | |

Rule: a phase is not "done" until its row is filled in. The ledger is itself a nutrient — it
routes to the next phase's estimate (mechanical) and to a wisdom memory when a lever lesson
generalizes (judgment).

## 7. Provenance

- Cost analysis + lock: session 4ed54beb, 2026-09-04.
- Doctrine the router runs on: ADR-075 (`_DECISIONS/ADR-075-metabolic-router-mechanical-judgment-split.md`).
- Specs: `_SPECS/metabolic-router-v1.md`, `_ARTIFACTS/atlas/cache-manifest.spec.md`.
- Gap-handling rule for anything missing from this plan: proactive spec + NET-NEW / FORK-AND-MOD verdict (memory `proactive-spec-jtbd-reverse-lookup-flag`).
