# Curated MUI Bases + ShadCN-as-Design-Token-Source

> **Context:** resume-tailor Tauri app. MUI is the component runtime.
> Goal: three themes (formal/corporate, casual/startup, neutral/versatile),
> forked from a polished open-source base, polished with impeccable.
> Magic Patterns MCP available as an accelerator for generating theme artifacts.

---

## 1. ShadCN vs MUI — different paradigms, don't mix casually

**ShadCN is not a component library.** It is copy/paste components built on
Radix UI primitives + Tailwind CSS. You own the code in your project. The design
language is Tailwind tokens (colors in `globals.css`, spacing via Tailwind scale,
radius via `--radius-*`).

**MUI is a component library.** You install it, import components, and theme it
via `createTheme()` + `ThemeProvider`. The design language is MUI's theme tokens
(palette, typography, spacing, shape, shadows, components overrides via `sx` prop
or `components` key in the theme).

**What this means for your project:**

If the app shell is MUI (which it is, per the earlier spec), then:
- ShadCN is **not your component runtime** — you don't install shadcn/ui and
  use its Button/Card/Input in an MUI app.
- ShadCN **can be your design-token inspiration source.** ShadCN's default theme
  has a coherent, polished set of tokens (slate neutrals, a snappy radius, a clean
  type scale, good default shadows). You can read those tokens and translate the
  *intent* into MUI's `createTheme()` — not the code, the taste.

If you were building a Tailwind app instead of MUI, ShadCN would be the component
runtime and you'd theme it by editing `globals.css` + component files directly.

**Bottom line:** ShadCN informs the *design taste*. MUI is the *component runtime*.
They're compatible at the level of "what should this look like," not at the level
of "import this component."

---

## 2. Curated MUI bases worth forking + polishing

These are real, existing, open-source MUI themes/templates you can fork, audit,
and refine into your three themes. Each is a starting point for the *taste*, not
the final product.

### A. MUI's own starter templates (official)

- **Where:** `mui.com` → Templates section; GitHub repos under the MUI org; the
  `create-mui-app` ecosystem has starter templates.
- **What you get:** Official, well-maintained, up-to-date with the current MUI
  version. Clean component usage, correct ThemeProvider wiring, no stale patterns.
- **Best for:** The safe starting point. You inherit correct MUI idioms and don't
  fight a stale template. The default look is Material-y; your polish job is to
  move it away from default-Material into your register (formal/casual/neutral).
- **Polish work:** Typography pairing, color system (move off default Material
  primary/shade), spacing rhythm, component overrides for your surfaces (Button,
  Card, TextField, Chip).

### B. Creative Tim — MUI Material templates (free + paid)

- **Where:** `creative-tim.com` → MUI Material section; GitHub mirrors of their
  free templates.
- **What you get:** Polished dashboard/admin templates with a more designed feel
  than raw MUI defaults. Several free options; paid ones are more complete.
- **Best for:** A more finished starting point than official templates. The free
  ones are worth auditing as a taste reference even if you don't fork them
  directly.
- **Polish work:** Audit against your three registers. Creative Tim templates tend
  toward a specific "dashboard" register — you'd extract the type/color/spacing
  system and re-shape it for formal/casual/neutral rather than keep the dashboard
  voice.

### C. Community MUI dashboard/admin templates on GitHub

- **Where:** Search GitHub for `mui-dashboard`, `mui-admin-template`,
  `mui-theme-preset`, `material-ui-template`. Sort by stars / recent activity.
- **What you get:** A range of community-built starts. Quality varies; some are
  genuinely polished, some are generic. The good ones give you a coherent type
  scale, color system, and component overlay pattern you can fork.
- **Best for:** Finding a base whose *taste* is closest to what you want, then
  fork + polish. The value is in the design tokens and component override patterns,
  not the template's specific layout.
- **Polish work:** Read the theme config first (the `createTheme` call, the color
  definitions, the typography). Audit it. Keep what's coherent. Cut what's generic.
  Re-shape for your three registers.

### D. Contrast Design System (MUI-based, by Creative Tim)

