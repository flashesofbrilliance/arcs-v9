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

> Moved verbatim to `.claude/rules/world-product.md` (2026-10-17, WS1 slice 3). It loads when you read, write or edit anything in the src or prisma folders.

## THE ARTIFACTS

> Moved verbatim to `.claude/rules/world-product.md` (2026-10-17, WS1 slice 3). It loads when you read, write or edit anything in the src or prisma folders.

## THE TERRAIN METAPHOR (Backcountry Avalanche)

> Moved verbatim to `.claude/rules/world-product.md` (2026-10-17, WS1 slice 3). It loads when you read, write or edit anything in the src or prisma folders.

## THE BAR EDGE (Free Solo)

> Moved verbatim to `.claude/rules/world-product.md` (2026-10-17, WS1 slice 3). It loads when you read, write or edit anything in the src or prisma folders.

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

## THE HUD (route-finding, Zach 2026-11-01)

**Pick the destination, see the whole route, take the safest clear step next, never cross a
one-way door in fog.** The field HUD is not a troubleshooting console or a picture to admire. It
answers one question: what is the clearest, safest approach to this destination? It loads three
layers onto one field. **Terrain:** the canon lattice, what is load-bearing, blocked, or thin on
proof. **Route:** the backlog graph from a chosen job, where slope is ruin and one-way doors,
visibility is evidence, holds are blocked rows and pending decisions, and the safe bearing is the
next step that is ready, reversible, tooled and ripe. **Time:** belief change, scrubbed by date,
where a falsified belief shows as a repaired seam in gold, never silently erased. Every reading
earns its fidelity: a gauge with too little evidence renders grain and prints its sample size, and a
visual that cannot go flat on empty data is decoration. Specs: the HUD moire audit and ruling
sheet in `_PROPOSALS/`.

---

## THE PROGRESSION

> Moved verbatim to `.claude/rules/world-render.md` (2026-10-17, WS1 slice 3). It loads when you read, write or edit anything in the src, public or _ARTIFACTS folders.

## THE TONAL REGISTER

For every build decision, ask: **Does this feel like Myst or does it feel like SaaS onboarding?**

Myst trusted you. It gave you a world and let you navigate it. It didn't celebrate with confetti. It rendered at full fidelity and expected you to rise to it.

**Calm. Precise. Serious play. Tools that feel like instruments in skilled hands.**

Copy that doesn't explain what you already understand. Visual fidelity that is *earned*, not assumed.

---

## BRAND IDENTITY

> Moved verbatim to `.claude/rules/world-render.md` (2026-10-17, WS1 slice 3). It loads when you read, write or edit anything in the src, public or _ARTIFACTS folders.

## THE RENDER SCALE

The brief and all UI sections render at **earned fidelity**: never at higher resolution than the data deserves.

Text always renders at full opacity (Zach, 2026-10-11). Fog is shown through weight, tracking and the grain overlay, never by dimming the words: a fog you cannot read fails the contrast floor, and the brief must stay legible at every depth.

**Earned fidelity has a floor: coherent wrapping.** One shared px measure for body text, ledes at full width, verified with the surface's own gate (AGENTS.md gotcha 13).

> The Y-state fidelity table and the full reading are in `.claude/rules/world-render.md`, which loads when you read, write or edit anything in the src, public or _ARTIFACTS folders.

## THE FIRST THING TO BUILD

> Moved verbatim to `.claude/rules/world-product.md` (2026-10-17, WS1 slice 3). It loads when you read, write or edit anything in the src or prisma folders.

