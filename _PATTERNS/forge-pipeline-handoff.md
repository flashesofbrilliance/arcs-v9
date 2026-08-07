# Forge pipeline — fresh-session pickup (run the CLI parameterized version)

_2026-08-07. Start here for the fresh session that builds and runs the parameterized/componentized
counterpart forge with args / depts / runtime configs._

## STATUS (updated 2026-08-07, later session) — ALL 4 surfaces shipped + live

`scripts/forge_counterpart.py` is live and gate-hardened. All 4 surfaces shipped + deployed (canonical
tokens, 0 em-dash, 0 side-tab, 0 dark-glow, detector-clean, honesty+attribution gates that refuse to
write on FAIL):
- **receipt** (`--surface receipt`): robin-receipt (trued off omakase; waveform uses the canonical #tip,
  not native <title>) + yuri-receipt (acceptance: ex-ante `kleban.json` scored vs `kleban-recoil.json`,
  single-call, belief-flip). LIVE.
- **profile** (`--surface profile`): robin-profile + yuri-profile (public-only caveat + dial-up honesty
  flag; loop re-tiered to yuri-receipt). LIVE.
- **codex** (`--surface codex`): dual-tab Read+Instrument, extended 5-field #tip, computed spark arcs,
  phase-color-coded beats. robin-codex onto canon. LIVE.
- **onedoor** (`--surface onedoor`): facesnav -> seed -> STORY-led -> how-it-works -> where-it-goes ->
  how-to-start -> for-the-room. **yuri.html LEADS with the belief-flip story** (fan -> he runs the exact
  team), clean 3-read triad, gated "yuri". robin.html master cleaned in place (5 side-tabs + LED glow). LIVE.
- Companion: `scripts/gen_receipt_close.py` + `.claude/skills/forge/SKILL.md` (`/forge`).
- SSOTs: `runtime/recoil/generated/2026-08-05-daniels-{receipt,profile,codex}.json` (Robin) +
  `2026-07-23-kleban-{receipt,profile,onedoor}.json` (Yuri).

**Receipt Studio — SHIPPED + LIVE (2026-08-07).** Interactive file/score/close at
`robin-receipt.arcs.care` -> `/api/receipts/studio/[tenant]` (registry route, robin_app RLS applied to
prod, `ROBIN_DATABASE_URL` set Production). CISO+SRE reviewed, findings fixed, STU-015/016 ledgered,
live round-trip verified. Details + go-live gotchas in [[counterpart-forge-pipeline]] memory.

**REMAINING (optional / lower priority):**
0. **Receipt Studio follow-ups:** set `ROBIN_DATABASE_URL` for Preview too (currently Production-only);
   fold the throttle-sweep (STU-016) into the louisville route when next touched; onboard more tenants by
   adding a registry row + a `<tenant>_app` RLS migration + secret (never generalize the sessionId
   write-bearer to a sensitive tenant, STU-015).
1. **yuri-codex** via the dual-tab renderer (the existing 5-altitude `yuri-codex` + `yuri-demo` are now
   correctly RE-TIERED as the deeper how-it-scales layer, linked from the one-door, not top-level; the
   clean triad profile->recoil->receipt is the entry). A dual-tab yuri-codex on the single Jul-23 call is
   nice-to-have, not blocking.
2. **Receipt Studio integration** — interactive file/close a receipt: see
   `_PATTERNS/receipt-studio-integration-scope.md` (Robin tenant of the Louisville Studio + reuse; D6 defers
   RLS to engagement-live). Touches auth+schema -> ciso/sre review before ship. This is the real next build.
3. Robin's bespoke one-door blocks (belief-ledger, advisory board, volley quadrants, download-receipt card)
   are NOT in `render_onedoor` yet — robin.html keeps them hand-authored. Add as optional typed blocks if a
   counterpart needs them.

Encoders (learned this session): authored prose fields carry HTML entities -> insert RAW; attribute
values -> `A()` (escapes " and < only, preserves entities); only machine/plain values -> `E()`. Running
`E()` on an entity-bearing authored field double-escapes it (visible as literal `&middot;`).

---
### Original spec (below) — still the SSOT for the remaining work

## Read first (the full spec)
`_PATTERNS/counterpart-artifact-family-blueprint.md` — §1-11. It carries the floor plan, component
grammar, decision log, roadmap suite, the Robin platinum-master extraction, the UI-kit truing, and the
generation honesty gate. Do not re-derive; that file is the SSOT.

## Goal
A re-runnable CLI (`/forge <name>`) that generates a counterpart's clean surface family from their SSOTs,
to Robin's crispness bar. Deterministic SSOT -> render, one token source, honest about resolution.

## The order of work
1. **True up the UI kit FIRST (§10).** Canonical tokens = `src/ui-kit/recoil-report/_tokens.css`
   (== `src/document/tokens.ts`), standard ARCS dark-cockpit. Extract the §2 grammar into partials that
   import it; no per-page `:root`. Make the `#tip` data-vis hover/tap tooltip a canonical kit component.
   Regenerate `public/robin-receipt.html` off its omakase drift back onto canon (omakase house style stays
   scoped to the omakase/louisville family only).
2. **Extract Robin's 4 surfaces as parameterized templates (§9):** `robin.html` (one-door, leads with the
   real-call STORY not a diagram), `robin-profile` (the read), `robin-codex` (dual Read + Instrument),
   `robin-receipt` (forensic close: bet-filed-before -> scored-after). Crispness rules = generation constraints.
3. **Build the generator + skill:** `scripts/forge_counterpart.py` (SSOT -> templates -> pages, follow
   `recoil_brief.py` / `gen_recoil_artifact.py` / `receipt_lookup.py` + add `gen_receipt_close.py`), the
   `/forge` skill orchestrating gather->synth->generate->verify->deploy, reusing recoil-new/prep/close/ship.
4. **Verify gate:** impeccable detector, 0 em-dashes, fabrication/air-gap scan (role-archetypes only),
   attribution check (Me=Zach / Them=counterpart), and the **honesty gate (§11):** insufficient signal ->
   flag `additional enrichment source inputs required`, never fabricate or import-to-fill.
5. **Acceptance test = regenerate Yuri to Robin's bar (§9):** profile already regrounded; add a `yuri-receipt`
   (ex-ante `kleban.json` scored against `kleban-recoil.json`); restructure `yuri.html` to lead with the real
   belief-flip story; re-tier codex+demo as the deeper how-it-scales layer. Single-call (no multi-call arc).

## Runtime / deploy notes
- Deploy from the **main worktree only** (`git worktree list` first). Vercel CLI auto-refreshes its token
  (`vercel whoami` works even when the raw auth.json token is expired); add subdomains with
  `vercel domains add <domain>` from the linked project dir (project `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`),
  and mirror the `next.config.ts` `beforeFiles` rewrites off the existing `yuri-*` / `robin-*` entries.
- Model-efficient: cheap tier for mechanical stages, higher only for synthesis/verify. Quality floor
  non-negotiable; overengineering is the anti-goal.
- The earlier forge task (`task_56561b51`) started before blueprint §7-11 existed — restart it or have it
  re-read the blueprint so it runs against the complete spec.
