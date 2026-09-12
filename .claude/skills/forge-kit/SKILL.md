---
name: forge-kit
description: Magnetically scaffold a whole engagement macro-construction — food, experience, tuned-explanation (oriented by a guest intake), and gift — by forking existing ARCS templates in one move. The macro BETWEEN tool-forge (one CLI) and a full bespoke build. Use when standing up a new counterpart/subject universe and you want the four-station experience, aimed by asking the guest what they're craving rather than only modeling them.
---

# /forge-kit — one intake, four stations, a whole universe forked

> **Blueprint status:** DESIGN (composition + protocol). It orchestrates existing tools; it does
> not replace them. Governed by ADR-080 (instance→class self-promotion).
> **Relationship:** `tool-forge` forges the **micro** (one self-contained CLI package).
> `omakase-pipeline` produces the **three-surface universe** (back-of-house SSOT → cellar/canon →
> front-of-house suite). **forge-kit is the orchestrator between them** — it composes
> `omakase-pipeline`, the `recoil-{new,prep,close,ship}` loop, `tool-forge`, the artifact aesthetic,
> and the gift into ONE forkable macro construction, and it adds the missing front door: the intake.

## The four stations (map to what already exists)

A complete macro construction has four stations. The kit's job is to fill all four by forking, not
authoring from scratch:

| Station | What it is | Fork from |
|---|---|---|
| **1 · The Food** | the substance — the coursed omakase / canon / cellar | `omakase-pipeline` (three-surface family) |
| **2 · The Experience** | the interactive vessel it's served on | `_ARTIFACTS/*.html` cockpit instruments + `src/document/` patterns + `public/templates/call-brief-template.html` |
| **3 · The Tuned Explanation** | what it is · how it helps **them**, in their register | `recoil-prep` scans **+ the Intake (below)** |
| **4 · The Gift** | the take-home that outlives the meeting | `Receipt.tsx` / `Brief.tsx` + `souvenir-ship-ritual` |

The air-gap holds across all four (see the internal/external memory): **front-of-house is public,
the cellar is internal.** The recipe books in the cellar *are* the receipts (recipe/receipt =
`recipere`, doublets — the instruction you take, and the record of what you received).

## The Intake — the front door (the give/take)

The old failure mode: tune the explanation from our *derived model* of the guest (scans alone) —
the audience-model trap. The fix is **omakase with a whispered intake**: ask one orienting round,
then plate. The chef still controls the surprise and the craft; the guest's answer only *aims* it.
This is active listening as the first move — ask them, don't only model them — and it is Tao verse
vii made operational ("serve only what the guest can eat"): the intake is *how you learn the
appetite you're plating to.* The **give** (their reference) earns the **take** (your tuning), and it
is their consent to the co-creation.

Five intake questions (adapt; keep it short — this is a whisper, not a survey):

1. **Terrain** — what are you working on / deciding right now?
2. **Bearing** — what does good look like here? what would make this worth your time?
3. **Reference** — give me one thing you love, admire, or want this to feel like. (orients register + aesthetic)
4. **Appetite** — full tasting, or one sharp bite? (orients the portion — right-sizing)
5. **Gift** — what would be genuinely useful to walk away holding?

Their answers set the dials: #3 tunes station 3's register, #4 sets the portion across all
stations, #5 aims station 4. If a guest declines the intake (pure chef's-choice, or no bandwidth),
fall back to `recoil-prep` scans and note the tuning is *modeled, not asked*.

## The Fish Finder — classify the water before you open the tackle box

Before picking gear, read what kind of fishing this is. The **fish finder** = the Kairos detector
(ADR-081) + the intake; the **tackle box** = this kit. Bringing the wrong tackle IS the waste. Three
modes, read from stakes × reversibility · relationship horizon · target-specificity · crew/effort:

| Mode | Water | Tackle (which stations) |
|---|---|---|
| **Deep sea** | high stakes, low reversibility, full crew, trophy expedition | **all four stations** — the full omakase macro construction |
| **Fly fishing** | long horizon, catch-and-release, high skill, relationship-first, low pressure | **light tackle** — a tuned bite + the relationship; NO full spread |
| **Spear fishing** | one exact target, solo, minimal gear, single precise shot | **one station** — a single sharp decision/artifact |

Two rules: (1) **classify before you fork** — deep-sea gear in a trout stream is the Shannon error
(a nine-course monologue trawled at a survival-mode contact who was fly-water). (2) **the water
changes** — the same counterpart can be fly-fishing now and deep-sea when their horizon reopens; the
fish finder re-reads every time, it does not file-and-forget.

## Fork procedure (the magnetic scaffold)

1. **Intake** — run the five questions (or scans if declined). Record the reference + appetite + gift target.
2. **Fish-finder + size** — classify the mode (deep sea / fly / spear) and size the opportunity
   (core-function ADR). The mode picks the tackle subset. Sometimes the
   right macro construction is a single bite, not the four-station tasting. Do NOT omakase a Tuesday
   lunch (Tao vi). The kit scales down to one station.
3. **Fork the stations you sized in** — `recoil-new` for the SSOT; `omakase-pipeline` for food+cellar;
   copy an `_ARTIFACTS/` instrument for the experience; `Receipt`/`Brief` for the gift.
4. **Tune to the intake** — apply the reference (register/aesthetic), the appetite (portion), the gift target.
5. **Air-gap** — split front-of-house (public, silkscreen, no client specifics) from cellar
   (internal SSOT, receipts, experiments). Enforce with `recoil_brief.py --audience external` /
   `leak_check.sh`.
6. **Prove + ship** — screenshot the front of house before any deploy (deploy-antipattern memory);
   `recoil-ship` projects and drafts the note (never auto-sends).

## Right-sizing (the kit is not "always the full omakase")

The most important dial is #4 (appetite) crossed with the opportunity size. High stakes + high
appetite → full four-station build. Low appetite (survival mode) → one load-removing bite, or
nothing. Serving the whole kitchen to a nugget appetite is as wasteful as under-prepping a
ruin-stakes decision (Tao vii; core-function ADR). Cook to the stakes; plate to the appetite.

## Anti-goals

- Don't fork all four stations by reflex — size first; most guests are not a full tasting.
- Don't tune from the model alone when you can ask (intake > audience-model projection).
- Don't leak the cellar into the front of house — recipes/receipts/experiments stay internal.
- Don't author from scratch what a template already casts — fork it (ADR-080).
- Don't skip the screenshot before deploying the experience.
