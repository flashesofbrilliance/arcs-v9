# Memo: Best Official MUI Template/Base for Theming Engine Reference

**Date:** 2026-08-27  
**From:** subagent research  
**Re:** correctness + usage-reference base for resume-tailor three-theme engine

---

## Best Candidate

**MUI official free templates — shared theme infrastructure (`AppTheme` + `themePrimitives` + customization modules)**

- **URL:** https://github.com/mui/material-ui/tree/master/docs/data/material/getting-started/templates/
- **Free/Paid:** Free (part of the MUI open-source monorepo)
- **License:** MIT — same as MUI itself. No attribution requirement beyond the standard MIT notice.

This is NOT one template but the **shared theme layer** all official MUI free templates are built on: `AppTheme.tsx`, `themePrimitives.ts`, and the five categorized customization modules (inputs, dataDisplay, feedback, navigation, surfaces). Every official free template (Dashboard, Marketing Page, Checkout, Sign-in, Sign-up, Blog, CRUD Dashboard) uses this exact same `AppTheme` wrapper. It is the single most authoritative source for correct MUI theming idiom available.

---

## Theme Setup (what `AppTheme` actually does)

`AppTheme.tsx` wraps children in:

```ts
const theme = createTheme({
  cssVariables: {
    colorSchemeSelector: 'data-mui-color-scheme',
    cssVarPrefix: 'template',
  },
  colorSchemes,          // light + dark via MUI v6 colorSchemes API
  typography,            // full type scale, Inter font
  shadows,               // custom shadows, CSS-variable-backed
  shape,                 // borderRadius: 8
  components: {
    ...inputsCustomizations,
    ...dataDisplayCustomizations,
    ...feedbackCustomizations,
    ...navigationCustomizations,
    ...surfacesCustomizations,
    ...themeComponents,   // template-specific overrides injected here
  },
});
```

**`themePrimitives.ts`** supplies:
- Color palettes as HSL tokens: `brand` (blue), `gray`, `green`, `orange`, `red` — each with 50–900 range
- `getDesignTokens(mode)` — full palette definition for light/dark including `primary`, `info`, `warning`, `error`, `success`, `grey`, `divider`, `background`, `text`, `action`
- `colorSchemes` object — separate light/dark palette trees
- `typography` — h1–h6, subtitle1/2, body1/2, caption; all via `pxToRem`; fontFamily `Inter, sans-serif`
- `shape: { borderRadius: 8 }`
- `shadows` — custom array with CSS variable `var(--template-palette-baseShadow)` as index 1

**Customization modules** show the canonical modern MUI component-override pattern:
- Typed as `Components<Theme>`
- `styleOverrides` with variant arrays (e.g. `MuiButton` has 7 variants: contained primary, contained secondary, outlined, outlined secondary, text, text secondary, small/medium size)
- `defaultProps` for things like `disableElevation`, `disableRipple`, `IconComponent`
- `theme.vars` access for CSS-variable mode: `(theme.vars || theme).palette.text.primary`
- `theme.applyStyles('dark', {...})` for dark-mode overrides inline
- `alpha()` from `@mui/material/styles` for transparent overlays

---

## Surfaces/Components Covered

The customization modules touch every surface in our spec:

| Spec surface | Covered by |
|---|---|
| `MuiButton` | `inputsCustomizations` — full variant × size matrix, no boxShadow, borderRadius from shape, textTransform: none |
| `MuiCard` | `surfacesCustomizations` — padding 16, gap 16, border + divider, no shadow, borderRadius from shape, dark mode bg |
| `MuiTextField` / `MuiOutlinedInput` | `inputsCustomizations` — border, radius, focus ring (3px outline), hover/focus transitions, notchedOutline: border none |
| `MuiChip` | `dataDisplayCustomizations` — border, borderRadius 999px, color variants (default/success/error), small/medium sizes |
| `MuiTypography` | via `typography` in `themePrimitives` — full scale, font family, weights; not per-instance sx |
| Plus: `MuiIconButton`, `MuiToggleButton`, `MuiCheckbox`, `MuiMenu`, `MuiSelect`, `MuiLink`, `MuiDrawer`, `MuiTabs`, `MuiTab`, `MuiDialog`, `MuiAlert`, `MuiLinearProgress`, `MuiAccordion` | all have overrides |

---

## Why It's the Best Correctness Reference

