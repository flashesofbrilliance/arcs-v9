# Prospecting Survey — Loop 1 (Index) · 2026-09-03

**Cycle:** the harvest cycle, `_CANON/flora-and-fauna.md` §IX (index → catalog → organize → bundle)
**Instrument:** `python3 scripts/corpus_prospector.py index --out _STATE/2026-09-03-corpus-index.jsonl`
**Ore ledger:** `python3 scripts/corpus_prospector.py orphans --out _STATE/2026-09-03-orphan-ore-ledger.jsonl`
**Branch:** `claude/arcs-ecosystem-flora-fauna-sos9m7` · **Loop status:** 1 of 4 · gate PASSED (see §5)

> **Read this first (Kintsugi seam).** This clone is **shallow** — git only holds the last 123
> commits (oldest 2026-08-23). Every `last_commit` / `age_days` in the ledger is therefore a
> *lower bound*, not an age. "Nobody points at it" is measured honestly; "it has not moved in a
> season" is not measurable from here. Re-run on a full clone before trusting any dormancy claim.
>
> Second seam: on the first rerun the index file listed every path, so every orphan looked homed
> (131 → 42). The instrument was citing itself. Its own outputs are now excluded from the citation
> corpus (`SELF_OUTPUT_RE`). Third seam: landmark files (README, index.*, ledgers, short stems) were
> never scanned for citations but were reported as orphans anyway — UNDEFINED collapsed to NULL.
> They now carry `ref_scanned: false` and are never orphans. Both fixes are in the script's history.

---

## 1. What "addressable" covered

Every tracked file outside `src/` and `node_modules/` that matches an ARCS artifact class, plus
untracked files inside `_ARTIFACTS/ _STATE/ _INBOX/ _QUEUE/ _PATTERNS/ runtime/` (flagged
`tracked: false`). Instruments (`scripts/ operators/ .claude/{skills,commands,agents}`) are
rostered but **not graded** — they are fauna, not corpus.

Classes: ADR · COLLISION · DECISION · DEWY · APEX · PROVERB · MOMENT · CANON · WITNESS · KINTSUGI ·
HANDOFF · MEMORY · SEED · PATTERN · QUEUE · SCRATCH · RECOIL · WARROOM · SPEC · RUNTIME · ARTIFACT ·
STATE · WORLD, and the five instrument classes.

## 2. Headline numbers

| | |
|---|---|
| Files indexed | **800** |
| Corpus files graded (instruments excluded) | **614** |
| Grade A / B / C / D | **255 / 158 / 163 / 38** (41% / 25% / 26% / 6%) |
| Training-grade (A+B) | **413 · 67%** |
| Orphans (scanned, zero inbound references) | **132 · 10.3 MB** |
| Orphans by grade | B 48 · C 46 · D 38 (an orphan can score at most B, by definition) |
| Secret-pattern hits | **0** |

**Grade** = one point each for *dated · provenance · referenced · well-formed*. It is a
training-reuse heuristic, not worth. A secret hit caps at D.

## 3. By class

