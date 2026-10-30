---
version: 0.1.0
date: 2026-10-30
status: PROPOSED (read-only pass; nothing merged or deployed)
backlog: unified-design-system-receipts-reports
grammar source: runtime/specs/grammar-chips.json v0.2.0 (branch claude/sharp-visvesvaraya-c391ba, local, commits f2ade692 and 1965839d)
---

# One design system for ARCS: reconcile the claim chip grammar with every live surface

Prior art: DESIGN.md "Sanctioned Visual Worlds" and "Motion and safety"; `scripts/token_source_gate.py`; memory `single-file-artifacts-inherit-tokens-never-copy`; `public/proof.html` (PRs 1868, 1871).

Scope split: the apex-design-audit session (local_156f76c6) is auditing the Dioptra index page only (its note `apex-audit-and-gauntlet.md`). No surface overlaps with this pass.

## The finding in one paragraph

Tokens are already unified on the HTML side: every surface below passes `token_source_gate` (it inlines `_tokens.css` verbatim), and NFTT passes as its own sanctioned world. What is NOT unified is the layer above the tokens. Each page invents its own chip, LED and card classes (`.chip`, `.su-chip`, `.pres-chip`, `.unlock-chip`, `.ezchip`, `.led`, `.pip`, `.mp-dot`, `.pulse-dot`, `.badge`), and none of them uses the grammar's glyph and tag pairs. Worse, `/proof` (the page named as the model) assigns the grammar's glyphs to different meanings. The React app (compass, brief, receipt, debrief) reads a second token source, `src/ui/tokens.ts`, and the grammar branch would add a third, `src/ui/grammarChipTokens.ts`. The fix is one atom layer, not a repaint.

## 1. Inventory

Token column: "kit" = inlines `src/ui-kit/recoil-report/_tokens.css` (gate PASS, run 2026-10-30); "ui/tokens.ts" = React token module; "NFTT" = sanctioned literary world. Hex count = distinct 6-digit hexes in the file (palette re-authoring pressure).

| Surface | File | Tokens | Hex | Chip / badge / pill | LED / dot | Card | Button |
|---|---|---|---|---|---|---|---|
| arcs.care (question compass) | `src/app/page.tsx` -> `src/organisms/Landing.tsx`; atoms in `src/ui/` | ui/tokens.ts | 0 in page | `src/ui/ChipToggle.tsx`, `src/ui/Badge.tsx` | `src/ui/Gauge.tsx`, `ProgressBar`, `StepProgress` | `src/ui/Card.tsx` | `src/ui/Button.tsx` (Button, ButtonLink) |
| zach.md/proof | `public/proof.html` (built by `scripts/proof_emit.py`) | kit | 16 | none | `.led.shown` ▲ green, `.led.on-request` ◆ cyan, `.led.not-yet` ~ gold, `.pip` row glyphs | `.card` (one hero card) | `button.ref` |
| good.arcs.care | `public/good.html` | kit | 25 | `.chip`, `.chips` | `.dot`, `.mp-dot` | `.card`, `.cards`, `.mp-card` | `.btn` |
| good.arcs.care/audit | `public/good-agent-receipts-audit.html` | kit | 11 | none | none | `.card` | none |
| status.arcs.care | `public/status.html` | kit | 27 | `.chip`, `.su-chip(s)`, `.pres-chip`, `.unlock-chip`, `.pres-stage` tag | `.eyebrow-dot`, `.pres-dots`, `.pulse-dot` | `.rm-card`, `.su-card(s)`, `.su-icards`, `.unlock-card` | `.alt-btn`, `.focus-btn`, `.pres-btn`, `button` |
| status.arcs.care/beliefs | `public/belief-log.html` | kit | 23 | none | `.dot` | `.m-card` | none |
| status.arcs.care/gauntlets | `public/gauntlet-log.html` | kit | 19 | none | `.dot` | `.m-card` | none |
| playground.arcs.care | `public/playground.html` (+ `public/pf-*.html`) | kit | 27 | none | none | none (list rows) | none |
| surfaces.arcs.care | `runtime/warroom/surfaces.html` (admin-gated) | kit | 16 | `.chip`, `.chips`, `.badge` | none | none | none |
| NFTT index | `public/blog-nftt-index.html` | NFTT | 13 | `.ezchip`, `.ezchip-t`, `.sec-tag` | `.dot`, `.mp-dot` | `.card`, `.card-body/-d/-img/-t` | `.ezbtn`, `.ezbtn-ghost` |
| NFTT posts (41 files) | `public/blog-nftt-*.html` | NFTT | 13 | none | `.dot` | none | none |
| Receipt | `src/app/receipt/[receiptId]/page.tsx` + `src/document/screens/Receipt.tsx` | ui/tokens.ts | 0 | `src/molecules/ProvenanceTag.tsx` | none | `TribunePanel` | Button, ButtonLink |
| Brief | `src/app/brief/[receiptId]/page.tsx` + `src/document/screens/Brief.tsx` | ui/tokens.ts | 3 | Badge | none | Card (7 uses) | Button |
| Debrief | `src/app/debrief/[receiptId]/page.tsx` | ui/tokens.ts | 1 | none | none | Card (19 uses) | Button, ButtonLink |
| Recoil report | `src/app/recoil/[reportId]/page.tsx` -> `src/document/screens/RecoilReport.tsx` (admin) | ui/tokens.ts | 1 | none | none | report sections | ReportActions |
| Calibration chips | `src/molecules/CalibrationChips.tsx` | ui/tokens.ts | | conviction chips (PROTOTYPED) | | | |

