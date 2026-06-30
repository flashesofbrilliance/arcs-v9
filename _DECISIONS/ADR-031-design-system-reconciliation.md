# ADR-031: Design System Reconciliation — Extend vs. Namespace

**Status:** DECIDED  
**Date:** 2026-06-30  
**Author:** Claude Code (Haiku 4.5)  
**Stakeholders:** UI/Component owners, Compass Kit Phase 2 team

---

## Problem

The static Compass UI kit (`public/compass-kit/`) has a richer component API than the existing typed design system in `src/ui/`. The kit includes:
- Button variants: `outline-cyan`, `outline-green`, `outline-gold`, `outline-danger`, `ghost` (vs. current: `gold`, `primary`)
- Button sizes: `sm`, `md`, `lg` (vs. current: `sm`, `md`)
- Button glyphs/icons (vs. current: text-only)
- Card finishes: glass, underlit-LED (vs. current: basic accent + padding modes)
- New atoms: `Gauge`, `SegmentedSlider`, `ChipToggle`, `WeatherBar`, `StepProgress`, `ProgressBar` (not in src/ui/ yet)

**Decision:** How do we integrate this kit into the real app without forking the design system?

---

## Options

### Option A: Extend existing `src/ui/` (CHOSEN)
Evolve the existing design system by:
1. **Update core components:** Extend `Button.tsx`, `Badge.tsx`, `Card.tsx` with richer API (new variants, sizes, glyphs)
2. **Add new atoms:** Create new files for net-new components (`Gauge.tsx`, `SegmentedSlider.tsx`, etc.)
3. **Maintain single palette:** Reuse `tokens.ts` (kit's palette already matches it)
4. **Preserve import strategy:** Direct imports `@/ui/Button`, no barrel (ADR-011)

**Pros:**
- One source of truth for the DS
- No parallel implementations
- Cleaner codebase long-term
- Easier maintenance and future evolution

**Cons:**
- More upfront effort (reconcile while porting)
- Need to update call sites as API expands
- Requires careful typing of new variants

### Option B: Namespace as `src/ui/compass-kit/`
Keep kit as a parallel parallel design system:
1. Create `src/ui/compass-kit/` directory with all kit components
2. Use kit directly for Compass app routes
3. Keep existing `src/ui/` unchanged

**Pros:**
- Faster Phase 2 shipping (no reconciliation)
- Zero impact on existing code
- Can iterate on kit independently

**Cons:**
- Two competing design systems in one app
- Maintenance burden (duplicate components, diverging APIs)
- Confusing for new contributors ("which Button do I use?")
- Revisit cost when we eventually unify (compound work)

---

## Decision

**Option A: Extend existing `src/ui/`**

### Rationale

1. **Correctness**: One design system is architecturally correct. Two is technical debt.
2. **Sustainability**: Kit is well-designed and represents the "right" evolution. Commit to it rather than isolating it.
3. **Leverage existing investment**: `tokens.ts` is already correct; Button/Badge/Card structure is solid. Extend, don't duplicate.
4. **Long-term win**: Small upfront work (reconcile during Phase 2) buys long-term clarity.

---

## Implementation

### Phase 2a: Port atoms while reconciling DS

1. **Update core components** (`Button`, `Badge`, `Card`):
   - Add kit variant enums (e.g., `outline-cyan`, `ghost` for Button)
   - Add kit size enums (e.g., `lg` for Button)
   - Support glyph prop on Button
   - Add card finishes (glass, underlit-LED)
   - Full TypeScript typing with discriminated unions for variant safety

2. **Add new atoms**:
   - Create new files: `Gauge.tsx`, `SegmentedSlider.tsx`, `ChipToggle.tsx`, `WeatherBar.tsx`, `StepProgress.tsx`, `ProgressBar.tsx`
   - Each typed with full props interface
   - Use `tokens.ts` exclusively
   - Mark with `"use client"` if hooks/handlers

3. **Update call sites**:
   - Existing `Button variant="gold"` stays the same (backward compat via enum)
   - New variants available (`variant="outline-cyan"`, `size="lg"`)
   - Update Compass Kit Phase 2 components to use full API

4. **Validation**:
   - Build TypeScript: `npx next build` (strict type checking)
   - Visual parity: `/compass-kit` (static preview) vs. real app
   - No barrel exports (ADR-011 stands)

### Trigger to revisit

If we hit **≥8 components**, ADR-011 should reconsider a barrel export (currently prohibited).

---

## Consequences

1. **Scope increase:** Phase 2 now includes DS reconciliation, not just kit port
2. **Complexity:** Need careful typing and variant management, but improves overall codebase health
3. **Maintenance:** Single DS is easier to maintain than two
4. **Future**: Clear path for design evolution — extend `src/ui/` as the product grows

---

## Alignment

- **ADR-009** (Design system canonicalization): Affirms one DS is correct
- **ADR-011** (No barrel imports): Direct imports still the rule
- **Compass Kit Phase 2 handoff**: "Reconcile, don't fork" aligns with this choice
- **WORLD.md** (Instrument register tone): Extended DS supports the fidelity principles (SHARP, GRAIN, MOIRE)

---

## Sign-off

- **Decision:** Extend `src/ui/`
- **Owner:** Phase 2 implementation
- **Confidence:** GREEN / HIGH / STABLE
- **Revisit after:** Phase 2 ships; assess if barrel export is needed