| class | files | KB | orphans | A | B | C | D |
|---|---:|---:|---:|---:|---:|---:|---:|
| ARTIFACT | 176 | 14977 | 72 | 22 | 41 | 79 | 34 |
| RECOIL | 133 | 1430 | 29 | 52 | 54 | 26 | 1 |
| SCRIPT | 78 | 924 | 0 | 0 | 0 | 0 | 0 |
| ADR | 69 | 426 | 0 | 69 | 0 | 0 | 0 |
| OPERATOR | 61 | 931 | 0 | 0 | 0 | 0 | 0 |
| PATTERN | 39 | 340 | 2 | 27 | 11 | 1 | 0 |
| SPEC | 33 | 482 | 0 | 14 | 11 | 8 | 0 |
| WARROOM | 33 | 1869 | 4 | 2 | 3 | 27 | 1 |
| STATE | 30 | 611 | 10 | 16 | 9 | 5 | 0 |
| SKILL | 27 | 101 | 0 | 0 | 0 | 0 | 0 |
| CANON | 26 | 629 | 0 | 8 | 10 | 8 | 0 |
| COMMAND | 13 | 59 | 0 | 0 | 0 | 0 | 0 |
| SCRATCH | 13 | 143 | 2 | 9 | 2 | 1 | 1 |
| DEWY | 10 | 64 | 3 | 7 | 3 | 0 | 0 |
| WITNESS | 9 | 44 | 0 | 9 | 0 | 0 | 0 |
| QUEUE | 8 | 34 | 6 | 1 | 4 | 3 | 0 |
| SEED | 8 | 91 | 0 | 7 | 1 | 0 | 0 |
| AGENT | 7 | 11 | 0 | 0 | 0 | 0 | 0 |
| MEMORY | 7 | 81 | 0 | 4 | 3 | 0 | 0 |
| HANDOFF | 4 | 232 | 2 | 1 | 2 | 1 | 0 |
| KINTSUGI | 4 | 30 | 1 | 1 | 0 | 2 | 1 |
| WORLD | 3 | 33 | 0 | 1 | 1 | 1 | 0 |
| DECISION | 3 | 38 | 1 | 0 | 2 | 1 | 0 |
| COLLISION | 2 | 8 | 0 | 2 | 0 | 0 | 0 |
| APEX | 1 | 5 | 0 | 1 | 0 | 0 | 0 |
| MOMENT | 1 | 8 | 0 | 1 | 0 | 0 | 0 |
| PROVERB | 1 | 108 | 0 | 1 | 0 | 0 | 0 |
| RUNTIME | 1 | 11 | 0 | 0 | 1 | 0 | 0 |

Reading it: **ARTIFACT** holds 72 of the 132 orphans and almost all the orphan bytes (résumé
renders, print PDFs, CRM exports). **RECOIL** holds 29 — per-counterpart ledgers that are dated
and well-formed but linked from nothing. Everything in the canon/decision spine (ADR, WITNESS,
PROVERB, APEX, COLLISION, MEMORY) is fully homed: zero orphans, all Grade A.

## 4. The deposits — named work list for Loop 2 (catalog)

Grades as the field guide uses them (§VII). Paths are exact; nothing here was invented.

### Grade A / native metal — refined and homeless
- `_ARTIFACTS/forensic-recoil-2026-08-27/FORENSIC_REPORT.md` + `mine/g1…g6-*.jsonl` (6 files) —
  190 decision-lineage records, 22 folksonomy tags, skeptic-adjudicated. **Highest-yield deposit
  in the tree.** Loop 2 should start by re-reading its "Verified Net-New" list against today's
  canon (the Norse candidates it surfaced are now in `runtime/specs/`; the rest may already be homed).
- `_ARTIFACTS/blog/nftt-gauntlet-findings.json`, `field-notes-provenance.json` — gauntlet outputs
  with provenance, no index.
- `_STATE/2026-08-14-session-decisions.dewy.json`, `2026-08-16-…`, `2026-09-01-…` — three DEWY
  receipts nothing cites. Candidates for the receipt index / `_DECISIONS/index.json` companion.
- `_STATE/handoff-2026-07-19-status-live.md`, `handoff-2026-07-19-zero-trust.md` — two handoffs
  that never made it into `_ARCHIVE/handoffs.md`.

### Grade B / rich vein — finished, one signal short
- **NFTT stories never published** (`_ARTIFACTS/blog/stories/`): `induction-surface`,
  `self-cataloging-{full,brief,exec}`, `sixth-coordinate`, `take-home-trap` (.story.md) and
  `field-notes-germinate-pollinate.md`. Envelope + prose already in the story-factory format.
- **Seven vision-film transcripts** (`_ARTIFACTS/vision-films-hyperstition/transcripts/01–07`) —
  the hyperstition miss-column denominator (handoff v3.49 open item 1) needs exactly these.
- **Per-counterpart recoil ledgers** (`runtime/recoil/generated/2026-06-25 … 2026-08-27`, 19 JSON
  files: lamontagne, daniel, labella, christopher, james-trainor, hila-lewoof-faire, danny, hotes,
  joe-kim, kleban ×5, daniels ×2, kam, 140-day) — dated, well-formed, uncited. A recoil index
  (one JSONL row per engagement) would home all of them in one edge.
