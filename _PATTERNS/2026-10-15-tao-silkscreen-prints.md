# Tao silkscreen prints: design note and pre-registered kills (2026-10-15)

Idea (Zach, 2026-10-15): serial screenprint form, the ARCS Möbius, and the Raw Capture instrument, used to mint shareable Tao prints.
Status: prototype only. No series minted. Nothing published.

## Form, not subject
Borrowed form: one mold repeated in a grid, flat inks, registration and ink loss drifting across repeats.
Not used: any crash imagery, any existing artist's work. The subject is a proverb and its source.
v1 used a flat lemniscate and was wrong. v2 uses the actual ARCS Möbius: the parametric strip, two offset strand families and gold horizon from `_ARTIFACTS/arcs-moire-mobius.html`. v3 drew the strip as depth-sorted flat facets in the four signal inks, one ink per face and band, so the twist is visible as the face colour flips. Four plates slip apart, ink drops out in patches and the horizon breaks, all scaling with (1 - f) and the repeat index.

v4 (permutations, Zach 2026-10-15 "need to be more pronounced"): each of the nine repeats is a lawful variant of the one mold: its own strip rotation, ink rotation (which plate prints which face), and a flat ink ground on five of nine. Degradation by fidelity is layered on top. Caveat: the K3 proxy margin shrank (score 72.9 to 76.0 across f) because flat ground area is constant; rho still passes but the proxy is now weak, and the human ranking matters more.

## Finding that changes the design
`runtime/tao/proverbs.json` rows carry id, aspect, verb, source, text, canon_ref. They carry NO NCI and NO Y state.
So "image derived from the proverb's NCI and Y state" cannot be done from data today.
Decision: shape code (aspect x verb) drives mold geometry and ink order; fidelity `f` is a DECLARED recipe input.
A print must say so on its face. Wiring real fidelity needs a receipt link per proverb (source ADR to receipt NCI), not built.

## Pre-registered kills (written before the check ran)
| id | claim | kill if |
|---|---|---|
| K1 | A print is reproducible | same (id, recipe, seed) gives different bytes, or a different seed gives the same bytes |
| K2 | Encoding is monotonic | mean registration offset or total grain count rises anywhere as fidelity rises |
| K3 | Encoding is perceivable | six prints, shuffled, cannot be ranked by fidelity from pixels alone (Spearman rho < 0.9). Machine proxy now; the human version is a blind sheet, 6 prints, Zach ranks them, kill if he mis-ranks 2 or more adjacent pairs |
| K4 | Möbius closure is real | closing panel is not mirrored with swapped inks, or any other panel is |
| K5 | Möbius layout legible at phone width | text on the strip below 11px at a 360px viewport, or panels unreadable: ship the flat grid only |
| K6 | Shareable | no export path outside the Artifact viewer: ship a link only |
| K7 | Public-safe | the proverb's source is a counterpart document or names a person: do not mint |

## Results (this session)
- K1 PASS, K2 PASS (registration 3.47 to 0.12, specks 1289 to 45 across f 0.15 to 0.97), K4 PASS: `python3 scripts/tao_print_check.py`.
- K3 machine proxy PASS (rho 1.0 on v3). The pixel score was rewritten twice after the v1 score failed on new molds (now: share of inked pixels that are a pure plate ink, minus grain share); the rho >= 0.9 bar was not changed. Caveat: this only proves the encoding is recoverable from pixels. I built the encoding, so it does not prove a person perceives it. Human blind sheet still pending.
- K5 PARTIAL at 360px (Playwright): no horizontal scroll, proverb text about 12.7px (passes the 11px floor). The provenance caption was about 7px and was raised to 12 units (about 10px at 360px, still under 11; move it into HTML before minting a series). Strip panels are about 50px wide and read as shapes, not detail.
- K6: no PNG export route found. `scripts/html_video_render.mjs` renders video frames and posters via Playwright; a still PNG would be a 10-line Playwright call (the check script already does this). Not built into a route.
- K7: prototype proverb `adr039-W-recapitulate` sources from ADR-080, no person. An earlier candidate (`lyndon-onesheet-W-synthesize`) sources from a counterpart PDF and was excluded.

## Open for Zach
1. Tao prints are public brand content (Zach, 2026-10-15). Still run the PII and air-gap review per proverb before any post.
2. Edition language: the print says "not an edition". Keep it so until a registry exists.
3. Human blind ranking of the 6-print sheet.
