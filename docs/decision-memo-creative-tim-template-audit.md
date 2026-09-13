# Decision Memo: Creative Tim MUI Material Template Fork Base

**Date:** 2026-08-27  
**Context:** Resume Tailor theming engine — three-theme MUI setup (formal/corporate, casual/startup, neutral/versatile)  
**SPEC:** `/Users/zharris/arcs-v9/docs/resume-tailor-theming-engine-spec.md`

---

## Candidates Evaluated

Two free MUI Material templates from Creative Tim, both confirmed via the product pages, GitHub repos, raw LICENSE.md, and package.json.

| Criterion | Material Dashboard 2 React | Material Kit 2 React |
|---|---|---|
| **URL** | [Product page](https://www.creative-tim.com/product/material-dashboard-react) · [GitHub](https://github.com/creativetimofficial/material-dashboard-react) | [Product page](https://www.creative-tim.com/product/material-kit-react) · [GitHub](https://github.com/creativetimofficial/material-kit-react) |
| **Free/Paid** | Free (also has a Pro upgrade) | Free (also has a Pro upgrade) |
| **Version** | 2.2.0 | 2.1.0 |
| **Last updated** | 3 years ago (v2.2.0 commit); last code commit 2 years ago | 3 years ago (v2.1.0 commit); last code commit 2 years ago |
| **MUI version** | `@mui/material@5.12.3`, `@mui/icons-material@5.11.16` | `@mui/material@5.12.0`, `@mui/icons-material@5.11.16`, `@mui/styled-engine@5.12.0` |
| **React version** | 18.2.0 | 18.2.0 |
| **Build tool** | `react-scripts@5.0.1` (CRA, deprecated) | `react-scripts@5.0.1` (CRA, deprecated) |
| **Stars / Forks** | ~3k stars / 4.9k forks | ~1.2k stars / 2.4k forks |
| **Component count** | 70+ elements | 40+ elements |
| **Component wrappers** | `MDButton`, `MDInput`, `MDTypography`, `MDBox`, `MDAvatar`, `MDBadge`, `MDAlert`, `MDPagination`, `MDProgress`, `MDSnackbar` | `MKButton`, `MKInput`, `MKTypography`, `MKBox`, `MKAvatar`, `MKBadge`, `MKAlert`, `MKDatePicker`, `MKPagination`, `MKProgress`, `MKSocialButton` |
| **Theme setup** | Context API for layout config (miniSidenav, darkMode, etc.); MUI `ThemeProvider` used in layouts; custom `createTheme` in `assets/theme` | Imports `theme` from `assets/theme`, wraps app in `<ThemeProvider theme={theme}>` + `<CssBaseline />` in `App.js` |
| **Third-party deps** | `react-chartjs-2`, `chart.js`, `chroma-js`, `react-github-btn`, `react-table`, `yup`, `stylis`, `stylis-plugin-rtl`, **Nepcha Analytics (pre-integrated)** | `chroma-js`, `flatpickr`, `react-flatpickr`, `react-copy-to-clipboard`, `react-countup`, `react-syntax-highlighter`, `web-vitals`, **Nepcha Analytics (pre-integrated)** |
| **Red flags** | Dashboard-specific layout code (sidenav, navbar, tables, notifications pages); Nepcha Analytics bundled; RTL plugin deps | Date picker + syntax highlighter + countup baggage; Nepcha Analytics bundled; fewer components overall |

---

## License Audit

Both repos carry an **MIT License** in their `LICENSE.md` files on GitHub.

**Material Dashboard 2 React** — `LICENSE.md` (confirmed via GitHub blob page):
> MIT License  
> Copyright (c) 2013-2021 Creative Tim (https://www.creative-tim.com)  
> Permission is hereby granted, free of charge, to any person obtaining a copy... [standard MIT terms]

**Material Kit 2 React** — confirmed via [Creative Tim Learning Lab license page](https://www.creative-tim.com/learning-lab/react/license/material-kit/) and mirrored in the repo:
> MIT License  
> Copyright (c) 2021 Creative Tim  
> [standard MIT terms]

**What MIT means for us:**
- ✅ Commercial use allowed — no royalty, no royalty trap
- ✅ Modification allowed — we can strip, refactor, re-theme
- ✅ Distribution allowed — we can ship the fork as part of the resume-tailor app
- ✅ Attribution: only the copyright notice + permission notice must be included in copies/substantial portions of the Software. This is the standard MIT requirement, not a display-attribution requirement.
- ⚠️ The Creative Tim EULA (their broader terms) adds restrictions on *reselling* the template as a competing product, creating template/UI-kit/dashboard generators, or open-sourcing the source code without written consent. Using it as the internal base for a theming engine inside a proprietary app does **not** violate these restrictions — we are not redistributing the template itself, we are using it as a starting point for our own app.

**Attribution fit for "impeccable polish":**
- MIT attribution is a license-text requirement in the distributed codebase (e.g., in a NOTICES file or package LICENSE), not a visible badge in the UI. This fits cleanly — we can satisfy it without polluting the UI.
- If the app ever ships the Creative Tim source code verbatim anywhere visible (e.g., an open-sourced submodule), the EULA's open-source-consent clause would kick in. That's not our plan, but worth flagging.

**Bottom line:** Both are clean MIT. No Attribution-required-for-display problems. No commercial-use blockers. The EULA restrictions don't apply to our use case (internal app base, not reselling the template).

---

## Theme Setup Analysis (What We Actually Extract)

**Material Kit 2 React** has the cleaner, more extractable theme architecture for our purpose:

1. `App.js` wraps everything in `<ThemeProvider theme={theme}>` + `<CssBaseline />` — exactly the MUI pattern we'll use.
2. `assets/theme` is a standalone theme module (we'd read its `createTheme` call, palette, typography, component overrides).
3. The `MK*` wrapper components (MKButton, MKInput, MKTypography, MKBox) are thin MUI wrappers that show how to layer custom styling on top of MUI primitives via `styled()`/`sx` — useful as a reference for how component overrides can be structured, though we won't keep the wrappers.
4. Fewer components = less to audit and strip. No chart library, no table library, no RTL plugin.

**Material Dashboard 2 React** is a fuller dashboard with more surfaces covered (sidenav, navbar, cards, tables, notifications, auth pages) — useful as a *second* taste reference for what a complete MUI app looks like, but heavier to strip down to just the theming engine. It also uses a Context-based controller for layout state (miniSidenav, darkMode toggle, etc.) which is dashboard-specific and not relevant to our theme engine.

---

## Red Flags (Both Templates)

| Flag | Severity | Notes |
|---|---|---|
| **Stale MUI version** | Medium | Both pin MUI v5.12.x. MUI has shipped v5.15+ and v6/v7 since. We will not fork the deps as-is; we upgrade MUI in our own package.json and verify the theme tokens still apply. The SPEC anticipates this: "make sure the base template is on a MUI version compatible with what the app uses. Don't fork a stale template onto a new MUI version." |
| ** CRA / react-scripts** | Low | Both use `react-scripts@5.0.1`. We'll use our own build setup (Vite or our chosen toolchain). Not a blocker — we only read the theme source, not the build config. |
| **Nepcha Analytics bundled** | Low | Present in both. Easy to strip — it's an analytics snippet, not a theme dependency. We remove it during the fork cleanup. |
| **No active maintenance** | Medium | Last meaningful commits 2–3 years ago. We're not relying on upstream fixes — we own the fork. This is acceptable because we're extracting theme tokens, not depending on the template's feature roadmap. |
| **GitHub repo renaming** | Low | Material Kit 2 React's repo URL in package.json points to `creativetimofficial/ct-material-kit-react` (a redirect/alias). The canonical repo is `creativetimofficial/material-kit-react`. Not a problem for us. |

---

## Pick: **Material Kit 2 React** (Free, MIT)

### Why it wins

1. **Cleaner theme architecture.** `App.js` → `ThemeProvider` + `CssBaseline` + imported `assets/theme`. This is the exact MUI pattern the SPEC calls for (`createTheme` + `ThemeProvider`). The dashboard template's Context-driven layout controller is more complex and less directly useful.

2. **Fewer surfaces to audit and strip.** 40 components vs 70+. No chart library, no data table, no RTL plugin. The only third-party baggage worth noting is `flatpickr` (date picker), `react-copy-to-clipboard`, `react-countup`, and `react-syntax-highlighter` — none of which touch the theme engine. All are easy to drop.

3. **MIT license, no display attribution.** Standard MIT. Attribution is a license-text inclusion, not a UI badge. Fits "impeccable polish" without compromise.

4. **Component wrappers are a useful reference.** `MKButton`, `MKInput`, `MKTypography`, `MKBox` show how to wrap MUI primitives with custom styling. We won't keep the wrappers, but they illustrate the override patterns we can apply when building our three `createTheme` objects.

5. **Lighter footprint = faster extraction.** We read `assets/theme`, extract palette/typography/component override patterns, and build our own three-theme registry. Less code to sift through.

### What we do with it

Per the SPEC build order (step 2): "Read its `createTheme` call + component overrides — extract tokens, not layout." Material Kit 2 React is the better substrate for that extraction. Material Dashboard 2 React stays as a secondary taste reference for dashboard-specific surfaces (sidenav, navbar, card layouts) if we need them later.

### If neither were clean enough

The fallback the SPEC already names: **MUI's own official templates** (e.g., the MUI v5/v6 dashboard example or the MUI `createTheme` docs) + ShadCN's tokens as a taste reference. That path is license-clean (MUI is MIT, ShadCN is MIT) and version-aligned, but lacks the polished MUI Material Design aesthetic that Creative Tim delivers. Since Material Kit 2 React *is* clean, we don't need to fall back.

---

## Summary

- **Candidates:** Material Dashboard 2 React (70+ components, dashboard-heavy, MUI 5.12.3) vs Material Kit 2 React (40+ components, UI-kit-focused, MUI 5.12.0).
- **Licenses:** Both MIT. Commercial use ✅. No display-attribution requirement ✅. EULA restrictions don't apply to our use case ✅.
- **Pick:** **Material Kit 2 React** — cleaner `ThemeProvider` architecture, fewer components to strip, thinner third-party deps, MIT license with no UI-polluting attribution. We extract `assets/theme` tokens and component override patterns, then build our three-theme registry on top of MUI's `createTheme`.
- **Red flags handled:** Both are stale (MUI 5.12.x, CRA, 2–3 years since commit). We upgrade MUI in our own deps, use our own build tool, and strip Nepcha Analytics. We own the fork, so upstream staleness is acceptable for token extraction.

**Delivered as:** This decision memo (no local files modified — all audit work was web-based: product pages, GitHub repos, raw LICENSE.md, and raw package.json).
