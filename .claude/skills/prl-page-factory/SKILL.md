---
name: prl-page-factory
description: Stamp a new PRL client-facing status page (or edit an existing one) that conforms exactly to the proven prl.arcs.care design system — atomic design layers at Todd's register (pilot-checklist, BLUF-first, plain language), spanning the exec→surgical altitude arch. Use whenever adding or restyling any PRL surface.
---

# PRL page factory — atoms → molecules → organisms → template → page

The design system was built and polished live across 8 surfaces (2026-08-18/19) and is FROZEN.
Never re-derive it; stamp from here. Reference implementation: `public/prl-status-build.html`.

## The stack (atomic design)

| Layer | What | Source of truth |
|---|---|---|
| **Atoms** | tokens (dark/gold palette), type scale (h1 30 balance, item 17, sub 15.5, mono meta 13, stat 12), 916px wrap, 22px gutters, `html{overflow-y:scroll}` | `atoms.css` (extracted from live build page) |
| **Molecules** | checklist row (mark·item·stat pill), card-stacking table (mobile <600px), status pills (ok/hold/bad), family nav pill, glass panel | `atoms.css` + `generate.py` emitters |
| **Organisms** | labeled glass section (checklist / table / ask block), sticky navbar, header block (kick+dot · h1 · meta), bluf, global footer | `generate.py` |
| **Template** | header → sticky nav → bluf → sections → footer | `generate.py page()` |
| **Page** | one JSON spec | `spec.example.json` |

Run: `python3 .claude/skills/prl-page-factory/generate.py spec.json > public/prl-status-<seg>.html`
Then: add the seg to `src/proxy.ts` MULTI_PATH_MAP **and** `next.config.ts` capture group,
`npm run build`, push, and verify live with `curl -sI | grep x-matched-path` (never trust a
green build — the beforeFiles re-catch bug class).

## Todd's register (non-negotiable, every altitude)
- **BLUF first**: one bold-gold-lead sentence that answers "what's the bottom line" — the bluf
  IS the exec layer. Pilot-checklist body: rows with ✓/→/! marks and honest status pills.
- Plain words, no vendor jargon on client surfaces ("automation platform" not "Zapier" when it
  reads cleaner; "CRM sandbox" not instance URLs). No em-dash chains; short sentences.
- Honest status only: verified ≠ built ≠ proposed. A promise not yet delivered gets a hold pill,
  never a green one. "Nothing has touched production" stated wherever true.

## The altitude arch (exec → surgical, one page, descending)
1. **Exec** = bluf (one sentence)
2. **Strategic** = first checklist section (status rows)
3. **Operational** = tables (best/base/worst, ownership maps)
4. **Tactical** = secondary sections (worked-around, what's-next ordered rows)
5. **Surgical** = collapsed `<details class="brief">` appendix — fine print, never open by default
Readers exit at their altitude; nothing above depends on anything below.

## Hard-won rules (violations were live bugs — do not relearn)
- viewport meta ALWAYS (980px zoom-out flash without it)
- table outside `.scroller`/`.tblwrap` + global min-width = mobile page stretch
- section `.wrap` must NOT carry page-end bottom padding (dead air per section)
- no `backdrop-filter:blur` on scroll-following panels (viewport-edge smear)
- inline styles on the nav element override the navbar rules (16px offset bug)
- `<p>` used as a block needs `margin:0` (default margins break vertical rhythm)
- mermaid pages: gate `pre.mermaid:not(:has(svg)){visibility:hidden}` (data-processed fires
  pre-render in v11); diagram internals are unstylable in artifacts — terse labels, detail in
  legend pills; real mermaid.js + themeVariables works on deployed static pages
- one wrap rule for all pages (916px) — no per-page exceptions, atlas included

## Generalization note
This is the PRL instance of a portable pattern (spec.json → conformant page). Second client =
extract into a client-agnostic skill with tokens as the only swap (rule of three applies).
Related seed: `engagement-universe-doll`.
