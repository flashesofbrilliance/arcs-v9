# Living Braid — pickup (WIP, uncommitted on branch claude/living-braid)

## Where
Worktree: .claude/worktrees/living-braid  (branch claude/living-braid, off main @ #175)
Engine: scripts/story_render.py  ·  Prototype target: post-2 only, NO deploy.
Serve: `cd public && python3 -m http.server 8790` then open blog-nftt-post-2-full.html
IMPORTANT: rail only shows at viewport >= 1040px (widen the pane or it's hidden by design).

## Shape brief (signed off)
Spine = ARCS Double Helix read-rail (2 backbones + base-pair rungs, rungs colored by the
section's data-thread, winds with scroll). Accents = yad (heading+bookmark), kintsugi cracks
(subtle bg layer), moire at fusion/vermillion beats ONLY. CUT = velocity turbulence, inline braid.
Register = calm instrument (Myst not SaaS). prefers-reduced-motion => static.

## Done
- Double helix renders full-height (fixed the SVG height:100% bug that squished it to 100px).
- Section data-thread pre-scan -> rungs recolor by current section.
- Yad + localStorage resume ("pick up where you left off") working.

## Next (to build against the brief)
1. Calm the helix: remove leftover velocity-turbulence (amp opens on fast scroll) -> steady radius.
2. Kintsugi cracks: low-opacity gold-seam background layer, behind text, no contrast loss.
3. Moire: only at vermillion/fusion beats.
4. Decide rail threshold (<=900?) or a narrow/mobile treatment.
Then: critique (impeccable) + polish, and only then consider engine-wide + deploy.
