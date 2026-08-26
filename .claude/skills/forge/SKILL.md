---
name: forge
description: Forge a counterpart's clean surface family (recoil / codex / receipt-close / diamond) from their SSOTs to Robin's crispness bar, then take it all the way to a send-worthy, register-fit, honesty-gated artifact. Full sequence — gather (incl. the full comms thread) → synth → generate → verify (gates incl. temporal-provenance ADR-044) → deploy → GAUNTLET LADDER (lens/transcript/persona via the counterpart-gauntlet workflow) → VIBE REFIT → SEND PREP → CAPTURE. Use to stand up, level, gauntlet, or ship a counterpart artifact universe end to end. Robin is the platinum master; Yuri (2026-08) is the acceptance test + the reference run.
---

# /forge <name> — the parameterized counterpart forge

This pipeline runs the ADR-068 verb arc: gather=analyze (source-traceability), synth=assess
(claim-vs-record), gauntlet ladder=evaluate (pass/conditional/fail), generate+deploy=synthesize
(ship/hold), send prep=recapitulate (sent/parked). Every stage prints through a gate to a fate.

Deterministic SSOT -> template -> page. One token source (canonical ARCS
dark-cockpit, `src/ui-kit/recoil-report/_tokens.css`, ADR-009/031). Crispness
rules are generation constraints, not hand-discipline. Run model-efficiently:
cheap tier for the mechanical stages, higher tier only for synthesis + verify.
Overengineering is the anti-goal; the quality floor is non-negotiable.

**Read before deriving anything:** `_PATTERNS/counterpart-artifact-family-blueprint.md`
(sec 1-11) is the SSOT floor plan. This skill executes it; it does not re-derive it.

## The surfaces (blueprint sec 1, sec 9) — the 3-read triad
| Surface | Job | Generator | Lives at |
|---|---|---|---|
| **recoil** | show the loop on THEIR own call (before/after) | `recoil_brief.py --format html` | `<name>-recoil.arcs.care` |
| **codex** | how the read is made (dual: Read + Instrument) | (hand template until extracted) | `<name>-codex.arcs.care` |
| **receipt** | the crispest proof: bet-filed-before -> scored-after | `forge_counterpart.py --surface receipt` | `<name>-receipt.arcs.care` |

Robin's 4 live surfaces are the platinum master. Do NOT hand-fix a counterpart
to the bar — generate to it. The receipt surface is fully mechanized in
`scripts/forge_counterpart.py`; recoil is mechanized in `scripts/recoil_brief.py`.

## Pipeline: gather -> synth -> generate -> verify -> deploy

### 1. gather (cheap tier) — reuse the recoil skills
- New relationship: `/recoil-new` scaffolds `runtime/recoil/generated/<date>-<name>.json`.
- Before a call: `/recoil-prep` fills Pre-Call + Ex-Ante (this is the **bet, filed before**).
- After the call: `/recoil-close` pulls the transcript, scores ex-ante vs reality, fills the recoil.
- Two seed inputs always (blueprint sec 0): enriched-profile SSOT (public scan + `resolution` caveat)
  and the **call transcript** (ground truth). Attribution: `Me`=Zach, `Them`=counterpart.
- **Third input, for the vibe refit (learned Yuri 2026-08): pull the FULL comms thread** (LinkedIn DMs +
  email) via the Gmail/LinkedIn MCP, not just the call. The call gives the register; the thread gives the
  vibe, the busy/bite-size cadence, and the decisive notes ("too abstract, how do I read this"). The thread
  is what the artifact must actually fit — ground the vibe refit (phase 7) in it, not in memory of it.

### 2. synth (higher tier) — assemble the receipt SSOT
- Scaffold: `python3 scripts/gen_receipt_close.py --recoil <recoil.json> --ex-ante <warroom.json> --out <name>-receipt.json`.
  It seeds `close.scorecard` from the recoil belief-update table (every row grounded in a verbatim
  line the counterpart said) and stubs the narrative fields as TODO.
- Enrich the TODO fields (waveform points, reverse-listening beats, kairos-lock, posterior, confidences).
  **Crispness constraints (blueprint sec 9, encode as you write):**
  - Lead with the real-call STORY and verbatim quotes, not an abstract diagram.
  - The receipt-close is first-class: predicted-before vs actual-after, honestly scored (HIT/MISS/PARTIAL).
  - Single-call counterparts render single-call — no multi-call arc (that is Robin-only).
  - **Honesty gate (sec 11):** if public signal is insufficient, add a `resolution_gaps` entry
    (`{what, inputs}`) rendered as a visible `additional enrichment source inputs required` flag.
    Never fabricate and never import a claim from the master to fill a gap.

