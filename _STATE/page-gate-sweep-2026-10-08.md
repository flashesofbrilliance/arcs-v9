# Page gate sweep, 2026-10-08 (read-only)

Strict gate (`python3 scripts/page_gate.py --matrix full --browser chrome <page>`): 9 device sizes including 320px reflow, light and dark, anchor-snap, console errors, axe-core WCAG 2.0 to 2.2 A and AA plus best practice. 8 of 179 `public/` pages sampled, served over local HTTP as the site serves them. Nothing in these pages was changed. Counterpart pages that were already sent (wing, and others) are point-in-time deliverables; findings there are informational.

Automated rules cover only part of WCAG. A clean row here is not an accessibility sign-off, and a finding is a lead to check, not a verdict.

| Page | Real errors (strict) | Notes |
|---|---|---|
| `public/pf-decision-geometry.html` | none | warnings only: landmarks, small touch targets (80x16 controls) |
| `public/blog-nftt-index.html` | 1 | link distinguishable only by colour |
| `public/build.html` | 1 | 5 links distinguishable only by colour |
| `public/honest.html` | 3 | ARIA attribute not permitted on `.pips`; 1 low-contrast node; scrollable `<pre>` not keyboard reachable |
| `public/resume.html` | 1 | 22 low-contrast link nodes |
| `public/status.html` | 2 | 37 low-contrast `.byline` nodes; scrollable `.su-tw` not keyboard reachable |
| `public/lewoof-intake.html` | 4 | 16 inputs without labels (critical), 20 low-contrast nodes, no `lang`, no doctype (quirks mode) |
| `public/wing.html` | 3 classes | 12 low-contrast nodes; 3 scrollable tables not keyboard reachable; `#legend` jump flagged on 6 devices (target above the viewport after the jump, 0px of sticky chrome: probably the page's collapse mechanics, needs a look, may be a gate false positive) |

Across all eight: no `<main>` landmark and unlabelled content regions on most pages (moderate), many controls and links 12 to 28px tall on touch (warning), a few heading-order jumps, en-dashes in visible text on status and wing.

Most common real finding: colour contrast (5 of 8 pages). Then scrollable regions that keyboards cannot reach (3), links told apart by colour alone (2), unlabelled form controls (1, critical).

Gate fixes made during the sweep: pages under `public/` are now served from a local HTTP root so root-relative fonts and paths resolve; expected platform 404s (`/_vercel/*`, `/api/*`, favicon) and cross-origin calls to the production API are ignored, while any other missing asset is an error.
