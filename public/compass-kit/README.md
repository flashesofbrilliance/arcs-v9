# ARCS Compass — UI Kit

A high-fidelity, click-through recreation of the **ARCS Field OS Compass** product
(`flashesofbrilliance/arcs-v9`). It reproduces the cockpit/instrument visual
language and the core decision flow as a fake, front-end-only prototype — no
backend, no real Claude pipeline. Open `index.html`.

## The flow
`Home` → `Question Compass` → `Receipt (result)` → `Cartography Brief`, plus
**tributaries** that loop a follow-up question back through the compass.

1. **Home** — marketing entry. Hero, an example Decision Receipt, "how it works".
2. **Question Compass** — the decision input: textarea, horizon, stakes, optional
   calibration (protection chips). Two starter examples seed the field.
3. **Receipt** — the result: terrain **weather bar**, **True North** conclusion,
   **NCI / coherence** instruments, **tributaries**, and expandable L0–L5 reasoning
   (Constitutional Court + advisors).
4. **Brief** — the cartography map: FATED decomposition, terrain paths, court, and a
   sticky conviction sidebar.

## Files
| File | Role |
|---|---|
| `index.html` | App shell — React state machine wiring the four screens + mock pipeline. |
| `primitives.jsx` | Tokens (`T`), `Wordmark`, `Label`, `Button`, `Badge`, `Card`, `Y_WEATHER`, helpers. Buttons/cards use the design-system **liquid-glass** treatment. |
| `mock.jsx` | `mockCompass(question)` → canned Receipt. Two scenarios (runway / hire). |
| `Home.jsx` | Marketing landing (recreates `src/app/page.tsx`). |
| `Compass.jsx` | The question form (`src/app/dashboard/page.tsx`, input half). |
| `Result.jsx` | The Receipt result view (`dashboard`, result half). |
| `Brief.jsx` | The two-column Cartography Brief. |

## Conventions
- **Inline styles only** — mirrors the product's no-CSS-framework rule.
- Components export to `window` (each Babel `<script>` is separately scoped).
- Tokens come from `T` in `primitives.jsx`, which mirrors the root
  `colors_and_type.css`. Fonts (Inter + JetBrains Mono) load via the kit's
  `<link>` to the root CSS.
- This is a **cosmetic recreation** — the mock returns fixed data; it does not
  reason. Swap `mockCompass` for a real `POST /api/compass` to wire it up.

## Not included (intentionally)
History list, magic-link auth, the live L0–L5 Claude pipeline, and the Observatory
replay layer — out of scope for a visual kit. The arcs.care marketing funnel is a
separate product and is documented in the root README, not recreated here.