### 3. generate (mechanical)
```bash
python3 scripts/forge_counterpart.py --surface receipt --data runtime/recoil/generated/<name>-receipt.json --out public/<name>-receipt.html
python3 scripts/recoil_brief.py --data runtime/recoil/generated/<name>-recoil.json --audience external --format html > public/<name>-recoil.html
```

### 4. verify (the automated quality floor — blueprint sec 4 + sec 10)
The generator runs the gates inline and **refuses to write on any FAIL**. It enforces:
- impeccable voice (0 em-dashes, no buzzword tells),
- **no side-tab** (colored `border-left/right` >1px on a callout — the top AI tell; craft-floor rule),
- canonical tokens only (fails on any omakase `#0B0B0C`/`#C9A227`/`#5C8A4E`/`#E34F1C`/Helvetica),
- honesty + attribution (every scorecard row has an observed outcome; every net-new signal a verbatim quote),
- **temporal-provenance (ADR-044):** refuses unhedged aspirational capability claims (`model-agnostic` /
  `runs on Gemini` / `nothing leaves Google/the building/your side` / `air-gapped`). ARCS runs on **Claude
  today**; a claim about a future/internal deployment must be hedged (`could` / `would` / `an internal
  version` / `Claude today`) or attributed to a product that genuinely is it (Agentum). See
  [[temporal-chain-of-custody-fact-vs-fiction]].

Then run the real detector + a browser look (screenshots are not enough — verify the render):
```bash
node ~/.claude/skills/impeccable/scripts/detect.mjs public/<name>-receipt.html   # want: 0 anti-patterns
python3 scripts/forge_counterpart.py --verify-only --file public/<name>-receipt.html
```
The automated gates are the **FLOOR, not the ceiling.** They pass artifacts that still carry
trust-breakers and register misfits. Before ship, run the **pre-send ladder** (below).

### 5. deploy (main worktree ONLY)
- `git worktree list` first; edit `public/` here, but the live subdomains serve from **main**.
- Add the rewrite to `next.config.ts` `beforeFiles`, mirroring the existing `robin-receipt` entry:
  `{ source: "/:path*", destination: "/<name>-receipt.html", has: [{ type: "host", value: "<name>-receipt.arcs.care" }] }`.
- Add the subdomain: `vercel domains add <name>-receipt.arcs.care` (project `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`;
  the Vercel CLI auto-refreshes its token). Deploy is a docs/public change on main -> one build.

## Acceptance test (proves the pipeline)
Regenerate Yuri to Robin's bar: `public/yuri-receipt.html` from
`runtime/recoil/generated/2026-07-23-kleban-receipt.json` (ex-ante `kleban.json` scored against
`kleban-recoil.json`), single-call, leading with the belief-flip story. If it matches Robin's
crispness and passes every gate + the detector, the forge is sound.

---

# The pre-send ladder (phases 6-9) — what actually makes it land

Back-propagated from the Yuri send (2026-08-10). The build (1-5) produces a *gate-clean* family; it does
NOT produce a *send-worthy* one. Passing the automated gates is necessary and not sufficient — a family
can be fabrication-free and still be over-built, mis-vibed, or carry a plausible-but-false claim. These
four phases are the difference between "renders" and "lands." Run them in order; loop 6 until clean.

## 6. Gauntlet ladder (parameterized) — verify by adversary, not by attention

**The progression (each catches what the prior passes):**
`mechanical detector  <  register-lens gauntlet  <  PRIMARY TRANSCRIPT grounding  <  counterpart-persona-facet gauntlet`

- **Lens gauntlet** — three lenses (COURT+LAB claims-skeptic / BAR ruin+register-fit / dual-bar-raiser
  guest-test) as adversarial subagents. Catches cross-counterpart contamination, false data-claims,
  handling-instructions, engine-poetry.
- **Primary-transcript grounding** — re-read the ACTUAL transcript (Granola MCP `get_meeting_transcript`),
  not memory of it, and final-pass every attributed belief/value/quote against it. The register gauntlet
  AND the detector both passed a *value fabricated onto Yuri* (a consent stance he disowned on tape); only
  the transcript caught it. Treat "this is who you are" claims as the highest-risk class.
