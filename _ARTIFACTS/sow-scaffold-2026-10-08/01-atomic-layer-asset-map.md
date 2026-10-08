# 01 Atomic-layer asset map (INTERNAL DRAFT, 2026-10-08)

Scope: reusable assets that can serve the My Ally LD scope of work. Source: the night-moves gather for 2026-10-08 (thin: 9 commits, no net-new tools today), the reuse catalog (`runtime/specs/artifact-reuse-catalog.md`, generated 2026-10-07), the tool catalog (`runtime/specs/tool-catalog.md`), and a read of the skill files named below. Every path was checked to exist in this worktree on 2026-10-08. "Start here" is a lead to check, not a verdict.

## Night-moves findings, scoped to reuse

- Net-new tools today: none. The day's work was the field universe, HUD fixes and a gate rebaseline, which nothing here depends on.
- The most reusable engagement assets are older and stable: the recoil skills (ADR-068 print schedule), `scripts/assumptions.py`, `scripts/projection_factory.py`, `scripts/page_gate.py`, and the kit under `src/ui-kit/`.
- The reuse catalog's "start here" list is dominated by copy-style notes and two scan HUDs; no entry is an engagement proposal or SOW. A search for statement-of-work in tracked md, json, py and html found only `public/prl-status-troubleshooting.html`, `runtime/specs/arcs-v9-consolidated-design-v1.md` and a forge bundle's notes, none a template. **Gap: there is no SOW template in the repo.** This scaffold is the first.

## Layer map

