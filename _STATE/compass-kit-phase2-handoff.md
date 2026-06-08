# Handoff — Compass UI Kit → Real App (Phase 2)

> **For the next session (recommended: fresh).** Everything below is on `main`.
> Phase 1 (live static preview) is shipped. Phase 2 is the real port + DS reconcile.
> Pickup: `/handoff-pickup`, then read this file top to bottom.

---

## Mission

Promote the **Compass UI kit** (cockpit/instrument redesign) into the real
arcs-v9 Next 16 app, replacing the mock pipeline with the live `/api/compass`.

**Target = arcs-v9 = `app.arcs.care`.** This is the full ARCS app, NOT the
`arcs.care` marketing site (separate repo, out of scope; the kit's own README
says it does not recreate it). Confirmed by the kit README.

Three routes get rebuilt on the kit:
| Route | File | Kit screen |
|---|---|---|
| `/` | `src/app/page.tsx` | `Home.jsx` |
| `/dashboard` | `src/app/dashboard/page.tsx` | `Compass.jsx` (input) + `Result.jsx` (result) |
| `/brief/[receiptId]` | `src/app/brief/[receiptId]/page.tsx` | `Brief.jsx` |

---

## Current state (Phase 1, done)

- **Live preview:** `app.arcs.care/compass-kit` — full click-through on the MOCK
  pipeline (Home → Compass → Receipt → Brief). Static, served like the Observatory.
  Zero changes to the working `/dashboard`.
- **Kit source:** `public/compass-kit/` — `primitives.jsx`, `atoms.jsx`, `mock.jsx`,
  `Home.jsx`, `Compass.jsx`, `Result.jsx`, `Brief.jsx`, `index.html`,
  `colors_and_type.css`, `README.md`.
- Route wired via `next.config.ts` rewrite `/compass-kit → /compass-kit/index.html`.

The kit is CDN-React + Babel-standalone + `window` globals (a prototype harness).
Phase 2 converts it to typed Next 16 TSX. **Do not ship the static kit as the
real app** — it's the design reference.

---

## Design-system reconciliation (the crux)

`src/ui/` ALREADY HAS a typed design system from ADR-009/011:
- `tokens.ts` — exports `surface, border, text, signal, font, radius, space, yGateColor`
- `Badge.tsx` (`register`), `Button.tsx` (`variant`), `Card.tsx` (`accent`, `padding`, `CardHeader`)

The kit's `primitives.jsx` `T` (flat token object) + `Button`/`Badge`/`Card` are the
**next evolution** of those — richer (Button gains `outline-cyan|green|gold|danger|ghost`
+ `glyph` + `sm|md|lg`; Card gains glass/underlit-LED finish; new `Gauge`).

**Decision the next session must make first (ADR-worthy):**
reconcile, don't fork. Options:
- **(A, recommended)** Extend the existing `src/ui/Button|Badge|Card` to the kit's
  richer API; add the net-new atoms as new files. One DS, evolved.
- (B) Namespace the kit under `src/ui/compass-kit/*` as a parallel set. Faster but
  forks the DS — only if (A) proves too disruptive to current consumers.

Import rule (ADR-011): direct imports `@/ui/Button`, **no barrel**.
Token rule: reuse `tokens.ts` (the kit `T` palette already equals it — see
`primitives.jsx` colors === `tokens.ts` signal/surface). Do NOT introduce a 2nd palette.

### Atom inventory to port (`primitives.jsx` + `atoms.jsx`)
Primitives: `Wordmark, Label, Button, Badge, Card, Gauge` + helpers `Y_WEATHER,
RES_STYLE, nciColor, signalGlow`.
Atoms: `SectionLabel, Rule, Field, Picker, Tabs, SegmentedSlider, ChipToggle,
WeatherBar, TrueNorthPanel, TributaryTile, Spinner, ProgressBar, StepProgress`.

Every component using hooks/handlers (Button, Field, Picker, Tabs,
SegmentedSlider, ChipToggle, TributaryTile, Spinner-host) → **`"use client"`**.

---

## Field mapping: kit `result` ↔ real `POST /api/compass`

Live response (verified `src/app/api/compass/route.ts:245`):
```
{ ok, receipt_id, session_id, session_version,
  decision_mode, door_class, y_state, y_conviction, render_resolution, nci_delta,
  ...parsed }     // parsed = the model JSON below
```
`parsed`: `true_north, why[], nci_score, coherence_pct, is_satoshi,
meta.macro_tags[], tributaries[], reasoning{ court[], court_verdict, advisors,
fated, nci_breakdown, paths[] }`.

| Kit reads | Real source | Action |
|---|---|---|
| `result.true_north / why / nci_score / coherence_pct / is_satoshi` | parsed.* | ✅ direct |
| `result.decision_mode / door_class / y_state / render_resolution / nci_delta` | top-level | ✅ direct |
| `result.reasoning.court[{name,verdict,detail}]` | parsed.reasoning.court | ✅ direct (verdict `PASS\|TENSION\|BLOCK`; kit handles PASS/TENSION/else) |
| `result.reasoning.court_verdict / advisors / fated / paths` | parsed.reasoning.* | ✅ direct |
| `result.tributaries[{type,label,prompt}]` | parsed.tributaries | ✅ **exact match** (types meta/challenge/adjacent) |
| `result.macro_tags` | parsed.**meta**.macro_tags | ⚠️ **remap** `result.meta?.macro_tags ?? []` |
| `result.question` | NOT echoed by API | ⚠️ keep the input question in client state; attach it |
| `result.receipt_id` | top-level `receipt_id` | ✅ (used for `/brief/${receipt_id}` + save) |

