# Profile Scan — Spec v1

**Status: SPEC — not yet wired to live data**
**Date:** 2026-06-23
**Source:** Canonical ARCS Document UIKit (`patterns.jsx` — "CANONICAL source of truth" per its own header), confirmed against the live `ui_kits/documents` Atom Isolation Reference. Input-tier contract confirmed directly by Zach this session.
**Supersedes:** the Perplexity-research PRD's "interactive SIMPLE/RICH/DEEP scanner with live score gauges and mode toggle" — that direction was explicitly rejected in favor of the canonical document shape below.

---

## What Profile Scan is

Profile Scan is a generated **document**, not an interactive app screen. It belongs to the same document family as Recoil Report, Brief, Prep Doc, and Receipt — all five are registered in `DOC_TYPES` in `patterns.jsx`. Profile Scan's entry: `{ id:'profile', label:'Profile Scan', mono:'PROFILE', accent:T.green, icon:'◈' }`.

It reads a person's signal (not the operator's own live state — that distinction killed the Perplexity PRD's framing) and produces a structured report on the pattern underneath it.

## Canonical document shape

Composed from existing `patterns.jsx` molecules, in this order:

1. **CoverBlock** — hero: badges (`Profile Scan` solid pill + tier pill), h1 title, subtitle, mono metadata line, action buttons. Accent: `T.green`.
2. **TwoColumn** ("01 · Signal Read") — left panel "what the input says" (stated/surface read), right panel "what it actually signals" (inferred read). Dark-left/standard-right contrast per the pattern's convention.
3. **SidelineList** ("02 · Thread Assessment") — four-thread read, left-border-accented cards:
   - Red Thread — recurring risk
   - Gold Thread — working asset
   - Green Thread — conviction / load-bearing strength
   - Vermillion (orange) — constraint / gap
4. **DataTable** ("03 · Evidence Ledger") — chronological rows of prior decisions/receipts showing the pattern recurring (or breaking).
5. **SmartGrid**, 2 cols ("04 · Capability Map") — four quadrants (Core / Compound / Signal / Gap).
6. **QuoteBlock** ("05 · Key Assertion") — single load-bearing sentence, attributed to "ARCS Profile Scan · Thread Analysis".

All tokens, spacing, and color math (`DIM(c)=c+'16'`, `BDR(c)=c+'35'`, `GLOW(c)=c+'55'`) are taken verbatim from `patterns.jsx` — no new visual language invented.

A throwaway HTML mockup of this exact composition was built and reviewed this session (claude.ai visualize widget, illustrative content only, not committed to the repo).

## Input tiers (revised — supersedes the original three-upload-types decision below)

**Original decision (session start):** three distinct, explicit input paths — SIMPLE=LinkedIn URL, RICH=profile PDF upload, DEEP=full data export upload, no auto-upgrade between them. **Revised after live testing** (SIMPLE-tier URL fetch turned out to be blocked — see finding above) to a single-input model:

| Tier | Input | Output depth |
|---|---|---|
| SIMPLE | LinkedIn profile PDF (the standard "Save to PDF" export) | Lightest report — likely just CoverBlock + QuoteBlock, or a thin TwoColumn |
| RICH | Same PDF input | Fuller report — adds SidelineList thread assessment + DataTable evidence ledger (dated tenure, confirmed available from this input in testing) |
| DEEP | PDF **plus** the full LinkedIn data-export ZIP as an enrichment layer | Fullest report — adds the export's qualitative signal (recommendation-text energizers/drainers, skill endorsements, connections breadth) on top of the PDF's dated structure, per the cross-tier finding above |

All three tiers now key off the same primary input (the profile PDF); DEEP is an *enrichment* of RICH with a second, optional upload, not a third independent input type. This also resolves the SIMPLE-tier blocker outright — no LinkedIn URL fetch needed at any tier.

**Not yet decided:** whether DEEP requires the full export or treats it as optional-but-recommended; what specifically gets added/removed from the document sections at each depth (the v1 draft above maps loosely to the SIMPLE/RICH/DEEP output-depth ladder, not confirmed section-by-section).

### DEEP tier is currently leaving most of its own input on the table