| Layer | Best starting point | Path | Use for the SOW | Caveat |
|---|---|---|---|---|
| Atoms | Design tokens (palette, type, space, radius) | `src/ui-kit/recoil-report/_tokens.css` | Inline verbatim in any page that is later built from this scaffold | Font names conflict with `DESIGN.md`; open backlog item `tokens-css-vs-ds-font-stack-drift` (`src/ui-kit/README.md`) |
| Atoms | Gates that police atoms | `scripts/token_source_gate.py`, `scripts/component_source_gate.py` | Block a re-authored palette | Pre-commit only fires on enrolled pages |
| Molecules | Probability bar, receipt table, signal-delta table | `src/ui-kit/recoil-report/07-probability-bar.html`, `08-receipt-table.html`, `04-signal-delta-table.html` | Best/base/worst cost band; line-item grade table; assumption table | Numbered primitives are `@dsCard` files; reuse by copying the class block |
| Molecules | Earned-fidelity twin | `src/ui-kit/recoil-report/14-earned-fidelity-twin.html` | Renders the per-item fidelity grade (SHARP / DEGRADED / GRAIN) | Matches WORLD.md render scale |
| Organisms | Pipeline stage tracker | `src/ui-kit/recoil-report/10-pipeline-stage-tracker.html` | Phase 0 as a four-stage strip: audit, discovery, shareback, workshop | |
| Organisms | Beat stepper, 90-day build | `06-beat-stepper.html`, `13-90day-build.html` | Sprint sequencing for tracks A, F, B | 90-day shape is a job-search artifact; retitle |
| Organisms | Stop-loss footer | `09-stop-loss-footer.html` | Exit criteria per phase (when to stop spending) | |
| Organisms | Recoil header, entity card, champion map | `01-recoil-header.html`, `03-entity-card.html`, `11-champion-map.html` | Internal war-room view of the four co-founders and their roles | Internal only; champion map names people, so it stays behind the gate |
| Templates | Template registry | `src/ui-kit/templates.json` | `recoil-report` is the closest template (mode `operate`); register a new `engagement-sow` template only if a page is built, per the README rule of one new `@dsCard` primitive | No SOW template exists |
| Templates | Page-wrap canon | `_PATTERNS/arcs-artifact-css-base.css`, `scripts/artifact_wrap_lint.py` | Mandatory for any html; lede spans the full lane | Gotcha #13 in AGENTS.md |
| Templates | Engagement SSOT template | `runtime/recoil/templates/war-room-6tab.template.json` via `.claude/skills/recoil-new/SKILL.md` | The ex-ante, war-room and close-loop tabs for the engagement; one JSON per counterpart | Needs a non-guessable gate password per the skill; scaffold only after Zach's yes |
| Templates | Projection factory | `scripts/projection_factory.py` | Air-gap by construction: an external SOW view built from a whitelist of fields, so internal prose cannot leak | Four-part contract (source ledger, whitelist, template, guarantee) |
| Pages | Counterpart surface family | `.claude/skills/forge/SKILL.md`, `.claude/skills/omakase-pipeline/SKILL.md`, `.claude/skills/teardown-page-factory/SKILL.md` | A counterpart-facing page, after the gates | Counterpart pages are gated and need Zach's yes to send |
| Pages | Gate for any standalone html | `.claude/skills/page-gate/SKILL.md`, `scripts/page_gate.py` | Acceptance check before showing a draft render | |
| Skills (process) | Recoil arc | `.claude/skills/recoil-new`, `recoil-prep`, `recoil-ship`, `recoil-close` | Ex-ante receipt before send, close-loop after reply (ADR-068, `_DECISIONS/ADR-068-verb-altitude-gate-matrix.md`) | Mandatory prints are blocking |
| Skills (process) | Pre-send gauntlet | `.claude/workflows/counterpart-gauntlet.js` | Simulate the counterparts (founder, counsel, a technical reviewer) against the draft before it leaves DRAFT | Workflow, multi-agent; cost it first with `token-savings-bank` |
| Skills (process) | Session decomposition | `.claude/skills/fold/SKILL.md` | Split a later dense session into composed sessions | |
| Routines | Assumptions ledger | `scripts/assumptions.py`, rows in `_STATE/assumptions.jsonl` (14 rows) | The draft rows in `03-assumptions-draft.jsonl` validate against it | Live ledger is append-only; do not append without Zach's yes |
| Routines | Reconciliation | `scripts/reconcile_epoch.py` | Re-check the SOW against its sources at review dates | Not run here |
| Routines | Cost kaizen | `scripts/token_kaizen.py`, `_PATTERNS/workflow-cost-ledger.md` | Model for the cost-baseline template's variance column: projected vs actual | The ledger itself records ARCS workflow spend, not client spend |
| Operators | LAB / BAR / Loki / Kintsugi | `operators/arcs_operators_lab.py`, `arcs_operators_bar.py`, `arcs_trace_loki.py`, `arcs_kintsugi.py` | Vocabulary and method for the Loki test and the premortem; the SOW's Loki pass here is performed by hand | `AGENTS.md` says operators are not wired into the compass route |
| Compass | Question Compass | `src/app/dashboard/page.tsx`, `src/app/api/compass/route.ts` | The decision-receipt workshop engine on the build-versus-hire fork | Claude L0 to L5 prompt with an advisory pre-screen, not a mechanical pipeline; stores receipts under `src/app/privacy` terms; **do not feed prospect material until NDA and Zach's yes** |
| Receipts | Decision receipt table | `public.decision_receipt` (Supabase), fixed form in `AGENTS.md` | One row per merge | Column constraints listed in AGENTS.md |

## Net-new tools and gaps this exercise exposes

1. No SOW or proposal template (above). Candidate: one `engagement-sow` template and a small emitter, only if the scaffold is reused for a second client. Not built here.
2. No premortem asset. LAB/BAR/Loki cover adversarial reasoning, but there is no named premortem script or skill. The workshop will run it by hand until one exists.
3. No cost-baseline template for a client's build (fixed, variable, hidden; best, base, worst). `04-cost-baseline-template.md` is the first.
4. No redaction recall test harness. Acceptance for the redaction design (B.4) needs a synthetic-IEP generator; nothing in the repo does this.
5. `scripts/gauntlet_log_emit.py` is listed INSTALLED-UNUSED in the tool catalog; it is the worked example of the projection factory and may serve as the pattern for an external SOW view.
