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
