<!-- ARCS ui-kit — atomic design SSOT for self-contained HTML surfaces. -->
# ARCS ui-kit — the visual SSOT pages snap into

This is the visual twin of the anti-slop eval suite (`scripts/slop_lint.py` + `slop_eval.py` +
`provenance_lint.py` + `_PATTERNS/slop-free-rubric.md`). The eval suite gates the *words*; this kit
gates the *look*. Both are single-source, opt-in, ratcheted gates.

**The problem it solves:** every self-contained page used to re-author its own CSS/tokens, so they
diverged and repeatedly failed `scripts/token_source_gate.py`. A census (2026-09-26) of 225 surfaces
found only 42 inherit the tokens (27 inline, 15 link) while 135 re-author the 4-signal palette (74
verbatim under canonical names, 27 under foreign names like `--nc`/`--vc`/`--acc`/`--bc`). Section
labels alone appear under 6 different class names; chips under 5. There was no atomic SSOT for pages
to *snap into*. This kit is that SSOT.

## The atomic hierarchy

```
atoms      → recoil-report/_tokens.css  (color · type · space · radius · glow)
             the ONE palette. Signal hexes #00F0FF #00FF9D #FFD700 #FF4D6D live here and NOWHERE else.
molecules  → section-label · chip/pill/badge · stat/prob tile · evidence-ref · callout · button · led
organisms  → recoil-report/NN-*.html (the 14 numbered @dsCard primitives):
             01 header · 02 hyperstition-arc · 03 entity-card · 04 signal-delta-table ·
             05 kairos-node · 06 beat-stepper · 07 probability-bar · 08 receipt-table ·
             09 stop-loss-footer · 10 pipeline-tracker · 11 champion-map · 12 role-thesis ·
             13 90day-build · 14 earned-fidelity-twin
templates  → a composition of organisms a page declares once and snaps into (see templates.json)
```

Each organism is a `@dsCard` file: line 1 is `<!-- @dsCard group=... name=... -->`, it `<link>`s
`_tokens.css`, and its `<style>` block owns the component classes. `index.html` assembles all of them.

## Templates map 1:1 onto a slop --mode (the organizing spine)

A page declares its template ONCE, and that declaration drives BOTH the visual composition AND the
anti-slop eval thresholds. Visual template and eval mode can never silently drift apart. Registry:
`src/ui-kit/templates.json`. Many templates may share one mode (mode drives thresholds, template
drives composition).

| template | slop `--mode` | kind | canonical example |
|---|---|---|---|
| `recoil-report` | `operate` | instrument dashboard | `src/ui-kit/recoil-report/index.html` |
| `scan-hud` | `operate` | instrument dashboard | `_ARTIFACTS/profile-scan-hud.html` |
| `candidate-brief` | `persuade` | persuasion surface | `public/success-academy.html`, `public/squad.html` |
| `nftt-essay` | `essay` | editorial longform | `public/blog-nftt-the-loop-closes.html` |
| `resume-print` | `resume` | print / paper | `public/vico-resume.html` |

Modes are defined in `scripts/slop_lint.py` `MODE_SPEC` (specificity floors; burstiness is
mode-independent). `essay`/`reflective`/`longform` carry the low 0.10 floor for evidence-dense prose;
`persuade`/`read` = 0.50; `operate`/`resume`/`default` = 0.60.

## How a page enrolls

Add two marker comments near the top of the page:

```html
<!-- @arcs-template: candidate-brief -->
<!-- @arcs-mode: persuade -->            <!-- optional; if present must match the template's mode -->
```

Then (a) inherit the palette and (b) assemble from the kit primitives:

- **Tokens:** inline `recoil-report/_tokens.css` VERBATIM (keep its sentinel line
  `/* ARCS Recoil Report — Design Tokens */`) for a self-contained page, or `<link>` it for a kit
  file. Never rename the tokens. A page may add its own NON-signal tokens in a second `:root{}`
  block (spacing scale, an extra neutral) as long as it never re-declares the 4 signal hexes.
