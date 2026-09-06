# The Desk — shape brief (revision 2: distilled + polished)

> Confirmed 2026-09-04 (Zach: "Go ahead"); three open decisions resolved 2026-09-06. Revision 2 is
> revision 1 distilled to essence and polished for consistency, per the impeccable `distill` and
> `polish` playbooks. Design brief only, no code. Next gates: `/dual-bar-raiser`, the brand-manager
> persona gauntlet, kintsugi. No build until the last clears. Plan: `_SPECS/reading-room-build-plan-v1.md`.

## The one goal
**You arrive mid-work, say what you are here to do, and land inside the right reference work at the
right altitude, without knowing the work's name.** Everything below serves that sentence.

## 1. Job and audience
The librarian's desk: intent router and gated front door for the private reading room. One reader
(Zach), usually mid-task, wanting a route, not a catalog. Mode: Operate.

## 2. Outcome and proof
The desk asks "what are you here to do?" and routes:
- skim the state -> **Almanac**
- trace a concept -> **Concordance**
- walk the history -> **Chronicle**
- define a term -> **Lexicon**
- find the ruling -> **Codex** (the full canon)

Proof it works: the Almanac already exists (264 graded nodes) and wires in as tenant #1.

## 3. Direction
- **Visual authority:** the ARCS FieldOS dark cockpit (WORLD.md; `#020408`, JetBrains Mono + Inter,
  earned-fidelity render scale). Do not re-derive.
- **Shared grammar:** the Reader's Skim / Scan / Trenches altitudes. Every tenant inherits it, so the
  room reads as one system.
- **First-screen order:** the five intents, then the tenants, then one corpus pulse (nodes · live ·
  drifted · stale; one plot, one number).
- **Focal moment:** the desk asks; one click lands you inside a work at the right altitude.
- **Implementation:** an admin-gated Next.js route at `/library`, reusing the `/recoil` gate (Auth.js
  session + `ADMIN_EMAILS`, fail-closed). Tenants are the existing local renders served through the
  frame, not rebuilt.

## 4. Scope
v1 = the desk + the Almanac wired. Concordance, Chronicle, Lexicon, Codex slot in as they are built.
Untouched: public surfaces, product routes, each tenant's own render.
Anti-goals: not a dashboard; never public; no new deps; no Tailwind; nothing auto-promoted to canon
or to public.

## 5. States
- **Locked out** (not admin): the gate.
- **Unbuilt tenant:** a shelf slot showing its question. Never a broken link.
- **Dirty slice** (cache manifest says stale): freshness badge on the front door; offer re-grade.
- **Fresh.** **Loading** a large render.

Ranges: 1 tenant now, 5 later; 264 nodes now, hundreds later.

## 6. Interaction and layout
- Hierarchy: intents dominate; tenants second; pulse third.
- Topology: desk -> tenant (full frame) -> back.
- Intents are large, calm targets. Freshness is a quiet badge. Export stays available inside every
  tenant.
- Feedback: the tenant opening at the right altitude is the confirmation. Nothing else.
- Responsive: one `--measure` token; `repeat(auto-fit, minmax())` grids; verified at desktop, ~790px,
  tablet, mobile (the wrap-regression class).

## 7. Constraints and decisions
- Platform: Next.js 16 app route; inline styles only; single `globals.css`.
- Gate: the `src/lib/admin.ts` pattern, fail-closed in prod.
- Reuse: the Reader as the tenant frame; the cache manifest for freshness.
- Delivery: local-first renders; the desk is the only hosted piece, and it is gated.
- **Decided 2026-09-06:** route is `/library`; freshness shows per tenant on the front door; Codex is
  the full canon.
- **One honest flag (from polish):** Codex is the only tenant that is not a Reader-rendered digest; it
  is the canon documents themselves. It needs its own frame decision (render the canon through the
  Reader, or link out to the docs) before it ships. Not a v1 blocker.

## Revision log
- r1 (2026-09-04): shape Phase 3 brief, three decisions open.
- r2 (2026-09-06): distilled (one goal stated once; repeated claims cut; sentences halved) and polished
  (terminology unified: desk / tenant / altitude / slice; decisions resolved; Codex frame flagged).
