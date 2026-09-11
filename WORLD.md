# ARCS FIELD OS — WORLD BUILDER v1.0
> "Render through the fog to earned clarity."
> Read this before touching a route, a schema, or a component.
> It is not documentation. It is the world.

---

## THE WORLD YOU ARE BUILDING IN

You are not building a SaaS dashboard.

You are building **a navigable world** — a place a person enters when they are stuck, pressurized, or standing at a fork in the terrain with fog on all sides and a decision that won't wait.

**Myst**: you arrive in a world with no tutorial. The world itself teaches you how to read it. When you solve something, you don't feel clever — you feel like you finally *understood* what was already there. That's the feeling ARCS produces. Not "the AI told me what to do." But: *"I can finally see the terrain."*

**Hitchhiker's Guide to the Galaxy**: the parser doesn't tell you what to type. The Guide has an answer for almost everything, and it's almost never what you expected — but it's always *useful*. ARCS is the Guide. The compass is the parser. The brief is the entry you just unlocked.

**Leisure Suit Larry**: the world has memory. What you did three rooms ago matters now. ARCS has the same mechanic — your receipt history is the world's memory. The terrain you've already navigated doesn't fog over again. Your past choices are *cartography*.

---

## THE PHYSICS

Decisions are positions on a manifold under pressure.

You enter in fog. Your position is defined by the DEWY state vector:

- **D** — the sharpened question. What you are actually deciding.
- **E** — the entity. Who or what else is in the terrain with you.
- **W** — the window. Today, this week, this quarter, years out.
- **Y** — the yellow gate. The conviction gradient. Solid, shifting, flat, or entangled?

### The Four Zones

```
OUTER FOG LAYER       →  Dense, low visibility, coarse grain.
                          Y: SCRATCH / PARADOX
                          Navigate: orient only. Don't commit.
                          Visual: barely legible, maximum grain.

PRESSURE BAND         →  Turbulent, phase-change territory.
                          Y: YELLOW / FORK / DELTA
                          Navigate: careful movement. Y gate active.
                          Visual: coarse grain, contested terrain.

CLARITY RIDGE         →  High ground. True North visible.
                          Y: GREEN / HIGH conviction
                          Navigate: move confidently. Lock what you've earned.
                          Visual: sharp, full contrast, fine grain.

SUPERIONIC NUCLEUS    →  Crystalline. Frictionless. Luminous.
                          Y: LOCKED / post-Court resolved
                          Navigate: flow state — decisions arrive before questions.
                          Visual: crystal-sharp, hard edges, maximum resolution.
```

### Phase States (Matter Metaphor)

| Phase | Decision quality | Visual |
|-------|-----------------|--------|
| Gas | SCATTER — no coherence | Fog particles, no structure |
| Liquid | FLOWING but unstable | Fluid grid, shifting terrain |
| Solid | LOCKED but brittle | Hard blocks, sharp shadows |
| **Superionic** | **Structure + flow fused** | **Luminous crystal, light through fixed form** |

---

## THE ARTIFACTS

**The Receipt** — a state vector frozen in time. A coordinate. A seed. Not a document — a position on the manifold with full DEWY decomposition.

**The Brief** — the cartography output. Renders when clarity is earned. Silkscreen fidelity: honest to the data. In dense fog, coarse-grained. At the clarity ridge, sharp and fully populated. The brief never lies about how certain it is.

**The Compass** — the parser. Takes a question, runs L0–L5, returns a bearing + Y gate state. Does not tell you what to decide. Tells you *where you are and which direction is uphill*.

**The PrepSession** — the calibration instrument. Five fields. Two minutes. Stakes, window, what you're protecting, how certain you already are, strongest argument against your instinct. Optional — but when used, the compass runs with richer context and the terrain sharpens.

**The Observatory** — instant replay theater. Every session recorded as a kinematic trajectory. Scrub backward to any Receipt. Watch conviction gradient peak and collapse. See where you overrode a YELLOW. Overlay two sessions. Annotate inflection points.