- **Persona-facet gauntlet (deepest)** — run the reusable Workflow:
  `Workflow({ name: 'counterpart-gauntlet', args: { counterpart, repo, transcript, comms_thread, surfaces:[{label,html,ssot}], memory:[...], register, already_healed } })`.
  Six facets BE the counterpart (most-technical / practitioner / hype-allergic-skeptic / no-ask-connector /
  situational-strategic / bite-size) at high burden of proof; an adversarial verifier rejects over-flags,
  dedups, ranks, and prescribes register-tuned fixes. It catches framing/mechanism cracks the lens gauntlet
  passes (buyer-relabeling, a self-flattering "ratchet," a chart whose copy contradicts its own data, the
  "machine" label pointing at the shallowest surface).

**Discipline (non-negotiable, every pass):**
1. **VERIFY each surviving flag against source yourself** — the gauntlet over-flags grounded things
   (it called "across Alphabet" unsourced when his LinkedIn had it). Reject over-flags with a reason.
2. **Heal in THEIR register** (kintsugi), keep what's grounded, do NOT touch the protected spine
   (self-scoring inversion, the earned-fidelity fence, the one honest self-falsifying bet, the hero line).
3. **Sweep EVERY surface + domain, not just the ones in the send** — grep `next.config.ts` for every
   `<name>-*.arcs.care` rewrite; healing the frame you're looking at leaves stale siblings live (a false
   claim survived on an orphaned `yuri-demo` and on Robin's one-door until the temporal gate swept them).
4. **One deploy per pass**, then re-run. Loop until the verifier says *send-worthy, no surviving pathogen*.

## 7. Vibe refit — fit their ACTUAL register (the counterpart-vantage pre-mortem)

Grounded in the FULL comms thread (phase 1's third input), not the call alone. Role-play AS them reading
the family; find where it loses them and why. The recurring fixes (Yuri): **redact the dossier** (the
"read of you" profile is the most abstract/least-asked-for surface — cut it from the send, keep the page
live but unlinked); **collapse the menu** (a busy bite-size reader wants "one clear thing," not a universe —
2 links, not 4); **open by answering their stated question** (hero says what it is in THEIR vocabulary —
"the pre-meeting brief your team builds, closed and scored"); **warm the register a notch** (match how they
actually talk, less cockpit-gravity); **name the machine honestly** (point "the machine / for builders" at
the surface that IS the mechanism, not the prettiest one). See [[counterpart-vantage-premortem]],
[[met-at-your-level-onramp-design-principle]], [[gauntlet-tuned-to-register-catches-what-detector-cannot]].

## 8. Send prep — draft in their register, replace stale drafts, never send

- **BLOCKING (ADR-068): verify the Ex-Ante tab is filed and CURRENT before drafting.** The
  bet-filed-before from phase 1 can be stale by send time — if the send is a new move (new
  artifact, new ask), file a fresh ex-ante entry (expected response, falsifier) in the SSOT
  first. No current ex-ante receipt, no send. Log the close-loop obligation (`/recoil-close`
  owed on their reply).
- Draft the channel messages (short in-thread reply + fuller email) in their register, fulfilling any
  promise already made in-thread ("something deeper and more self-explanatory"), answering their stated
  questions (how-to-read / who-for / how-to-use). Lead with the channel where they are **live and waiting**.
- **CHECK FOR AND REPLACE STALE DRAFTS.** A pre-existing Gmail draft can carry a now-false claim (Yuri's
  Aug-6 draft still asserted "model-agnostic, runs on Gemini"). List drafts (Gmail MCP), replace the body
  with the current honest version, keep the recipient + signature. Editing a **draft** is not sending.
- **NEVER send.** The human reviews and sends. Point them to the primary URL.

## 9. Capture — ADR + DEWY receipts + handoff (dogfood the loop)

- **ADR** for any durable/architectural decision (`_DECISIONS/ADR-0NN-*.md`, DEWY-structured: D/E/W/Y +
  Context/Options/Decision/Consequences). This session: ADR-044 (temporal-provenance gate).
- **DEWY receipts** for the session's decisions (`_STATE/<date>-session-decisions.dewy.json`, per
  `runtime/specs/dewy-receipt-schema-v1.json`) — dogfood the product on its own build.
- **Witness stubs** (advisory, NOTOMATION): if a naming moment fired live during the run,
  `/witness` it in the moment — never reconstruct it here (ADR-044 timing).
- **Handoff + memory** (`/handoff`): update snapshot + the single live CLAUDE.md handoff block, relocate
  the prior to `_ARCHIVE/handoffs.md`, mark the project memory SENT with the live reply-threads.
