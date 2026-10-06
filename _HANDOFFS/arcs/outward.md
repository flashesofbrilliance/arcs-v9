# Arc: outward (reconstructed 2026-10-06)

> The outward arc is everything a stranger can see: good.arcs.care (the public-goods and NFTT essay
> surface), the build/status faces, the Reading Room (Concordance, Almanac, Chronicle), the brand mark
> and icons, and the LinkedIn posts the essays grow from. From mid-July to early October 2026 it moved
> from one-off branded pages (v3.9.0) to a governed publishing system: a single literary NFTT template,
> head-meta and contrast conformance gated in CI, publish timestamps and a serialized thread spec,
> dated LinkedIn originals in every byline, a Möbius icon set served on every host, and OG cards pinned
> to app.arcs.care. What remains is mostly publishing decisions only Zach can make, plus a few
> generator and verification loose ends.

## Goal
Every public ARCS surface tells the truth about itself at earned fidelity: one brand mark, one token
source, honest provenance (dates, originals, receipts), and gates that fail the build on a whole bug
class (wrap, contrast, slop, tao coverage) rather than a single instance.

## What changed
- v3.9.0 (2026-07-19): branded receipt error/fallback page (part of #100).
- v3.18.0 (2026-07-24): status.arcs.care commit links 404 after the repo went private; "showcase mirror"
  idea opened.
- v3.36.0 (2026-08-17): good.arcs.care gains the OSS family install band (arcs-skills made visible).
- v3.53.0 to v3.57.0 (2026-09-04 to 09-07): universal ARCS Field OS wordmark on good/build/status nav;
  NFTT "Confirmed Not My Bug" live; NFTT post-4 impeccable pass clean; Reading Room tenant plan.
- v3.58.0 (2026-09-08): #312 retires the threaded `story_render.py` engine, literary template is the
  only NFTT standard; #348 "The Factory on Itself" live.
- v3.59.0: "Assets and Liabilities" essay and the Field Instruments chapter (good.arcs.care/instruments).
- v3.60.0 (2026-09-11): 720-degree brand-coherence session; #405 duality backlinks on build + good.
- v3.65.0 (2026-09-24): #490 "The Question That Found the Outage"; `token_source_gate` exempts the
  self-contained blog-nftt-* serif system.
- v3.66.0 to v3.67.0 (2026-09-26): cold-reconstruction NFTT trilogy; #510 slop_lint in the FE ship
  gate; whole-corpus head-meta conformance and contrast repair. Receipt
  `2026-09-26--nftt-dossier-contrast-and-gate-merge--ZH`.
- v3.70.0 (2026-09-28): good.arcs.care/audit "We keep our own ledger" card.
- v3.72.0 (2026-09-30): #651 Reading Room tenant 3, the Chronicle ("Drishti").
- v3.74.0 to v3.76.0 (2026-10-04): publish timestamps (`e6b54862`, `scripts/nftt_published.py`);
  serialized thread spec (`d606f62d`, `runtime/specs/nftt-series.json`); doctype fixes; dated
  LinkedIn originals in bylines (#697, #703, #706); #718 closes post-1 brief/exec wrap-lint.
- v3.77.0 (2026-10-04): "Tribes, Vibes, Lies" becomes draft PR #700 (preview, unrouted).
- v3.88.0 (2026-10-05): Möbius icon set replaces the "A" glyph: #814 (`d2a38a54`), #824 (`c18ea2ef`,
  shared icons excluded from host catch-all rewrites).
- v3.95.0 (2026-10-05): #848 (`996b0418`) pins OG image base to app.arcs.care; icon sweep 85 of 92
  hosts clean.
- v3.110.0 (2026-10-06): #661 LinkedIn queue matches what was scheduled; #912 `nftt_claim_batch.py`
  claim-check pilot recovered and merged.

## State
- 42 public NFTT pages (blog-nftt prefix, .html) on this worktree's tree (cut from origin/main).
- Reading Room API tenants on main: almanac, chronicle, concordance (`src/app/api/reading-room/chronicle/route.ts` (and almanac, concordance)).
- PR #700 is OPEN (draft); the Tribes, Vibes, Lies page file is not on main.
- Branch `claude/showcase-mirror` no longer exists on origin (ls-remote empty); no showcase-mirror
  PR found merged. status.arcs.care commit links: still broken (unverified live).
- Icon/OG commits `d2a38a54`, `c18ea2ef`, `996b0418` are ancestors of origin/main.
- Live admin render of app.arcs.care/reading-room/chronicle (unverified).
- Real LinkedIn/Slack/X unfurl of the new OG image (unverified).

## Decisions
- The literary NFTT template is the only standard (#312); never revive the threaded engine.
- A new NFTT page needs a tao proverb citing it or a declared waiver (`tao-coverage` pre-commit).
- Bylines say "From the LinkedIn original(s), <dates>", never "first published on LinkedIn": a label
  that sounds right can be false; verify each date.
- Tokens come from the kit; blog-nftt-* is the sanctioned exemption to `token_source_gate`.
- Shared icons and OG assets are served from one place (app.arcs.care); never from a client host.
- Publishing an essay needs Zach's explicit bless, merge with `--merge`, and one decision receipt.
- Ledes span the full lane except text index pages (good.arcs.care/series/*), which use the 680px measure.

## Open
1. Zach: finish or abandon draft #700 ("Tribes, Vibes, Lies"): fill the two placeholders, re-measure
   the 2/247 stat, mint a tao proverb, route in `src/proxy.ts`, add to the index, stamp, page-gate,
   bless.
2. Confirm `scripts/nftt_index_build.mjs` reproduces the live index without dropping posts (claimed
   stale on 10-04, after the 10-03 CI gate `e9085fd7`).
3. Tao backfill: confirm whether any routed NFTT post still lacks a proverb (4 were uncovered on 10-04;
   batches #617/#618 predate that).
4. Showcase mirror for status.arcs.care: the branch is gone; decide rebuild or drop.
5. Zach: LinkedIn headline/About still say "Product" and omit ARCS; pre-registered promo A/B
   (10-05 vs 10-12) readout pending.
6. Verify the Chronicle admin render and a real social unfurl of the OG card.
7. Placement idea: Apex Spine as the center reading room of the Alexandria performer (not integrated).

## Next action
Run `node scripts/nftt_index_build.mjs` in a worktree and diff against `public/` NFTT index; if it drops
posts, fix the POSTS list before any new essay (including #700) is routed.

## Cold-start
- Files: public NFTT pages (blog-nftt prefix, .html), `src/proxy.ts`, `scripts/nftt_index_build.mjs`,
  `scripts/nftt_index_layout.json`, `scripts/nftt_published.py`, `scripts/nftt_series.py`,
  `runtime/specs/nftt-series.json`, `scripts/artifact_wrap_lint.py`, `src/app/icon.svg`,
  `next.config.ts` (`withSharedIcons`), `src/app/api/reading-room/chronicle/route.ts` (and almanac, concordance).
- Commands: `gh pr view 700`; `git log origin/main --oneline -- public (glob on the blog-nftt prefix)`;
  `git ls-remote origin claude/showcase-mirror`.
- Skills: `nftt-story-factory`, `tao-mint`, `impeccable`.
- Tracker: tech-debt artifact `debt` collection, filter outward/nftt rows.
- Memory: `nftt-literary-template-is-the-standard`, `nftt-provenance-events-and-aphorisms`,
  `nftt-collision-both-posts-carried-same-false-timeline`, `good-arcs-care-embed-blog-prefix-and-probe-poison`,
  `linkedin-promo-post-engagement-playbook`, `design-full-width-lede-matches-heading`,
  `single-file-artifacts-inherit-tokens-never-copy`, `arcs-v9-repo-now-private-status-links-broken`.