1. **Authoritative — maintained by the MUI team in the monorepo.** This isn't a third-party interpretation; it's the reference implementation the MUI docs team ships. When in doubt about correct idiom, this is ground truth.

2. **Version-aligned.** Lives on `master` of `mui/material-ui`. Tracks MUI v6 → v9 as the repo moves. No risk of forking a stale template onto a newer MUI version.

3. **Shows the modern MUI v6/v9 theming surface in full.** CSS variables (`cssVariables`), `colorSchemes` for light/dark, `theme.vars` access, `theme.applyStyles('dark', ...)`, variant-array syntax in `styleOverrides`, module augmentation for custom variants (`PaperPropsVariantOverrides`). A theming engine built on these patterns will be future-proof.

4. **Organized by component category, not by template.** Because the same `AppTheme` backs Dashboard, Marketing Page, Checkout, Sign-in, etc., the customization modules are engineered to be reusable across very different surfaces — exactly the property a theming engine needs.

5. **Light + dark from the start.** `colorSchemes` + `getDesignTokens(mode)` + `theme.applyStyles('dark', ...)` everywhere. Our three themes may not need dark mode initially, but the reference shows how to structure it so adding dark later doesn't require a rewrite.

6. **Token-first, not component-first.** `themePrimitives.ts` defines color as HSL ranges and passes them through `getDesignTokens` → `createTheme`. This is the exact pattern our engine should follow: define tokens, compose themes from tokens, override components against those tokens.

7. **Dashboard is a clean usage reference.** The Dashboard template (https://github.com/mui/material-ui/tree/master/docs/data/material/getting-started/templates/dashboard/) uses `AppTheme` + `CssBaseline enableColorScheme` + MUI X Data Grid / Charts customizations. It's the most feature-rich official free template and shows how to layer template-specific overrides (`themeComponents`) on top of the shared theme.

8. **Marketing Page is a clean landing reference.** Hero, Features, Pricing, Testimonials, FAQ, Footer — all themed through the same `AppTheme`. Good reference for how consumer-facing surfaces consume the same tokens as admin surfaces.

---

## Also Note: Free Store Templates (for taste, not correctness)

The MUI Store free section has several MIT/free templates worth awareness:

| Template | License | Notes |
|---|---|---|
| **Devias Kit Free** | MIT (Devias) | React Admin Dashboard, 5.5k+ GitHub stars, MUI v5/v7-tracked |
| **Mantis Free** | MIT (CodedThemes) | React Material UI Dashboard, clean admin layout |
| **Berry Free** | MIT (codedthemes) | React Material Admin Dashboard |
| **Modernize Next.js Free** | Free | Next.js + MUI admin |
| **Minimal Free** | Free | React Admin Dashboard |
| **Aurora Free** | Free | Admin Dashboard and Web App |
| **SaasAble Free** | Free | Multipurpose UI Kit + Dashboard |
| **Paperbase** | Free | Admin & Dashboard |

These are fine as **visual taste references** but are NOT the correctness base. They are third-party products; their theme setup may use older MUI patterns, be version-skewed, or have their own opinions layered on top. The MUI official `AppTheme` infrastructure is the reference for *how MUI intends you to write a theme*.

---

## Recommendation for Our Engine

1. **Correctness base:** Mirror the `AppTheme` architecture. Build our three themes as `createTheme({ cssVariables, colorSchemes, typography, shadows, shape, components })` — same shape, same patterns (variant arrays, `theme.applyStyles`, `theme.vars` access, `alpha()` for transparency).

2. **Token structure:** Follow `themePrimitives.ts` — define per-theme color palettes as HSL ranges (or hex ranges), pass through a `getDesignTokens(mode)`-style function, feed into `createTheme`. Each of our three themes becomes a different token set feeding the same `createTheme` structure.

3. **Component overrides:** Reuse the categorization from the MUI official modules (inputs, dataDisplay, feedback, navigation, surfaces) and add our own per-theme variants. The `surfacesCustomizations` module is especially close to what we need — `MuiCard`, `MuiPaper`, `MuiAccordion` with border/radius/background treatment.

4. **Dashboard as usage reference** for the admin-side surfaces (data grid, sidebar, navigation). **Marketing Page as usage reference** for the consumer-facing surfaces (hero, features, testimonials).

5. **Fork base for the app shell** (separate decision per SPEC): still pick one Creative Tim free MUI template for layout/fork, but extract tokens from it — don't use its theme setup as the correctness reference.

---

*End of memo.*
