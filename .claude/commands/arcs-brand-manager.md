# /arcs-brand-manager

> Forked from Anthropic's `brand-guidelines` skill, adapted into an ARCS-specific brand
> manager. Use this whenever producing any ARCS-branded artifact — canvas-design posters,
> web-artifacts-builder mockups, pptx/docx exports, Gamma decks, or anything that needs to
> look like ARCS rather than generic dark-mode SaaS. This is a styling reference, not a
> code-generation tool — it tells you *which* tokens/voice to apply, the actual application
> still goes through whichever tool fits the artifact (canvas-design, web-artifacts-builder,
> pptx, etc.).

## Source of truth (do not invent new values — pull from here)

- `src/ui/tokens.ts` — the canonical token file. Colors, type scale, radius, spacing.
- `src/document/tokens.ts` — the document-kit's own token set (deliberately distinct fg
  tiers for reader-view content — do not remap onto `src/ui/tokens.ts`, they're separate
  on purpose).
- `WORLD.md` — the tonal/register law. Read this before writing any copy for an ARCS
  artifact, not just before touching visuals.

## Colors

**Surface hierarchy** (never pure black, never a flat single background):
- `bg` `#020408` — page background
- `panel` `#0d1117` — cards, modules
- `elevated` `#111827` — inputs, hover states

**Signal colors** — these are *semantic*, not decorative. Never reassign a signal color to
a different meaning inside one artifact:
| Color | Hex | Meaning |
|---|---|---|
| cyan | `#00F0FF` | True North, active bearing — the thing the artifact wants you to look at |
| green | `#00FF9D` | Coherent / SHARP / high conviction |
| gold | `#FFD700` | Court / LOCKED / caution |
| orange | `#ff9d3c` | Warning / macro-tag |
| red | `#FF4D6D` | Alert / GRAIN / ruin-exposure |
| steel | `#94a3b8` | Neutral / default |
| violet | `#A78BFA` | Conviction shift / DELTA |
| magenta | `#E879F9` | PARADOX / curator |

**Text**: `primary #e2e8f0` · `secondary #94a3b8` · `muted #475569` · `dimmed #64748b` — four
tiers, not two. A poster/deck that only uses primary+secondary is under-using the kit.

## Typography

- **Sans** (`'Inter', system-ui, -apple-system, sans-serif`) — all prose, headings, body.
- **Mono** (`'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace`) — labels, section
  indices, instrument readouts, anything that should read as *measured* rather than
  *written*. This is the single most distinctive ARCS typographic move — mono for data,
  sans for narrative. Don't blur that line.
- Six graded mono label tiers exist (`font.tier.t1`–`t6`) for a reason: as hierarchy rises,
  size increases and letter-spacing *tightens* (weight holds constant). Don't default to
  bold-for-emphasis; use the tier ladder instead.

## Visual grammar — what makes something look like ARCS, not generic dark mode

1. **Earned fidelity, not assumed.** A render's sharpness should reflect actual conviction
   (the Y-gate render-resolution scale: SHARP/DEGRADED/GRAIN/MOIRE — opacity 1.0→0.85→0.70→0.60,
   weight 500→400→300→300). A mockup that's uniformly crisp everywhere is lying about
   certainty it hasn't earned. If an artifact is illustrative/unconfirmed, it should *look*
   less certain — lower opacity, looser tracking — not just say so in a caption.
2. **Mono labels, sans prose.** Every section gets a small-caps-via-letter-spacing mono
   label (not actual uppercase text — `text-transform` semantics via tracking, see
   `font.tier`) before any sans heading.
3. **Subtle rail accents over full-card glow.** Per this session's own design fix on
   `/history` — a *list* of cards each gets a 2px left-rail accent in its semantic color,
   not a full glowing border. Full-card glow is reserved for exactly one element per
   composition (e.g. the True North panel) — if everything glows, nothing reads as
   load-bearing.
4. **No gradients-as-decoration.** The only gradients in this kit are functional: a subtle
   top-edge highlight (glass bevel) and the underlit-LED bloom on an accented card. Never a
   decorative background gradient sweep.
5. **Myst, not SaaS onboarding** (WORLD.md). No confetti, no "you're all set!" cheerfulness,
   no exclamation points. Calm, precise, instrument-panel register. Copy doesn't explain
   what the reader already understands from context.

## Tone (for any copy inside the artifact)

Pull from WORLD.md directly: *"Render through the fog to earned clarity."* Calm. Precise.
Serious play. The artifact should feel like an instrument in skilled hands, not a feature
announcement. If a sentence would work equally well in a consumer app's push notification,
rewrite it.

## Checklist before calling an ARCS-branded artifact done

- [ ] Used `src/ui/tokens.ts` (or `src/document/tokens.ts` for reader-view content) — no
      invented hex values
- [ ] Signal colors used semantically, not decoratively
- [ ] Mono for labels/data, sans for prose — not mixed
- [ ] Exactly one glowing/full-accent element per composition, everything else uses rail
      accents or no accent
- [ ] Render resolution (opacity/weight/tracking) matches the artifact's actual confidence
      level, not uniformly sharp
- [ ] No decorative gradients, no SaaS-onboarding tone
