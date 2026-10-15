# Cyan games: is the linking structure fractal, or only repeated?

Date: 2026-10-15. Origin: Zach's observation that the Miller brothers keep returning to one isomorphism (Obduction page). Status: pre-registration written BEFORE any game data was fetched; results appended below.

Ground: motivated by the en.wikipedia.org/wiki/Obduction_(video_game) page (Cyan calls it "Myst in space"; the team found itself returning to Myst-like structure). Companion to `_PATTERNS/2026-10-15-unearned-sharpness-detector.md` (arcs-v9 PR 1313, merged 97b31f7c).

## Definitions (fixed now)

- Linking device: an explicit in-fiction mechanism that moves the player between separate worlds.
- Nested scale: a traversable world contained inside another traversable world, joined by a linking device.
- FRACTAL (mechanism sense): the same linking structure appears at two or more nested scales within ONE game.
- Coding source: Wikipedia plus Cyan's own pages, secondary and unverified. My coding is my reading of those, not ground truth.

## Pre-registered beliefs

B8. Every main Cyan adventure title (Myst 1993, Riven 1997, Uru 2003, Obduction 2016, Firmament 2024) contains a linking device. Prior 0.85. Kill: any title lacks one.

B9. FRACTAL holds in at least 3 of those 5 titles. Prior 0.35 (I suspect nesting is single-level and "fractal" is a metaphor). Kill for fractal-as-mechanism: fewer than 3 of 5. If killed, "fractal" stays METAPHOR and the finding is "repeated, not self-similar".

B10. The structure is invariant to rendering paradigm: it survives the 1993 pre-rendered to real-time 3D change. Prior 0.9. Kill: a title built on the new paradigm drops the linking device.

Flag rule for the recapitulation: LOAD-BEARING = a diff whose removal would change a belief's verdict; COUNTERINTUITIVE = a result that moved against my stated prior by more than 0.3.

## Correction to the pre-registration (appended, original left as written)

Firmament is dated 2023 (Windows 2023-05-18, PlayStation 2025-07-02) per en.wikipedia.org/wiki/Firmament_(video_game) and the Cyan_Worlds list. The pre-registration above says 2024. My error; it does not change any belief.

## Serialized timeline (Cyan games, release order; source en.wikipedia.org/wiki/Cyan_Worlds)

Pre-Myst children's titles: The Manhole 1988, Cosmic Osmo 1989, Spelunx 1991. Then: Myst 1993 (pre-rendered), Riven 1997, realMyst 2000 (real-time remake), Uru 2003 (+ expansions 2004), Myst V 2005 (real-time, documented), Myst Online: Uru Live 2007, ports 2009 to 2013, realMyst Masterpiece 2014 (Unity), Obduction 2016, Myst VR remake 2020, Firmament 2023, Riven remake 2024. Myst IV and Revelation-era titles were not Cyan-developed per the same page. Myst V is outside the fixed B8/B9 set and is reported as an extra datapoint.

## Coding table (my reading of each page; "not stated" is not "absent")

| Title | Linking device (page) | Nested same-structure (page) | Source |
|---|---|---|---|
| Myst 1993 | Linking books to Ages; hub island | Not stated; trap books in the library are explicitly not linking books. Page read only to char 100000 of 152715. | en.wikipedia.org/wiki/Myst |
| Riven 1997 | Linking books exist; entry book is a trap book; Gehn trapped by removing the books | Not described. Five islands sit inside ONE Age. | en.wikipedia.org/wiki/Riven |
| Uru 2003 | Linking books; Relto hub holds a bookshelf of books to Ages | Hub-of-hubs appears only in previews of cancelled multiplayer, not confirmed in the shipped game | en.wikipedia.org/wiki/Uru:_Ages_Beyond_Myst |
| Myst V 2005 (extra) | Linking books; real-time 3D replaces pre-rendered | Ages divided into navigation nodes; no hierarchy among Ages described | en.wikipedia.org/wiki/Myst_V:_End_of_Ages |
| Obduction 2016 | Trees and Seeds swap spherical areas between four cells | Human sphere inside alien sphere; Tree-to-Heart link repeated per cell; self-similarity not stated | en.wikipedia.org/wiki/Obduction_(video_game) |
| Firmament 2023 | Conveyance Pods join Realms to a hub (the Swan) | Realms and Swan are parts of one starship; page says no worlds inside worlds | en.wikipedia.org/wiki/Firmament_(video_game) |

