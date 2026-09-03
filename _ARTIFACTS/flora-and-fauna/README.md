# Flora and Fauna — unified surface

Source of truth is `_CANON/flora-and-fauna.md`; this folder holds the interactive surface built from it.

- `surface.template.html` — the page with a `/*__SURVEY__*/{}` slot and `__GENERATED__` token.
- `surface.html` — the built page (survey JSON injected from `_STATE/2026-09-03-corpus-index.jsonl`).
- Rebuild: regenerate the index with `scripts/corpus_prospector.py index`, then fill the slot with the
  class table / grade totals (see `_STATE/2026-09-03-prospecting-survey.md` §2–3 for the shape).

Five lenses over one set of blocks: Guide (plates I–V) · Library (Dewey shelves 0xx–7xx) · Atlas
(WORLD.md zones at earned fidelity) · Observatory (the energy circuit) · Status (loop-1 survey).
Blocks are single DOM nodes that FLIP-animate between arrangements — the "magnetic blocks".
