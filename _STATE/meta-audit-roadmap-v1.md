---
version: 2.1.0
epoch: 2300012
date: 2026-07-12
artifact: https://claude.ai/code/artifact/cc787dbb-11e4-4576-a8d8-46822ca48f24
rom: runtime/specs/meta-audit-enrichment-rom.json
provenance: >
  Claimed by artifact v1.0.0 (§7 update law) but never minted — the audit drifted from
  its own law. Minted 2026-07-12 at v2.0.0, closing drift item Δ4. Append-only inchworm
  log at bottom; the Alchemist proposes entries, humans ratify them.
---

# ARCS Meta-Audit — L0→L5 — canonical twin

**True North (COURT, two-way door):** Close the loop — ship → measure → debrief →
truth-sync — before adding any new organ. The Alchemist tends the map overnight;
every ratification is human, at dawn, on the record.

**Gauges (earned, not asserted):** Conviction 78 · Coherence 82 · Done-state ~42%
(assessed) · Governed lines ~56K (assessed) · Drift ledger: 8 open / 1 closed.

## L0 · Atoms

25 canon docs (14,493 ln) · 32 ADR files (1 gap, 2 collisions) · 37 operator py
(17,353 ln) · 19 script py (8,809 ln) · 24 runtime specs · 130 src ts/tsx (15,297 ln) ·
20 API routes · 25 pages · 15 Prisma models · 20 public briefs · 15 published artifacts ·
7 patterns · 5 memory shards · 1 ordinal · 1 ROM candidate · **1 test file**.

**The Alchemist's Cookbook — structural ladder** (atomic design, literal in the tree;
three parallel atom systems are a named tension → ADR-031 reconciliation is the open receipt):

| Tier | Where | # | Members |
|---|---|---|---|
| Atoms | `src/ui/` + `src/ui-kit/recoil-report/` | 20+13 | Badge · Button · Card · ChipToggle · EyebrowToast · Field · Gauge · Label · Picker · PointerTypeProbe · ProgressBar · Rule · SectionLabel · SegmentedSlider · Spinner · StepProgress · StickyFooter · Tabs · ToastDrawerContext · Wordmark + wedge-kit 01–13; token sources `tokens.ts` / `_tokens.css` / `useVw` |
| Molecules | `src/molecules/` + `src/instrument/` + `src/components/` | 21 | AuthControl · CalibrationChips · CompassError · ConvictionSidebar · DebriefCard · ExpandableTributaries · FatedGrid · HeaderLockup · HorizonStakesRow · InstrumentCluster · PipelineRunning · PipelineTakeover · ReceiptPreviewWidget · SequenceLoader · TerrainPaths · TributariesStack + TributaryTile · TrueNorthPanel · WeatherBar + ClaimAnonymousReceipts · VercelToolbarToggle |
| Organisms | `src/organisms/` | 5 | Home · CompassForm · ResultView · Brief · ReflectLayer |
| Templates | `src/document/` + `public/templates/` + `src/emails/` | 21 | 10 document patterns + 5 document screens + call-brief `{{PLACEHOLDERS}}` + 4 emails + kit assembly |
| Pages | `src/app/` | 25 | dashboard · compass · prep · brief/reflect · receipt/reflect · guide · debrief · history · observatory · recoil ×3 · scan · onboarding · advisory · waitlist · admin · trust/privacy/terms · design-test · / |

**The Alchemist's Cookbook — elemental ladder** (nine classes; the reticulation taxonomy —
every atom is one of these):

