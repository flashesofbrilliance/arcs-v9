# ADR-003 — arcs.care: COCD as First-Class UX Primitive

> **Status:** DECIDED  
> **Date:** 2026-05-27  
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should the Calibrate → Orient → Chart → Detect loop be surfaced as the primary UX frame on arcs.care, replacing or supplementing the current hero ("Make your next hard decision feel 10x lighter")?

---

## E — Entity / System

- `arcs.care` — public site (Vercel project `arcs-care`, `dpl_4TBqvWxUbuXZ6cNT53TiqJyxaCRE`)
- `mcp.arcs.care` — Perplexity MCP endpoint (blocked: domain not yet wired to `perplexity-mcp`)
- `arcs-field-os/jtbd/jtbd-master-map.md` — canonical JTBD sequence (Calibrate → Orient → Chart → Detect)
- L0–L5 pipeline in `src/app/api/compass/route.ts`

---

## W — Window

**Horizon:** QUARTER  
**Revisit trigger:** After first 10 paid Decision Lab completions — check if COCD framing accelerates or confuses conversion.

---

## Context

### Current arcs.care state (audited 2026-05-27)

**Hero:** "Make your next hard decision feel 10x lighter."  
**Subhead:** "arcs.care is a live decision lab for founders and small business owners. Bring one real decision — leave with a clear next move and a simple receipt of why."  
**CTAs:** "Book a 90-Min Decision Lab →" + "Get my next move →"  
**Nav:** Compass · Book a Lab · Waitlist

**NCI audit (L0–L5):**
- L0 "what is this?" — PARTIAL (52/100). You get "decision tool" but not ARCS's specific geometry. Fails the cold visitor test in < 3 seconds.
- L1 specific believable claim — WEAK. "10x lighter" is unverifiable noise. No receipt language, no terrain metaphor, no ARCS-native vocabulary.
- L2 one clear action — SPLIT. Two CTAs (free Compass vs. paid Lab) compete without sequencing logic.
- L3 evidence — EXISTS. Four scenarios + pricing + "10 spots" urgency. Grounding is present but buried.
- L4/L5 — NOT PRESENT. No COCD, no Kairos, no drift language. Site sounds like any AI decision assistant.

**NCI score: 52/100**

### Top 3 pathogens

1. **"10x lighter"** — AI-generated noise. Unmeasurable, unreceipted, forgettable. No one has ever bought a decision OS because it felt lighter.
2. **Unsequenced dual CTA** — Compass (free) and Lab (paid) aren't positioned as steps in a loop. A cold visitor can't tell which to do first or why.
3. **No ARCS-native vocabulary on the surface** — The site could be any GPT wrapper. Receipt, terrain, compass bearing, conviction, drift — none visible above the fold. The world isn't present.

### COCD ↔ L0–L5 mapping (translation layer, not new doctrine)

| Phase | L-stack | ARCS artifact | Current product surface |
|-------|---------|---------------|------------------------|
| Calibrate | L0–L1 | PrepSession | Optional prep form (exists, not featured) |
| Orient | L2–L3 | Receipt + Y-gate | Compass output |
| Chart | L4 | Decision Receipt + Brief | Brief page |
| Detect | L5 + Drift Sentinel | Outcome + Observatory | Not yet built |

COCD is a translation layer over L0–L5, not new doctrine. Every ARCS surface already lives inside one of the four phases.

---

## Options Considered

### Option A — COCD as hero frame (replace current)
- Hero becomes: "Where are you in the loop?" + COCD four-phase diagram
- Each phase links to the corresponding ARCS feature
- Pros: immediately differentiates from generic AI decision tools; vocabulary is ARCS-native; creates a navigable mental model
- Cons: higher cognitive load for cold visitors; requires COCD diagram asset (SVG)

### Option B — COCD as secondary frame (supplement current)
- Keep current hero as conversion hook, add COCD section below as "how it works"
- Pros: lower risk to conversion; existing CTA flow preserved
- Cons: COCD gets buried; doesn't fix the L0 "what is this?" problem

### Option C — COCD as nav item only ("The Loop")
- Add "The Loop" to nav, build a dedicated page explaining COCD with live demo
- Pros: minimal disruption to current conversion path
- Cons: too easy to skip; doesn't fix the hero copy pathogen

---

## Decision

**Chosen:** Option A + Option C combined

**Rationale:**
- Hero must speak ARCS-natively. "10x lighter" is a pathogen — remove it. Replace with terrain-aware copy that earns the L0 test in < 3 seconds.
- COCD loop diagram as the primary "how it works" visual — earns vocabulary, creates mental model.
- "The Loop" as nav item → dedicated page for depth without cluttering the conversion path.
- Sequenced CTAs: Compass (free, Calibrate/Orient) → Lab (paid, Chart/Detect) — position them as phases 1+2 and 3+4 respectively.

**Trade-offs accepted:** Some cold visitors may need more explanation upfront. Acceptable: ARCS is not a mass-market product. It's for founders who will lean in if the vocabulary is right.

**Proposed hero copy:**
> *Calibrate. Orient. Chart. Detect.*  
> The decision loop for founders who can't afford to be wrong.

Or tighter:
> *Navigate the terrain. Log the receipt. Find the line.*

---

## Y — Conviction

**Polarity:** GREEN  
**Conviction:** HIGH  
**Stability:** STABLE

**Loki test:** What if COCD vocabulary alienates cold visitors who don't know ARCS? Counter: the current copy already fails cold visitors (NCI 52/100). The risk of being too generic outweighs the risk of being too specific for ARCS's target user.

---

## Consequences

**Implementation tickets (see _QUEUE/):**
1. Rewrite hero copy — COCD frame, remove "10x lighter"
2. Build COCD loop diagram — SVG, four phases, each lighting up on hover
3. Sequence CTAs — Compass as step 1 (Calibrate/Orient), Lab as step 2 (Chart/Detect)
4. Add "The Loop" nav item → dedicated /loop page
5. Tag each arcs.care feature section to its COCD phase
6. Add `cocd_phase` field to mcp.arcs.care API response schema (after DNS fix)

**DNS blocker (separate from this ADR):**  
`mcp.arcs.care` returns 404 — custom domain not in `perplexity-mcp` Vercel project. Must add domain before API docs page can reference `mcp.arcs.care`.

**Implementation pointer:** `flashesofbrilliance/arcs-care` repo

---

## Linked receipts / ADRs

- ADR-004 — mcp.arcs.care DNS fix (blocker for COCD API docs)
