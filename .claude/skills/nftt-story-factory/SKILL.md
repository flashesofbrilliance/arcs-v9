---
name: nftt-story-factory
description: Author and ship an NFTT post (Notes-from-the-Trenches class) at good.arcs.care/blog/nftt/<slug> in the LITERARY theme (the take-home-trap "With Life" standard) — a hand-authored editorial essay from a shared HTML template, routed via src/proxy.ts and carded on the index. Use whenever writing a new NFTT post.
---

# NFTT story factory — a literary essay, shipped at /blog/nftt/<slug>

The live NFTT series is **hand-authored editorial HTML** in one shared template: the
take-home-trap "With Life" standard. You clone the template chrome, write the essay as prose
sections, wire the route, add the index card, pass the gates, ship. There is no renderer and no
JSON envelope in this path.

- **Gold standard (chrome + register):** `public/blog-nftt-take-home-trap.html`
- **Latest worked example (this recipe, gauntlet-clean):** `public/blog-nftt-confirmed-not-my-bug.html`
- **Closest reflective-voice peer:** `public/blog-nftt-post-2.html`

> The data-driven THREADED engine (`story_render.py` + `.story.md` envelopes + `-full.html`
> renders) was **retired 2026-09-07** and lives in `_ARCHIVE/nftt-threaded-engine/` (see its
> README). The live series abandoned the braid; do not resurrect it for a normal NFTT post. It is
> kept only for a genuinely braided story (e.g. breach / patched / residual-risk threads), and even
> then, prefer the literary template unless the braid is load-bearing.

## The one idea: one template, N essays

The `<head>` + `<style>` block is a shared design system (Newsreader serif body, IBM Plex Mono
chrome, cyan/green/gold accents on the `#020408` void, 40rem wrap). It is **cloned verbatim** from a
reference post, never hand-retyped. Only the title, description, and the `<body>` essay change.

## Make a new post

```bash
# 1. clone the gold standard as your starting file
cp public/blog-nftt-take-home-trap.html public/blog-nftt-<slug>.html
```
Then, in the new file:
- **`<head>`**: change `<title>` (`... · NFTT`), the `<meta name="description">` (one real sentence,
  no em-dash), keep `robots`, keep the fonts/`<style>` block byte-for-byte.
- **`<body>`** (the only prose you write): the shared block grammar below.

```bash
# 2. route it — add to the 'good' block in src/proxy.ts:
#    '/blog/nftt/<slug>': '/blog-nftt-<slug>.html', '/blog/nftt/<slug>/full': '/blog-nftt-<slug>.html'
# 3. index it — add a card to public/blog-nftt-index.html:
#    new card = "Latest"; demote the previous "Latest" to its number (No. N).
# 4. run the gates (below), then commit; good.arcs.care deploys from main.
```

## Body block grammar (the literary devices — all already in the template CSS)

| Element | Purpose |
|---|---|
| `.topbar` (dot + "Notes from the Trenches" + `.sp` tag) | masthead; `.sp` is a short thematic tag or `No. N` |
| `.eyebrow` (mono, cyan) | the kicker line |
| `h1` (serif) | the title |
| `.standfirst` (italic) | the map/hook, one or two sentences |
| `.byline` (mono) | provenance line (e.g. redaction note, or "receipts included") |
| `section` + `.num` (`I · Heading`) | roman-numeral movements |
| `p.lead` (first para of section I) | cyan drop-cap opener |
| `.panel` + `.step` (`.k` / `<b>`) | a structured "receipts included" box (ledger, checklist, steps); `<code>` renders gold |
| `blockquote` | cyan-bordered pull-quote — the line that must survive |
| `.more` | the "read the rest of the series" link |
| `footer` | the standing grounded-claims footer |

Register: calm, precise, receipts-included. The unproven parts are marked unproven. See WORLD.md
tonal register (Myst, not SaaS).

## Ship-gates (blocking — verify every one before commit)

1. **Zero em-dashes** anywhere: `grep -c '—' public/blog-nftt-<slug>.html` must be `0` (also check
   en-dash `–` and minus `−` if you typed ranges).
2. **Head hygiene**: `robots` meta present; a non-empty, one-sentence `description`; title ends `· NFTT`.
3. **Contrast**: any custom color you introduce clears WCAG AA (>= 4.5:1) on `#020408`. The template
   palette already passes; re-check only what you add.
4. **Four-width sweep** 375 / 790 / 1024 / 1280: no horizontal overflow, `.panel` stacks to one column
   at <=520px, measure consistent. (Wrap-regression class, PRODUCT.md.)
5. **Wrap-lint** pre-commit hook passes (fires automatically on `git commit`).
6. **Build green**: `npm run build` (validates the proxy.ts route change; NODE_ENV pinned, per AGENTS gotcha 4).
7. **Depth ladder never dead-links**: the single served file answers both `/<slug>` and `/<slug>/full`;
   do not link tiers that do not exist.
8. **PII / counterpart gate** (publish is outward-facing): scan for any real name/email; if a real
   counterpart is involved, apply the pseudonym/redaction convention before the publish-bless.

## Publish-bless (consent gate)

This is public content. Render + verify locally, then **STOP and show the local file for bless BEFORE
adding the proxy route / deploying**. Draft-first. Do not publish on your own authority.

## After shipping

- Verify live (`curl -s -o /dev/null -w '%{http_code}' https://good.arcs.care/blog/nftt/<slug>` = 200).
- Witness/receipt the ship; update `_STATE/pickup-prompt.md` if a loop tracked it.
- Handoff per CLAUDE.md policy.
