# Strudel for Phosphor: decision note (2026-10-23)

Status: DRAFT for Zach. Nothing adopted, no dependency added, no Strudel code read or copied. Source: the second-hand brief `_PATTERNS/2026-10-23-strudel-for-phosphor-research-brief.md` (items it marks UNVERIFIED stay open here). Not legal advice.

## Adopt-vs-build lens (runtime/specs/phosphor-adopt-vs-build.md)

The spec's hard filter is permissive or file-level copyleft only (MIT, Apache-2.0, BSD, MPL-2.0); AGPL is "out unless the licensing is reviewed". Its decision rule is adopt only if it beats custom code on a measured harness. Applied to the brief:

| Check | Adopt @strudel/web (A) | Clean-room parser (B) | Do not adopt (C) |
|---|---|---|---|
| Licence filter | Fails: AGPL-3.0-or-later on every package checked | Passes if truly clean-room | Passes |
| Offline, no network request | Default samples load from the network; unproven offline | Passes (uses Phosphor's own audio) | Passes |
| Page cap 400,000 bytes (327,480 at release 7, headroom 72,520) | Fails: about 1.5 MB unpacked | Passes (estimate 3 to 8 KB, UNVERIFIED) | Passes |
| Measured win over custom code | None measurable: Phosphor has no pattern text today | Measurable by the check list in the prereg amendment 70 | n/a |

Verdict by the lens: A is rejected on three of four rows. B is the only option that adds the feature. C is the fallback if question 1 or 3 below is answered "no".

## One-way door: the licence choice

Bundling any @strudel package makes Phosphor a combined work under AGPL-3.0-or-later. The network clause (section 13) would then require offering the complete source of the served page to its users, and a public release attaches that duty permanently to that release; it cannot be taken back. That is a one-way door and needs Zach's explicit go. Until that go, no release, no public copy, and nothing in public/dj.html changes.

The clean-room route avoids the door only if it is real: the parser is written from public documentation and the brief alone, by someone who has not read Strudel source, with the dated log in `_PATTERNS/2026-10-23-phosphor-pattern-box-clean-room-log.md`. The maintainers state that clones based on reading their source count as derivative works. Whether names and syntax alone are free to reuse is a legal judgement for Zach and counsel, not settled here. The feature is never called "Strudel-compatible"; the label is "pattern text" in the UI and docs.

## Five questions for Zach (from the brief)

1. Is Phosphor allowed to become AGPL with its source offered, or is that excluded? (Recommended answer: excluded, so option A is closed.)
2. Is "uses Strudel mini-notation syntax" something kids need, or is a step grid with text export enough?
3. Who writes the parser, and can they avoid reading krill.pegjs, with a dated clean-room log?
4. Which operators are in scope? Proposal: sequence, [ ], *, < >, ~, _, !, ?, euclid; out: `,` `|` `.` `..` `@` `/` `:`.
5. Should the UI or docs ever say "Strudel-compatible", given trademark and the maintainers' derivative-work stance? (Recommended: no.)

## Smallest prototype (designed, not shipped)

Spec and checks are in prereg amendment 70. In short: a pattern text box in Parent mode only, filling the existing 16-step lanes (`LANES`/`SEQ.cells` in `_ARTIFACTS/phosphor-src/app.js`), no new audio engine, no samples, no network, no dependency. Cost estimate 1 to 2 days with tests, from the brief. Gated on questions 1 to 4.

## Open

Brief items still UNVERIFIED: euclid rotation direction, how `?` derives its random from cycle time, offline behaviour of a bundled build, per-bank sample licences. The clean-room parser must pick its own documented behaviour for these and say so in the UI, not claim Strudel's.
