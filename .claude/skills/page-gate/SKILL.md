---
name: page-gate
description: Gate any standalone HTML page (public/, _ARTIFACTS/, _PROPOSALS/ drafts, any page family) before it is shown to anyone or committed - doctype, utf-8 charset in the first 1024 bytes, viewport, baked-in mojibake, the wrap lint, and a headless overflow sweep at 375/790/1280 with a lede-vs-heading check. Use whenever you create, clone, restyle, or bulk-edit an HTML page, before sending a draft render to Zach's phone, and as the acceptance check for any multi-page sweep. Wraps scripts/page_gate.py.
---

# /page-gate: one gate for every page

Every page family grew its own partial gate (`nftt-gates.sh`, `nftt_meta_gate.py`, the
pre-commit wrap guard on ADDED `public/` files). Nothing checked a `_PROPOSALS/` draft, and
nothing checked encoding at all, so on 2026-10-03 a draft cloned from the NFTT master rendered
"No. 2 Â·" on a phone (fix `719ed7f`). This skill is the one gate that runs on any page.

## Run it

```bash
python3 scripts/page_gate.py path/to/page.html [more.html ...]      # full: static + render
python3 scripts/page_gate.py --static public/*.html                  # fast sweep, no browser
```

Exit codes: `0` pass (warnings allowed) · `1` an error · `2` render checks were requested but
no browser was found. **Exit 2 is not a pass.** Say "render unverified", never "clean".

Playwright: the script looks in the repo's `node_modules`, then the global npm root. In a cloud
session the repo's packages are usually not installed; the global copy is enough.

## What it checks

| Kind | Check | Why it matters |
|---|---|---|
| ERROR | doctype first | without it the browser falls back to quirks mode (legacy layout rules) |
| ERROR | `<meta charset="utf-8">` in the first 1024 bytes | the spec's prescan window; later or missing, a file opened without a server header gets its encoding guessed (the `Â·` bug) |
| ERROR | viewport meta | phones otherwise render a zoomed-out desktop page |
| ERROR | mojibake already in the file | `Â·`, `â€”` mean text was once decoded wrong and saved |
| ERROR | `artifact_wrap_lint.py` | em-dash, `ch` caps, container/measure mismatch |
| ERROR | overflow at 375 / 790 / 1280 | horizontal scroll on phones and the 700-1000 band |
| warn | lede ends short of the heading's lane at 1280 | the standing full-width-lede preference; an INDEX page's 680px measure is the sanctioned exception, so judge it |
| warn | en-dash in visible text | fine in a range, otherwise reword |
| warn | Google Fonts dependency | render-blocking chain and a visible font swap; self-host |
| warn | public page without `/_vercel/insights` | analytics coverage |

## Rules

1. Run the **full** gate (not `--static`) before showing a rendered page to Zach or calling a
   sweep done. Report the pass count and every warning you chose to leave, with the reason.
2. Clone a template, then gate it immediately: the NFTT master `public/blog-nftt-take-home-trap.html`
   lacks doctype and charset, so every clone inherits the gap until the master is fixed.
3. For a bulk edit, take a `--static` baseline first, then gate after; the delta is the receipt.
4. The pre-commit hook runs the static checks on NEWLY ADDED pages in `public/`, `_ARTIFACTS/`
   and `_PROPOSALS/` (hooks are active only after `git config core.hooksPath scripts/git-hooks`).
   Legacy pages are not blocked on edit; clear them in a sweep.
5. A new failure class goes into `page_gate.py` with a fail-on-bad and pass-on-good proof
   (AGENTS.md gotcha 15), not into this prose.

## Fixing what it finds

- **google-fonts / charset**: `python3 scripts/fonts_selfhost.py apply <page>` self-hosts the
  page's fonts from `public/fonts/` (preload, metric-matched fallback) and adds the charset.
  New family: add it to `FAMILIES`, run `fetch`, then `apply`. `check` lists pages still on Google.
- **doctype on a legacy page**: NOT mechanical. A doctype moves the page from quirks to
  standards mode; on 2026-10-03 it moved layout on 21 of 30 pages (hero sections 500-680px
  shorter, the take-home-trap dossier 1,400px taller). Add it with `fonts_selfhost.py apply
  --doctype <page>`, then compare element positions with and without it at 375 and 1280, and
  keep it only if nothing moved or a human approves the new layout from screenshots.
- **viewport**: never add blind. A page built without one may be a desktop-only layout that
  gets worse on a phone once it has one.

## Baseline

| Date | Pass | doctype | charset | viewport | google-fonts |
|---|---|---|---|---|---|
| 2026-10-03 before sweep | 149/181 | 30 | 23 | 5 | 78 |
| 2026-10-03 after sweep | 158/181 | 21 | 0 | 5 | 0 |
| 2026-10-03 after viewport fix | 160/181 | 21 | 0 | 0 | 0 |

The 21 doctype pages (layout moves in standards mode; review one by one): eight NFTT hero
posts and the take-home-trap dossier, `forge-cut`, `forge-pattern`, `lewoof-intake`, eight `prl-status-*`,
`state-of-union`. Viewport: all pages carry one since 2026-10-03 (the last five were not desktop-only;
Zach confirmed). Render overflow on fixed-width resume sheets (441px at 375) predates the sweep.