So: **2 remaps total** (`macro_tags`, `question`). Everything else is 1:1.

Mock-only fields not in real output (degrade gracefully — guard with `?.`):
`paths[].tag` exists in both; `advisors.bayesian_*` exists in both. Nothing missing.

---

## Build plan (suggested order)

1. **DS reconcile (ADR first)** — decide (A) vs (B) above; land tokens helpers
   (`Y_WEATHER, RES_STYLE, nciColor, signalGlow`) into `src/ui/tokens.ts`.
2. **Port atoms** → `src/ui/*.tsx` (typed, `"use client"` where needed). Build a
   throwaway `/compass-kit-tsx` gallery route to eyeball parity vs the static preview.
3. **`/dashboard`** — the big one. Compass form (Field/Picker/SegmentedSlider/
   ChipToggle) → on submit `fetch('/api/compass', { question, horizon, stakes,
   protecting })`; render `Result` on response. Preserve existing PrepSession
   (`/api/prep`), receipt save, History, auth gating — restyle, don't remove.
   The kit fakes L0–L5 progress with `setInterval`; real call is one request —
   keep faux `StepProgress` during the await (or wire SSE later).
3b. Keep the **ReceiptSavePrompt / soft-auth nudge** (PLG-critical, AGENTS backlog).
4. **`/`** (Home) — static marketing; buttons → `router.push('/dashboard')`.
5. **`/brief/[receiptId]`** — already fetches `/api/brief/[receiptId]`; map its
   `receipt` + `brief` data onto the kit `Brief` layout (FATED / paths / court /
   sticky conviction sidebar). NOTE: `/brief` index now redirects to `/dashboard`
   (added this session); the real route is `/brief/[receiptId]`.
6. **Promote**: preview-deploy the branch first, parity-check vs `/compass-kit`,
   then merge to `main`. Consider keeping `/compass-kit` as a living style reference
   (or delete once parity is reached).

---

## Conventions / gotchas (Next 16 + this repo)

- Inline styles only — no Tailwind/CSS modules/className-driven styling.
- `npx next build` for typecheck (NOT `tsc --noEmit` — TS5090 false positive).
- Next 16: middleware is `proxy.ts`; there is no `next lint`.
- JSON arrays persist as TEXT (SQLite dev) — `JSON.stringify`/`parse` at the boundary.
- Commit style: `type(scope): imperative [NCI:XX]`.
- **Branch policy:** develop on your own feature branch; preview-deploy; merge to
  `main` only when parity is confirmed (don't destabilize the live `/dashboard`).
- Prod builds from `main` are green; `target:null` preview builds ERROR on missing
  Preview `DATABASE_URL` (known, harmless — see snapshot open items).

---

## Meta-prompts (paste-ready)

**Kickoff (start the fresh session with this):**
> Read `_STATE/compass-kit-phase2-handoff.md`. We're promoting the Compass UI kit
> (`public/compass-kit/`, live preview at app.arcs.care/compass-kit) into the real
> arcs-v9 app: `/`, `/dashboard`, `/brief/[receiptId]`, swapping mock → `/api/compass`.
> First task: write an ADR deciding DS reconciliation option A vs B, then port the
> atoms to `src/ui/`. Do NOT touch the live `/dashboard` until parity is proven on a
> branch preview.

**Per-component conversion:**
> Convert `<Atom>` from `public/compass-kit/{primitives,atoms}.jsx` into a typed
> `src/ui/<Atom>.tsx`: inline styles verbatim, `"use client"` if it uses hooks,
> props as a typed interface, tokens from `@/ui/tokens`. Keep the visual output
> byte-identical to the kit. No barrel import.

**API wiring (`/dashboard`):**
> Wire the Compass form to the real pipeline: POST `/api/compass` with
> `{ question, horizon, stakes, protecting }`, keep the question in client state,
> render `Result` on the response. Apply the 2 field remaps from the handoff
> (`macro_tags` ← `meta.macro_tags`; attach `question`). Preserve PrepSession,
> receipt save, History, and auth gating — restyle only.

**Parity QA:**
> Open `/compass-kit` (mock) and the new TSX route side by side. Diff spacing,
> color, glow, hover, and the four screens' layouts. List every visual drift and
> fix to match the kit, which is the source of truth.

**Quality gate (before merge):**
> Run `/ultrareview` on the diff, then `/dual-bar-raiser` to classify
> (Implementer vs Architect). Confirm `npx next build` is clean and the branch
> preview renders all four screens before merging to `main`.

**Design-system note (if extending the DS):**
> This continues the ADR-009/011 design system in `src/ui/`. Reconcile, don't fork:
> extend existing `Button/Badge/Card` to the kit's richer API; add net-new atoms as
> new files. One palette (`tokens.ts`), direct imports, no barrel. Revisit-trigger:
> ≥8 components → reconsider a barrel (ADR-011).

---

## Verification checklist (phase 2 done when)

- [ ] ADR for DS reconciliation committed
- [ ] All kit atoms exist as typed `src/ui/*.tsx`, parity-checked vs preview
- [ ] `/`, `/dashboard`, `/brief/[receiptId]` rebuilt on the kit
- [ ] `mockCompass` → `fetch('/api/compass')`; 2 remaps applied; real receipt persists
- [ ] PrepSession, History, auth gate, receipt-save nudge all preserved
- [ ] `npx next build` clean; branch preview renders 4 screens
- [ ] Merged to `main`; `app.arcs.care` shows the new compass end-to-end
