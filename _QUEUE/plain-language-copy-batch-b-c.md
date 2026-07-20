# Handoff — plain-language copy pass, Batch B + C (pending)

**Status:** open. Batch A (safe mechanical fixes) is DONE and shipped on branch
`claude/arcs-plain-language-voice-000f32` (PR #120), commit
`style(copy): plain-language pass on static UI copy (Batch A, safe fixes)`.

This doc holds the remaining two batches. It is self-contained — you do not need
the originating conversation. Line numbers were captured against the worktree at
handoff time; re-grep before editing (Batch A already shifted some lines).

## Origin

The compass/brief/guide SYSTEM prompts got a VOICE block (PR #120, first commit):
plain language, no em/en-dashes, no semicolon splices, no invented metaphor, no
ARCS terms of art unless the user used them first. That governs MODEL OUTPUT.
This copy pass applies the same register to HAND-WRITTEN static UI copy.

Batch A already removed every em/en-dash and semicolon-splice from the
visitor-facing pages (trust, privacy, terms, compass, onboarding, prep, advisory,
scan, dashboard, receipt, guide, debrief), punctuation-only, no wording/brand/
legal changes.

## TWO RULINGS NEEDED BEFORE BATCH B/C (ask Zach)

**Ruling 1 — brand-metaphor policy.** Proposed split (not yet confirmed):
- KEEP everywhere (core product nouns): `compass`, `True North`, `bearing`,
  `tributaries`, `Recoil`, `Drift Sentinel`, `Y-Gate`, `ARCS FIELD OS`, `kairos`.
- STRIP on plain surfaces only (trust/privacy/terms/onboarding + functional
  forms): `terrain`, `fog`, `navigator/the line`, `at the fork`, `decision arc`,
  `silkscreen`, `substrate/written world`. KEEP them on landing / observatory /
  recoil where the world-metaphor is the intended voice.

**Ruling 2 — Batch C scope.** `recoil/page.tsx` and `observatory/page.tsx` carry
most of their dashes inside HARDCODED demo/sample data (the Figma/Deloitte
example receipt; the 8-week trajectory arrays), not evergreen copy. Confirm
whether to clean the sample data too, or leave it.

---

## BATCH B — elevated phrasing + metaphor strip (needs Ruling 1)

### B1. Elevated / performative phrasing (recommend regardless of Ruling 1)
- `src/app/prep/page.tsx` — `placeholder="One sentence. The Loki vector."`
  -> `"One sentence. The strongest argument you'd least want to be true."`
  (Loki vector is opaque jargon on a first-use form field.)
- `src/app/trust/page.tsx` — `Repair seam (2026-07-13), kept visible on purpose:`
  -> `A fix we're keeping visible on purpose (2026-07-13):`
- `src/app/privacy/page.tsx` — `Scout's honor.` (in the NEVER band) -> drop it;
  keep `Enforced by architecture and covenant, not just policy.`
- `src/app/terms/page.tsx` — `demonstrated reciprocity` (2 spots: the axiom line
  and the arcs-commitment row) -> `reciprocity`, or `by earning your trust`.
- `src/app/guide/[receiptId]/page.tsx` — `CollapsibleBand title="Agenda: In My Head"`
  -> `"Agenda"` (drop "In My Head"; Batch A already fixed its dash to a colon).
- `src/app/guide/[receiptId]/page.tsx` — `"⚠ Midcurve Tripwire"` heading ->
  `"Where this goes sideways"` (Midcurve is undecodable to a reader).
- `src/app/debrief/[receiptId]/page.tsx` — `The shoe has dropped.` opening
  -> `The outcome is in.` (or drop, lead with "A receipt can't close itself.").
- `src/app/receipt/[receiptId]/page.tsx` — ephemeral empty-state headline
  `This bearing didn't travel here` -> `Nothing to show here` (also a brand call).
- `src/app/recoil/page.tsx` — `assessment bandwidth` -> `time`; `does not clear the
  survivability bar at current information state` -> `with what we know now, this
  bet isn't worth it`; `probability tree` -> `odds`. (These live in recoil, so
  fold into Batch C if you do recoil there.)

### B2. Metaphor strip on plain surfaces (ONLY if Ruling 1 = strip)
- `src/app/trust/page.tsx` — L~24 `Contested terrain` / `probe the terrain`;
  L~159-163 `surfaces the terrain`; L~171 `the navigator chooses the line`;
  `catches you at the fork`; `decision arc`. Swap: terrain -> "the situation";
  "the navigator chooses the line" -> "you choose"; "at the fork" -> "at a
  decision point"; "decision arc" -> "your decision".
- `src/app/terms/page.tsx` — L~19 `terrain` -> "the situation". L~157/167
  `decision navigation instrument`, `directional bearing`, `tributaries`,
  `coherence signal` are the heaviest legal-copy jargon cluster — "tributaries:
  adjacent questions worth asking" already self-glosses; decide per Ruling 1.
- `src/app/prep/page.tsx` — L~103 `2 minutes. Sharper terrain.` -> `A clearer
  picture.`; L~106 `who else is in the terrain`; L~139 field label `Who else is
  in this terrain?` -> `Who else is affected by this?`; L~145 button `Enter the
  compass` + `Loading terrain…` -> `Start` / `Loading…` (functional form, not a
  landing page — metaphor on labels/buttons costs first-use clarity).
- `src/app/brief/[receiptId]/page.tsx` — SequenceLoader stage names
  `TERRAIN PATHS`, `SILKSCREEN`, footer `Reading the terrain…` (brief render is
  interior; decide per Ruling 1).
- `src/app/privacy/page.tsx` — `covenant` reads elevated on a policy page (low
  risk; optional).

---

## BATCH C — recoil + observatory (needs Ruling 2; mostly demo data)

### C1. src/app/recoil/page.tsx (~24 dashes, 3 semicolon splices)
Sidebar/heading separators (`X — Label` -> `X: Label`): L~33-35 (D/E/W), L~339
`Signal Delta — Expected vs. Actual`. Entity rows L~47-51 (`Name — detail` ->
`Name, detail`). Signal-delta cells L~55-61 (`Confirmed — ...` -> two sentences or
colon). Semicolons L~59, L~61 (-> comma / colon). Next-steps L~75/77/304/305
(en-dash ranges -> "3 to 7 days" etc.; em-dash -> period). Body prose
L~284/331/371/425/434/437/473 (dashes; L~425 also a semicolon splice "is not
noise; it means" -> "is not noise. It means"). NOTE: most of this is the
hardcoded Figma/Deloitte SAMPLE receipt, not evergreen marketing copy.
Brand terms here (`cartographic`, `survivable`, `Recoil Report`, `Drift
Sentinel`, `Y-Gate`, `Signal Delta`) are established nomenclature — keep.

### C2. src/app/observatory/page.tsx (~14 dashes, 5 semicolon splices)
UI chrome L~302-305 / 796 / 988 / 1128: mostly cosmetic `—` -> `·` in
cockpit-register legend/labels. Editorial data arrays (hardcoded EVENTS/RISKS/
LAYERS): dashes L~52-61 / 65 / 97; semicolon splices L~66, 67, 69, 70, 77 (->
two sentences). House tokens `L0–L5`, `3–5` recur — if applying the en-dash ban
strictly, normalize to `L0-L5` / "3 to 5", but confirm as a consistency call.
`substrate / written world` (L~77) is a brand-voice call (Ruling 1).

---

## Sequencing when rulings land
1. B1 (elevated) — safe, do first, one commit.
2. B2 (metaphor strip) — only if Ruling 1 = strip; one commit.
3. C1 + C2 — only if Ruling 2 = yes; one commit (or skip).

## Verify
`npm run build` (NOT bare `npx next build` — NODE_ENV gotcha, AGENTS.md §4).
After edits: `git diff -U0 | grep '^\+' | grep -E '—|–'` must be empty.