Opened the real export ZIP and counted rows directly (not inferred from the parser's output) — `linkedin_export.py` surfaces a small fraction of what's actually present:

| Dimension | Present in export | Currently parsed/surfaced |
|---|---|---|
| Connections | 11,235 rows | Just the count (`network_size`) |
| Recommendations received | 31 full text | A handful, sampled into `energy_signals` |
| Endorsements received | 765 rows (`Endorsement_Received_Info.csv`) | **0 — not parsed at all** |
| Skills | 100 listed (`Skills.csv`) | 15 (`skill_clusters`) |
| LinkedIn's own ad-targeting inferences about the user | 8 rows (`Inferences_about_you.csv`) | **0 — not parsed at all** |
| Authored articles | 38 full HTML essays (`Articles/Articles/*.html`) | **0 — not parsed, not even enumerated** |

Two of these are qualitatively different signal types than anything the document currently has a slot for:
- **`Inferences_about_you.csv`** is LinkedIn's own model of the person (ad-targeting categories like "Affinity for Electric Vehicles," "Interested in media about technology"), not biographical data. This is a genuinely separate input class — call it the "platform inference" layer — and the canonical document shape (CoverBlock/TwoColumn/SidelineList/DataTable/SmartGrid/QuoteBlock) has no existing section built for it.
- **38 full authored articles** is a large first-person long-form corpus, distinct from the short recommendation quotes the thread assessment currently draws on.

**Implication:** "DEEP = PDF + full export enrichment" undersells what DEEP could be. The export alone, fully used, materially increases scan resolution beyond what the current `linkedin_export.py` extracts — this is a parser-completeness gap, not just a future nice-to-have. Worth deciding whether to (a) extend `linkedin_export.py` to use these fields before building anything else, or (b) ship DEEP v1 against the current partial parse and treat full-field coverage as a fast-follow.

**Decided: (a).** Extended `/Users/zharris/arcs_cfa/arcs_cfa/linkedin_export.py` this session (not yet committed — `arcs_cfa` isn't a tracked-in-memory repo, check its own git status before assuming this is safe to leave uncommitted). Changes, all verified against the real export:

- **Fixed a real bug, not a data limitation:** `_parse_positions` only ever tried `datetime.strptime(date, "%Y-%m-%d")`, but LinkedIn's actual export dates are bare years (`"2025"`) or `"Mon YYYY"` (`"Jan 2020"`) — every row threw, was caught by a bare `except:`, and silently produced `tenure_years=None` for 100% of positions. This is why DEEP tier's `tenure_patterns` came back empty earlier this session. Added `_parse_linkedin_date()` trying `%Y-%m-%d`, `%b %Y`, `%B %Y`, `%Y` in order, returning `None` (not swallowing) on failure. Re-ran on the same real export: 16 real tenure values now populate, `years_experience` computes to ~32.1 (this sums tenure across all positions including concurrent ones — a pre-existing semantic question, not something this fix introduced or resolved; "years of experience" via simple sum over a portfolio career with concurrent roles is its own open modeling question, flagged but not changed).
- **`skills_full`** — new field, all 100 skills with real per-skill endorsement counts (e.g. Advertising: 92, Digital Strategy: 72, Marketing: 51), not just the 15-skill `skill_clusters` cut.
- **`endorsements_total`** — new field, real count (765 on the test export), previously discarded after being used only to rank the top-15 list.
- **`platform_inferences`** — new field + new `_parse_inferences()` parsing `Inferences_about_you.csv`. This is LinkedIn's own ad-targeting model of the user (category/type/description/value), a genuinely different signal class than anything biographical. No document section currently consumes it — still needs a slot designed.
- **`articles`** — new field + new `_parse_articles()` parsing the 38 raw HTML files under `Articles/Articles/`, stripped to plain text via `bs4` (falls back to a regex tag-strip if `bs4` isn't installed — the project's own `venv` has it, the system `python3.11` does not). Verified real extraction: longest article came back as 6,013 words of real body text. **This is the primary input for the Rhetorical Resonance Engine (PRD-B, from the original Perplexity doc)** — first-person long-form corpus is exactly what an audience/altitude/resonance model would need, more so than short recommendation-quote snippets.
- **Environment note:** this module requires Python ≥3.10 (`str | Path` union syntax) and, for article parsing, `bs4`. The system default `python3` is 3.9.6 and lacks `bs4`; `arcs_cfa`'s own `venv/bin/python3` (3.11.14) has both. Anything that calls this module needs to either run inside that venv or have its own equivalent.

## Known gaps before this is buildable

- **Source-of-truth location unconfirmed.** `patterns.jsx` was read from `~/Downloads/patterns.jsx`, a local file, not from a repo. Its own header says it's loaded by `ui_kits/documents/index.html` and "the integration/Step1 Atom Reference" — neither of those paths exists in `arcs-v9`. Before this spec can be implemented, find/confirm which repo actually owns `ui_kits/documents/` (candidate: `arcs-field-os`, unverified) and port or vendor it into `arcs-v9` rather than building against a Downloads-folder copy.
- **No generation pipeline defined yet.** This spec covers the *output shape* and the *input contract*. It does not yet define: how a LinkedIn URL/PDF/export gets parsed into the `TwoColumn`/`SidelineList`/`DataTable`/`SmartGrid` content fields, what model or service does that extraction, or where parsed data is persisted. That's the next spec (`runtime/flows/profile-scan-flow-v0.1.md`, per the original Phase 1 plan), not this one.
- **Relationship to `arcs-field-scan`** (the v0 TS prototype confirmed live on GitHub this session, with its own `DepthMode`/`ScanResult` types) is now an open question — that prototype was built against the *rejected* interactive-scanner framing, not this document framing. Needs a fresh look before assuming any of its code ports forward.
- **LinkedIn data parsing — FOUND.** `/Users/zharris/arcs_cfa/arcs_cfa/linkedin_export.py` already parses LinkedIn data-export ZIPs (positions, education, skills, endorsements, recommendations, connections CSVs) into structured data — this is effectively the DEEP-tier input parser, unbuilt-from-scratch. `/Users/zharris/arcs_cfa/personal_analysis.py` ("Personal Waveform Analysis") already consumes that output to surface energizer/drainer/collaborator patterns, which is conceptually adjacent to (maybe a direct precursor of) the SidelineList four-thread read in section 02 above. Neither file lives in `arcs-v9` or any `arcs-v9` worktree — they're in a separate, previously-untracked-in-memory repo (`arcs_cfa`). Porting/wiring this in is net-new integration work, not net-new parsing logic.
  - **Requires Python 3.11+** — `linkedin_export.py` uses `str | Path` union syntax that fails on the system default `python3` (3.9.6). Confirmed working via `/opt/homebrew/bin/python3.11`.
  - **Tested live against a real export** (`Complete_LinkedInDataExport_06-09-2026.zip.zip`) this session. Output included real energizer/drainer quotes, skill clusters, prior companies, and a `drainer_flags: ["Frequent role changes (5+ positions)"]` signal — but `tenure_patterns` came back empty; the parser does not currently surface dated position history from the full export's CSVs, even though the source data almost certainly contains dates.
- **RICH tier (profile PDF) — tested live, and it's not strictly "less than DEEP."** Read a real LinkedIn "Save to PDF" profile export directly (no existing parser — read and structured manually this session). It contained full dated tenure for every position, which DEEP tier's CSV parse did not surface. Cross-checking the two: DEEP tier's `drainer_flags: "frequent role changes (5+ positions)"` does not survive contact with the RICH-tier dates — 3 of those "5+ positions" (Le woof Brand, Cornell Tech, Outlier Ventures) are concurrent advisor/mentor roles running alongside one 6.5-year anchor engagement (Mañana), not sequential job-hopping. **Implication for the spec:** tier richness is input-dependent, not strictly ordered SIMPLE < RICH < DEEP — a generation pipeline that runs DEEP tier should also check whether a RICH-tier PDF is available and prefer its dated tenure data over the export's undated one. No PDF parser exists yet; this session's structuring was done by hand, not a built tool.
- **SIMPLE tier (LinkedIn URL) — real blocker, not just "unbuilt."** Did not attempt to fetch `linkedin.com/in/zharris` live: LinkedIn requires login to view profiles and actively blocks unauthenticated scraping. Building this tier as "just paste a URL, we'll fetch it" doesn't work without either (a) official LinkedIn API access — requires a partner/OAuth relationship, not just an API key, or (b) asking the user to paste the public profile text themselves, which somewhat defeats the "no friction, just a URL" pitch for the lightest tier. This needs a product decision, not just an engineering task.

## Explicit → implicit inference: content timing vs. network response

Zach's idea: correlate when content was published against downstream audience response (saves, applies, follower influx) to surface "echo" signal — content that doesn't explicitly announce something but produces a measurable, targeted (IYKYK) response from a specific audience. Tested this directly against the real export rather than speculating.

**Hard limit, confirmed by inspection — flag before designing anything around this:** the personal LinkedIn data export contains no audience-side engagement data. `Reactions_8561261.csv`, `Comments_8561261.csv`, `Shares_8561261.csv`, `Saved_Items_8561261.csv`, `Votes_8561261.csv`, `InstantReposts_8561261.csv` are all **outbound** — things the account owner did to *other* people's content, not what others did to *theirs*. There is no per-post view count, no list of who saved/liked/commented on your own posts, and no "applied because of this post" linkage anywhere in this export. That data exists only in LinkedIn's in-app Creator Analytics, which is not part of the personal data export and would need a different acquisition path entirely (manual screenshot, or LinkedIn's separate analytics export if one exists — not verified).

**What's real and did hold up as a proxy:** "Project Titan" turned out to be a regular post (`Shares_8561261.csv`, `ShareCommentary` text match), not a long-form Article — dated 2026-03-01, 2026-06-02, 2026-06-07. Checking `Connections.csv` ("Connected On" dates, all 11,233 parsed) by month: **57 new connections in Feb 2026 → 89 in Mar 2026** (right after the Mar 1 post), and June's partial month (only ~9 days of data in this export) already at **14**, well above April's full-month **22** — both bumps land right after a Titan post. Directional, not proof: small N, no control for other simultaneous activity, and the June comparison is an incomplete month.

**What didn't hold up:** tried endorsement-date clustering as a second independent proxy. `Endorsement_Received_Info.csv` timestamps (765 rows, format `%Y/%m/%d %H:%M:%S UTC` — not documented anywhere, found by inspection) cluster into exactly 3 tight batches (2025-11-04, 2025-11-07, 2026-02-25, seconds apart within each batch) — almost certainly a "request endorsements" campaign or LinkedIn's own bulk-suggestion event, with zero relationship to the Titan post dates. This proxy is noise, not signal, for timing-correlation purposes. Worth knowing before building a feature on top of it.

**Net assessment:** the connections-growth proxy is real and usable as a weak signal (content timing ↔ network response), but "saves and applies" specifically — the part of Zach's example with the most explicit-to-implicit narrative power — isn't reconstructable from this data source at all. If that signal matters enough to build for, it needs a different acquisition path (LinkedIn Creator Analytics export, or a manually-supplied number), not an inference from the personal data export.

**Named example, checked precisely:** "Project Titan" was the article `how-apples-forgetting-machine-killed-apple-carand-what-zach-harris-czw5e` ("Apple's 'Forgetting Machine' Killed the Apple Car"), published **2026-01-29 16:01** exactly (timestamp parsed straight from the article body, not estimated). Re-ran the connections check at daily resolution around that exact timestamp instead of the monthly buckets above:

- **6 new connections on the publish day itself**, vs. a **1.71/day average** for the rest of January pre-publish — a clean **~3.5x same-day spike**, settling back to near-baseline within 2-3 days.
- Checked whether any of those 6 connections list Apple as employer (`Connections.csv` has Company/Position fields) — **none did** (an HR consultant, a UX consultant, and four startup founders/co-founders instead). The "Apple insiders specifically" part of the claim doesn't hold up against this evidence, though it's not strong counter-evidence either: saving/sharing an article internally doesn't require connecting, so an Apple employee engaging with this wouldn't necessarily ever appear in `Connections.csv` at all — which is just a sharper restatement of the hard limit above (audience-side engagement, including who-specifically engaged, is invisible to this export by design).

**Conclusion:** the timing-correlation technique itself is validated — real, sharp, same-day signal exists and is cheaply computable from data already in the export. The specific audience-composition claim (this reached Apple insiders) is plausible and directionally consistent with the spike, but not provable from this data source. Any feature built on this should surface the spike as "this content produced a measurable timing-correlated response" without claiming to know *who* responded beyond what's directly checkable.

**Followers vs. connections — checked, doesn't exist.** Zach asked to compare followers against new connections specifically. There is no followers data anywhere in this export — `Member_Follows_8561261.csv`, `Company Follows.csv`, and `Hashtag_Follows_8561261.csv` are all outbound (who/what *you* follow), and `Profile.csv`/`Profile Summary.csv` have no follower-count field. LinkedIn auto-follows on connect but also allows one-directional follows without connecting, so a real follower count would be ≥ the connection count — that delta is structurally invisible to the personal data export, same root cause as the saves/views gap above. `Connections.csv` is the richest inbound-relationship signal this data source has; there is no second, fuller metric hiding elsewhere in the export.

**Chain effect (not single posts in isolation) — tested, and it's real but conditional.** Zach's hypothesis: LinkedIn's algorithm rewards recycling/teasing the same content across multiple posts, so the connection-growth signal should be checked as a *chain* of related posts, not one isolated publish event. Found the actual chain by keyword-matching the Forgetting Machine article's themes (`titan`, `apple car`, `forgetting machine`) across `Shares_8561261.csv`: 12 posts from 2026-01-29 to 2026-06-08, explicitly self-referential ("In January 2026, I said...", "#ProjectTitan never died"). Measured connections in the 3 days following each post against the 1.82/day window baseline (Jan 1–Jun 9 2026):

| Post date | 3-day total | vs. baseline |
|---|---|---|
| 2026-01-29 (original article) | 10 | 1.8x |
| 2026-02-03 | 3 | 0.6x |
| 2026-02-10 | 2 | 0.4x |
| **2026-02-25** ("#ProjectTitan never died") | **19** | **3.5x** |
| 2026-02-27 | 10 | 1.8x |
| 2026-02-28 | 9 | 1.7x |
| 2026-03-01 | 11 | 2.0x |
| 2026-05-25 (first mention after a 3-month gap) | 3 | 0.6x |
| 2026-06-02 | 9 | 1.7x |
| 2026-06-05 | 4 | 0.7x |
| 2026-06-07 | 1 | 0.2x |
| 2026-06-08 | 0 | 0.0x |

**The hypothesis holds, conditionally.** The Feb 25–Mar 1 stretch is four consecutive posts all running above baseline together, peaking at the Feb 25 post and sustaining through Mar 1 — real evidence that tight-cadence recycling compounds response rather than each post standing alone. But the June reactivation after the 3-month gap doesn't inherit that momentum: the gap-breaking post (May 25) underperforms baseline, and the brief June 2 bump decays to near-zero within days (Jun 7–8). **Conclusion: chaining is real but cadence-dependent** — sustained near-daily/weekly recycling compounds engagement; a single post resuming a stale thread does not automatically get the earlier chain's lift. n=12 posts on one account; treat as a directional pattern worth designing around, not a proven mechanism.

**External news-cycle timing — checked against real dates, and it reframes the chain finding.** Zach's hypothesis: LinkedIn's algorithm widens distribution ("edge rank") for posts that land during a relevant external news cycle (e.g. Apple's 50th anniversary, WWDC). Verified the actual dates via web search rather than assuming them:

- **WWDC 2026 ran June 8–12** ([Apple Newsroom](https://www.apple.com/newsroom/2026/05/apple-kicks-off-worldwide-developers-conference-on-june-8/), [MacRumors](https://www.macrumors.com/roundup/wwdc/)).
- **Apple's 50th anniversary was officially April 1, 2026 (founded April 1, 1976), with celebrations running throughout March leading up to it** ([Apple Newsroom, March 2026](https://www.apple.com/newsroom/2026/03/apple-to-celebrate-50-years-of-thinking-different/), [NPR](https://www.npr.org/2026/04/01/nx-s1-5753784/apple-50-anniversary-think-different-myth-reality)).

Both real news pegs line up with the post chain — but the relationship is the opposite of "more news relevance = more reach":

- The strongest sustained cluster (Feb 25–Mar 1, 1.7x–3.5x) sits in the **anticipatory window before** the 50th-anniversary peak (officially April 1), not during or after it.
- The **WWDC keynote-day posts themselves (Jun 7 eve-of, Jun 8 day-of) cratered** (0.2x, 0.0x) — the worst results in the entire 12-post chain — while the lead-in post 6 days before the keynote (Jun 2) got a real bump (1.7x).

**Plausible mechanism, not confirmed:** on the actual peak day of a major external news cycle, every account's feed fills with content on the same topic simultaneously — an individual post's share of attention (and likely its edge-rank competition) may get *worse*, not better, exactly when topical relevance peaks. **Revised conclusion:** external news-cycle proximity does appear to matter, but the actionable pattern is "post in the anticipatory lead-in to a known news cycle," not "post on the day of." This sharpens the cadence finding above rather than replacing it — the Feb cluster's momentum may be partly explained by news-cycle timing, not posting cadence alone; with n=12 these two effects are confounded and not separable from this dataset.

### Correction — real Creator Analytics data superseded the connections-proxy analysis above

Zach supplied the actual LinkedIn Creator Analytics export (`AggregateAnalytics_Zach Harris_2025-06-25_2026-06-24.xlsx` — `DISCOVERY`/`ENGAGEMENT`/`TOP POSTS`/`FOLLOWERS`/`DEMOGRAPHICS` sheets, full year, daily granularity). This is exactly the audience-side data flagged as structurally unavailable from the personal data export above. It confirms some of the proxy-based findings, but **directly overturns part of the WWDC conclusion** — recorded here rather than quietly edited away, per this session's own verify-before-relaying standard.

**Confirmed exactly as predicted:** total followers (12,092 as of 6/24/2026) > total connections from the export (11,235) — followers really is the superset of connections, as flagged as a structural fact (not yet evidenced) earlier in this doc.

**Confirmed and sharpened:** the Jan 29 Forgetting Machine post is the #1 post of the entire year by both engagement (98) and impressions (74,851) — real data agrees with the connections-proxy finding, but reveals the proxy's timing was off: impressions lag the post by roughly a day, not same-day. Jan 29 itself only logged 991 impressions; **56,193 landed the next day (Jan 30)** — the single biggest impression-day in the whole dataset. "Same-day spike" (the connections framing used above) measured a real but much smaller and differently-timed signal than what actually happened.

**Corrected — the earlier "WWDC day-of post crashed" conclusion was wrong.** Real whole-profile daily impressions (`ENGAGEMENT` sheet, baseline 1,029/day) climbed through the entire WWDC week and peaked the day *after* the keynote, not on it: Jun 7 (12,584) → Jun 8 keynote day (14,205) → **Jun 9 (29,876 — second-biggest day in the dataset)** → Jun 10 (16,498). The specific day-of post that scored badly on its own (TOP POSTS: only 2,409 impressions) wasn't the vehicle for the week's real performance — broader profile-level visibility was, and the connections-proxy analysis had no way to see that distinction because it could only measure one narrow downstream effect (new connections), not overall reach. The 60-new-follower, ~20x-baseline spike found in the real `FOLLOWERS` sheet starting Jun 8 lines up with this multi-day impressions wave, not with the individual post's weak stats.

**Confirmed, more clearly:** the Apple-50th-anniversary anticipatory window shows a real, sustained multi-day impressions build — Feb 24 (4,368) → Feb 25 (13,563) → Feb 26 (16,223) — consistent with the anticipatory-timing pattern, independent of any single post "succeeding" or "failing."

**A new finding the connections-proxy method could never have surfaced:** the May 25, 2026 post — which connections data made look like a failed, underperforming reactivation (0.6x baseline) — was actually the **#3 post of the entire year** by both engagement (52) and impressions (51,059). Impressions/engagement and connection-growth are not interchangeable signals and can diverge sharply in either direction; connections-as-proxy should not be relied on alone going forward now that real analytics data exists.

**Implication for the spec:** wherever this work continues, prefer the real Creator Analytics export (`ENGAGEMENT`, `FOLLOWERS`, `TOP POSTS` sheets) over the personal-data-export connections proxy for any timing/resonance analysis — it's not just richer, it changes conclusions, not only their confidence level.

**Access constraint, confirmed from Zach's own LinkedIn screen:** this analytics page (Content analytics, 365-day export) requires LinkedIn Creator Mode — not available on every account. Any feature design that assumes this data source needs a fallback path for accounts without Creator Mode (i.e. most SIMPLE/RICH-tier users probably can't supply this at all).

### The anticipatory-timing pattern wasn't inferred after the fact — it was engineered

Zach confirmed directly: these posts were deliberately timed using ARCS's existing **Trend Surfing** molecule, applied to an "attention value" signal he was tracking via Perplexity, not timed by intuition. Verified this molecule is real, not aspirational — `/Users/zharris/arcs_cfa/arcs_cfa/server.py` exposes `POST /primitives/trend-surfing` (`TrendSurfingMolecule`), a generic velocity/acceleration entry-exit-point detector over any time series (`signal_data`, `velocity_threshold`, `acceleration_threshold`, `time_window` → entry/exit indices + confidence/trend-strength). It's listed in the canon (`operators/docs/ARCS-AtomicDesign-ProductionGuide.md`) as one of 25 molecules, defined but only ~15% implemented/5% production-grade at the canon's own last self-assessment — yet this specific instance clearly was used in production for real timing decisions. **This changes the finding's status from "observed correlation, mechanism unclear" to "this is the validated output of an existing ARCS primitive being used for exactly the purpose it was built for."** Directly relevant to the Rhetorical Resonance Engine (PRD-B): Trend Surfing applied to attention-value signal *is* a candidate implementation for that engine's "adaptive altitude" timing component, not a separate thing to build.

**Open counter-consideration, not resolved — flagged rather than guessed at:** Zach's point: the "feed gets crowded on event-day" mechanism I proposed earlier isn't the only candidate. LinkedIn's homepage surfaces trending content by hashtag — so a hashtagged day-of post could get a *discovery* boost from homepage placement even while losing *feed* share to topic-crowding. These two mechanisms predict opposite things for day-of hashtagged content, and **neither the `DISCOVERY` sheet (just total impressions + members-reached, no source breakdown) nor `DEMOGRAPHICS` (audience composition, not traffic source) can adjudicate between them.** Would need a traffic-source breakdown (feed vs. search vs. hashtag-page vs. homepage-trending) that isn't present anywhere in this export. Leave both mechanisms live; don't pick one without that data.

**Demographic cross-check:** `DEMOGRAPHICS` sheet lists `Apple` as a top-company in the audience (`<1%` — LinkedIn floors anything below 1%, so no exact count available). This is real, partial confirmation of the "Apple insiders" claim from earlier in this doc, which had been flagged as unprovable from the personal-data export alone — now at least nominally evidenced from a different data source, though still not precise enough to confirm the specific same-day-spike-was-Apple-employees claim.

### Trend Surfing extended with jerk (third derivative) — validated, not just theorized

Zach's refinement: surf the slope of the *second* derivative, and use jerk (third derivative) to detect deceleration *before* it shows up in acceleration — catch the peak approaching, not just confirm it after the fact. Checked the existing implementation first: `DeceleratorAtom.is_decelerating()` in `/Users/zharris/arcs_cfa/arcs_cfa/primitives.py` only fires on `velocity > 0 & acceleration < 0` — i.e., only after acceleration has already crossed zero. No jerk/third-derivative existed anywhere in the module before this session.

Added `ThirdDerivativeAtom` (jerk = d(acceleration)/dt) and a new `TrendSurfingMolecule.pre_peak_warning()` method (`acceleration > 0 & jerk < 0` — still climbing, but the climb's acceleration is already falling). Tested directly against the real `ENGAGEMENT` daily-impressions series from the Creator Analytics export, at the two real peaks already confirmed in this doc:

| Event | Real peak day | Old `exit_points()` fires | New `pre_peak_warning()` fires |
|---|---|---|---|
| Jan 30, 2026 (56,193 impressions) | Jan 30 | Jan 30 (same day as peak) | **Jan 29 — one day early** |
| Jun 9, 2026 (29,876 impressions) | Jun 9 | Jun 9 (same day as peak) | **Jun 8 — one day early** |

Both real cases confirm the gap Zach identified: the old signal only *confirms* deceleration once the peak has already happened in the data; jerk genuinely buys a day of lead time in both tests run. This is a validated improvement against real production data, not a theoretical one — but n=2 peak events on one signal series; worth re-checking against more peaks (or other signal types — followers, connections) before treating the 1-day lead time as a stable constant rather than a property of this specific dataset's sampling rate (daily). Changes made directly to `/Users/zharris/arcs_cfa/arcs_cfa/primitives.py`, not yet committed (same uncommitted-`arcs_cfa` caveat as `linkedin_export.py` above).

### A third LinkedIn data surface — the actual "quiet signal" layer

This investigation has now touched three genuinely separate LinkedIn data surfaces, each with different coverage:

1. **Personal data export ZIP** (`linkedin_export.py`'s input) — biographical + the account owner's own outbound activity only. Zero audience-engagement data of any kind.
2. **Content Analytics 365-day export** (the `AggregateAnalytics_*.xlsx` file, Creator Mode required) — aggregate `Impressions`/`Engagements`/`Followers`/`TOP POSTS`, daily granularity, but `Engagements` is a single rolled-up number with no sub-type breakdown.
3. **Live in-app analytics UI** — Zach shared a view showing **Saves: 50, Sends on LinkedIn: 10** over a rolling 90-day window, aggregated across all posts in that window. This is the actual non-public "quiet, IYKYK" signal layer the original saves/applies hypothesis was about (see the "explicit → implicit inference" section above) — and it's real and viewable, just not in either of the two data sources already parsed. Saves and Sends are bookmark/forward actions that leave no public trace (no like, no comment, no repost) — closer to the targeted-insider-echo Zach originally described than any public metric in this doc so far.

**What this doesn't yet give us:** the 90-day figure is a rolling aggregate, not a time series and not attributed to individual posts — it cannot be correlated against the specific post dates (Jan 29, Feb 24–26, May 25, Jun 2–9) the way `ENGAGEMENT`/`FOLLOWERS` could. If per-post Saves/Sends breakdown exists somewhere in LinkedIn's per-post analytics detail view (unconfirmed — not checked this session), that would be the thing to find next to actually close the loop on the original hypothesis. Capturing this aggregate figure at multiple points in time (instead of once) would be the fallback if per-post breakdown doesn't exist.

### Fourth data surface — per-post analytics, and it closes the loop

Zach supplied `SinglePostAnalytics_Zach Harris_7468499877107372034.xlsx` — a fourth, even more granular LinkedIn data surface (per-post detail view, single "Post analytics" sheet). Confirmed by URL match: this is the **Jun 4, 2026 post** (the #2 post of the year in the 365-day export, 71,906 impressions). This is the data source that finally closes the original explicit→implicit/saves hypothesis properly:

- **Followers gained from this post: 19** — directly attributed to one post, no inference-from-date-windows needed (supersedes the connections/followers proxy method used earlier in this doc for any post where this sheet is available).
- **Profile viewers from this post: 85.**
- **Saves: 33, Sends on LinkedIn: 7.** Cross-referencing against the 90-day rolling aggregate Zach showed earlier (Saves: 50, Sends: 10, all posts) — **this single post accounts for the large majority of both totals across the entire 90-day window.** This is the concrete, attributable version of the "quiet IYKYK echo" signal the whole investigation set out to find.
- **Per-post viewer demographics, and they sharpen the "Apple insiders" claim dramatically:** Apple is **9%** of viewing companies for this specific post — an order of magnitude higher than the account-wide `<1%` figure found earlier. Top job title: Software Engineer (25%). Top locations: San Francisco Bay Area (31%), Greater Seattle Area (12%) — the actual Apple/big-tech engineering hubs. 49% of viewers work at companies with 10,001+ employees. This is a real, measured, well-evidenced confirmation, not a plausible-but-unprovable inference — the original hypothesis (this content reached a targeted insider technical audience, recognizable by composition even without a public trace) holds up directly against this data.
- **Discrepancy worth flagging, not smoothing over:** this sheet reports Social engagements: 82 for this post; the 365-day `TOP POSTS` export reported 83 for the same URL. A 1-unit drift between two LinkedIn-native exports of the same metric, cause unknown — noted rather than silently reconciled.

**Net effect on this whole section:** the four-surface map is now (1) personal data export — biographical/outbound only, (2) 365-day Content Analytics — aggregate impressions/engagement/followers/top-posts, (3) live 90-day rolling Saves/Sends aggregate, (4) **per-post analytics — the most granular surface, with attributable follower-gain, attributable saves/sends, and attributable audience demographics all in one place.** If this kind of analysis continues, (4) is the surface to pull for every post in a chain, not just the one Zach happened to screenshot — it would let every finding in this document be re-run with real per-post attribution instead of date-window inference.

### Per-post analytics for the year's top 6 posts — full reconciliation

Zach supplied all six. Identified each by URL/date match against the 365-day export and `Shares_8561261.csv`:

| Date | Topic | Impressions | Followers gained | Saves | Sends | Save-rate* | Send-rate* |
|---|---|---|---|---|---|---|---|
| Jan 29 | "Forgetting Machine" / Project Titan (original) | 74,851 | 12 | 17 | 2 | 0.023% | 0.0027% |
| Feb 24 (3:35pm) | Apple "one more thing" / competing-in-physics (probable match, timestamp not exactly reconciled — UTC offset ambiguity, see caveat) | 27,568 | 3 | 5 | 1 | 0.018% | 0.0036% |
| Feb 24 (9:08pm) | One of 5 posts published that day; exact text-to-post match not confirmed (timestamp didn't cleanly reconcile to any one of the 5 candidates) | 26,756 | 2 | 6 | 1 | 0.022% | 0.0037% |
| May 25 | "Everyone said Apple missed AI... wrong instrument" (gap-breaker) | 51,059 | 5 | 9 | 2 | 0.018% | 0.0039% |
| Jun 3 | **Off-thesis** — "the beliefs I actually changed didn't shift because I thought harder" (not about Apple/Titan at all) | 41,710 | 4 | 2 | 0 | 0.0048% | 0.0000% |
| Jun 4 | "In January 2026, I said Apple wasn't competing on AI demos" (direct callback to the Jan 29 thesis) | 71,906 | 19 | 33 | 7 | 0.046% | 0.0097% |

*Save-rate/Send-rate = Saves or Sends ÷ Impressions, a reach-normalized "quiet resonance density" metric, not in any LinkedIn export directly — computed here to separate "got a lot of reach" from "the reach that landed, landed quietly and specifically."

**Two findings that change the shape of this whole investigation:**

1. **The 90-day rolling Saves/Sends aggregate (50/10) reconciles cleanly once the window boundary is accounted for.** Today is ~Jun 24, 2026, so a 90-day trailing window starts ~Mar 26 — excluding Jan 29 and both Feb 24 posts entirely. Summing only the in-window posts: May 25 + Jun 3 + Jun 4 = 44 of 50 saves (88%) and 9 of 10 sends (90%). The remaining ~6 saves/1 send are smaller posts outside this top-6 list. This is a clean, internally consistent cross-check across two independently-pulled LinkedIn surfaces.

2. **Reach and quiet-resonance are clearly separable axes, and topical consistency (not just reach) predicts the latter.** Jun 3 (off-thesis, 41,710 impressions — the 4th-highest reach of the six) has by far the *lowest* save-rate (0.0048%) and the only zero send-rate. Jun 4 (on-thesis, a direct callback to the Jan 29 article) has both strong reach *and* by a wide margin the highest save-rate (0.046%, ~2x the next-highest) and send-rate (0.0097%, ~2.5x the next-highest). High reach does not predict high quiet-resonance on its own — staying on-thesis appears to. n=6, one account, but this is now the most concrete, falsifiable signal in the whole document for what the Rhetorical Resonance Engine should actually be optimizing toward: not impressions, but reach-normalized save/send density on thesis-consistent content.

**Caveat on the two Feb 24 posts:** five posts were published that day (`Shares_8561261.csv`); only one timestamp (3:35pm post → 20:35:25 in the export, consistent with EST UTC−5) reconciled cleanly to a specific post-text candidate. The 9:08pm post's exact text wasn't confidently matched — flagging the ambiguity rather than guessing.

## Data acquisition pipeline — confirmed, four steps, all manual

The full signal stack used to build the final SIMPLE/RICH/DEEP document (a working mockup of all three tiers was built and reviewed this session, populated entirely with real data, not illustrative content) required four separate exports:

1. **Export profile PDF** — LinkedIn's "Save to PDF" profile export. Source of dated tenure, certifications, top skills, summary. Feeds RICH tier.
2. **Export full LinkedIn data** — the personal data export ZIP. Source of `skills_full` (100, endorsement-ranked), `platform_inferences` (LinkedIn's own ad-targeting model of the user), and the 38 authored articles. Feeds DEEP tier. Required fixing a real date-parsing bug and adding four new parser fields this session (`linkedin_export.py`, committed `fd6ea07`).
3. **Export audience-level insights** — the 365-day Content Analytics export (`DISCOVERY`/`ENGAGEMENT`/`TOP POSTS`/`FOLLOWERS`/`DEMOGRAPHICS`). Requires LinkedIn Creator Mode. Source of aggregate impressions/engagement/follower trends and account-level audience composition.
4. **Export post-level insights** — per-post analytics, one file per post, also Creator Mode-gated. Source of attributable followers-gained, Saves/Sends, and per-post audience demographics — the data that actually closed the original "quiet IYKYK signal" hypothesis and produced the thesis-consistency finding above.

**All four are manual UI exports — none are API-automatable**, confirmed by what was actually done this session (no programmatic access attempted or found for any of them; steps 3–4 are gated behind Creator Mode specifically). Any product built on this pipeline needs to either accept that manual-export friction as part of the DEEP-tier UX, or treat it as a real, unsolved acquisition problem before assuming this scales beyond a one-person manual walkthrough.

## The missing archetype field — found, with a real method constraint

The canonical document's `ProfileSignature` archetype field (used as a placeholder label, e.g. "Pattern Matcher," in earlier mockups this session) has a real source: `/Users/zharris/Downloads/Book of ARCS v2 Deep.md` defines the canonical "Atomic Family" — **seven archetypes**: Dreamer (IPLR), Guardian (CEL), Elder (LRV), Shapeshifter (BFQ), Bridge (CVI), Heart (SBW), Sage (FPER). Each has a genesis parable, gift/lesson, and energy tags.

**Diagnostic method, per the canon itself:** a 4-channel "Atomic Signature" — Geometry, Somatic Scan (physical/breath response to scripted scenarios), Mirror Test (relational — who you feel "same species" with), and Receipts (behavioral pattern) — synthesized into a consensus primary, shadow, and secondary (bridging) archetype.

**Real constraint, not a future nice-to-have:** three of the four channels (Geometry, Somatic Scan, Mirror Test) require data Profile Scan's LinkedIn-based pipeline structurally cannot supply — there's no body-response or relational data anywhere in any of the four LinkedIn surfaces used this session. Only **Receipts** (behavioral pattern from career/decision history) is even plausibly approximable from what's already been gathered. Asserting a confident archetype label from LinkedIn data alone would not be a faithful application of the canon's own method — flagging this rather than fabricating one.

**Resolved — a live Calibration Call covers all four channels, not just Receipts.** Zach's proposal: gate the missing channels behind a 60-minute human-reviewed call where the person reacts to their draft Profile Scan report — what resonates, what doesn't, anti-patterns and anti-signals, pre-conscious somatic cues as a proxy for energizers/drainers. Checked the canon's own channel definitions before assuming this covers the gap, and it does, more completely than expected:

| Channel | Canon's own method (`Book of ARCS v2 Deep.md` §2.1–2.4) | Calibration-call equivalent |
|---|---|---|
| Geometry | "Sacred Heptagram" — mark primary pull + shadow distance directly on a 7-point star | Same — direct self-report, just ask |
| Mirror Test | List 3 people you feel most alive with; what attracted/kept/repelled | Same — direct self-report, just ask |
| Somatic Scan | Scripted scenarios, observed breath/lean — open vs. contracted = candidate primary/shadow | Live resonance/anti-resonance reaction to the draft report — genuinely needs a proxy, this is it |
| Receipts | Behavioral pattern across career/decisions | Already covered — this *is* the Profile Scan document itself |

Geometry and Mirror Test turn out to be direct self-report exercises in the canon's own protocol, not sensor data — trivially askable in any live conversation. Only Somatic Scan genuinely requires *watching a reaction* rather than asking a question, which is exactly what the calibration call's live-resonance-tracking is for. **Implication:** the archetype field doesn't need to stay permanently unavailable or Receipts-only — it should be gated behind this fifth, human-in-the-loop session type (distinct from the four automated LinkedIn-export tiers above), not solved by trying to infer body/relational signal from passive data.

**RESOLVED — it's the Calibrate surface, not Court.** The open question (does the Calibration Call map onto the existing "Court" session concept?) is settled against the canon: **no, it maps to Calibrate.** The two operate on different objects:
- **Court** operates on a *decision* — WORLD.md: "deliberate probing before committing to a line"; `mode=COURT` is the existential / zero-reversibility / Y=RED escalation (auto-triggered per ADR-020 at irreversibility ≥ 0.7, BAR Ruin, or identity-wavefunction conflict); `operators/arcs_constitutional_court.py` = axiom enforcement on a high-stakes call.
- **The Calibration Call** operates on an *operator-state / instrument* — surfacing which archetype, what resonates vs. anti-resonates, energizers/drainers via somatic proxy. It adjudicates nothing; it calibrates a reading.

These are different points in the flow: Calibrate is the **"D" surface** in the canonical JTBD master map (D→A→C→B = Calibrate→Orient→Chart→Detect, per `arcs-field-os/jtbd/jtbd-master-map.md` and the CLAUDE.md handoff history); it is also the surface Book II Part V §5.7 routes malformed questions to. Court is a downstream deep-escalation when stakes spike. Conflating them would muddy both. **The Calibration Call is therefore an instance of the already-canonical Calibrate surface, not a brand-new session type** — which is a cleaner result than the earlier "fifth session type" framing: it has an existing home in the canon, it just hasn't been wired to Profile Scan's archetype field yet. Still needs: the consensus-scoring logic across the 4 channels per §2.5 of `Book of ARCS v2 Deep.md`, and confirmation of how a Calibrate session attaches its output back to a prior Profile Scan receipt.

## Real production variants reveal a composable block library, not one fixed document

Checked three real Gamma documents Zach has built (`get_gammas`/`read_gamma`, query "profile scan"/"ARCS scan"/"360"). These are not depth variants of the same document — they're three different **use-case modes**, each composing a shared block library differently:

| Variant | Use case | Distinctive structure |
|---|---|---|
| **"720° Profile Scan"** (Chris) | Recruiting/talent evaluation | 5D×5H×5W×5C×5R (Dimensions/Histories/Whys/Capabilities/Risks) + thesis (0°–360°) and anti-thesis/pre-mortem (360°–720°) orbits + closing Sales-Entry-Points block |
| **"ARCS Scan - Harry Wilson"** (Fathom variant) | Relationship/partnership-building, subject-paced | "Five Fathoms" (Executive→Strategic→Operational→Tactical→Surgical→Appendix), depth controlled by the *subject* not the presenter; multi-person Founding-Genome table; per-person "Signal" sections; recursive cross-scale "Fractal Pattern" table |
| **"360° 5D Harmony Report"** (Martin/millionways) | Investment/partnership evaluation | PCI/HCI coherence scores, First Wave analysis, 5D Harmony with per-dimension Resonance Scores, Cross-Dimensional Coherence matrix, risk-leveled Blindspot Detection, closing Collaboration Fit Score *with Zach specifically* |

**Confirms the pass-through parameter grammar concretely, not just as a spec proposal.** The Chris variant literally prints its own invocation params as visible text in the document: `Adaptive Altitude: DEEP + RICH · Register: Operator-to-Operator · Audience: Seasoned AI-native systems builder`. This is direct evidence the `init arcs config=...` grammar (proposed at the very start of this whole investigation, from the original Perplexity PRD) is real and already in active use — not hypothetical.

**Recurring primitives across all three** (the actual composable block library, reused regardless of mode): color-coded Threads (Gold/Vermillion — consistent with `patterns.jsx`'s thread system), an N-dimensional scoring grid (5D/5H/5W/5C/5R or PCI/HCI/Resonance-per-dimension), a Risk/Blindspot/Pre-Mortem section, and a closing action-oriented block tailored to the use case (Sales-Entry-Points, Strategic-Recommendations, or Collaboration-Fit-Score).

**Implication for the spec:** Profile Scan's output isn't fully described by SIMPLE/RICH/DEEP depth alone — there's an orthogonal **mode** dimension (recruiting eval vs. partnership eval vs. relationship-building) that selects a different composition of the same block library. The canonical `patterns.jsx` document shape used earlier in this spec (CoverBlock/TwoColumn/SidelineList/DataTable/SmartGrid/QuoteBlock) is one realization of this library, not the only one. Worth deciding whether `mode=` becomes a first-class pass-through param alongside `domain=PROFILE-SCAN` and the depth tier, before locking the `ProfileScanRequest`/`ProfileScanResponse` schema.

### Not a static template at all — full atomic-design composability, plus a third axis: audience direction

Zach's correction, confirmed against the actual content of the three Gammas already read (not just taken on description): Profile Scan has no single template. It composes atoms → molecules → organisms → templates → pages based on contextual/situational awareness and use case — and there is a third axis beyond depth (SIMPLE/RICH/DEEP) and mode (recruiting/partnership/relationship) that the three-variant comparison above didn't separate out: **audience direction.**

- **Internal** — briefings for Zach (or a mutual connection) about the subject, never shown to the subject. Confirmed in two of the three Gammas: the Chris 720° doc's "Sales Strategy / Easiest Entry Points" section explicitly discusses "team penetration difficulty" as a sales target, not subject-facing content; the Martin 360° Harmony Report contains a "Note for Ben Allen" and a "Collaboration Fit Score: Zach × Martin" — content that can only be meant for Zach's (or Ben's) decision-making, not Martin's.
- **External** — written directly to the subject, in their native register, already resonance-optimized. Confirmed in the Harry Wilson "Fathom" doc: second-person address throughout ("This is a mirror, not a verdict... tell me where I'm wrong"), entirely composed in Harry's own register (quarterback reads, pressure, athletic conditioning, "depth of field"), with a real partnership ask (ARCS × Limitless Minds) embedded inside that register-matched language rather than stated in ARCS's own internal vocabulary.

**This collapses something significant for PRD-B.** The Harry Wilson doc isn't a hypothetical precursor to the Rhetorical Resonance Engine — it's a real, already-built instance of its actual output: the same underlying scan data, wrapped in language matched to the subject's register, deployed to make a specific ask land. PRD-B is not just unblocked on inputs (per the four-step acquisition pipeline above) — a working example of its target output already exists in production. The remaining gap is formalizing *how* the register-matching happened (manually, this time) into something the pipeline can do systematically.

**Revised model:** Profile Scan generation = atomic composition selected by **(depth × mode × audience-direction)**, not a fixed document with a depth toggle. All three axes need to be in the eventual `ProfileScanRequest` parameter grammar, not just depth and domain.

### Governing invariants for the block library

Zach's explicit requirement for every atom/molecule/organism/template/page in this system, regardless of mode/depth/audience-direction — recorded here as a durable constraint on the architecture above, not a one-off note:

- **Traceable** — every block's content must cite which real data source produced it (a specific export field, a specific per-post file, a specific quote). This spec's own practice throughout this session (always naming the source file/field per claim) is the standard, not an exception.
- **Transparent** — no block hides its scoring logic or asserts certainty it hasn't earned. Consistent with this session's repeated practice of flagging "plausible but unprovable" rather than smoothing over a gap (the Apple-insiders claim, the Feb 24 9:08pm post, the archetype field) — that discipline is now a structural requirement on the system, not just a session habit.
- **Composable** — a block must combine with others without bespoke per-combination glue code. The same Thread or Evidence-Ledger atom slots into a recruiting-mode page, a partnership-mode page, or a relationship-building page unmodified.
- **Interoperable** — a block built for one mode must be reusable verbatim in another. Atoms stay agnostic to which template/page/audience-direction they end up composed into.
- **Factual** — no fabricated content in any block, ever. Every number, quote, or claim must trace to real data — the same standard already enforced throughout this spec (e.g., refusing to force-match the Feb 24 9:08pm post to a specific text candidate rather than guess).
- **Invariant-bearing** — certain rules hold no matter the composition: the thread-color convention (red=risk, gold=working asset, green=conviction, vermillion=constraint) means the same thing in every document it appears in; depth nests (DEEP ⊇ RICH ⊇ SIMPLE), it never contradicts across tiers.
- **Fractal / recursive** — a block must work standalone (e.g., a single Thread card dropped into a message) *and* as a nested component inside arbitrarily larger compositions. Direct precedent already found this session: the Harry Wilson doc's own "Fractal Pattern" section, which names the same diagnostic recurring at individual → leadership-team → organization → category scale as a structural principle, not a one-off observation.
- **Within the established visual grammar** — composability is freedom of *content and structure*, not freedom of *visual language*. Every block still uses the locked token set (`T.bg`/`T.cyan`/mono labels/thread-color conventions from `primitives.jsx`/`patterns.jsx`) regardless of which mode or audience-direction it's composed for.

### Term collision — same words, different ontological definitions across the corpus

Zach flagged this directly, and checking it against everything actually read this session confirms it's real and worse than expected — it includes a drift in this spec's own mockup, not just across the three Gammas. Same category of issue this repo has hit before (`MEMORY.md` [v3.1.0]: BAR/KKL meant two different things in two canon files, resolved via `/dual-bar-raiser`). This is the Profile Scan-specific instance of that same pattern:

| Term | `patterns.jsx` canonical (`ProfileScan()`) | This session's mockup (drifted, unflagged until now) | Harry Wilson Gamma | Martin 360° Gamma |
|---|---|---|---|---|
| **Thread** (Red/Gold/Green/Vermillion) | Red=Chain of Custody, Gold=Provenance, Green=Conviction, Vermillion=Constraint | Red=Recurring Risk, Gold=Working Asset, Green=Conviction, Vermillion=Constraint — *similar spirit, not the same definition* | Gold Thread = autobiographical-before-commercial framing device; Vermillion Thread = closing constraint synthesis — not a 4-part scoring system at all | Not used |
| **Signal** | Not used as a named section | "01 · Signal Read" = stated-vs-observed TwoColumn | "Signal One/Two/Three/Four" = one per founder, each a distinct person's frequency/amplitude/form | Not used as a section name; "Resonance Score" is the closest analog |
| **5D** | Not used | Not used | Not used (this doc uses 5D/5H/5W/5C/5R, a different variant — see Chris doc below) | Identity/Capability/Environment/Relationships/Purpose — five *analytical scoring axes* |
| **5D** (Chris 720° Gamma, distinct from Martin's) | — | — | "What He Is" — five *role-type descriptors* (Signals Architect, AI-Native Orchestrator, etc.) | — |
| **Genome** | "Provenance Theorem" — a single coherent pattern across one person's career | Not used | "Founding Genome" — a *multi-person* construct (the founding team's four combined signals) | Not used |

**Authority-of-record located: `ARCS-Glossary-v0.2.md`** (Zach's working dictionary; "extend by receipt, not by vibe"; has a v0.3+ entry schema with Term/Type/Trigger/Action/Related/Provenance/Version/Coverage fields). Checked the four colliding terms against it — and the finding sharpens: **the glossary does not contain Thread, Signal, 5D, or Genome at all.** The collision is not "canon defines them inconsistently" — it's that **canon is silent on exactly these four**, so each document instance minted its own operational definition unchecked. That is *why* they drift, and it means the collision cannot be resolved by pointing at canon (there's nothing to point at). What the glossary *does* authoritatively confirm: **Folksonomy** is an operator ("bottom-up patterning… emerge from repeated real use" — verbatim support for RC-OPS-002); **First/Second Derivative** and **Decelerator** match `primitives.py` exactly; **Visceral Translator** ("recodes abstract language into felt stakes… without becoming manipulative") is the canonical primitive underneath the Rhetorical Resonance Engine. Two naming spreads also surfaced: the folksonomy operator appears as *Folksonomy* (glossary) / *Folksonomist* (`arcs_core.py`) / *Organic Folksonomy Cultivator* (glossary meta-operator); *Curator* appears as both a role-lens and an archetype in the same doc. One net-new gap created this session: **Jerk / Third Derivative** now has working code (`primitives.py`, the `pre_peak_warning` capability) and real-data validation but **no glossary entry** — the glossary has 1st/2nd-derivative + Decelerator but not 3rd.

**This is not cosmetic.** If `mode=`/`audience-direction` selects which block composition to use (per the architecture above), and the same word means structurally different things depending on which block/mode produced it, then a block can't actually be **interoperable** (one of the invariants just locked in) without either (a) each term being explicitly scoped per-mode in documentation, so a reader always knows which definition is active, or (b) picking one canonical operational definition per term and migrating every variant to match it. **Concretely: the highest-value glossary expansion is operational definitions for the four canon-silent colliding terms (Thread, Signal, 5D, Genome) plus a Jerk/Third-Derivative entry — using the v0.2 entry schema, which already has the per-term scoping fields (Trigger/Action/Provenance) needed to disambiguate them.** The glossary's own "extend by receipt" rule is the right governor: these terms have earned entry through repeated real use across the variant corpus. Recommend treating this the same way the BAR/KKL collision was resolved previously: don't silently pick one — name the collision explicitly in whatever spec or canon doc ends up governing the block library, and route the actual resolution through whatever review process this repo already uses for canon collisions.

**Counter-consideration, raised by Zach and worth taking seriously rather than overriding:** because ARCS reasons abductively (best-fit-per-target, not fixed top-down rules) and is built on a folksonomy data model, term variation across variants may not be a defect to standardize away — it may be the system working as designed. This maps precisely onto existing canon, not a new claim: `scripts/arcs_core.py`'s Folksonomist operator and **ADR-023 (Observability as a Superionic Goal Lattice)** already define observability/categorization as an *inferred, weighted folksonomy DAG over receipts*, not a declared taxonomy — the framing is to watch **edge-weight tightening**, not enforce node-state consistency. "The web tightens with each net-new cut" restates that ADR's own model: each new Profile Scan variant is a receipt: the category boundaries (what "Thread" or "Signal" means) should sharpen statistically as volume accumulates, rather than needing to be locked by fiat now.

**The caveat that has to travel with this, though:** ADR-023 itself gates that tightening claim behind a **100+ receipt threshold** for a measurable real-corpus Zipf baseline — specifically because at low volume, apparent convergence is indistinguishable from coincidence. The Profile Scan corpus actually examined this session is five documents (three Gammas, one mockup, one canonical reference) — nowhere near the volume the theory itself requires before trusting tightening over noise. **Conclusion: don't resolve the term collision by fiat right now, but also don't treat folksonomy-tightening as already-active at n=5 — that's exactly the regime ADR-023 says not to trust.** The right move is to keep generating variants (each one a receipt) and revisit whether the terms are actually converging once there's enough volume to check, rather than assuming convergence is already happening.

**Registered as `RC-OPS-002`** in `operators/README.md`'s ROM Candidates table — not canonical, not to be depended on for any decision-gating.

**On the gate threshold — the 100 is arbitrary, but don't just lower it to another guessed number.** Zach's right that 100 was loosely set. Traced it: ADR-020 is internally inconsistent (it says "50+ receipts" in two places and "100+ receipts (L6 engine territory)" in a third), and ADR-023 inherited the 100 as "same L6 gate as ADR-020." So the number is a round-number proxy bolted to a qualitative tier label, not a derived statistic — and it doesn't even agree with itself. **But** the *substantive* gate underneath it is real and not arbitrary: ADR-023's structural-integrity section requires `g > Gini_baseline(corpus)` where "that baseline is a **measured** quantity — the reason synthetic data cannot finalize the constants." The number stands in for "enough real receipts that the measured Zipf/Gini baseline is stable rather than noise." **The principled fix is to replace the magic-number gate with a measured-stability gate: promote when the corpus's measured Gini/Zipf baseline has *stabilized* (stops moving materially as N grows, or its estimate's CI is tight enough), whatever N that turns out to be — possibly well under 100.** This is strictly more faithful to ADR-023's own "measured, not assumed" logic than swapping 100 for 50 would be (50 is equally arbitrary). Lowering the number is the wrong lever; removing the number in favor of a stability criterion is the right one. (This observation also applies upstream — ADR-020/ADR-023's 100 gate itself is a candidate for the same treatment; flagged here, not changed in those ADRs this session.)

## Depth model, finalized: one document, progressively truncated

Confirmed directly by Zach, exact mapping: **SIMPLE = ultra-collapsed, RICH = collapsed, DEEP = expanded** — one document, three truncation depths, not three separate documents or data models. Concretely, given the six-section canonical shape above:

- **SIMPLE (ultra-collapsed)** ≈ section 01 (Signal Read) + section 06 (Key Assertion) only
- **RICH (collapsed)** ≈ sections 01–03 (adds Evidence Ledger, Thread Assessment)
- **DEEP (expanded)** = all six sections (adds Capability Map, Content Resonance)

This means depth is a **rendering/truncation concern, not a content-generation concern** — there is one `ProfileScanResponse`-equivalent document, and SIMPLE/RICH/DEEP just decide how much of it to show. No separate per-tier data model, no client-side mode-toggle state machine needed. (This also explains a build issue from earlier this session: a scripted SIMPLE/RICH/DEEP toggle widget failed to render — rebuilding it as plain static HTML showing the full document worked immediately. The toggle was solving a problem that doesn't exist once depth is understood as truncation, not branching.)

**Readiness for the Rhetorical Resonance Engine (PRD-B):** this pipeline now satisfies PRD-B's original input contract concretely rather than speculatively — `profileScan` (steps 1–2, the document built this session), `targetAudience` (steps 3–4's demographics, now measured not guessed), and `content` (step 2's 38 articles, the real long-form corpus). The response side's `resonanceMode`/`audienceWavefunction` concepts are grounded in a real, falsifiable finding (thesis-consistency predicts save/send density independent of reach) rather than an unvalidated model. PRD-B is no longer blocked on "what would the input even look like" — it's blocked on actually being scoped and built, which hasn't happened yet.

## Out of scope for v1

- The interactive scanner UI, mode-toggle re-render, and live score gauges from the Perplexity PRD — explicitly discarded.
- Generation pipeline / LLM wiring (next spec).
- Auth gating per tier (likely needed for RICH/DEEP given PDF/export upload, but not decided here).

---

# Provenance & Open-Question Ledger (session close, 2026-06-24)

> Purpose (per `/goal`): the biggest unclear terms, the assumptions resting on inference rather than authority-of-record, and the levers that make the next session cheaper. Ranked by impact within each list. This exists so the next session does NOT re-derive any of it.

## A. Unclear terms — definitions NOT from authority-of-record

| Rank | Term | Status | What would resolve it |
|---|---|---|---|
| 1 | **Thread** (Red/Gold/Green/Vermillion) | Canon-SILENT (not in `ARCS-Glossary-v0.2.md`). 3+ live meanings: 4-axis scoring [patterns.jsx] · per-person frequency descriptor [Harry doc] · narrative framing device [Gold/Vermillion] · and my own drifted "Risk/Working-Asset" mockup labels. | Glossary v0.3 entry with per-sense scoping (Trigger/Action/Provenance fields). |
| 2 | **5D** | Canon-SILENT. Two incompatible meanings: five role-type *descriptors* [Chris 720°] vs. five analytical *scoring axes* (Identity/Capability/Environment/Relationships/Purpose) [Martin 360°]. | Glossary entry; decide if these are two terms or one with variants. |
| 3 | **Signal** | Canon-SILENT as a section term. Means: stated-vs-observed read [my mockup "01 Signal Read"] · per-person frequency [Harry doc "Signal One/Two…"] · ≈ Resonance Score [Martin]. | Glossary entry. |
| 4 | **Genome** | Canon-SILENT. Single-person ("Provenance Theorem") vs. multi-person ("Founding Genome"). | Glossary entry. |
| 5 | **Folksonomy / Folksonomist / Organic Folksonomy Cultivator** | One concept, 3 names across glossary (operator + meta-operator) and `arcs_core.py` (`folksonomist_cluster`). | Pick canonical name + alias-map (glossary v0.5 alias layer). |
| 6 | **Curator** | Listed as BOTH a role-lens AND an archetype in the glossary itself. | Decide which; or document as deliberately dual. |
| 7 | **mode=** enum (recruiting / partnership-eval / relationship-building) | MY inference from 3 Gammas, not an authority list. Likely incomplete — only 3 search terms were tried. | Zach confirms the canonical enum (or a Gamma sweep at higher volume). |
| 8 | **audience-direction** (internal / external) | MY coined axis, inferred from the 3 Gammas. Not a canon term. | Confirm + name canonically. |
| 9 | **"quiet resonance density" / save-rate / send-rate** | MY coined metric this session. Real (computed from real data) but not canon. | Glossary entry if it earns keep. |
| 10 | **Calibration Call** | MY name; resolved this session to the canonical *Calibrate* surface — but the label itself is mine. | Confirm naming against Calibrate surface canon. |

## B. Assumptions resting on inference, NOT authority-of-record

| Rank | Assumption | Why it's inference | Risk if wrong |
|---|---|---|---|
| 1 | ~~`patterns.jsx` is THE canonical document shape~~ — **RESOLVED 2026-06-24** | Verified via `gh search` + disk: `patterns.jsx` is faithfully ported into arcs-v9 as `src/document/{registry.ts, tokens.ts, primitives.tsx, patterns/, screens/}` with a `/design-test` render page; `DOC_TYPES` includes the `profile`/Profile Scan/◈/green entry. The document-shape spec rests on **committed in-repo code**, not a Downloads orphan. Original `patterns.jsx` provenance = the "ARCS OS - Design System" export bundle. | ~~HIGH~~ → RESOLVED. Phase-1 build target = `src/document/`. |
| 2 | **Thesis-consistency predicts save/send density** (Jun 3 vs Jun 4) | Real per-post data, but n=6 posts, one account. Empirical hypothesis, not law. | Over-generalizing a small-sample pattern into a design principle. MED. |
| 3 | **Anticipatory timing beats day-of** | n=12, one account, AND confounded with posting cadence (can't separate the two). Already self-corrected once (WWDC reversal). | Cadence may be the real driver, not news-cycle timing. MED. |
| 4 | **"Apple insiders" reach** | Per-post demographics confirm 9% Apple on Jun 4 (real) — but the original *same-day-connection-spike-was-Apple* claim is still inference. | Conflating "audience contains Apple" with "the spike was Apple." LOW-MED. |
| 5 | **Jerk fires ~1 day before peak** | n=2 peaks. Real validation, tiny sample; lead-time may be an artifact of daily sampling. | Treating a 2-point result as a stable constant. MED. |
| 6 | **Calibration Call fully covers the 4 archetype channels** | Verified channel *definitions* (§2.1–2.4), but did NOT read the §2.5 consensus-scoring logic in full. | The scoring synthesis may not work as assumed. MED. |
| 7 | **Folksonomy-tightening (RC-OPS-002)** | Explicitly gated/unverified at n=5. Flagged, not claimed. | (Already correctly held as unverified.) LOW. |
| 8 | **The "100-receipt gate" is arbitrary** | Now evidence-backed (ADR-020 says 50 twice, 100 once) — so this is NO LONGER pure inference. But "measured-baseline-stability is the right replacement" IS my proposed design, unconfirmed. | The replacement criterion is unratified. LOW-MED. |
| 9 | **arcs-field-scan v0 framing is dead** | Zach chose the document template; I inferred the interactive-scanner prototype is superseded, but disposition (archive/keep) never confirmed. | Orphan repo left in limbo. LOW. |

## C. Levers — make my work easier + Zach's spend more cost-effective

| Rank | Lever | Payoff |
|---|---|---|
| 1 | **An authority-of-record MAP** — one table: "for question X, the authority is file Y." | Biggest single cost cut. Most spend this session was re-deriving which file governs what (Downloads PDFs, Gammas, xlsx, canon). A map kills repeated re-reads. |
| 2 | **Confirm `ui_kits/documents/` repo ownership** | Stops me building the whole spec against an unverified Downloads file (Assumption B1). |
| 3 | **Drop the richer glossary corpus** (Zach offered) | Lets me stop *inferring* term meanings (kills most of List A). |
| 4 | **Decide `arcs_cfa` disposition** — is it the pipeline's home, or does it port into `arcs-v9`? | I'm currently editing a separate, uncommitted repo. Commit `fd6ea07` sits local-only, unpushed. Needs a call. |
| 5 | **Lock the param grammar** — confirm `mode=` enum + `audience-direction` values + depth tiers | Unblocks the `ProfileScanRequest`/`ProfileScanResponse` schema (the load-bearing interface for both this PRD and PRD-B). |
| 6 | **Standardize Python to 3.11** for this pipeline | Recurring friction: `str | Path` + `bs4` both need 3.11; system default is 3.9.6. One `.python-version` / venv decision ends it. |
| 7 | **Pointer to §2.5 consensus-scoring** (or confirm it's fine) | Closes Assumption B6 cheaply. |
| 8 | **Decide whether to amend ADR-020/023's 100-gate** | I flagged it; changing actual ADRs should route through Zach's review, not be done unilaterally. |

## D. The single most cost-effective next move

Provide (or point me to) the **authority-of-record map + the richer glossary**. Together they collapse Lists A and B almost entirely: ~17 of the ~19 open items above are "I inferred this because I couldn't find the authority." Supply the authority once, and every future session stops paying to re-derive it — which is exactly the folksonomy "extend by receipt" discipline applied to the spec's own provenance.
