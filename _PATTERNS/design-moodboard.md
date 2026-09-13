# ARCS Design Moodboard — direction input (the upstream of `.impeccable/design.json`)

> **What this is.** The *inspiration* layer, not the *derived system* layer.
> `.impeccable/design.json` is the machine-readable design system reverse-derived from shipped
> artifacts (color ramps, type roles, shadows, motion, components). `_PATTERNS/arcs-artifact-css-base.css`
> is the artifact CSS canon. **This file is the missing upstream:** the external references we aim at
> and *what specifically we take from each*, so a future redesign (or an Impeccable/Plan run) has the
> direction in hand instead of re-deriving it from the last artifact. Add a row when a reference
> actually shapes a shipped surface; keep it to references + the one thing we adopt. No em-dashes.

Related: memory `arcs-fieldos-design-system`, `earned-fidelity-not-maximal-diamond-cut`,
`design-full-width-lede-matches-heading`; AGENTS.md gotcha #13; `WORLD.md` (the render scale + tonal register).

---

## The house world (non-negotiable frame)

Every reference is adopted *through* the ARCS world, never wholesale. The frame is set in `WORLD.md`:
Myst over SaaS onboarding, calm/precise/serious-play, earned fidelity (never render higher resolution
than the data deserves), the dark FieldOS palette. We borrow other work's **layout grammar and craft**,
not its palette or voice.

- **Palette (locked):** obsidian `#020408` ground; True North Cyan `#00F0FF` (primary), Coherent Green
  `#00FF9D`, Locked Gold `#FFD700`, Ruin Red `#FF4D6D`. Full ramps in `.impeccable/design.json`.
- **Type roles:** Newsreader serif = canon / headlines / load-bearing quotes (the oral-history register);
  Inter = reading sans; JetBrains Mono = instrument labels, indices, gauge units (uppercase, tracked).
- **Light, not shadow:** depth via restrained bloom (`signal-glow`, `locked-bloom`), not cast shadows.

---

## References adopted (moodboard rows)

| Reference | What we take (only this) | Where it shipped | Do NOT copy |
|---|---|---|---|
| **every.to** | Modular editorial grammar: a large featured lead, a mixed-density grid, category/section pills with a rule line, cover thumbnails, compact archive rows for the long tail. | NFTT index redesign (good.arcs.care/blog/nftt), 2026-09-13, PR #426 | Its light palette and publication-network chrome. We keep the dark FieldOS world. |
| **The Mobius-traversal hero system** | One motif (single-surface loop = "same circuit, opposite sign"), rendered from multiple vantages/orientations over time; luminous line-work on obsidian. Reuse the same few renders across a serialized arc rather than one-off art per post. | NFTT essay heroes + the "Apple Ledger" grid; 4 distinct renders across 7 posts | Photoreal or stocky imagery; anything that breaks the single-surface-loop read. |
| **The Jobs distortion-field composite** | A portrait dissolving into a force-field/wave as the *featured* lead only (the serialized arc's cover). Contained frame (`.cover`, rounded, bordered), natural aspect ratio so baked-in quote/ring never crop. | Tuning into the Distortion Field hero + NFTT featured card | Using a real person's likeness anywhere beyond this one owned composite; cropping that slices the baked quote. |
| **Silkscreen / earned-fidelity render scale** (WORLD.md) | Fidelity tracks conviction: SHARP at GREEN, GRAIN/MOIRE in fog. A brief never renders sharper than its data. | Y-gate render resolution across product surfaces | Confetti, celebratory motion, or maxing fidelity by default. |

---

## Craft rails that ride along (from AGENTS.md #13 / WORLD.md)

- One shared px `--measure` for body/card reading text; **never** per-element `ch` caps (ragged right edge reads as broken wrapping).
- **Ledes are the exception:** a hero/section lede spans the full lane width of its heading (`max-width:none`), never the narrow body measure. Eyeball lede-vs-heading right edges at ~1280px; the "too narrow" symptom is invisible to overflow gates.
- Em-dashes stay at 0 (writing + gate). Verify single-file HTML with `scripts/artifact_wrap_lint.py` and a 360-1440 sweep incl. the 700-1000 band, run from your own worktree copy.

---

## How this feeds Impeccable

`impeccable-documenter` derives `design.json` from finished builds (output). When starting a redesign,
read THIS file for direction first, then let the build realize it, then let the documenter re-derive the
system. Inspiration in, artifact out, system re-derived. Keep the three layers distinct.
