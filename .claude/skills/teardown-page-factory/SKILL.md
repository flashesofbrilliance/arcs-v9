---
name: teardown-page-factory
description: Stamp a counterpart-facing S-tier diamond teardown surface at <name>.arcs.care from source teardown MDs — the wing.arcs.care pattern (Chan build-record skeleton re-cut as claim-vs-record teardown with PRESENT mode). Use whenever a founder/counterpart asks for direct feedback on their essay, pitch, or company and the deliverable is a read-at-any-depth teardown page plus a hand-sent note.
---

# Teardown page factory — source MDs → live <name>.arcs.care surface

Proven instance: `public/wing.html` (wing.arcs.care, shipped 2026-08-23, PR #153).
Ancestor design system: `public/chan.html` (chan.arcs.care). Do not re-derive either;
clone `wing.html` and re-fill. The CSS tokens, section mechanics, and PRESENT engine
are FROZEN; only content and slide data vary per counterpart.

## Inputs (the spec)

| Param | Example (wing) | Notes |
|---|---|---|
| `counterpart` | Sean Wing | Person who asked for the teardown |
| `subject` | "The End of Managing Money Alone" | The essay/pitch/company under teardown |
| `subdomain` | wing | → `public/<subdomain>.html` + `<subdomain>.arcs.care` |
| `source_mds` | md(2) readable + md(1) forensic | The already-run teardown reports. The page PROJECTS them; it never adds claims |
| `register` | "asked for the good, the bad, and the ugly" | The counterpart's own stated tolerance, quoted in the lede |
| `threads` | gold / red / vermillion | sound / unresolved-load-bearing / urgent-cheap |
| `stat_strip` | CRD · $124T · ~$128K/2 · 1 afternoon | 4 numbers: 2 verified-green, 1 gap-red, 1 fix-gold |

## Component inventory (what maps to what)

| Content shape in source MD | Component in the template |
|---|---|
| Claim vs. public-record pairs | `.echo-row` (claim ↔ record + "Why it matters" footer) |
| Gauge checklist (license? scale? disclosure?) | `.gauge-grid`, dot color = status (green/gold/red) |
| Timing/kairos bullets, gauntlet lenses, numbered frameworks | `.learn` rows (left-border color = thread) |
| Entity/filing chronology | `.ms-list` forensic timeline |
| Objection tables, pre-mortem tables | `.risk-table` inside `.tbl-scroll` + severity `.chip`s |
| Jargon | `.term data-def` tooltips + Legend section (every term, plain words) |
| Recapitulation + recommendation | Shavasana section: fix-now (verm) / needs-growth (red) / the-gift (green) |

Read-at-any-depth = the focus-bar + collapsible sections with `.sec-tldr` one-liners
(every section MUST have a tldr; collapsed tldrs ARE the exec read).

## PRESENT mode (the deck)

The pres engine is embedded in the file. Only `SLIDES` and `CH` (act colors) change.
Slide schema: `{act, ac (accent), chip, g (grade key), h, b, div?, num?, horizon?}`.
Arc for a teardown: OPENING (method) → ACT I divider + 2-4 verified slides →
ACT II divider + 2-3 gap slides (incl. the pathogen claim) → ACT III divider +
2 forensic slides → THE FIX (sequence by cost) → THE GIFT (what they get to keep) →
YOUR MOVE (horizon: true, the surgical question).
Earned fidelity is enforced in `presRender`: verified `g` renders `res-sharp`, gaps
`res-degraded`, unresolved forensic `res-grain`. Never present a gap at sharp.

## Ship gates (all BLOCKING, run before push)

1. **No-new-claims gate**: every fact on the page traces to a source MD line. The page
   is a projection, not a second analysis. Diligence framing stays: "question, not
   allegation" register line in the footer is mandatory for any forensic content.
2. **Em-dash rule (final pass)**: counterpart-facing copy carries ZERO em-dashes.
   Enforce mechanically: `grep -c "—" public/<subdomain>.html` must print `0`.
   Rewrite with periods, commas, or colons; never just delete the dash.
3. **Tripwire**: `bash scripts/tripwire.sh public/<subdomain>.html` → clean.
4. **Leak check**: `bash scripts/leak_check.sh` → no internal markers on the new file;
   include the `/_vercel/insights/script.js` snippet + the section-dwell script.
5. **Pixels**: screenshot locally (Browser pane opens the file on Write) at top,
   one open section, and one pres slide AFTER the fade settles. Never grep-verify UI.
6. **noindex**: `<meta name="robots" content="noindex, nofollow">` — these pages are
   unlisted-by-URL, never linked from the mothership.

## Routing + deploy (chan pattern, single-destination host)

1. One line in `next.config.ts` beforeFiles:
   `{ source: "/:path*", destination: "/<subdomain>.html", has: [{ type: "host", value: "<subdomain>.arcs.care" }] }`
   (multi-path pages use `src/proxy.ts` MULTI_PATH_MAP instead; see prl-page-factory.)
2. Commit on a branch → PR → merge to main (pre-push hook runs `npm run build`).
3. Wildcard `*.arcs.care` is already attached to the Vercel project: the subdomain
   serves as soon as main deploys. Verify live: `curl -s https://<subdomain>.arcs.care/ | grep -o "<title>[^<]*"`.

## The note (never auto-sent)

Draft the counterpart message to `_ARTIFACTS/<subdomain>-<name>-linkedin-draft.md`:
lead with their own ask quoted back, the link, then good → bad → ugly in that order,
close with the surgical question AND the gift. Same em-dash rule. Zach sends by hand.

## Efficiency contract (post-mortem 2026-08-23, wing run burned ~20% of a 5h window)

The first wing run paid one-time archaeology costs this skill now amortizes. Rules that
keep the next run at ~1/3 the spend:

1. **Never read `chan.html`** (1,611 lines). Clone `public/wing.html` and re-fill; the
   CSS + PRESENT engine travel with it.
2. **Dedupe inputs before reading.** If a PDF has an MD twin, the PDF is never opened
   (PDF pages are vision-priced). Sample >200KB logs head/tail only.
3. **One branch, one build, one PR.** Page + deck + note + favicon + polish ship
   together. Never sequential PR cycles for one deliverable family.
4. **Quiet pushes**: `git push 2>&1 | tail -3`; `--no-verify` for docs-only pushes.
5. **Pixel protocol**: front the Browser tab BEFORE capturing (hidden pane returns
   black frames); max 3 checkpoint screenshots: hero, one open section, one settled
   pres slide. Verify structure via DOM metrics, not repeated screenshots.
6. **One CI watcher, armed after the final push**, never before an expected commit.
7. **Spec-first invocation** is the ideal input packet: "run teardown-page-factory for
   <name>" + one deduped source MD + spec params. Full scope stated upfront.
