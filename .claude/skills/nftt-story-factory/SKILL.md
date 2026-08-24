---
name: nftt-story-factory
description: Stamp a data-driven ARCS story (Notes-from-the-Trenches class) at good.arcs.care/blog/nftt/<slug> from a story envelope + prose. The extensible successor to the post-1/post-2 render — threads (palette + node shapes) and the narrative arc are DATA, the essay body stays prose, and an illegible arc cannot ship (Bierut five-second gate is mechanical). Use whenever writing a new NFTT post or any threaded trench story.
---

# NFTT story factory — envelope + prose → live /blog/nftt/<slug>

Proven instance: `_ARTIFACTS/blog/stories/germinate-pollinate.story.md` → `public/blog-nftt-post-2-full.html`
(good.arcs.care/blog/nftt/post-2/full). Reviewed through a Michael Bierut lens and hardened by the
ARCS full gauntlet (scar-log: `_ARTIFACTS/blog/GAUNTLET.md`). Engine: `scripts/story_render.py`
(stdlib only, zero LLM). Contract: `scripts/nftt-story.schema.json`.

## The one idea: separate the SYSTEM from the VOICE

- **VOICE** stays prose. You write an essay in markdown, not a form. Bierut would revolt at authoring a story in JSON, and he would be right.
- **SYSTEM** is data. A `---story---` JSON envelope at the top of the file declares the threads, the arc, the tier, and metadata. Nothing about the palette or the arc is hardcoded, so the template extends past NFTT to any threaded trench story (2 to N threads, any palette, any shapes).

## Inputs (the envelope — see the schema for the full contract)

```
---story---
{
  "slug": "germinate-pollinate",
  "tier": "full",
  "eyebrow": "NOTES FROM THE TRENCHES // ...",
  "threads": [
    {"id":"red",  "hex":"#FF4D6D", "name":"red · gates",         "shape":"diamond"},
    {"id":"gold", "hex":"#FFD700", "name":"gold · assets",       "shape":"circle"},
    {"id":"verm", "hex":"#FF6B2C", "name":"vermillion · fusion", "shape":"square"}
  ],
  "arc": {"caption":"the germination arc", "stops":[
    {"label":"quiet channel", "thread":"red"},
    {"label":"give back their line", "thread":"gold"}
  ]}
}
---/story---

# <eyebrow line, becomes the cyan kicker>
## <title, becomes the h1>
*<standfirst: the reader's map. Name the threads here.>*
## <first section> ...
```

- **threads**: the braid. `name`'s word before `·` is matched against stitch openers to auto-color them. `shape` carries meaning independent of color (colorblind-safe).
- **arc**: optional. Omit it if the story has no arc; a data-driven arc is never decoration. Place it in the body with a lone `[[ARC]]` line.

## Body block grammar (the prose devices)

| Author writes | Renders as |
|---|---|
| `# line` | masthead eyebrow (cyan mono kicker) |
| `## line` (first) | h1 title; (rest) section heading + gradient tick |
| `*italic block*` before first `##` | standfirst (the map). Thread-key auto-inserts after it. |
| `*In plain terms: ...*` | green plain-terms aside box |
| `*italic block*` after a `##` | neutral aside box |
| `— *Red/Gold/...: ...*` | thread stitch (auto-colored `══` glyph) |
| `>> line` | pull-quote (display) |
| `> line` | blockquote |
| `[[ARC]]` | the arc (horizontal if short, vertical ladder if long) |
| `- item` | list |
| a `## ...braid...` heading | emits the braid SVG under the heading |

## Ship-gates (blocking; the engine or a check enforces each)

1. **Zero em-dashes** anywhere in the output, CSS comments and SVG included. `grep -c '—' out.html` must be 0.
2. **Arc legibility (Bierut five-second gate)**: arcs over `ARC_MAX_HORIZONTAL_STOPS` (6) auto-reflow to the vertical ladder; label floor `ARC_LABEL_PX`. An illegible cramped sparkline cannot ship by construction.
3. **Honesty refusals**: the engine exits non-zero with NO output on a broken/dishonest envelope (fewer than 2 threads, undefined thread ref in an arc, missing envelope, illegal shape). Never patch around a refusal; fix the story.
4. **Analytics + description**: every page carries the `/_vercel/insights` script and a non-empty meta description (baked into the template).
5. **Thread contrast**: every thread `hex` must clear WCAG AA (>= 4.5:1) on `#020408`. (Author-checked; verify before shipping.)
6. **Depth ladder never dead-links**: only tiers whose files exist are linked; a single-tier post shows no ladder.
7. **Four-width sweep**: verify 375 / 790 / tablet / 1280 — no horizontal overflow, arc ladder legible, measure consistent. (Wrap-regression class, PRODUCT.md.)

## Make a new story

```bash
# 1. author the story
cp _ARTIFACTS/blog/stories/germinate-pollinate.story.md _ARTIFACTS/blog/stories/<slug>.story.md
#    edit the envelope (threads, arc, slug) and write the prose body.
# 2. render
python3 scripts/story_render.py _ARTIFACTS/blog/stories/<slug>.story.md public/blog-nftt-<slug>-full.html
# 3. gates
grep -c '—' public/blog-nftt-<slug>-full.html   # must be 0
# 4. route: add '/blog/nftt/<slug>{,/full}' to the 'good' block in src/proxy.ts
# 5. verify live at good.arcs.care/blog/nftt/<slug>/full, then it deploys from main
```

## Generalization note

The engine is the class; each story is a two-minute run. Threads/arc-as-data is the extensibility
seam: a security post-mortem could run `breach / patched / residual-risk` threads; a launch retro
could run `shipped / cut / learned`. Same engine, different envelope. Do not fork the engine per
story; add a block type to the grammar only on the rule of three.