---

## THE TERRAIN METAPHOR (Backcountry Avalanche)

Think backcountry avalanche terrain, not a marked resort trail.

- **Fresh snow** = apparent optionality. Many lines look open; most hide unknown layers.
- **Hidden weak layers** = unseen constraints and ruin risks (legal, reputational, liquidity, relationships).
- **Avalanche forecast + snowpit** = prep + Court — deliberate probing before committing to a line.
- **Skintrack choice** = path selection at a FORK — once you traverse onto a slab, some options disappear.
- **Safe travel protocols** = Y gate + BAR — assume hidden failure modes and move in ways that survive being wrong.

ARCS is the avalanche education + beacon + map + trip report system for decisions. You don't ride because the bowl looks good. You check layers, pick a line with survivable failure, and log what you saw so the next tour (future you) isn't guessing under fresh snow again.

---

## THE BAR EDGE (Free Solo)

Free solo is the BAR/Ruin edge in its purest form: one hidden constraint, one missed hold = total loss.

In ARCS terms:
- Stakes = existential, reversibility = zero → `mode = COURT`, Y = **RED**
- The system's job is to surface: *"You're free-soloing this decision. Any slip is unrecoverable. Are you sure you want this topology?"*
- ARCS strongly biases toward **adding protection or changing the climb**: partners, belay, smaller bet, simulation first.

If the underlying reality is "0% margin of error," the correct ARCS behavior treats it as a **design bug, not a personality quirk.** Redesign the decision so that a single mistake is survivable. Do not optimize grip strength on a no-rope route.

The Y gate's RED state is the system saying: "This is a free-solo topology. The Court has reviewed the route. You are exposed."

---

## THE ENEMY

No boss. No villain. The terrain is not hostile.

The enemy is **entropy masquerading as motion.** Spin cycles. The feeling of navigating while actually looping.

The Drift Sentinel detects this. After 5 turns without a new artifact: *"You've been in this zone for a while. Do you want to land the plane, or keep exploring?"*

---

## THE WITNESS

The opposite failure mode: a tree falls in the forest and nobody attests to it. A flash of
brilliance crystallizes mid-conversation — a principle names itself, a "wait, that's it"
lands — and it either gets folded into whatever gets written hours later (reconstruction,
not witness) or evaporates entirely.

A receipt filed after the fact, describing itself as having been there when it wasn't, is the
same dishonesty ADR-044 gates on the aspiration side. The fix isn't a new artifact type. It's
timing: attest in the moment, not at handoff.

The Witness Trigger fires when Claude notices the signal live — the user's own "wait, that's
it" / "yes exactly" / a naming moment, or Claude's own insight compressing into something
sharper than the conversation around it. It doesn't wait to be asked. It surfaces `/witness`
right there, one line: *"Can I get a witness — should I attest that this just happened?"* A
`yes` files a verbatim, timestamped stub — the sound the tree made, not a summary of it. That
stub is upstream of an ADR or DEWY receipt: raw material, promoted later only if it proves
durable, never dressed up as more than it was in the moment.

---

## THE PRINT SCHEDULE (ADR-068)

The five-verb arc — analyze → assess → evaluate → synthesize → recapitulate — is not a
narrative convention; it is a print schedule. **Every stage cut prints an artifact, through a
gate, to a fate.** A stage without a print happened only in conversation and will be re-derived
at full cost. A print without a gate is decoration. A gate without a fate gates nothing.
Mandatory-blocking: ex-ante receipt before any counterpart send · pre-send gauntlet ·
close-loop when they respond. Altitude is orthogonal; earned fidelity binds fate to render.

## THE FIELD GEOMETRY (Tao §V)

