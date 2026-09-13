# ADR-032 — Parameterized Brief Generation with Provable CLI Provenance

> **Status:** DRAFT
> **Date:** 2026-07-10
> **Commit:** (set at merge)

## D — The Decision

**Sharp question:** Should call-brief artifacts display the CLI invocation that produced them — and if so, do we build a real generator first, or stamp artifacts with provenance the toolchain can't actually reproduce?

## E — Entity / System

- `public/templates/call-brief-template.html` — canonical template (8 metadata `{{PLACEHOLDERS}}`, content slots as HTML comments)
- `public/*.html` — 13 live call-brief artifacts (see `_STATE/snapshot.json` → `ui_artifacts.call_briefs`)
- `scripts/arcs_cli.py` — existing 5-verb pipeline; the design precedent (self-sovereign, stdlib-only, open JSON envelope contract)
- **New:** `scripts/brief_render.py` + `briefs/<name>.params.json` (git-tracked params, NOT under `public/` — params contain the gate password and private content)
- `_STATE/snapshot.json` → `ui_artifacts.authoring_workflow` — the workflow this ADR amends

## W — Window

**Horizon:** PERMANENT (authoring workflow change; applies to every brief created after this ADR)
**Revisit trigger:** (a) a brief needs a section shape the card schema + `html` escape hatch can't express cleanly three times in a row; (b) a client or prospect asks to reproduce an artifact and the provenance footer fails them; (c) briefs move off static HTML onto a dynamic route.

## Context

The 13 live briefs are produced by a manual copy-template-and-fill workflow. Zach asked whether every artifact should display its generating CLI to demonstrate ARCS principles (traceability / transparency / composability / interoperability / atomic design). Investigation found the CLI shown would not exist: `arcs_cli.py` is real and genuinely composable, but it reasons over scanner envelopes — nothing in the repo generates a brief from parameters. Displaying a fake invocation inverts the "make it provable" rule (the governing /goal): the first viewer who tries to run it turns the transparency claim into a credibility hole.

Secondary finding: all live briefs have diverged from the template (labella 1560 lines, peter 1025 with bespoke Call Walk / Probability Tree sections). Placeholder-fill drift is already the failure mode of the manual workflow.

## Options Considered

### Option A — Stamp artifacts with a pseudo-CLI provenance block, no generator
- What it is: add a footer showing a notional `arcs brief render …` command to each artifact.
- Pros: hours of work; immediate visual story.
- Cons: provenance theater. Command is not runnable; fails Loki test on first contact with a technical viewer; violates "cut, don't add; make it provable."

### Option B — Build `brief_render.py`, stamp only what it actually renders, adopt forward-only (CHOSEN)
- What it is: stdlib-only generator, `params.json` + canonical template → `public/<name>.html`, deterministic (byte-identical re-render from same inputs). Provenance embeds the exact invocation + SHA-256 of params and template + template version. Two visibility tiers set per-params: `full` (internal/demo artifacts — visible CLI card) and `receipt` (client-facing — one mono line: template version + params hash + date; no internal command surface, per Fanatics redaction constraints). Existing 13 briefs untouched; new briefs go through the generator; backfill only what gets actively demoed.
- Pros: every displayed claim is executable and reproducible — the principles are demonstrated, not asserted. Kills placeholder-drift for new briefs. Template stays hand-authorable (generator splices at existing tab markers; no structural template change).
- Cons: bespoke sections must be expressed as params cards (an `html` escape-hatch card type covers arbitrary shapes at the cost of putting raw HTML in JSON). One more script to maintain.

### Option C — Option B plus full backfill of all 13 live briefs
- What it is: extract every live brief's content into params files.
- Pros: uniform provenance across the whole roster.
- Cons: 13 bespoke artifacts ≈ days of extraction with clobber risk on live client pages (labella, fanatics, cj-brief) for near-zero payoff — old briefs are historical record, not demos. Fails "cut, don't add."

## Decision

**Chosen:** Option B
**Rationale:** The CLI stamp is only worth showing if running it reproduces the artifact. Building the smallest real generator makes the transparency claim true, then the display is free. Forward-only adoption concentrates rigor where it's material (artifacts still being created) instead of retrofitting history.
**Trade-offs accepted:** Live briefs keep no provenance; roster is two-generation until old briefs retire. Bespoke content in params-JSON is less pleasant to author than raw HTML — accepted because the template's card patterns cover the common 90%.

## Y — Conviction

**Polarity:** [SCRATCH | YELLOW | GREEN | LOCKED]
**Conviction:** [LOW | MEDIUM | HIGH]
**Stability:** [SHIFTING | CONTESTED | STABLE | REVISIT]

**Loki test:** The strongest case against: briefs are one-off, hand-tuned persuasion artifacts, and every real one has diverged from the template — so the generator may become a machine nobody uses, and the params-JSON authoring step may be slower than copy-and-edit for exactly the bespoke briefs that matter. If the next two real briefs route around `brief_render.py`, the generator is shelf-ware and the provenance story should be retired rather than faked. (Mitigation baked in: the `html` card type keeps bespoke authoring one JSON field away; revisit trigger (a) above.)

## Consequences

- New artifacts carry runnable provenance; "traceability / composability" claims on demos become demonstrable live.
- `_STATE/snapshot.json` → `ui_artifacts.authoring_workflow` gains the CLI path as the preferred route for new briefs (manual path remains valid).
- Client-facing tier (receipt line) is the default for any brief whose subdomain is shared externally; `full` tier requires explicitly opting in via params — consistent with the Fanatics redaction rules (no vendor/tooling exposure on target pages).
- Params files under `briefs/` become the source of truth for generated briefs; editing the rendered HTML directly is now drift and should be caught in review.
- Creates a future decision point: whether `brief_render` graduates into `arcs_cli.py` as a sixth verb or stays standalone (deferred until the envelope contracts converge).

**Implementation pointer:** `scripts/brief_render.py`, `briefs/demo.params.json`, `public/demo-brief.html` (proof artifact, full-tier provenance), this branch (`claude/parameterized-artifacts-cli-41aff5`).
