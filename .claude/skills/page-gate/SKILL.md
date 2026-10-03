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

## Baseline (2026-10-03, `--static --no-wrap-lint public/*.html`)

149 of 181 pass. Errors: doctype 30, charset 23, viewport 5, mojibake 0. Warnings: Google Fonts
78, en-dash 38.
