# Upstream bug report — Impeccable design detector (`impeccable detect`)

**To:** owner of the `anthropic-skills:impeccable` skill
**Filed:** 2026-09-26 · by the ARCS build (arcs-v9)
**Component:** `impeccable detect` (design anti-pattern scanner)
**Versions:** skill `4.3.1` (SKILL.md) · detector binary `scripts/VERSION` = `0.1.5`
**Severity:** medium (correctness / false-positive rate) — no crashes; produces false findings that
force per-project `ignoreValues` workarounds and can mask real regressions.

> Filed as a repo doc because the skill exposes no issue tracker or `feedback` subcommand and this
> was a non-interactive session. Please forward to the skill owner. Two confirmed detector bugs and
> one lower-priority observation, each with a minimal repro and evidence. One rule (`theater-slop-phrase`)
> is included as a *correctly-firing* calibration note, not a bug.

---

## Bug 1 — `low-contrast` composites translucent backgrounds over WHITE, not the actual backdrop

**What happens.** On a dark page, an element with a translucent background (an `rgba()` fill or a
gradient with an `rgba()` stop) is scored for text contrast as if its background were opaque white.
The detector reports a phantom light background and a failing ratio.

**Minimal repro.** Dark page (`--bg:#020408`), element:
```css
.vector{ background:linear-gradient(180deg, rgba(255,77,109,.05), var(--bg)); }
```
with light body text (`#e7ecf3`) inside.

**Observed:** `low-contrast` finding, `text #e7ecf3 on #fff6f8`, ratio **1.1:1**.
**Expected:** composite the translucent layer over the real backdrop. `rgba(255,77,109,.05)` over
`#020408` = `#0f080d` (near-black); the actual ratio is **16.7:1** (cyan `#00f0ff` = 14.1:1). No finding.

**Proof it composites over white.** `#fff6f8` is exactly `rgba(255,77,109,.05)` over `#ffffff`
(255, 255·.95+77·.05=246, 255·.95+109·.05=248). The same pattern produces the detector's `#ffffff`
backdrop for fully transparent elements (it defaults the backdrop to white rather than resolving the
painted pixel behind the element).

**Impact.** 25 false `low-contrast` findings on one page (`blog-nftt-take-home-trap.html`), and the
dominant share of low-contrast findings across a 30-page dark-themed family — all on translucent or
transparent elements. This is the single largest false-positive source we hit.

**Suggested fix.** Resolve the effective background by compositing all translucent layers over the
nearest opaque ancestor background (falling back to the document/`body` background), not over white.

---

## Bug 2 — chrome labels misclassified as body text (`all-caps-body`, `wide-tracking`, `tiny-text`)

**What happens.** Small mono tracked-caps **labels/kickers/legends** (eyebrows, section numbers,
table-column keys, meta lines) are treated as reading body copy, firing `all-caps-body`,
`wide-tracking` (letter-spacing on "body"), and `tiny-text` (font < 12px on "body").

**Minimal repro.** Any of these label roles:
```css
.eyebrow{ font-family:mono; font-size:12px; letter-spacing:.22em; text-transform:uppercase; }  /* kicker */
.num{ font-family:mono; font-size:12px; letter-spacing:.24em; text-transform:uppercase; }       /* section label */
.rsec-tag{ font-family:mono; font-size:11px; letter-spacing:.18em; text-transform:uppercase; }  /* section tag */
.k{ font-family:mono; font-size:10px; text-transform:uppercase; }                               /* table key column */
```

**Observed:** `all-caps-body`, `wide-tracking`, and/or `tiny-text` on each.
**Expected:** distinguish label/kicker/legend/meta roles (short, mono, tracked-caps, non-paragraph,
often inside a heading/label slot) from reading body copy, and exempt them from the body-text rules.

**Impact.** ~12 false findings per standard post in our literary family; more on data-dense pages.
Note: these rules *are* valuable on real body copy — the problem is purely the body-vs-chrome
classification.

**Suggested fix.** A heuristic for "chrome label" (short run length, monospace, uppercase, wide
tracking, small size, not inside a `<p>`/prose block) that removes it from body-text scoring — or let
`DESIGN.md`/config declare label roles.

---

## Observation 3 (lower priority) — `cramped-padding` ignores descendant padding

`cramped-padding` fired on a horizontal-scroll wrapper (`overflow-x:auto`, border, radius, **no
padding**) whose only child is a table whose cells carry `td{padding:11px 14px}`. The visible text is
not cramped; the wrapper border simply frames a scrollable table. The rule appears to measure the
immediate child's distance to the container edge without accounting for the child's own internal
padding.

**Suggested fix.** When the flagged container's children are a table/grid (or any element that itself
provides internal padding to its text), consider effective text inset, not just the wrapper's padding.

---

## Not a bug — `theater-slop-phrase` (calibration note)

`theater-slop-phrase` correctly flagged "green theater" in agent-generated report text. We left it
visible on purpose (a real writing-slop signal on generated output). Included only to confirm the rule
works as intended; the "X theater" construction is occasionally a substantive term (cf. "security
theater"), so a confidence/allowlist tier could reduce borderline hits, but this is not a defect.

---

## How we worked around it (so upstream knows the blast radius)

Per-project `.impeccable/config.json` `detector.ignoreValues`, scoped by glob to the affected family
(`public/blog-nftt-*.html`), for `low-contrast`, `all-caps-body`, `wide-tracking`, `tiny-text`,
`cramped-padding` (plus `design-system-*` for a deliberately separate design world). Each entry
documents the audit reasoning. We fixed the *one* genuine issue each audit surfaced (a `--dim` token
at 4.0:1 → AA, and a single 10px explanatory sentence → 11px) rather than suppress it. Full audit
trail: `_PATTERNS/kintsugi-visual-grammar-seams.md`.

Fixing Bugs 1 and 2 upstream would let dark-themed, self-contained design systems pass `detect`
cleanly without any of these ignores.
