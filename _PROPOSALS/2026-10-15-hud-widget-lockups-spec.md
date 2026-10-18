# Chip: spec the HUD widget lockups (sticky, closable, draggable, grid-snapping)

Prior art: scripts/prior_art.py ranked src/ui (Gauge, CloseButton, ChipToggle), the ui-kit README, operators/arcs_primitives.py and _PATTERNS/jtbd-orchestration-map.md. Nothing in src draws a draggable widget yet except two hits in src/app/jobs/lane/LaneSurfaces.tsx. This chip writes a SPEC only. It changes no production file.

## Ground truth
- The field HUD is src/organisms/Scope.tsx (1284 lines, one monolith) with its readout panel in src/organisms/ScopeHud.tsx, mounted full screen at /hud by src/app/hud/page.tsx.
- ScopeHud draws these rows today: Conviction ("No signal"), Clarity, Coherence, Cohesion, Consonance. Values come from src/data/universe-field.json (81 nodes, 119 edges).
- Atoms that already exist: src/ui/Gauge.tsx (instrument tile with label, value, sub, accent), src/ui/CloseButton.tsx (44px hit area, keyboard ring), src/ui/ChipToggle.tsx, src/ui/StickyFooter.tsx. Tokens: src/ui/tokens.ts.
- Rules in force: inline styles only, no new npm dependencies, build with npm run build, em-dashes 0, render at earned fidelity (WORLD.md).
- The audit this spec builds on found that the five gauges (fidelity, conviction, clarity, coherence, consonance) mix two definitions per name and show no sample size. The audit is committed in the same change as this spec (see Outputs).

## Assumption to confirm (Zach dismissed the question)
"Widgets 1 to 5" is read here as the five gauges. If it means controls C1 to C5 or decisions D1 to D5 in the audit, only the Widget table below changes; the contract, behaviours and fixtures stay.

## SSOT
- One registry file (path under Outputs), generated and grep-verified, never hand-written, emitted by a script patterned on scripts/operator_registry_emit.py (it refuses any binding whose symbol it cannot find).
- Layout state is per viewer and optional: a try/catch-wrapped localStorage record. The HUD must render correctly with it empty.

## Widget contract (each widget is a standalone micro service)
A widget is a pure function plus a view:
- read(source) returns a Reading: value, n (sample size), grain (0 to 1, from n), asOf, source id. No hidden inputs, no network call inside the widget.
- view(Reading) renders with src/ui/Gauge.tsx. Below the n threshold it renders GRAIN and prints n. Conviction with no data prints "No signal".
- A widget imports nothing from another widget. It imports only tokens and atoms.
- Declared bindings in the registry: reads (a data file, receipts table or operator), emits (close, move, snap events), and optional links to an operator id from operators/OPERATOR-REGISTRY.json, a command or skill from runtime/specs/tool-catalog.json, and a watcher. The emitter fails on any link that does not resolve.

## Widget table (assumption: the five gauges)
| # | Widget | Reads | n shown | Threshold for non-grain |
|---|--------|-------|---------|-------------------------|
| 1 | Fidelity | renderResolution of the receipt, or node grain from evidence | receipts or evidence count | 10 evidence |
| 2 | Conviction | NCI from receipts | receipt count | none until receipts are tagged real |
| 3 | Clarity | nci_by_lens.clarity, lattice nodes_clear | questions or nodes | 10 |
| 4 | Coherence | lattice diamonds and hardness, under its own name | nodes | 10 |
| 5 | Consonance | mean NCI minus matched-outcome rate, per cohort | closed receipts | 30 (the Accountant rule) |

## Behaviours
- Sticky: a widget is positioned fixed inside the HUD, above the canvas, and survives fathom changes.
- Closable: the CloseButton atom hides it; a tray of ChipToggle chips re-opens it. Closed state is stored with the layout.
- Draggable: pointer events with pointer capture, clamped to the viewport. Keyboard alternative required: focus the widget, arrow keys move by one grid cell, Escape cancels.
- Grid view: a pure function snap(x, y, orientation) returns a cell. Orientation is portrait or landscape from the viewport. Cells follow chip size (1 by 1) and one-sheet lockup size (2 by 3 landscape, 3 by 2 portrait). On drop the widget animates to its cell; reduced motion skips the animation.
- Plain scroll and the canvas camera gestures keep working outside widgets.

## Routes (build order, tiered; precompute first)
1. Tier 0, script, no model: emit the widget registry and a check that every binding resolves. Prints widgets, unresolved bindings, and the judgment residue.
2. Tier 2, Sonnet: widget views and the drag and snap hook, one file per widget in a new hud organisms folder (path under Outputs), plus the pure snap function.
3. Tier 2, Sonnet: mount behind the same admin check the ziggurat loader uses in src/app/hud/page.tsx.
4. Tier 4, Zach: approve the mount, and approve making widgets public.
No tier below Opus-or-human for anything that deploys or publishes.

## Gates
- Fixtures fixed here before any build.
- snap() known-bad: points outside the viewport and a zero-size viewport must clamp or return null, never NaN. Known-good: a table of 12 points per orientation maps to the listed cells exactly.
- Layout known-bad: corrupt or missing localStorage must render the default layout with no exception. Known-good: close, reload and reopen restores the layout.
- Keyboard known-bad: a widget with no keyboard move path fails. Known-good: arrow keys move one cell and Escape restores.
- Honesty known-bad: a widget with n below its threshold rendered sharp fails. Known-good: the same widget renders GRAIN and prints n.
- Isolation known-bad: any import from another widget fails. Known-good: imports are tokens and atoms only.
- Run scripts/page_gate.py and scripts/component_source_gate.py on any rendered page, npm run build, and scripts/artifact_wrap_lint.py where a page is produced.

## Corrections (priors updated before this plan)
- The HUD audit said the echo and embedding code "run in tests". There is no test file; the embedding module has a --self-test that was not run, because this worktree has no operator virtualenv. The audit now says so.
- The audit named one sub-11px canvas label. Scope.tsx has five (lines 763, 823, 831, 947, 950). The audit now says so.
- A first write of the audit JSON silently failed because a stray stdin read swallowed the script. The file was checked after rewriting.
- The 11px floor is this plan's own, not a confirmed kit rule.

## Outputs
- _PROPOSALS/2026-10-15-hud-moire-audit.json and its rendered page (already written, uncommitted).
- _PROPOSALS/2026-10-15-hud-widget-lockups-spec.md (this file).
- Later, after approval: runtime/specs/hud-widgets.json, scripts/hud_widget_emit.py, src/organisms/hud/*.tsx.

## Close protocol
- Receipt row in decision_receipt per AGENTS.md for any merge. Neighbor scan with scripts/neighbor_scan.py before the merge.
- Open decisions for Zach: which five widgets; production go; admin-only first or public.