- **Where:** Creative Tim → Contrast Design System; has a MUI variant.
- **What you get:** A more opinionated, design-system-flavored MUI surface. More
  "this is a system" than "this is a Material template."
- **Best for:** If you want a base that already reads as a design system rather than
  a Material template. The register is its own thing; you'd re-shape it.

---

## 3. ShadCN's actual contribution here (design-token source)

If you look at ShadCN's default theme tokens, these are the pieces worth borrowing
*as intent* and translating into MUI:

| ShadCN dimension | What it gets right | MUI translation |
|---|---|---|
| **Neutrals** | Slate-based, coherent scale from bg to border to muted text | Build a slate/neutral scale in `palette.common` / `palette.grey` that reads clean, not default-Material-grey |
| **Radius** | Consistent `--radius` token, snappy but not bubbly | `shape.borderRadius` tuned to your register (subtle for formal, softer for casual) |
| **Type scale** | Clean, modern, readable hierarchy | `typography` in `createTheme` — pick your pairing, tune the scale, make headings read as headings |
| **Shadows** | Subtle, purposeful, not default-Material-deep | `shadows` array tuned per register — quiet for formal, a little more life for casual |
| **Component defaults** | Button, Card, Input each have a considered default | Component overrides in the theme's `components` key — your surfaces look right without `sx` everywhere |

The move: inspect ShadCN's tokens as a *taste reference*, then express the same
intent in MUI theme tokens. Don't copy the code; copy the taste.

---

## 4. How Magic Patterns MCP accelerates the fork + polish

Given Magic Patterns MCP is available, the workflow for the three themes is:

1. **Pick the base.** One MUI template/theme whose tokens you'll fork. Read its
   `createTheme` call and component overrides.
2. **Define the three theme objects.** `createTheme({...})` for formal, casual,
   neutral. Each is a full object — palette, typography, spacing, shape, shadows,
   component overrides for the surfaces you use (Button, Card, TextField, Chip,
   maybe a few more). Not color swaps.
3. **Use Magic Patterns to generate/refine.** Instead of hand-tuning every token by
   feel, feed Magic Patterns the base theme + the register brief for each theme
   (formal = trustworthy/restrained/precise; casual = energetic/approachable/modern;
   neutral = clean/versatile). Ask it to produce the three `createTheme` objects
   with coherent tokens. Then audit the output — correct anything that reads wrong.
4. **Polish pass.** The output from Magic Patterns is a strong first draft, not the
   final word. Audit each theme against its register. Does formal actually read
   formal? Does casual actually read casual? Fix the dissonance by hand — that's
   the "impeccable" part Magic Patterns doesn't fully own.
5. **Wire ThemeProvider.** Route the three themes through a ThemeRegistry + picker,
   with inference from the job posting as the intelligent default.

Magic Patterns is the accelerator for steps 2-3. The audit + polish (step 4) is
still human judgment, because "does this read as formal?" is a register judgement,
not a token problem.

---

## 5. Recommendation — given your actual goal

**Start from an MUI base, not ShadCN.** ShadCN is the wrong runtime for an MUI
app. Use ShadCN only as a design-token taste reference.

**The base:** I'd start from one of the cleaner community MUI templates or an
official MUI starter — the one whose type scale and color system is closest to a
register you can imagine refining into formal/casual/neutral. Don't over-index on
which one; the polish work is where the themes actually get made. The base is just
the starting tokens.

**The three themes are the product of the polish, not the base.** The base gives
you a coherent starting point. Your taste (informed by ShadCN's defaults, refined
by Magic Patterns, audited by hand) produces the three registers. That's the
"fork and polish with impeccable" move.

**Don't build a theme editor.** Three preset themes, a picker, inference as default
override. That's the scope. A live theme builder is scope creep and not what a
$25 one-off needs.

**What I'd do next, concretely:**

1. Pick one MUI base (official starter or a clean community template).
2. Read its `createTheme` + component overrides.
3. Spin Magic Patterns to produce three `createTheme` objects from the base + the
   three register briefs.
4. Audit and polish by hand against the registers.
5. Wire them up in the app with a picker + inference hook.

Want me to spin the frontend-theming agent with this as the spec, or do you want
to pick the MUI base first?