| Class | Members / law |
|---|---|
| **Ordinals** | #001 Glossary v0.1 (`ARCS-ORD-20260624-0136-ZH`). Mint-don't-edit; repo inscribes, never mints; v0.3 fork backed out, awaiting primary ruling. |
| **Invariants** | 5 ROM primitives (NOTOMATION, Manifold, Hyperstition, Inchworm, Echo) + operational law (inline-styles-only — **VIOLATED** at `src/app/layout.tsx` · honest gauges · JSON-as-TEXT · no unasked deps · append-only handoffs · deploy from main · subdomains ungated). |
| **Primitives** | DEWY vector · ARCS Law `C = αA − β(S−S_min)² + γW` · CoherenceSignal/Receipt · FATEDReasoning · AxiomCheck · SomaticReading · Y-gate 12D two-zone manifold · render scale GRAIN→LOCKED · tributaries EXACTLY-3. |
| **Protocols** | Hyperstition pipeline · Accumulation (II·V) · Shared Court (II·VI, gated) · Recoil · Handoff chain (append-only, 20 entries) · canon-collision escalation · two-surface · drift sentry (designed, unbuilt). |
| **Operators** | LAB · BAR · SAGE · CURATOR · KAIROS · CONTRACT · OPERATOR20 · KINTSUGI + Court/HC/LTE/ROM/Trace systems + infra. 37 files, 17,353 LOC, zero production callers (canon-in-code). RC-OPS-001 gated. |
| **Advisors** | Loki · The Advisors · The Bayesian · dual Bar Raiser (Architect + Implementer) · The Curator · Fun House Mirror · DRIFT Sentinel · Kairos · **The Alchemist** (new this epoch — overnight enricher, proposes only). |
| **Risks** | No-Go Inventory v1.0 (Kintsugi ROM artifact; append-only, receipt-tagged): `BSS_WALL` · `TRIUNE_REMAINDER` · `KINTSUGI_SCAR` · `STRUCTURAL_BLIND`. Live BAR register: DATABASE_URL rotation (ADR-005) · key-man · canon-drift-as-trust-ruin · 1-test coverage. Standing redaction law (5 Fanatics rules). Precedent: SageTrace RLS breach caught + fixed. |
| **Patterns** | `_PATTERNS/` ×7 (governance roadmap w/ pathogen taxonomy · prose-rule audit · S-tier plan · kinematics adjudication · TEI budget · session post-mortem · two-surface protocol) + 4-tab call-brief engagement pattern. Law: minted from what broke, cited by roadmaps, never silently edited. |
| **Archetypes** | 8 cross-domain in `scripts/arcs_core.py`, shared by every scanner: Builder · Navigator · Illuminator · Instrumentor · Mediator · Orienter · Chartist · Focused Executor — color + keyword lattice; `classify_archetype()` scores resonance; UNDEFINED never force-classified. |

## L1 · Bonds (organs)

- **Canon organ** — Book II Parts I–VI (IV draft/CONDITIONAL CLEAR pending) + reference
  (trust-contract v1.1, Canon v2.0) + theory + living + supplement tiers.
- **Decision book** — ADR-001→031 + `index.json` + `_QUEUE/` bus. Integrity: ADR-021
  never minted; ADR-024 ×2; ADR-025 ×2.
- **Spec organ** — DEWY receipt schema v1 (Kairos-locked) · time-quality ROM ·
  lattice-pressure ROM · recoil modes · field-os archive (9 + JTBD map).
- **Product surface** — 25 pages · 20 routes · 15 models · compass chain
  (question+prep → Claude L0–L5 → Y-gate → receipt → brief → debrief).
- **Artifact wedge** — 13+ engagement subdomains · 20 public briefs · canonical template ·
  15 published Claude artifacts. The de-facto revenue organ.
- **Memory organ** — CLAUDE.md handoff chain · MEMORY.md · snapshot.json · `_MEMORY/` ×5 ·
  `_PATTERNS/` ×7.

## L2 · Laws (enforcement ledger)

Prose-rule audit 2026-06-23: **0/6 in-scope rules have tripwires.** Status today:
NOTOMATION HELD · inline-styles **VIOLATED** (layout.tsx) · honest-gauges HELD ·
append-only HELD-unenforced · ordinal law HELD (1 fork caught) · JSON-TEXT / no-deps /
commit-format HELD-unenforced · CI trip signals DORMANT (live only in inactive arcs-care) ·
deploy-from-main HELD-unenforced (burned once). Render law: GREEN→SHARP · YELLOW/FORK→
DEGRADED · SCRATCH/DELTA/DRIFT→GRAIN · PARADOX→MOIRE · RED→GRAIN.

## L3 · Cascade (roadmap)

```
HARD FORK receipt (#06) ────────→ #07 monetization rail (RED until filed)
100 receipts → Observatory period → RC-OPS-001 promotion → ADR-020/023 impl
backlog #3 log consolidation ───→ #6 DEWY commit stamp
Dan Pascone approval ───────────→ case-study flip → 30-day Lab clock (ADR-013)
eval harness (move 04) ─────────→ wire-or-retire /svc/sage + operators
Alchemist ROM v0.1.0 ───────────→ nightly enrichment → registries stay true
```

