# ADR-083 — ui-kit atomic SSOT + component-source gate for self-contained HTML surfaces

> **Status:** PROPOSED
> **Date:** 2026-09-26
> **Author:** Claude Opus 4.8
> **Oracle:** number allocated via `scripts/oracle.py next adr` (83); `_SEEDS/_oracle.json` committed.
> **Renumber note (2026-09-26):** originally minted as ADR-082, which collided with the Track-B
> slop-gate-oss-publish fork's ADR-82 (already pushed to origin/claude/slop-gate-consolidate-dist-a34d1c);
> both allocated 82 off a main at high-water 81. This un-pushed decision moved to the oracle-issued 83.
> No content change.
> **Stakeholders:** ARCS design-system owners; anyone shipping a `public/*.html` or `_ARTIFACTS/*.html` surface.
> **Relationship to ADR-009:** ADR-009 canonicalized the React `src/ui/` component library for the
> Next.js product. This ADR is its sibling for the ~225 SELF-CONTAINED single-file HTML surfaces
> (counterpart briefs, NFTT essays, scan HUDs, resumes) that do NOT consume `src/ui/` and instead
> re-author their own CSS. It does not touch ADR-009's React library.

---

## D — The Decision

**Sharp question:** Should self-contained HTML surfaces snap into an atomic-design SSOT in
`src/ui-kit/` (tokens + numbered `@dsCard` primitives + a template registry), enforced by an opt-in,
ratcheted `component-source` gate that is the visual twin of `token_source_gate.py` — rather than each
page continuing to re-author its own component grammar?

**Proposed answer (for review, not decreed):** Yes. Extract the atomic hierarchy that already exists
implicitly in `src/ui-kit/recoil-report/`, document it (`src/ui-kit/README.md` + `templates.json`),
bind each template to exactly one `slop_lint --mode` so visual composition and eval thresholds cannot
drift, and gate enrolled pages with `scripts/component_source_gate.py`. Roll out surface-by-surface;
do not mass-migrate.

---

## E — Entity / System

- `src/ui-kit/recoil-report/_tokens.css` — the atoms (the ONE signal palette; sentinel-line SSOT).
- `src/ui-kit/recoil-report/NN-*.html` — 14 `@dsCard` organism primitives (already exist).
- `src/ui-kit/templates.json` — NEW: template registry (name → mode + signature selectors).
- `src/ui-kit/README.md` — NEW: the atomic hierarchy, template↔mode map, enrollment, brand profile.
- `scripts/component_source_gate.py` — NEW: the gate (opt-in via `<!-- @arcs-template: -->`, ratcheted).
- `scripts/token_source_gate.py` / `scripts/slop_lint.py` — existing twins this composes with.
- `.impeccable/config.json` — the Impeccable detector's brand exemptions (verified working mechanism).
- ~225 self-contained HTML surfaces (42 inherit tokens today; 135 re-author) — the migration surface.

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** a second template family needs signatures finalized; or the font-stack drift
(`tokens-css-vs-ds-font-stack-drift`) is reconciled and `_tokens.css` changes; or enrolled-page count
crosses ~10 and the signature-selector heuristic proves too coarse.

---

## Y — Gate

**State:** YELLOW/FORK — a proposal with one PoC, not a ratified mass migration. The load-bearing
open decision (which token vocabulary is canonical: `_tokens.css` Geist/Instrument vs DESIGN.md
Inter/JetBrains) is explicitly deferred, not resolved here.

---

## Context

A 2026-09-26 census of 225 self-contained surfaces: 27 inline `_tokens.css` (sentinel), 15 link it,
135 re-author the 4-signal palette (74 verbatim under canonical names, 27 under foreign names), 48 are
not palette surfaces. Section labels appear under 6 class names, chips under 5; the `@dsCard` primitive
class is used in 10 kit files and NOWHERE downstream. `token_source_gate.py` blocks NEW re-authoring
but the divergence has no positive SSOT to snap into — this ADR supplies it.

The gate is deliberately the same shape as the anti-slop eval suite it complements: single-source,
opt-in (a marker), ratcheted against HEAD, with a `--self-test` proving fails-on-bad + passes-on-good.

## Consequences

- **Positive:** one visual SSOT; visual template and eval mode declared together (can't drift); new
  pages snap in; migration is surface-by-surface with a ratchet so day-one breakage is zero.
- **Cost/risk:** `templates.json` signature selectors are a coarse proxy for "assembles from the kit"
  (a page could reference a signature class yet still diverge); resume-print signatures are unset until
  first enrollment; the brand-profile exemptions are per-file and must be added as surfaces enroll.
- **Explicitly NOT decided here:** the `_tokens.css`-vs-DESIGN.md font-stack canonicalization (cross-
  session; backlog `tokens-css-vs-ds-font-stack-drift`); whether the NFTT `blog-nftt-*` token
  exemption in `token_source_gate.py` should be retired in favor of enrollment.

## PoC (this change)

`_ARTIFACTS/profile-scan-hud.html` migrated off its `--palette-*` block onto verbatim `_tokens.css`,
enrolled in template `scan-hud` (mode `operate`). Passes token/component/wrap/slop gates; Impeccable
findings drop 120→76 under the brand profile (only genuine legibility debt remains). Closes backlog
`scan-huds-migrate-to-tokens-css` for the profile HUD.