Counted by `scan.py` over class selectors; React counts are identifier mentions. A class list is a lower bound: inline-styled spans in TSX are not counted.

## 2. Reconcile to the grammar

Grammar: tones say ▲ cyan, show ● green, limit ◆ gold, fail ✕ red, shift ◇ violet, neutral · slate; fidelity sharp, degraded, grain, moire; materials field (recessed well, breathing LED) and pocket (bezel, raised keys, LED tiles).

| Pattern | Verdict | Mapping or gap |
|---|---|---|
| proof `.led.shown` ▲ green | **Conflict, must fix** | ▲ is SAY (cyan) in the grammar. "Shown" means evidence: becomes SHOW ●. |
| proof `.led.on-request` ◆ cyan | **Conflict, needs a new tone** | ◆ is LIMIT (gold). "On request" is evidence that exists but is held private. Neither SHOW nor LIMIT. Propose tone `held` (glyph ◐, tag HELD, slate-cyan), or map to neutral with tag ON REQUEST. Zach's call. |
| proof `.led.not-yet` ~ gold | Maps (glyph swap) | LIMIT ◆, tag NOT YET. |
| proof `.pip` per-row glyph strip | Maps | A row of grammar glyphs at `field` material; becomes the `ChipStrip` atom. |
| status `.su-chip`, `.pres-chip`, `.chip` | Maps | Status words map to show / limit / fail / neutral. |
| status `.unlock-chip`, `.unlock-card` | Separate (control, not a claim) | A gate affordance, stays a button. |
| status `.pulse-dot`, `.eyebrow-dot` | Maps to material | `field` breathing LED; motion must use `--mo-*` (DESIGN.md "Motion and safety"). |
| belief-log / gauntlet-log `.dot` | Maps | Belief kept = show, broken = fail, revised = shift. These two pages are the best fit for the grammar on the site. |
| good `.chip`, `.dot`, `.mp-*` | Maps | |
| surfaces `.chip`, `.badge` | Maps | Route kinds are neutral; live/dead status is show/fail. |
| playground | No chips today | Fidelity grain/moire is the natural home (pf-moire). |
| ProvenanceTag (receipt) | Maps | Provenance source tags are neutral; verified/unverified = show/limit. |
| Badge.tsx, ChipToggle.tsx | Maps (become GrammarChip skins) | ChipToggle is input, so pocket material (raised key). |
| CalibrationChips (conviction) | Maps plus fidelity | Conviction level drives fidelity (sharp to grain), not tone. |
| Y-gate states on receipts | Maps | GREEN=show sharp, YELLOW/FORK=limit degraded, RED=fail grain, DELTA/DRIFT=shift grain, PARADOX=limit moire, SCRATCH=neutral grain. |
| NFTT `.ezchip`, `.card`, `.dot` | **Sanctioned separate world** | Stays NFTT unless Zach says otherwise. Only the label heuristics row touches it. |
| Light paper pages | Sanctioned separate world | The grammar already carries a light column for it. |
| Pocket skin (dj.arcs.care) | Sanctioned world, source of `pocket` material | Not migrated; it lends the material. |

Needs-new list: one tone (`held`, or a neutral tag), nothing else. No new material.

## 3. Gold standards and what becomes a kit atom

**Question compass (arcs.care)** is `src/organisms/Landing.tsx` on `src/ui/*`. It is polished because it is assembled from atoms, not page CSS. Promote as-is into the kit spec (they already are atoms; they need the grammar wired in): `Button` (primary and ghost), `Card`, `SectionLabel`, `Rule`, `Gauge`, `StepProgress`. `Badge` and `ChipToggle` are replaced by `GrammarChip` (field and pocket).

