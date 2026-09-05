# The Desk — shape brief v1 (impeccable `shape`, Phase 3)

> Confirmed by Zach 2026-09-04 ("Go ahead") after the compact-confirmation round. This is the
> design BRIEF, not a build: shape stops here. Next: polish -> refine -> distill -> `/dual-bar-raiser`
> -> persona brand-manager gauntlet -> kintsugi -> then build. Plan: `_SPECS/reading-room-build-plan-v1.md`.

## 1. Job and audience
The librarian's desk: the intent router and federated front door for the PRIVATE reading room.
Audience of one (Zach), arriving to *do* something with the corpus, usually mid-work, wanting a
route not a catalog. Visitor mode: **Operate** (a tool), with a Read-mode lean for the works it opens.

## 2. Outcome and proof
Primary task: answer "what are you here to do?" and route: skim the state (Almanac) · trace a
concept (Concordance) · walk the history (Chronicle) · define a term (Lexicon) · find the ruling
(Codex / ADRs). Success = you land and get routed **without knowing the name of the reference
work.** Product truth: a reading room organized by the *question each work answers*, not by content;
every public surface (NFTT, briefs, goods) is a lawful air-gapped projection of a private original
that lives behind this desk. Evidence: the Almanac already exists (264 graded nodes) as tenant #1.

## 3. Selected direction
Visual authority: the ARCS FieldOS dark cockpit (WORLD.md; `#020408`, JetBrains Mono + Inter,
earned-fidelity render scale). Structural thesis: the Reader's Skim/Scan/Trenches altitude grammar is
the shared language every tenant inherits, so the desk and its works read as one system. Sequence:
the question first (the intent prompts), the tenants second, the corpus state third. Focal moment:
the moment the desk asks *what are you here to do* and one click lands you inside the right work at
the right altitude. Implementation consequence: an admin-gated Next.js route reusing the `/recoil`
gate (Auth.js session + `ADMIN_EMAILS`, fail-closed); tenants are the existing local renders served
through it, not rebuilt.

## 4. Scope and boundaries
Fidelity: production-ready gated route, v1 = the desk + Almanac wired. Breadth: one screen (the
desk) + tenant frames. Interactivity: intent routing, tenant switching, freshness read-out. Named
target: `app.arcs.care/library` (or `/reading-room`, open decision). Untouched: the public surfaces,
the app's product routes, the tenants' own renders. Anti-goals: NOT a dashboard, NEVER public, no
new deps, no Tailwind, no auto-promotion of anything to canon or to public, no re-deriving the
design system.

## 5. States and ranges
Tenants: 1 today (Almanac) -> 5 (Concordance, Chronicle, Lexicon, Codex). Corpus: 264 nodes now,
hundreds later. States: locked-out (non-admin -> the gate), empty tenant (work not built yet: show
it as a shelf slot with its question, never a broken link), stale slice (cache-manifest says dirty:
show a freshness badge, offer re-grade), fresh, loading a large render.

## 6. Interaction and layout
Hierarchy: the intent prompts dominate the first screen; tenant list second; corpus pulse (nodes ·
live · drifted · stale, one plot) third. Topology: desk -> tenant (full frame) -> back. Responsive:
one shared `--measure` token, `repeat(auto-fit, minmax())` grids, verified at desktop / ~790 /
tablet / mobile (the wrap-regression class). Affordances: intent = large calm targets, not buttons
shouting; tenant freshness as a quiet badge; every tenant's export stays available. Feedback: route
confirmation is the tenant opening at the right altitude, nothing else.

## 7. Constraints and open decisions
Platform: Next.js 16 app route, inline styles only, single `globals.css`. Gate: `src/lib/admin.ts`
pattern, fail-closed in prod. Reusable components: the Reader (research_render.py output) as the
tenant frame; the cache manifest for freshness. Delivery: local-first renders, the desk is the only
hosted piece and it is gated. Open decisions a builder must NOT invent: (1) route name `/library`
vs `/reading-room`; (2) whether freshness shows per tenant on the front door or only inside a tenant;
(3) whether the Codex tenant is the ADR index or the full canon.