- **Components:** use the template's signature selectors from `templates.json`. If the page needs a
  shape the kit lacks, add ONE new `@dsCard` primitive file to `recoil-report/` (so it can round-trip
  to the DS via `/design-sync`), then use it. Do NOT hand-roll a bespoke redesign.

## The two gates

- **`scripts/token_source_gate.py`** (already on main): a page painting an ARCS signal hex in a
  custom property must inherit `_tokens.css`. Blocks the re-authored-palette class.
- **`scripts/component_source_gate.py`** (this change): the visual twin. For an ENROLLED page it
  requires the template to be registered, tokens inherited, `@arcs-mode` (if present) to match the
  template, and at least `min_signatures` of the template's signature selectors present (proof of
  kit assembly, not bespoke CSS). Un-enrolled pages PASS (`not enrolled`) so it rolls out
  surface-by-surface. `--pair` ratchets: an already-enrolled+failing HEAD warns, never blocks.
  Self-test: `python3 scripts/component_source_gate.py --self-test`.

## The Impeccable DESIGN detector & the ARCS brand profile

The Impeccable detector (`~/.claude/skills/impeccable/scripts/impeccable detect`) reads its design
system from `DESIGN.md` (Inter + JetBrains Mono). The recoil-report kit is a deliberately separate
visual world (Geist / Instrument / Bricolage per `_tokens.css`), so a kit-inheriting page trips
`design-system-*` findings that are BRAND, not slop.

**The real, verified exemption mechanism (do not trust the old `rule: null` gotcha — it is stale).**
Empirically (controlled A/B/C/D/E test, 2026-09-26): a detector finding has no `rule` key; the rule id
lives under `antipattern` and the matched value under `ignoreValue`. The engine maps a config
`ignoreValues` entry's `rule` onto the finding's `antipattern`, `value:"*"` is a wildcard, and `files`
is an enforced glob. Removing the exemptions surfaced 12 findings on a kit page; the real config
produced 0. So **rule-keyed `ignoreValues` DO work.** Add them with the detector's own CLI (JSON-safe):

```
impeccable ignores add-value design-system-color "*" --file "<glob>" --reason "..."
```

or `ignores add-file "<glob>"` to waive ALL rules for a file (whole-file separate world).

**The ARCS brand profile = which antipatterns are brand-deliberate (exempt) vs which stay live:**

- EXEMPT (recoil-report kit grammar): `design-system-font`, `design-system-font-size`,
  `design-system-color`, `design-system-radius`, `dark-glow` (status-LED / earned-fidelity bloom),
  `all-caps-body` + `wide-tracking` (mono tracked-caps label voice), `border-accent-on-rounded`
  (signal-color card border), `side-tab` (the 4px thread rail / entity strip).
- STAY LIVE (real debt + generic AI tells): `tiny-text`, `undersized-ui-text`, `low-contrast`,
  `cramped-padding`, `skipped-heading`, plus generic slop tells (glassmorphism, radial halo, unrelated
  glyph/badge rows) which are simply not in the exempt list.

Proof it is load-bearing on the PoC (`_ARTIFACTS/profile-scan-hud.html`): 120 findings with no
profile → 76 with the profile (only the debt classes remain; all 44 brand-class findings suppressed).

## Known open decision (do NOT resolve unilaterally — cross-session)

`_tokens.css` names Geist/Instrument/Bricolage; `DESIGN.md` + the DS adherence linter permit only
Inter + JetBrains Mono. Enrolling a page onto `_tokens.css` therefore trips `design-system-font`
(handled by the brand profile above) and shifts sans rendering to a system fallback. The reconciliation
(`/design-sync` one component at a time) is backlog item `tokens-css-vs-ds-font-stack-drift` and is not
this change's to decide.