Stack rank: 01 ship loop live (GREEN·S) · 02 canon truth-sync (GREEN·S) · 03 debrief
loop (YELLOW·M) · 04 eval harness (YELLOW·M) · 05 kairos breadcrumbs (YELLOW·S) ·
06 HARD FORK receipt (FORK) · 07 rail (RED until 06). Carried: #2 rotation (Zach) ·
#4 drift-sensor (Alchemist SCAN = v0) · #8 reformat · #13 orphan tables (Zach) · #14 WARNs.

## L4 · Echo (drift ledger + parity)

| Δ | Item | Status |
|---|---|---|
| Δ1 | ATG narrated as backlog; shipped | OPEN |
| Δ2 | Outcome loop narrated as unbuilt; exists | OPEN |
| Δ3 | /svc/sage mounted, zero callers | OPEN |
| Δ4 | Twin claimed at _STATE/, absent | **CLOSED — minted this epoch** |
| Δ5 | ADR-021 numbering gap | OPEN |
| Δ6 | ADR-024 ×2 · ADR-025 ×2 collisions | OPEN — renumber via successor receipts |
| Δ7 | operators/README counts stale (34/16.6K vs 37/17.4K) | OPEN |
| Δ8 | AGENTS.md operator table mirrors Δ7 | OPEN |
| Δ9 | Tailwind classes in layout.tsx vs inline-only law | OPEN — fix or amend law |

Parity: compass/Y-gate/receipts/ATG/outcome **PARITY** (canon stale) · prep/scan/
accumulation PARTIAL · observatory GATED 100R · operators CANON-IN-CODE · kairos/sentinel
GAP (Alchemist SCAN = v0) · shared court + L6–L7 GATED correctly · billing HELD.

Recursion: corpus → ALCHEMIST (scan→reticulate→enrich→propose→receipt) → branch +
morning brief → **HUMAN RATIFIES** → corpus′ → twin + artifact redeployed.

## L5 · North

**BAR:** no fatal exposure; live risks = DATABASE_URL rotation (ADR-005) · key-man ·
canon-drift-as-trust-ruin · ~zero test coverage. **COURT:** NOTOMATION PASS · honesty
PASS · consistency TENSION (8 open Δ). **LAB:** enricher can fake progress — guard:
evidence-only re-grades, no new organs · n=1 steering · 100R is the slowest clock.
**KKL:** wedge + overnight-batch windows OPEN; enterprise + premature operator wiring CLOSED.

**Hardening plan:** H1 tripwires for the unenforced laws (CI greps) · H2 tests for
ygate/compass-parse/persistence · H3 repair ADR chain (successor ADRs, VOID 021, regen
index.json from tree) · H4 schedule the Alchemist (nightly 03:30 ET, kill switch human-held) ·
H5 truth-sync narrating docs (this ledger is the diff).

---

## Inchworm log (append-only; newest first)

- **2026-07-12 · v2.1.0 · epoch 2300012** — The Alchemist's Cookbook completed: structural
  ladder inventoried from the tree (33 atoms · 21 molecules · 5 organisms · 21 templates ·
  25 pages; three parallel atom systems named → ADR-031); elemental ladder grows to nine
  classes — Risks (NGI ×4 + BAR register), Patterns (×7), Archetypes (×8) join; enrichment
  ROM bumped to v0.2.0 carrying the full cookbook as reticulation taxonomy.
- **2026-07-12 · v2.0.0 · epoch 19dd948** — The corpus enters the instrument. Six strata
  L0→L5 with live registries; aperture + black-point + tilt optics join fidelity/resolution;
  twin minted (Δ4 closed); Alchemist ROM v0.1.0 pinned + `/alchemist` routine authored;
  drift ledger at 8 open (Δ5–Δ9 newly filed); hardening H1–H5 filed.
- **2026-07-10 · v1.1.0 · epoch 1a4c350** — Atomic Surface Map filed: 3 component systems +
  3 token sources · Manifest Law (zod) · 6-service decomposition · receipts-as-traces OTel
  mapping (held) · self-sovereignty ladder L1✅→L4.
- **2026-07-10 · v1.0.0 · epoch e802ed7** — Audit created. Funnel instrumentation shipped
  (NCI:88). Stale-canon findings filed: ATG · outcome loop · sage orphan. Fork receipt (#06)
  not yet filed.
