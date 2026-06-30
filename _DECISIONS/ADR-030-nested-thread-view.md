# ADR-030 — Nested thread view for tributary follow-ups

> **Status:** DECIDED (architecture) — Option B chosen on real production data; not yet built
> **Date:** 2026-06-29
> **Commit:** (set at merge)

---

## D — The Decision

Build a real nested/threaded view of a receipt's follow-up chain (tributary → completed follow-up receipt → its own follow-ups) on `/brief/[receiptId]`, instead of the current flat "↳ N follow-ups" count badge that only shows on History.

**Sharp question:** Should ARCS render the actual lineage tree (parent → children → grandchildren) as nested UI, or keep surfacing it as a flat count?

---

## E — Entity / System

- `prisma/schema.prisma` — **no schema change needed.** `Receipt.parentId`, `Receipt.parentTributaryIndex` (0/1/2 — which tributary spawned this), and `Receipt.children` (self-relation, named `"lineage"`) already model the full tree. Confirmed by reading the schema directly, not assumed.
- `src/app/api/brief/[receiptId]/route.ts` — already does one level of `children` include (`select: id, decision, trueNorth, yState, nciScore, version, createdAt`, ordered by `createdAt asc`). Arbitrary-depth rendering needs either recursive includes (Prisma doesn't support unbounded recursive include natively — would need a raw recursive CTE or N sequential queries) or lazy per-node fetch on expand.
- `src/organisms/Brief.tsx` — currently renders `ExpandableTributariesStack` (the *suggested* tributary prompts, not completed follow-ups) via `result.tributaries`. Needs a new section rendering actual `children`.
- `src/app/history/page.tsx` — currently shows `↳ N follow-ups` as a flat badge per row (`r.children?.length`), no nesting. Out of scope for v1 per the phasing below, but the same tree-render component should be reusable here later.
- New component candidate: `src/molecules/ThreadTree.tsx` (or similar) — recursive node renderer, reusable across Brief and (later) History.

---

## W — Window

**Horizon:** QUARTER (real feature, not a quick fix — Zach's own framing in the toolbar thread)
**Revisit trigger:** if receipt trees start running deep (4+ levels) in practice, the "lazy per-node fetch" approach (Option B below) becomes necessary regardless of which option ships first, since recursive Prisma includes don't scale.

---

## Context

Toolbar thread `e7tomv612gRX` (asked on `/brief/cmqbd3i3k000104lawptiz7x0`): *"if we do include this feature is there a nested way to show sub questions / follow-ups based on primary thread? I know we were showing them in history but not in a nested sub-item capacity."*

Confirmed by reading the code (not assumed): History's badge is a count only, no nesting, no link into the children themselves. Brief shows zero children info today — it only shows the *forward-looking* tributary suggestions, which is a completely different artifact (a prompt to ask next) from a *completed* follow-up receipt (an actual answered question). The data to build real threading already exists and is already queried one level deep; the gap is entirely UI.

---

## Options Considered

### Option A — Single-level nested list (cheap, ships now)
- Render each `children[]` entry directly under the parent's True North on `/brief`, as a small indented card (tributary-type-colored rail, same visual language as the existing tributary chips) linking to `/brief/{childId}`.
- Grandchildren (children-of-children) are NOT rendered inline — clicking through to the child's own `/brief` page shows *its* children, recursively, one click at a time.
- Pros: no new API work (the one level of `children` already returned by `/api/brief/[receiptId]` is sufficient), no recursive-query problem, ships fast.
- Cons: not a true "nested thread view" — it's click-through pagination dressed as nesting. Doesn't satisfy "see the whole tree at a glance."

### Option B — True recursive tree, lazy-loaded per node
- A new endpoint (or extending the existing one) returns the full descendant tree, fetched breadth-first: query children of the root, then a second query for children-of-children only for nodes the user expands (accordion-style), capped at some depth (e.g. 5) to bound cost.
- Render as an actual indented tree component (`ThreadTree`), each node showing decision/True North/conviction snippet + expand toggle.
- Pros: matches what Zach actually asked for — see the shape of the whole conversation thread, not just one level.
- Cons: real build — new query pattern, new component, expand/collapse state, decide what happens with deep/wide trees (most receipts probably have 0-3 children in practice, so this may be over-engineering relative to actual usage — worth checking real tree depth/width in the DB before committing to this).

### Option C — Full recursive tree, eager, single CTE query
- One raw SQL recursive CTE (`WITH RECURSIVE`) pulls the entire descendant tree in one round trip, rendered fully expanded by default.
- Pros: simplest *rendering* code (no lazy-load state machine), single query.
- Cons: raw SQL outside Prisma's query builder (maintainability cost), unbounded tree size is a real risk if a thread ever gets deep/wide — needs a hard depth cap regardless.

---

## Decision

**Real production data checked (2026-06-29, via `supabase db query`, recursive CTE on `Receipt`):**
- Max thread depth: **6 levels**
- Widest single node: **5 children** (the pinned demo receipt itself, `cmqbd3i3k000104lawptiz7x0` — exceeds the nominal 3-tributary cap, since a parent can be revisited more than once)
- 198 total receipts currently in lineage chains

This disproves the "probably shallow" assumption that would have justified shipping Option A alone — trees already reach 6 levels in real usage, so a click-through-one-level-at-a-time view would force 6 page loads to see a thread that's only 6 nodes deep. **Option B (recursive, lazy-loaded-per-node tree) is the right target**, not a "maybe later" — Option A's single-level view does not satisfy the actual ask at current data depth.

**Chosen: Option B**, scoped down for v1 to a fixed depth cap of 8 (covers the observed max of 6 with headroom) rather than fully unbounded, to avoid Option C's unbounded-tree risk without the added complexity of a raw recursive CTE — sequential per-level Prisma queries (cap 8 levels) keep it inside the existing query builder.

**Trade-offs accepted:** real build, not a quick fix — new `ThreadTree` component, expand/collapse state, a capped multi-query fetch (not free). Depth cap of 8 means a future thread deeper than 8 silently truncates rather than erroring — acceptable for v1, flagged for revisit if it's ever hit.

---

## Y — Conviction

**Polarity:** GREEN — decision is now grounded in real data, not assumption
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Could the depth-8 cap bite in practice? Current max is 6, so there's 2 levels of headroom — but if Zach's own usage pattern (chaining follow-ups from follow-ups) continues, 8 could be hit within a few months. Mitigated by the cap silently truncating (not erroring) and being a single constant to bump later, not an architectural limit.

---

## Consequences

- Unblocks: a real answer to the toolbar thread, either as a shipped A or a scoped B/C build ticket.
- Does not change History's flat-badge behavior in v1 — explicitly deferred, not forgotten.
- Next decision this creates: depth/width query on real data, to settle A-vs-B before more build time goes in.

**Implementation pointer:** not started. Toolbar thread `e7tomv612gRX` has this ADR linked as the scoping response.

---

## Linked receipts / ADRs

- Toolbar thread `e7tomv612gRX` — the original ask
