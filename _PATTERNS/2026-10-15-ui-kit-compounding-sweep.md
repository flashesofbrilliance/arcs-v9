# UI kit compounding sweep from Raw Capture

Date: 2026-10-15. Purpose: make the design system compound, so the next page starts from primitives and tokens instead of an override layer. Sources read: `DESIGN.md`, `src/ui-kit/recoil-report/_tokens.css`, `src/ui-kit/README.md`, `src/ui-kit/templates.json`, the 15 numbered primitives, and a census of `src/**/*.tsx`.

## Finding 1: the kit tokens disagree with DESIGN.md

The design-debt gate judges pages against DESIGN.md. Pages that inherit `_tokens.css` verbatim then fail on fonts, radii and a surface color, so each page grows an override layer. Raw Capture needed three overrides and five gate rounds.

| Token | `_tokens.css` (legacy) | DESIGN.md | Status |
|---|---|---|---|
| `--surface-2` vs elevated | `#121820` | `#111827` | drift |
| radii | 4, 8, 12 px | 3, 6, 10, 16 px, pill | all three differ |
| sans font | InstrumentSans | Inter | drift |
| mono font | GeistMono | JetBrains Mono | drift |
| display font | BricolageGrotesque | Iowan Old Style serif | drift |
| warning orange | absent | `#ff9d3c` | missing |
| conviction violet (DELTA) | absent | `#A78BFA` | missing |
| paradox magenta (PARADOX, MOIRE) | absent | `#E879F9` | missing |
| text secondary | absent | `#94a3b8` | missing |
| other 7 colors | match | match | ok |

The 15 numbered primitives use 14 distinct pixel font sizes (9px appears 26 times across 14 files) against DESIGN.md's four-step ramp.

## What changed now (additive, no existing value touched)

- `_tokens.css`: a conformance layer with `--elevated`, `--text-secondary`, `--orange`, `--violet`, `--magenta`, the `--ds-r-*` radii, the `--fs-*` ramp, the `--ds-font-*` stacks, and proposed motion tokens (`--dur-*`, `--ease-out`). Numstat shows insertions only. The legacy surfaces are untouched by construction; I did not re-render them.
- Five new primitives in a new group, Instrument Lab: 16 instrument panel, 17 altitude ladder, 18 contact sheet, 19 gate ladder, 20 transport. Each links `_tokens.css`, uses only the new tokens, and passes `page_gate` and wrap-lint.
- Template `instrument-lab` in `templates.json` (mode `operate`), listed in the README.
- `_ARTIFACTS/raw-capture.html` is enrolled in that template, inlines the full tokens file, and carries no override layer. `component_source_gate`, `token_source_gate`, wrap-lint, card-gutter and `page_gate` pass.

## Candidates by atomic level

| Level | Candidate | State |
|---|---|---|
| Atom | DESIGN.md conformance tokens, motion tokens | done (motion is proposed) |
| Molecule | segmented control, labeled range, readout cell, Y-state pill, tier tag, transport | in 16 to 20; tier tag and pill are not yet their own files |
| Molecule | section-label, chip, tile, button, callout, evidence-ref, led | named in the README, never written as files |
| Organism | instrument panel, altitude ladder, contact sheet, gate ladder | done (16 to 19) |
| Organism | claim table with a tag column, write-lock declaration block, pipeline strip | on Raw Capture, not extracted; the strip overlaps primitive 10 |
| Template | `instrument-lab` | done |
| Page | Raw Capture | enrolled |

## JSX side (src/**/*.tsx)

There is no tokens module in `src/lib`. Census: `border-radius` 4 (53 uses), 8 (43 with and without a space) and 5 (30) are off the DESIGN.md scale; `fontSize` 11 (334), 12 (115), 13 (77) and 14 (33) account for most sizes; hex literals scatter, including `#94a3b8` (25) which is DESIGN.md's text secondary but absent from the kit, plus near-palette values like `#8593a6`, `#707e92`, `#0a1016`, `#243042`, `#0e151e` and `#cbd5e1`. Candidate: a tokens module under `src/lib` (name to be chosen) that exports the same names as the CSS layer so inline styles reference tokens. Not built: this is a code change in the product tree and the rule on new files there should be asked first.

## Edge cases hit (each is a candidate gate or doc fix)

- The detector flags Inter as an overused primary font, and DESIGN.md specifies Inter for body text. The conformant sans stack in `_tokens.css` puts `system-ui` first and keeps Inter as the named fallback. Worth asking whether the detector or DESIGN.md should give way.
- The design-debt detector reads the page in its default light scheme, so a light palette trips it; the kit is dark-only, so Raw Capture committed to one dark look.
- `border: 1px solid currentColor` is read as black by the detector; set `border-color` explicitly on state classes.
- The detector flags sentence-length text at 11px even in a mono label style; keep tier notes at body size.
- The preview pane renders files outside the project folder as static snapshots, so a relative `_tokens.css` link does not load there. Use Playwright or the project preview.
- Passing gates did not mean a consistent page: the lane-edge miss was in none of them. See `_PATTERNS/2026-10-15-sibling-edge-root-cause.md`.

## Decisions this leaves for the owner

1. Reconcile the legacy tokens with DESIGN.md, or declare DESIGN.md the source and migrate. The legacy set is inherited by about 42 surfaces, so a change is not additive.
2. Add a motion section to DESIGN.md (the tokens here are proposed).
3. Whether to add a JSX tokens module and migrate the off-scale radii and sizes.

Not verified: the other surfaces after the additive tokens, and a visual pass on primitives 17 to 20 (only 16 was looked at).
