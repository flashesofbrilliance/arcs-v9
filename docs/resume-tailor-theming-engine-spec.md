# Resume Tailor — Frontend Theming Engine

> **Status:** SPECCED
> **Decision:** MUI official base + one Creative Tim free MUI template as taste reference.
> **Goal:** three polished themes (formal/corporate, casual/startup, neutral/versatile) + theme switcher + inference hook, wired through MUI's `createTheme` + `ThemeProvider`.

---

## Why this base

| Criterion | How it clears |
|---|---|
| **(A) Commercial licensing** | MUI is MIT (free commercial, no attribution). Creative Tim free templates are free commercial use with attribution — read the specific template's license file; attribution is the main thing to check. |
| **(B) Well-rated/reviewed** | MUI official templates are version-aligned and maintained. Creative Tim free templates have user base + GitHub stars + track record. Both are reasonable signals. |
| **(C) Security / injection** | Static source, not binaries. Fork the source, audit dependencies, strip anything not needed, own the build. "Prompt injection" is not the right frame for a frontend theme — the real diligence is dependency audit + owning the chain. |
| **(D) Theming engine extensibility** | MUI's `createTheme` + `ThemeProvider` + component overrides are the extensibility layer. Official templates use them correctly. Creative Tim uses them but is a product, not an engine — we extract tokens and build the engine on top of MUI's system. |

**ShadCN/Tailwind was considered** — it clears A/B/D well and the owned-source extensibility model is strong, but the user said MUI theming options, so we're on MUI. ShadCN's design tokens serve as a taste reference only.

---

## The three themes

Each is a full `createTheme({...})` — palette, typography, spacing, shape, shadows, and component overrides for the surfaces we use. Not color swaps.

### Formal (corporate)
- **Register:** trustworthy, restrained, precise, serious
- **Palette:** deep slate/navy/charcoal base; one disciplined accent (muted blue or restrained gold); cool-toned neutrals; high contrast text; quiet surfaces
- **Typography:** refined pairing — strong sans for body, distinguished heading treatment; tight, authoritative hierarchy
- **Spacing:** structured, purposeful; less whitespace-as-decor, more whitespace-as-grid
- **Shape:** subtle radii (4-6px cards, 2-4px buttons); edges read as precise
- **Shadows:** quiet, flat or very subtle depth; surfaces read as structured planes
- **Motion:** minimal, deliberate; short transitions, nothing bouncy

### Casual (startup)
- **Register:** energetic, approachable, modern, warm
- **Palette:** off-white/cream or lighter friendly surface; a confident accent (coral, teal, or amber); warm neutrals; approachable contrast
- **Typography:** single confident sans; slightly relaxed hierarchy; contemporary display weight for headers that reads as modern, not corporate
- **Spacing:** generous whitespace; airier; components breathe
- **Shape:** softer radii (8-12px cards, 8px+ buttons); edges read as approachable
- **Shadows:** a little more depth or soft glow where it adds warmth, not just dimension
- **Motion:** a little more life; slightly longer easing; responsive hover states; nothing cartoonish

### Neutral (versatile)
- **Register:** clean, contemporary, doesn't over-commit to a register
- **Palette:** balanced neutrals; a moderate accent; leans neither strongly formal nor casual
- **Typography:** clean, contemporary sans; balanced hierarchy
- **Spacing:** balanced; not too tight, not too airy
- **Shape:** moderate radii; middle register
- **Shadows:** moderate depth; clean without being flat or dramatic
- **Motion:** balanced; purposeful with a little life

---

## Implementation

### Surfaces to theme (the ones we actually use)
- `MuiButton` — variants, colors, radius, focus state
- `MuiCard` — elevation, radius, padding
- `MuiTextField` / `MuiInput` — border, radius, focus style
- `MuiChip` — palette, radius
- `MuiTypography` — scale + font family (via theme.typography, not per-instance sx)
- Any other surface we end up using — add to this list as we go

### Architecture
```
ThemeRegistry
  - formal : createTheme({...})
  - casual : createTheme({...})
  - neutral: createTheme({...})
  ↓
User picks: Formal | Casual | Neutral  (three buttons, explicit override)
  ↓
Inference hook: soft signal from job posting → default theme
  - formal signals: finance/legal/healthcare/enterprise/consulting/regulated/Fortune 500-ish → Formal
  - casual signals: early-stage/"team of 5"/product-led/consumer/creative/"move fast" → Casual
  - ambiguous/mixed → Neutral
  ↓
ThemeProvider theme={selectedTheme}  — wraps the whole app, all components consume tokens
  ↓
No hard-coded values in components — everything comes from theme.typography / palette / spacing / shape
```

### Scope discipline
- Three preset themes, no theme editor, no live color picker.
- User can override the inference via the picker; inference is the intelligent default, not the only path.
- Persist selection in local state / localStorage (web) or app state (Tauri desktop).
- Only ship MUI components we use — tree-shake the rest.

---

## Taste references (not code sources)

- **ShadCN's default tokens** — slate neutrals, consistent radius, clean type scale, subtle shadows. Read as a taste reference for what "coherent, polished" looks like; translate the *intent* into MUI theme tokens.
- **Dribbble** — open a few material-ui-dashboard shots to see "polished MUI" in the wild. Visual reference only; do not fork as code.

---

## Build order

1. Pick one concrete Creative Tim free MUI template as the fork base (audit license on the specific template).
2. Read its `createTheme` call + component overrides — extract tokens, not layout.
3. Build the three `createTheme` objects as full theme definitions.
4. Wire ThemeProvider at the app root.
5. Add the theme switcher (three buttons + inference hook).
6. Polish pass — audit each theme against its register. Does formal read formal? Does casual read casual? Fix dissonance by hand.
7. Tree-shake unused MUI components.

---

## Notes

- Attribution: if the Creative Tim free template requires attribution, check whether it's displayable-removable in your app context. If not removable in a way that fits "impeccable polish," either pick a different template or surface the attribution cleanly.
- Version alignment: make sure the base template is on a MUI version compatible with what the app uses. Don't fork a stale template onto a new MUI version.
- Do not build a theme editor. Three presets + picker + inference. That's the scope.
