# partials/ -- single source of truth for the counterpart-forge artifact family

These CSS/JS fragments are the reusable atoms/molecules extracted from the live Yuri suite
(`public/yuri{,-recoil,-codex,-demo}.html`). `scripts/forge_counterpart.py` reads them, substitutes
`{{PLACEHOLDER}}` tokens, and inlines them into the four generated surfaces. Editing a partial here
changes every counterpart's family on the next `forge` run. Inline-styles-only is honored: nothing
here ships as an external stylesheet; it all lands inside each page's single `<style>`/`<script>`.

| File | Role | Surfaces |
|------|------|----------|
| `tokens.css` | ARCS dark-cockpit `:root` tokens (superset incl `--steel`) | all |
| `base.css` | header, cards, `.said` speaker quote, tables, lists, sub-nav | all |
| `gate.css` / `gate.js` | pw-gate overlay (`{{GATE_KEY}}`, `{{GATE_PW}}`) | recoil, codex, demo |
| `scrollspy.js` | IntersectionObserver sub-nav highlight | recoil, codex |
| `codex.css` | headline+lede+`<details>` progressive disclosure, altitude cards | codex |
| `present.css` / `present.js` | presentation mode (keyboard nav, G=go deeper) | codex |
| `ledger.css` / `ledger.js` | two-band inference ledger, confidence meter, conviction chip, belief timeline, JSON export (`{{EXPORT_FILE}}`) | demo |
| `dwell.js` | section-dwell -> Vercel custom events | all |

## The forge SSOT

One JSON per counterpart: `runtime/recoil/generated/<name>-forge.json`. It is the synthesis of the two
seeds (enriched-profile scan + call transcript) into the single record all four surfaces render from.
Schema is documented in `scripts/forge_counterpart.py` (`FORGE_SCHEMA_DOC`). `kleban-forge.json` is the
worked example / regression fixture.

### Non-negotiables (blueprint + project rules)
- ARCS dark-cockpit tokens, inline styles only, **zero em-dashes** anywhere in rendered output.
- pw-gate = counterpart first name; `noindex` on every surface.
- The fence: show shape + value, withhold the transform. `meta.fence` (`tight|standard|loose`) dials it.
- Role-archetypes only for real orgs; never fabricate interiority about named people.
- Attribution: `said[].speaker` is `zach` (cyan) or `counterpart` (green). Never mislabel.
- Deterministic SSOT -> render; output is JSON-exportable (demo surface).
- One deploy per surface, from the **main** worktree only (cost discipline).
