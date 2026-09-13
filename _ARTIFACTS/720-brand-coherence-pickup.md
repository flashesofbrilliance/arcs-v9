# 720° brand-coherence wire — pickup spec (parked at 98% weekly budget, 2026-09-09)

## The finding (confirmed live, this session)
Six owned surfaces all return 200, but from a serialized 720° POV they do NOT fly one flag.
The duality is TRUE but UNWIRED — every surface is a dead-end showing one lane:
- **prl.arcs.care** (live client-sprint proof): ZERO backlink to the consulting door.
- **build / good**: never name that the same operator does dedicated client work.
- **zachharris.xyz**: the ONLY node gesturing at both (carries "ARCS" + "Case Studies"), which is
  why Zach reads it as the singular front door — but its case studies don't link the live proof (prl).
- **resume.arcs.care · status.arcs.care · zachharris.xyz**: EMPTY `<meta description>` → blank to
  machines/unfurls. resume also has NO h1/lede — worst offender, highest stakes.

## The positioning (Zach's words, this session — the SSOT intent)
The point of building in public = **pre-empt the "consultant who doesn't ship" assumption** and flip it
to **anti-consultant who lives in the trenches and ships proof** — WITHOUT the term "FDE" or leaning on
"engineer" (audience doesn't know FDE, distrusts "engineer"). The proof surfaces carry it in plain words.
It is a coherent DUALITY (independent consulting sprints ⇄ dedicated in-house), one operator + one method
(ARCS), not a split. zachharris.xyz's existing voice already IS this register ("you get me, not a middle
layer"; "measured, not promised"); the gap is the claim and its evidence don't touch.

## The green-go flag (candidate — NOT yet blessed; lock wording BEFORE wiring)
Lead candidate: **"Proof, not promises. Watch me ship."** paired with the existing Wall-St-quality line.
Longer form: "I don't hand you a deck and leave. I build the thing, in the open, and you watch it ship.
One operator, accountable end to end. The work is live, not promised. (receipts: prl.arcs.care, build.arcs.care)"
> ACTION: confirm the exact line with Zach first — it's the SSOT every surface inherits.

## STATUS 2026-09-11: flag BLESSED, 4 of 6 faces WIRED
Blessed green-go flag (SSOT): **"Proof over promises, one operator accountable end to end."**
- [x] **resume.arcs.care + status.arcs.care metas filled** (PR #404, merged, live). resume h1/lede
      already render client-side, so only the machine-read meta was the gap.
- [x] **build.arcs.care + good.arcs.care footers** carry the operator line + backlink to zachharris.xyz
      (PR #405, merged). Cleared one prose em-dash in build.html; data-placeholder glyphs left as idiom.
- [ ] **prl provenance footer — DROPPED ON PURPOSE.** prl.arcs.care is client-confidential (Todd/PRL),
      not a billboard for Zach's consulting. Do NOT add a hire-me backlink there.
- [ ] **zachharris.xyz (separate static repo, NOT this worktree)** — still open, HAND-OFF:
      (a) fill empty `<meta name="description">` with: "Zach Harris, one operator accountable end to end.
      Wall Street quality, Main Street prices. Proof over promises: the work ships in the open."
      (b) Case-Studies link → point at build.arcs.care (public proof), NOT prl. Run its `npm test` gate.
- [ ] **LinkedIn** — the 6th face, unreachable by tools. Headline still says "Product". Get Zach's
      current headline + About, fold into the flag grammar (anti-consultant-who-ships, no FDE/"engineer").

## Gates (all blocking)
`npm run build` · `./scripts/artifact_wrap_lint.py <files>` (from THIS worktree, not main-checkout path) ·
em-dash grep = 0 · verify live per surface after merge · watch for proxy.ts merge-race (other sessions active).

## Cost note
Parked because at 98% weekly budget the read+build+PR+merge+verify-live loop across 4 surfaces is NOT
low-touch, and the flag wording was unlocked. Banking > half-wiring an unblessed verdict.