**One field, sovereign zeros, lawful transforms, preserved invariants.** No origin is
canonical — not the author's, not the machine's. Every artifact declares its frame; every
projection factory is a lawful transform; the lossless invariants are what must survive every
change of basis. Returning to zero returns *you* to *your* null point.

---

## THE PROGRESSION

Receipts earned → fog retreats → terrain readable → nucleus approaches.

Early: heavy fog, coarse briefs, Y gates firing yellow often.
Mid: patterns surface in Observatory, compass gets faster, NCI climbing.
Late: navigating from clarity ridge. Receipt history becomes a personal atlas.
Superionic: structure of clarity + fluidity of instinct. Decisions move through you like charge through crystal — fast, directional, lossless.

---

## THE TONAL REGISTER

For every build decision, ask: **Does this feel like Myst or does it feel like SaaS onboarding?**

Myst trusted you. It gave you a world and let you navigate it. It didn't celebrate with confetti. It rendered at full fidelity and expected you to rise to it.

**Calm. Precise. Serious play. Tools that feel like instruments in skilled hands.**

Copy that doesn't explain what you already understand. Visual fidelity that is *earned*, not assumed.

---

## BRAND IDENTITY

**Name:** ARCS  
**Tagline:** *Navigate to clarity. Survive the pressure. Find the flow.*  
**Visual world:** 2.5D isometric decision observatory — mission control + geological survey + instant replay theater

**Tagline system:**
- Primary: *Navigate to clarity.*
- Secondary: *Render through the fog.*
- Mechanic: *Survive the pressure. Find the flow.*
- Observatory: *Every decision, recorded. Every path, replayable.*
- Nucleus: *Superionic: where structure meets flow.*

---

## THE RENDER SCALE

The brief and all UI sections render at **earned fidelity** — never at higher resolution than the data deserves.

| Y State | Fog density | renderResolution | Visual treatment |
|---------|-------------|-----------------|-----------------|
| SCRATCH / EPHEMERAL | Pea soup | GRAIN | opacity: 0.70, weight: 300, tracking: +0.02em |
| PARADOX | Dense fog | MOIRE | opacity: 0.60, weight: 300, tracking: +0.03em + CSS ::after |
| YELLOW / CONTESTED | Clearing | DEGRADED | opacity: 0.85, weight: 400, tracking: +0.01em |
| GREEN / HIGH | Clear | SHARP | opacity: 1.0, weight: 500, tracking: normal |
| LOCKED / Nucleus | Crystal | SHARP + hard edges | opacity: 1.0, weight: 600, tracking: -0.01em |

**Earned fidelity has a floor: coherent wrapping.** Fidelity is the *resolution* of the render, never a licence for a ragged one. BODY reading text on a surface shares ONE measure (a single px `--measure`, never per-element `ch` caps); bordered callouts carry that measure on the box so every right edge lines up. But a LEDE is not body text: a hero or section lede spans the full lane, edge-to-edge with its heading — a lede pinched to the narrow body measure leaves a dead right gutter that reads as broken and abridged, the fog leaking back in from the other side. Both failures are the same sin (a text block whose width lies about its role), and the narrow one is invisible to overflow gates — so eyeball the lede against its heading, not just the sweep. Verify across the full width band (360–1440, especially 700–1000) with the surface's own gate before calling anything SHARP. Canon: `_PATTERNS/arcs-artifact-css-base.css`; enforcement in AGENTS.md gotcha #13; preference in memory `design-full-width-lede-matches-heading`.

---

## THE FIRST THING TO BUILD

One isometric terrain tile. Four fog densities. A glowing navigator node. A True North bearing arrow.

Drop the navigator into the outermost fog tile. Watch the terrain clarify as the compass runs. The brief renders as the silkscreen sharpens beneath the navigator's feet.

That single animation is the product demo, the brand story, the onboarding sequence, and the investor deck simultaneously.

Everything else is navigation.

```
// END WORLD BUILDER BRIEF v1.0
// Situational awareness loaded.
// The world is live.
// Begin.
```