**/proof (zach.md)** is `public/proof.html` from `scripts/proof_emit.py`. What makes it the model for receipts: a ledger hero card with three counted totals, every claim a row with a question, a one-line answer, and a glyph strip, rows that open in place ("tap any line to zoom in"), one lane, one measure. Atoms to extract:
1. `LedgerHero`: eyebrow with as-of date, title, full-width lede, a 3-up `StatTriad` (number over LED label).
2. `ClaimRow`: index "01 / 06", question, answer, right-aligned `ChipStrip`, expands to evidence.
3. `ChipStrip`: N grammar glyphs, one per evidence item.
4. `LedLabel`: glyph plus mono uppercase tag (this IS the grammar chip at its smallest size).
5. `ExpandAll` control.

Both families need a source the HTML side and the JSX side share. `grammar_chips_emit.py` already emits both; extend it to emit these five atoms as an `@dsCard` primitive file under `src/ui-kit/` and as TSX under `src/ui/`.

## 4. Receipts and reports redesign, modelled on /proof

A receipt is a proof ledger for one decision. Same skeleton:

| /proof part | Receipt | Recoil report | Brief |
|---|---|---|---|
| LedgerHero: name, as-of, lede | the question, event date, true north as lede | counterpart, call date, one-line read | the question, render fidelity |
| StatTriad: shown / on request / not yet | confirmed / unconfirmed / changed (show, limit, shift) | held / broke / new (show, fail, shift) | paths open / closed / forked |
| ClaimRow per question | one row per DEWY field and per tributary | one row per operator lens | one row per terrain path |
| ChipStrip | evidence per row from `what_confirmed[]` / `what_unconfirmed[]` | sources per lens | |
| Fidelity | Y-gate drives the whole page's render resolution | | |

Rules: one lane, one `--measure`, ledes full width, text full opacity (fog through weight and grain only), motion through `--mo-*`. Field material by default; pocket only on input controls.

## 5. Migration order (visitor value against effort)

| # | Step | Visitor value | Effort | Closes |
|---|---|---|---|---|
| 0 | Decide the `held` tone and land the grammar branch (spec + emitter + GrammarChip) | enables all | S | |
| 1 | Fix /proof glyphs to the grammar (▲ to ●, ~ to ◆, ◆ to held) | high (public, live in hiring loops) | XS, `proof_emit.py` only | |
| 2 | Extract the five /proof atoms into the kit (HTML primitive + TSX) | none directly | M | `tokens-css-vs-ds-font-stack-drift` (atoms force one font stack; reconcile `_tokens.css` GeistMono/InstrumentSans against DESIGN.md first) |
| 3 | Receipt page on the ledger skeleton | high (the product artifact; also fix the example link, see Evidence) | M | part of `recoil-renderer-design-debt` |
| 4 | Brief and debrief on the same atoms | high | M | |
| 5 | Recoil report renderer on the atoms | medium (admin) | M | `recoil-renderer-design-debt` |
| 6 | CalibrationChips as GrammarChip with fidelity | medium | S | `conviction-chips-calibration` |
| 7 | status, beliefs, gauntlets: swap page chips and dots for the kit chip | medium | S each | |
| 8 | good, surfaces, playground chips | low to medium | S | |
| 9 | Scan HUDs: last file `target-role-scan-hud.html` drops its 4 `--palette-*` props | low (internal) | XS | `scan-huds-migrate-to-tokens-css` |
| 10 | NFTT: label heuristics and contrast only, inside its own world | medium | S | `nftt-template-kintsugi-contrast-and-label-heuristics` |

Gate each step with `token_source_gate`, `artifact_wrap_lint`, `motion_policy_gate`, `card_gutter_check.mjs`, and Impeccable detect (waivers in `.impeccable/config.json`, scoped and reasoned). Add one Frustration Gate in step 2: a lint that fails any new page-local class matching `chip|badge|pill|led|dot` outside the kit.

## Open decisions (Zach)

1. "On request" evidence: new `held` tone, or neutral with tag ON REQUEST?
2. Two token sources (`_tokens.css` and `src/ui/tokens.ts`): emit both from one JSON (recommended), or keep them hand-synced?
3. Is the pocket material allowed outside dj.arcs.care for input controls on receipts?

## Evidence

Screenshots, live 2026-10-30, in `_ARTIFACTS/unified-ds-reconcile/` (`<surface>-1280.png`, `<surface>-375.png`): arcs-care-compass, proof, good, status, status-beliefs, playground, surfaces (local file, the host is admin-gated), nftt-index, nftt-post, brief, receipt.

Found while shooting: `/receipt/cmqbd3i3k000104lawptiz7x0` (the pinned example id in `src/app/page.tsx`) renders "Couldn't load this receipt / Receipt not found". The id is a brief id, and the receipt route does not resolve it. The receipt screenshot therefore shows the error state; a real receipt needs a valid receipt id.

Gate run: `python3 scripts/token_source_gate.py` on the ten HTML surfaces above: 10 PASS (8 kit, 2 NFTT).
