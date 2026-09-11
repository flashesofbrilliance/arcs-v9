# Dealroom Talent — Report Grammar & MCP-Led-Growth Study
*Delegated research crawl, 2026-09-04. Source: public pages at dealroom.co/talent (+ /pricing, /mcp). MCP endpoint mcp.dealroom.co was NOT called — only read about on public pages.*

## Overview
Dealroom's `/talent/` hub is packaged as **"Startup talent, four ways"** — four productized surfaces (Founder DNA, Operator Talent, Founder Mafias, Just Founded; plus University Networks) over one **"people graph."** It reads as a premium research product, not a dashboard, via a consistent kit: small-caps grey **eyebrow** over a **serif display headline with one italic accent word** ("Founder *mafias*."), a persistent sticky **talent sub-nav** (emoji glyph + label; active = purple pill), breadcrumbs, and a near-monochrome palette (white ground, near-black text, one **indigo primary ~#5b3df5**, **green reserved for LIVE/data**). Every product leads **viz-first** (chart/feed above the fold, prose beneath); numbers are **always paired with a denominator** ("1,672 of 4,712 founders"); the whole thing is a **freemium funnel** (free overview → mid-scroll email gate → 🔒 locked filters → book a demo). Every chart ships a **"Download PNG (agent endpoint)"** and every product exposes a Platform/API/**MCP** access triad — the reports are built to be consumed by agents.

## Per-product formatting patterns
- **Founder DNA** — numbered 5-section scrollytelling (`01·ORIGINS … 05·THE SCORE`). Signature = the **paired flip-flow chart** (left source bars ↔ right destination bars, linked by hover, big all-caps callout stat above). Ranked horizontal bars with flag glyphs + right-aligned tabular counts; toggle segmented controls; **three-number stat trios** (big number / label / fine-print denominator); a node-link **lineage map** (§04); closes on **"The Score"** — a distribution curve with the right tail annotated (descriptive stats → predictive product).
- **Operator Talent** — "Coming Soon" (the slot itself is roadmap signaling).
- **Founder Mafias** — a **card grid of 73 mafias** (not one graph): parent logo centered, ringed by **circular monogram avatars** (alumni founders), `COUNTRY·SECTOR` eyebrow, name, and a **two-metric line** ("$1.9T alumni EV · 125 startups"), ranked by alumni EV. **Live auto-scrolling ticker** of newest breakouts; **counted facet filters** ("Fintech (17)"). Real node-link graph is gated.
- **Just Founded** — a **dated LIVE feed** ("refreshed every other day"). Company cards: status pill (PRE-FUNDING/FUNDED), name, `City·Founded`, a **verbatim founder tagline**, **monogram avatars + "Ex-Company" lineage**. Freemium via **🔒 locked filter rows** and blurred teaser cards. Access triad as three icon cards (🔎 Platform / 🔌 API / 🤖 MCP).

## Reusable takeaways for an ARCS founder/operator/talent surface
1. Lead viz-first, caption-second; open each section with the chart + an all-caps callout stat.
2. **Always pair a number with its denominator** — the single biggest "this is research, not marketing" move.
3. The **paired flip-flow chart** (source→destination, hover-linked, headline stat above) transfers to any "X came from / X ended up" dimension.
4. **Monogram-avatar clusters around a hub logo** render a network cheaply; reserve the true node-link graph for premium depth.
5. **"ex-Company +N" lineage badges** compress a career into one pill with graceful overflow.
6. **Exactly two headline numbers per card** — resist more.
7. **Counted facet filters** ("USA (34)") — the distribution is the insight.
8. **Numbered section spine** + serif headline + one italic accent word = long-scroll authority.
9. Reserve one semantic color (green = LIVE/data); keep the accent for brand; everything else near-monochrome so data pops.
10. Ranked tables with glyph row-tokens + right-aligned tabular numerals read Bloomberg-grade.
11. **Close the analytical arc on a predictive "Score"** (distribution + right-tail annotation) — maps directly to ARCS NCI / a founder-DNA score.
12. Freemium seams (inline email gate, 🔒 rows, blurred cards) are design elements, not afterthoughts.
13. Dated "LIVE / last refresh" stamp + auto-scroll ticker = cheap always-on freshness signal (fits an ARCS "just founded"-style receipt feed).
14. Persistent product sub-nav with emoji glyphs ties a family of surfaces into one system; "Coming Soon" slots signal roadmap.
15. **Ship every chart with a machine-readable export** ("Download · agent endpoint") — design reports to be consumed by agents.

## Access / productization model + MCP-led growth (the sharp lesson for ARCS)
**Tier ladder** (self-serve priced, MCP threaded as the up-sell axis): Premium €12,600/yr (MCP "free with every seat, limited time") → Premium Plus €17,000/yr ("Most Popular," MCP connection access) → Enterprise (full API + "hosted MCP server for AI agents," SSO) → standalone **API + MCP** (hosted at mcp.dealroom.co, real-time sync).

**How MCP is positioned** (`/mcp/`):
- **PLG, not enterprise-gated**: "Bring Dealroom into your AI tools — free with every Premium seat, no setup, just sign in." MCP is the *land*; the API is the *expand*.
- **Trust as the wedge**: "Every answer is live Dealroom data, attributable to its source — not the model guessing." MCP sold as the anti-hallucination layer. **Nearly identical to ARCS's receipts / attributable-not-guessing promise.**
- **Client sprawl**: Claude.ai, Claude Code, Cursor, VS Code, Codex, Gemini CLI, Perplexity — copy-paste setup per client.
- **22 read-only tools**, verb+entity namespaced (`search_companies`, `analyze_founder`, `entity_alumni`) — safe by construction ("every tool reads, nothing changes").
- **A prompt-pack PDF + templated example prompts** teach the workflow; "skills & plugins coming soon" productizes onboarding itself.
- The **"agent endpoint" PNG downloads on every chart** mean the content-marketing surfaces ARE the MCP on-ramps.

**Takeaways for an ARCS MCP-led-growth motion:**
1. Make **MCP the free land layer on top of a paid/authed core**, not enterprise-only — "free with your seat, just sign in, no setup" kills activation friction; the API tier captures expand revenue.
2. Lead with the ARCS-native trust claim: **"every answer is a live, attributable ARCS receipt — not the model guessing."** Attribution IS the MCP value prop, and it is already ARCS's core promise.
3. Ship **read-only, verb+entity-namespaced tools** (`analyze_receipt`, `search_decisions`, `compare_founders`, `entity_lineage`) — safety-by-construction is part of the pitch.
4. Publish **per-client copy-paste setup + a prompt pack + example JTBD workflows** ("use the ARCS connector to file the ex-ante receipt before my call"). Teach the job, not the schema.
5. **Turn every public content surface into an MCP on-ramp** — a "Connect an agent →" affordance on each ARCS report/receipt so the marketing artifact and the connector are one funnel.
6. Pre-announce a **"skill + one-click recipe"** as coming-soon; limited-time-free framing creates activation urgency.

## URLs to revisit
- dealroom.co/talent/ (four-ways hub) · /talent/founder-dna/ (best chart grammar) · /talent/founder-mafias/ (JS-rendered; card grid + ticker) · /just-founded/ (JS-rendered; feed + locked-filter freemium) · /pricing/ · /mcp/