- `_STATE/2026-08-13-fortnight-retrospective.md`, `…-oss-family-gtm-positioning-voice-umbrella.md`,
  `…-umbrella-dunford-positioning-canvas.md`, `2026-08-14-milestone-artifact-engine-plan.md`,
  `pickup-trust-contract-privacy.md` — August strategy notes with no pointer.
- `_PATTERNS/2026-06-24-profile-scan-tei-budget.md`, `2026-07-10-landing-page-optimization-master.md`.
- `_QUEUE/ADR-020-pickup.md`, `ADR-058-pickup.md`, `toolbar-open-items-2026-06-25.md` — six of
  eight queue files are orphans; the backlog doctrine says open work lives in
  `_QUEUE/induced-backlog.jsonl`, so these are either absorbed or stale. Judgment item.
- `_DECISIONS/RECOIL-REPORT-Zach-Dom-2026-06-16.md` — a recoil report filed among ADRs, cited by
  nothing; probably belongs in `runtime/recoil/`.
- `_ARTIFACTS/ticket-zach-north-star-resonance-gradient-field.html` (180 KB),
  `analysis/detections/social-engineering-tells.md`, `_ARTIFACTS/prl-1-1-evidence/1.2A-build-prompts-3-versions.md`.

### Grade C / placer — real content, thin metadata
- `runtime/warroom/{jalaja,joe-war,peter}.html` + two louisville gift-card variants — war rooms
  with no index page.
- PRL close-loop notes (`_ARTIFACTS/prl-1-2-close-loop/*`, `prl-1-1-evidence/*`, `prl-zap-kit/README.md`).
- `runtime/scan/generated/zach.json` — a profile scan output with no pointer. (README and
  index files are landmarks and are never scanned for citations, so none appear here.)

### Grade D / overburden — heavy, low doctrine yield, keep private
- `_ARTIFACTS/resume-*/` renders (PDF/PNG/ATS text; ~6 MB), `_ARTIFACTS/profile-scan-*.pdf`,
  `_ARTIFACTS/prl-baseline/*.json` (CRM exports; 2.4 MB), `todd-call-proposal-backup-2026-08-04.html`,
  `2026-09-01-nextsteps-email-DRAFT.md`. Fate to declare in Loop 4: PRIVATE bundle or leave in
  place. **Never host.**

### Not ore — dormant seeds (do not bundle away)
- `_SEEDS/index.jsonl`, `ledger.jsonl`, `registry-artifacts.jsonl` are landmark ledgers and are
  never scanned for citations (`ref_scanned: false`); they are the bank, not the deposit. Tao §IV
  applies to every row inside them.

## 5. Loop 1 gate

| Criterion | Result |
|---|---|
| Every addressable file classed | PASS — 800 rows, 0 unclassed in candidate dirs |
| Secret-pattern hits = 0 | PASS — 0 |
| Shallow-clone caveat stated | PASS — header of this file + `_meta.age_caveat` in the ledger |
| Instrument falsified against itself | PASS — self-citation and UNDEFINED→NULL both caught and fixed |

**Gate: PASSED. Loop 2 (catalog) may start.**

## 6. Loop 2 plan (catalog) — judgment work, not shell work

1. Re-read `FORENSIC_REPORT.md` §4 against today's canon; mark each item
   `ALREADY_CANON / VARIANT / NET_NEW` (claims-skeptic agent). Expected: most now homed.
2. Run the Folksonomist (Op20) over the Grade A/B residue above — the 19 recoil ledgers, the 6
   stories, the 7 transcripts, the 5 August notes — to coin tags bottom-up. Gate: ≥90% tagged.
3. For every NET_NEW claim, a Loki inversion before it may be proposed for a number.
4. Print: `_STATE/<date>-catalog.jsonl` (one row per item: path, tags, canon-status, proposed home).

Loop 3 (organize) then mints only through the oracle and creates the homing edges; Loop 4
(bundle) writes one manifest per bundle with a fate per Grade D item. The cycle stops on the
operator's ruling, never on its own.

---

*Regenerate:* `python3 scripts/corpus_prospector.py index --out _STATE/<date>-corpus-index.jsonl`
then `orphans --out _STATE/<date>-orphan-ore-ledger.jsonl`. Dated filenames; never overwrite a
prior survey.
