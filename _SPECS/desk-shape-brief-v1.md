# The Desk — shape brief v1.1 (impeccable `shape`, Phase 3 — gauntleted)

> v1 confirmed by Zach 2026-09-04 ("Go ahead"). v1.1 (2026-09-06): polish -> `/dual-bar-raiser`
> (α PASS-WITH-FIXES, β PASS-WITH-FIXES, held as ROM CANDIDATE) -> brand-manager persona gauntlet
> (REVISE -> applied) -> kintsugi receipt `_STATE/2026-09-06-desk-brief-kintsugi.json`. Material
> state: **SOLID**. Hierarchy level: **template** (the desk grammar) instantiating one **page**.
> Still a BRIEF, not a build: the three operator decisions in §7 are unresolved and a builder must not
> invent them. Plan: `_SPECS/reading-room-build-plan-v1.md`.

## 1. Job and audience
The librarian's desk: the *reader's* intent router (distinct from the Metabolic Router of ADR-075, which routes records, not people — a naming seam, resolved here by qualification) and federated front door for the PRIVATE reading room.
Audience of one (Zach), arriving to *do* something with the corpus, usually mid-work, wanting a
route not a catalog. Visitor mode: **Operate** (a tool), with a Read-mode lean for the works it opens.

## 2. Outcome and proof
Primary task: answer "what are you here to do?" and route: skim the state (Almanac) · trace a
concept (Concordance) · walk the history (Chronicle) · define a term (Lexicon) · find the ruling
(Codex / ADRs). Success = you land and get routed **without knowing the name of the reference work.** Failure (the
kill condition) = the desk shows a catalog of five names and makes you pick; if the first screen is
legible as a list of works rather than a list of questions, the brief has not been honored. Product truth: a reading room organized by the *question each work answers*, not by content;
every public surface (NFTT, briefs, goods) is a lawful air-gapped projection of a private original
that lives behind this desk. Evidence: the Almanac already exists (264 graded nodes) as tenant #1.

## 3. Selected direction
Visual authority: the ARCS FieldOS dark cockpit (WORLD.md; `#020408`, JetBrains Mono + Inter,
earned-fidelity render scale). Structural thesis: the Reader's Skim/Scan/Trenches altitude grammar is
the shared language every tenant inherits, because altitude is the earned-fidelity scale (WORLD.md
render table) applied to reading: the reader gets no more resolution than the slice's freshness has
earned. That is why it, and not a content schema, is the invariant that survives the change of basis
from desk to tenant (Tao §V); the desk and its works read as one system. Sequence:
the question first (the intent prompts), the tenants second, the corpus state third. Focal moment:
the moment the desk asks *what are you here to do* and one click lands you inside the right work at
the right altitude. Implementation consequence: an admin-gated Next.js route reusing the `/recoil`
gate (Auth.js session + `ADMIN_EMAILS`, fail-closed); tenants are the existing local renders served
through it, not rebuilt.

## 4. Scope and boundaries
Fidelity: production-ready gated route at hierarchy level *template* (the desk grammar)
instantiating one *page*; v1 = the desk + Almanac wired. Breadth: one screen (the
desk) + tenant frames. Interactivity: intent routing, tenant switching, freshness read-out. Named
target: `app.arcs.care/library` (or `/reading-room`, open decision). Untouched: the public surfaces,
the app's product routes, the tenants' own renders. Anti-goals: NOT a dashboard, NEVER public, no
new deps, no Tailwind, no auto-promotion of anything to canon or to public, no re-deriving the
design system.

## 5. States and ranges
Tenants: 1 today (Almanac) -> 5 (Concordance, Chronicle, Lexicon, Codex). Corpus: 264 nodes now,
hundreds later. States: locked-out (non-admin -> the gate), empty tenant (work not built yet: show
it as a shelf slot with its question, never a broken link, and never a fake shelf — the slot is
labeled *unbuilt*, not styled as if it had contents; earned fidelity applies to the desk itself), stale slice (cache-manifest says dirty:
mark the slice stale in the tenant's rail; re-grade lives inside the tenant, not on the desk), fresh, loading a large render.

## 6. Interaction and layout
Hierarchy: the intent prompts dominate the first screen; tenant list second; corpus readout (node
count · last graded · drift, one mono line, **no plot**) third. Seam shown: v1 said "corpus pulse …
one plot", which contradicted §4's NOT-a-dashboard anti-goal on the same screen; a plot on a router is
decoration, a readout is an instrument. Topology: desk -> tenant (full frame) -> back. Responsive:
one shared `--measure` token, `repeat(auto-fit, minmax())` grids, verified at desktop / ~790 /
tablet / mobile (the wrap-regression class). Affordances: intent = the questions the room answers, set as type, not as buttons — draft copy (to
be tuned, not renamed into a menu): *what changed since I last looked?* (Almanac) · *where does this
idea show up?* (Concordance) · *how did we get here?* (Chronicle) · *what does this word mean here?*
(Lexicon) · *what did we rule?* (Codex). The desk never prints "what are you here to do?"; the
questions are the heading. Tenant freshness as a dated mono stamp (`graded 2026-09-04`), muted tier,
not a status pill; every tenant's export stays available. Feedback: route
confirmation is the tenant opening at the right altitude, nothing else.

## 7. Constraints and open decisions
Platform: Next.js 16 app route, inline styles only, single `globals.css`. Gate: `src/lib/admin.ts`
pattern, fail-closed in prod. Reusable components: the Reader (research_render.py output) as the
tenant frame; the cache manifest for freshness; the desk's intents and tenant slots are read from a
manifest (data), never hardcoded in the route, so a second tool can consume the same shelf.
Open build seam (named, not solved): the Almanac is LOCAL-only while the desk is hosted; how a local
render becomes a served frame (commit the render? build-time generation? admin upload?) is a
Phase-1c design question, not something this brief implies is settled. Delivery: local-first renders, the desk is the only
hosted piece and it is gated. Open decisions a builder must NOT invent, with the corpus evidence each gauntlet found:
(1) route name `/library` vs `/reading-room` — the build plan §3 row 1c already names
`app.arcs.care/library`; `/reading-room` appears only in CLAUDE.md; personas lean `/library` (a place).
(2) freshness on the front door vs inside a tenant only — `cache-manifest.spec.md` puts freshness per
slice inside the Reader; engineer and brand-manager personas lean inside-only, the mid-work operator
wants the dated stamp on the shelf slot so a stale Almanac is not a surprise on arrival.
(3) Codex tenant = ADR index or full canon — "Codex" already names the full canon
(`_CANON/living/ARCS-Codex-v8.5.md`); calling the ADR index "Codex" would collide with an existing name.