## Verdicts against the pre-registered kills

B8 (linking device in all five): NOT CONFIRMED. Four of five document an explicit linking device between worlds. Firmament's Realms are compartments of one ship per the page (a category tag says "planets", the text does not), so under the definition fixed above ("separate worlds") it fails, and under a loose reading (pods count) it passes. Prior 0.85. Verdict rests on one coding decision.

B9 (FRACTAL in at least 3 of 5): KILLED. Documented count is 0 clear and 1 weak (Obduction's nested spheres, self-similarity unstated). Prior 0.35. "Fractal" stays METAPHOR. Caveat: the Myst page was only read to character 100000 of 152715, so a "not stated" for Myst is weaker than the others.

B10 (structure survives the pre-rendered to real-time change): PARTLY. It holds for Myst V (documented) and Obduction (Seeds device documented; that it is real-time is from my memory, not from a page I fetched). The one real-time title that drops the book device is Firmament, a different IP, so the literal kill ("a new-paradigm title drops the device") is met only through the same Firmament coding decision as B8. Confounded by IP, not by rendering.

## Flags

LOAD-BEARING:
1. The Firmament coding decision alone flips B8 and the B10 kill. It is the highest-leverage unverified judgment in this audit. Resolve it from a primary source (Cyan's own pages or developer statements), not Wikipedia.
2. The Myst page was truncated at 100000 of 152715 characters. Every "not stated" for Myst is provisional until the remaining 52715 are read.

COUNTERINTUITIVE:
1. Riven, the direct sequel to the book-linking game, collapses the hub of separate Ages into five islands inside ONE Age and makes linking the denied resource (Gehn trapped by removing the books; player enters via a trap book). The sequel is less linking-centered in play than the original. Nothing I pre-registered predicted this.
2. The strongest "nesting" evidence is Obduction (containment), not Myst. The studio that built the linking-book icon shows its clearest nested structure in the title that claims to be Myst in space.
3. Cyan itself says it tried to leave the Myst structure and found itself returning to it (Obduction page). Repetition is documented by the studio. Self-similarity is not.

## Recapitulation

Repeated, not recursive. Across the sources read, Cyan reuses one idea, a device that moves you between separate places, in five different costumes: linking books, trap books, the Relto bookshelf, Seeds, Pods. That is MECHANISM at the level of "a transport device organizes the game". "Fractal" fails its own pre-registered test: the sources show one level of nesting, with the single weak exception of Obduction.

Post-hoc hypothesis (B11, NOT a result, registered now, untested): the defensible self-similarity is a graph of nodes at two scales, navigation nodes inside an Age (Myst V page) and Ages as nodes joined by linking books (Myst page). Test on fresh evidence: count title by title whether both scales exist. Kill: fewer than 3 of 5. It was formed after seeing the data, so it carries no weight until tested on pages not yet read.

Not done: reading the unread Myst text, primary Cyan sources, any title outside the five, and no check of non-Wikipedia accounts. Echo to ARCS (a position as a node in a graph at several scales) stays METAPHOR.

---

## Round 2 pre-registration (written 2026-10-15 BEFORE any round-2 page was fetched)

Open items from round 1: (1) Firmament coding, (2) unread Myst text, (3) B11 test, (4) Obduction real-time status.

R1. Firmament: Cyan's own pages or developer statements say Conveyance Pods join separate worlds. Prior 0.5. Decision rule: "worlds" if a Cyan or developer source calls Realms worlds/planets/places apart from the ship; "compartments" if it calls them parts of the ship. If no such source is found, the coding stays UNRESOLVED and B8 stays NOT CONFIRMED (no source, no flip).
R2. Remaining Myst page text (chars 100000 to 152715) contains no statement of nested same-structure linking. Prior 0.8. Kill: any such statement. Every Myst "not stated" is re-checked against it.
R3. Obduction is real-time 3D (Unreal Engine 4). Prior 0.95. Kill: a fetched source says otherwise.
B11 test (title by title, pages not yet read in round 1: use only passages not already quoted above; where a page was read, new sections or a different page such as the Cyan wiki or developer statements). Two-scale graph exists if the source describes (a) nodes of movement inside a world AND (b) worlds as nodes joined by a linking device. Kill stays: fewer than 3 of 5 (Myst, Riven, Uru, Obduction, Firmament). Prior 0.4. Note: a title whose worlds are only compartments of one ship counts as (b) failing.
Em-dashes 0. Caveat unchanged: sources are secondary unless marked Cyan or developer.

## Round 2 results (2026-10-15)

R1 Firmament coding: UNRESOLVED, leaning "compartments". Cyan's own Kickstarter pitch (kickstarter.com/projects/1252280491/firmament) says "this world" (singular) and "locations", and calls the game "an entirely new property". Cyan's FAQ pages (cyan.com/docs/what-is-firmament, cyan.com/docs/firmament-is-being-made-by-cyan-is-it-a-myst-game) say nothing on structure beyond "created in the spirit of Myst". No Cyan or developer source calls the Realms separate worlds or planets, and none describes the Pods; the Pod and Swan facts still come from secondary reviews (Wikipedia, PC Gamer, Adventure Game Hotspot via search summaries, not read in full). Under the round-2 decision rule, no source means no flip. B8 stays NOT CONFIRMED (4 of 5 documented, Firmament as compartments of one world). B10's kill stays met only through Firmament and stays confounded by IP. Limits: cyan.com and Kickstarter blocked the fetch tool (403) and were read in the in-app browser; the Kickstarter update posts (#28, #35) rendered no body text, so developer interviews were not read.

R2 Myst remainder: CONFIRMED, trivially. Characters 100000 to 152715 are references, external links, navigation templates and category tags; they hold no design prose. So the round 1 "weaker not stated" caveat is retired: every Myst "not stated" now rests on the whole prose of the page. (That is a fact about this one page. It does not make Wikipedia complete.)

R3 Obduction real-time: CONFIRMED. The Wikipedia infobox names Unreal Engine 4; the GDC 2016 session "Building Obduction: Cyan's Custom UE4 Art Tools" and Road to VR describe real-time rendered environments. The round 1 line "from my memory" is now sourced. Cyan's own Firmament pitch also says "Unreal 4" for Firmament and says Obduction was built PC first, then VR.

B11 (two-scale graph, kill if fewer than 3 of 5): INCONCLUSIVE, and not cleanly testable this round. Rule broken on purpose and disclosed: the fresh-pages-only rule could not be met for three titles, because the free sources that describe both scales are the Wikipedia pages already read. Count with that contamination marked:
- Myst: scale 2 (Ages joined by books) documented in round 1; scale 1 (nodes inside an Age) not fetched this round. UNTESTED.
- Riven: both documented on the REREAD page (stills with click movement; five islands of one Age, Ages joined by books). Holds, contaminated.
- Uru: scale 2 holds; scale 1 FAILS on a strict reading: search summaries of Wikipedia and reviewers describe third-person 3D movement inside Ages, not fixed nodes. Fails.
- Obduction: REREAD page says "node-based point and click" movement alongside free movement, and Seeds swapping areas between worlds. The page does not frame the worlds as nodes. Weak, contaminated.
- Firmament: compartments of one world under the lean from R1; scale 2 fails. Fails.
Best case 3 of 5 (Myst assumed), strict case 2. Both the threshold and the evidence are on the edge, and the hypothesis was formed post hoc. B11 carries no weight: it is neither confirmed nor killed. A fair test needs a source that states, per title, how movement inside a world works, not a page already read. Also note the two "scales" use different mechanisms (click nodes versus a linking panel), so even a pass shows a shared graph shape, not one repeated rule.

Flags (round 2):
LOAD-BEARING: the Firmament coding still decides B8; Cyan's own words lean compartments but do not settle it. B11 fails to resolve on the evidence available.
COUNTERINTUITIVE: nothing moved a prior by more than 0.3. R2 (0.8) and R3 (0.95) held.

Open after round 2: Pod mechanics from a Cyan source, developer interviews (Kickstarter updates #28 and #35 need the logged-in page), Myst scale-1 sentence, and a per-title movement source for B11.

## Echo tests run (2026-10-15, after round 2)

Run on prod via `supabase db query --linked` (read-only select) and a grep of this worktree. Kills were fixed in backlog rows echo-raw-capture-regenerate-briefs, echo-surface-restates-receipt-audit and echo-fake-exit-audit before running.

Test 1, raw capture (receipt is the raw, surfaces are developments): PARTLY SUPPORTED, with one design finding.
- `rawResponse` is filled on 271 of 271 receipts and parses as JSON on all 271 after fence stripping. The raw is really kept.
- Parsed columns match the raw: `trueNorth` 0 mismatches of 271, `nciScore` 0 of 271.
- Tributaries: the persisted `atgTributaries` column is null on 197 of 271; those surfaces fall back to `rawResponse` (src/lib/tributaries.ts). So for 73 percent of receipts the raw is the only source, and the fallback is working as designed. Of the 74 with both, 1 differs: the column holds short labels (Meta, Challenge, Adjacent) where the raw has longer ones. That is a write-time relabel, a lawful transform, not a loss, but I compared labels only, not prompt text, for the other 73.
- NOT run: regenerating three briefs and diffing. The brief prose (`situationFraming`) comes from a model call (`/api/brief/[receiptId]`), is generated once and stored, so a regenerate is not deterministic and would spend the shared API budget. By design that layer is a baked output, not a re-developable one. The "regenerate and diff" kill therefore cannot be applied to it. The prior survives for the deterministic layer (publicReceipt, scrubbing, tributaries) and is untested for the prose layer. Note also that the brief call reads parsed columns plus prep, not `rawResponse`, so "develop from the raw" is not what the brief does.

Test 2, surfaces restate the receipt: NOT TESTED beyond a structural check.
- All four receipt and brief pages (brief, brief reflect, receipt, receipt reflect) read through the one endpoint `/api/brief/[receiptId]`, which supports "one description, many entry points" for that family.
- Eleven other client pages also fetch receipt-family APIs, and 19 files read Receipt or Brief rows directly. I did not audit whether any of them carry claims not traceable to a receipt field. Kill not applied.

Test 3, fake exits: NO FINDING, weak test. A static scan of src/app found no `href="#"`, empty hrefs, no-op onClick handlers or permanent `disabled` buttons (the one hit is the design-test demo). Only 9 static internal hrefs exist; most navigation is built from template strings or router calls, which this scan cannot see. It rules out the crudest dead controls only. Undeclared one-way doors were not audited.

Net: nothing killed. One finding worth keeping: the brief prose layer is the baked JPEG in this metaphor, and the receipt raw is intact.

## Correction to the echo tests (2026-10-15, appended, earlier text left as written)

Test 1 above says the `atgTributaries` fallback "is working as designed". That is wrong. The column was introduced and never backfilled, so 197 receipts depend on the raw reply for tributaries. A follow-up chat message also called the 06-12 to 06-29 stretch an inconsistent write window. That was wrong too: I took the earliest filled row as the start, and that row is a one-off. Receipts in creation order: one filled row on 2026-06-12 (index 28), 169 empty rows after it, then an unbroken run of 73 filled rows from the first receipt after 2026-06-29. The boundary is clean, so the zero point (T0) is that run's start. Counts: 197 empty, 74 filled, 271 total. The contact sheet in `_ARTIFACTS/raw-capture.html` shows the same data.
