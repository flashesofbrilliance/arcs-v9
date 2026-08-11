# Week in Receipts — Pre-mortem / Post-mortem Learnings (2026-08-05 → 2026-08-11)

> Coverage note: the ex-ante/outcome corpus is concentrated on **Aug 9–11**. `_STATE/night-moves/`
> holds one digest (`2026-08-10.md`), `_STATE/witness/` one entry (`2026-08-11.jsonl`), and the DEWY
> receipt files cover the 08-10 and 08-11 sessions only. No receipts exist for 08-05→08-08; git
> activity in that span is not represented in the dated-receipt sources. Everything below is drawn
> from files that actually exist.

## Timeline

- **2026-08-09** — Diamond-cut recoil for Yuri scoped as *earned* fidelity (2 dimensions, not a 12D flex); 6-facet persona-gauntlet method run pre-send. (`_STATE/2026-08-10-session-decisions.dewy.json`)
- **2026-08-10** — Temporal-provenance gate built and shipped (ADR-044); caught a *second* live false claim (Robin) on first corpus sweep. (`_DECISIONS/ADR-044-temporal-provenance-gate.md`)
- **2026-08-10** — Yuri artifact family SENT via Gmail after 4 gauntlets + replacing the stale draft carrying the false "model-agnostic/Gemini" claim. (`_STATE/2026-08-10-session-decisions.dewy.json`)
- **2026-08-10** — ADR-043 (adaptive rhetorical resonance) minted; ADR/DEWY + surface watchers built and wired into hooks; Todd/PRL anti-ICP/spam engine shipped to staging. 53 commits across 6 worktrees. (`_STATE/night-moves/2026-08-10.md`)
- **2026-08-10** — `/night-moves` digest routine built (ADR-045); first run had to be pointed at 08-10 because the session crossed midnight.
- **2026-08-11 06:00** — Witness trigger conceived mid-session ("can I get a witness…"), captured live as the founding witness entry, GREEN. (`_STATE/witness/2026-08-11.jsonl`)
- **2026-08-11** — `/witness` command + WORLD.md THE WITNESS trigger built (ADR-046).
- **2026-08-11** — Model-tier router built (ADR-047): recommends Haiku/Sonnet/Opus by reversibility × value, never auto-switches. Numbering collision noted (seeding task called it "045"; filed as 047).
- **2026-08-11** — Lab-factory governed: surfaces moved out of `/tmp` scratchpad into git-tracked `_ARTIFACTS/lab/`, lab-mint skill added, `receipt_outcome_matched` emitted on loop-close; Rayan/Ahmed forge seeds + `forge.arcs.care` pattern published; handoff v3.32.0.

## Pre-mortems (what we predicted could go wrong)

| Decision / receipt | Pre-mortem (risk flagged ex-ante) | Source |
|---|---|---|
| Temporal-provenance gate (ADR-044) | A heuristic phrase-gate could **false-positive a legitimately hedged claim** and block a good write. Mitigated by Agentum-exception + generous hedge window + tuneable lists. | ADR-044; DEWY `2026-08-10-temporal-provenance-gate` |
| Diamond-cut recoil (08-09) | A pixel-precise 12D chart off one 30-min call **implies measurement it doesn't have** and self-refutes against refusal-to-overclaim. Mitigated by 2 dimensions only, 5-pt rounding, loud fidelity fence. | DEWY `2026-08-09-diamond-earned-fidelity` |
| Redact dossier / two-link warm (08-10) | **Over-building for a busy bite-size reader** → he bounces and never reaches the good part. | DEWY `2026-08-10-redact-dossier-two-link-warm` |
| Persona-facet gauntlet | **Over-flagging** — the verifier could reject real content; self-review is the weakest check. Mitigated by adversarial verifier + re-verify each flag vs source. | DEWY `2026-08-09-persona-facet-gauntlet` |
| `/night-moves` (ADR-045) | A **manually-invoked** routine gets skipped on exactly the busy nights it's most valuable; and past-midnight sessions mis-date the digest. Mitigated by optional date arg (back-fillable). | ADR-045 Loki test |
| `/witness` (ADR-046) | A **third parallel logging surface** fragments "where do I look"; and the trigger **over-fires** → ceremony fatigue. Mitigated by non-overlapping timescales + "deliberately rare" + not wiring into night-moves yet. | ADR-046 Loki; DEWY `2026-08-11-witness-trigger-built` |
| Model-tier router (ADR-047) | A **hand-tuned lexicon is brittle**, will misroute novel phrasing, giving false confidence; and cost-descent could downgrade a ruin-exposed task. Mitigated by recommend-only, ruin-floor at OPUS, ambiguity rounds up, `--self-test` pins the invariant. | ADR-047 Loki |
| Todd/PRL capture flow | UX pre-mortem run on the lead-capture flow before shipping (state-resolver robustness, capture-reachable-channel-first). | `_STATE/night-moves/2026-08-10.md` |

## Post-mortems (what actually happened + the learning)

- **Temporal-provenance gate — the pre-mortem was already reality.** The failure it guards against had *already happened once* (the Yuri "model-agnostic, runs on Gemini" claim). On its **first corpus sweep the gate caught a second, still-live instance** the hand-fix had missed (Robin's "air-gapped… nothing leaves Zensai"). Learning: **fact-vs-fiction needs a chain of custody, not a claim** — vigilance had already proven insufficient, so the honesty hole had to be closed by machine, not attention. ARCS already had this primitive (the ex-ante receipt) but had never turned it on claims about *itself*. Source: ADR-044; `_STATE/night-moves/2026-08-10.md`.
- **Yuri family — the fix was subtraction, not addition.** After 4 gauntlets the diamond surface's cure "wasn't more content, it was removing a self-contradiction and an over-anchor to internal-Google framing." Family SENT 08-10 after replacing the stale draft. Outcome still open ("ball in Yuri's court"). Source: `_STATE/night-moves/2026-08-10.md`.
- **Persona-gauntlet — over-flag risk materialized and was caught by design.** The adversarial verifier **rejected 4 over-flags** while the persona pass caught framing/mechanism cracks the register + lens gauntlets had passed clean. Neither detector nor register-lens gauntlet is enough alone; *being* the counterpart across facets at high burden of proof is the deepest check. Source: DEWY `2026-08-09-persona-facet-gauntlet`.
- **`/night-moves` — its own pre-mortem fired on run #1.** The past-midnight edge case wasn't hypothetical: the first digest had to be **explicitly pointed at 2026-08-10**. The mitigation (optional date arg) was validated by being immediately needed. Source: ADR-045 Consequences.
- **`/witness` — the trigger proved itself at birth.** The founding witness entry *is* the moment the feature was conceived, captured live rather than reconstructed. Conviction filed honestly as **MEDIUM / SHIFTING** ("not yet used in anger"). Source: `_STATE/witness/2026-08-11.jsonl`.
- **Model-tier router — the ADR itself records a process miss.** The seeding task mislabeled it "ADR-045" (already taken); caught and filed as 047. Parallel-worktree ADR numbering can collide. Source: ADR-047 numbering note.
- **Lab-factory — a latent ruin vector was found and closed.** Lab surfaces had been deploying **from the `/tmp` scratchpad**, a data-loss risk; moved into git-tracked `_ARTIFACTS/lab/` with serializable `STATE.json`. The loop was also closed: Briefing Record → Conviction Ledger via a `#bet=` seed. Source: commits `063588a`, `6dab72a`.

## Cross-pattern relevancy (recurring themes)

**1. Honesty is enforced by machine at the moment of creation, not by later vigilance.**
Recurs in: ADR-044 (refuse to *write* unhedged aspiration), ADR-046 (`/witness` attests *at the moment* — a reconstructed witness is the same dishonesty as aspiration-as-fact), earned-fidelity receipts (render only what the data supports). ADR-046 explicitly names ADR-044 as the same principle on the attestation side.
**Transferable principle:** *A claim (about capability, a decision, a moment) must carry its temporal chain of custody, and the honest place to enforce that is at write-time — vigilance is the control that already failed once.*

**2. Recommend, never act — keep the human in the loop on any ruin edge.**
Recurs in: ADR-047 (router *recommends*, never auto-switches; ruin cues floor at OPUS + require confirm), the watcher family (surface candidates, never promote), ADR-034 enforcement-parity lineage.
**Transferable principle:** *Scaffold cognition (NOTOMATION); when cost-optimization meets an irreversible/ruin-exposed task, fail toward the safer option and hand the decision to the human.*

**3. Mechanize only after N≥2 hand-runs — never off a single instance.**
Recurs in: counterpart-gauntlet ("mechanize once you've run it by hand twice"), ATG mechanization *deliberately held* for a second clean instance (ADR-039), `/witness` **not** wired into `/night-moves` until real firings prove the pattern.
**Transferable principle:** *Build the reusable machine on instance #2, not #1; premature coupling is a cost you unwind if the pattern doesn't hold.*

**4. Match the artifact's weight to the thing it captures; the fix is usually subtraction.**
Recurs in: ADR-046 (one-line witness stub, not heavy `/dewy-stub`), diamond-cut earned-fidelity (2 dimensions, not 12D), Yuri redact-to-two-links, the diamond fix (removed a contradiction, added nothing).
**Transferable principle:** *Earned fidelity, not maximal — over-building for a bite-size reader (or over-ceremony-ing a fleeting insight) is the failure mode; cut to fit.*

**5. Capture/tooling follows the proven house shape: deterministic gather + narrative synthesis, cheap and stdlib.**
Recurs in: ADR-045 (`/night-moves` = git gather script + skill synthesis, mirroring `/handoff`), ADR-047 (router reuses the watcher's stdlib cue-lexicon shape), the watcher family.
**Transferable principle:** *When adding a routine, reuse the shape the repo already trusts — split the expensive (LLM) part from a deterministic, auditable, zero-network gather.*

**6. Durability = relocate out of the ephemeral, into git-tracked state.**
Recurs in: lab-factory move `/tmp` → `_ARTIFACTS/lab/` + `STATE.json` (ADR-041 lineage), witness/DEWY/night-moves logs as git-tracked `_STATE/` surfaces, `receipt_outcome_matched` closing the record→receipt→outcome loop.
**Transferable principle:** *A deliverable or record living in scratchpad is a data-loss (ruin) vector; make it durable, serializable, and build-excluded.*

## Highest-conviction transferable lessons (top 5, ranked)

1. **Turn your own decision primitive on yourself.** ARCS had the ex-ante-receipt chain of custody for object-level decisions but never applied it to claims about ARCS itself — that gap produced the false "model-agnostic" claim. Enforce fact-vs-fiction (temporal provenance) at write-time. *(ADR-044 — caught a 2nd live instance on first run.)*
2. **On any ruin edge, recommend-don't-act and fail toward safety.** Cheapness must never beat survivability; ruin cues floor the recommendation at the most capable tier and demand human confirm. *(ADR-047.)*
3. **Being the counterpart across facets beats any detector.** The persona-gauntlet caught mechanism cracks the register/lens gauntlets passed clean; pair every pass with an adversarial verifier that re-checks each flag against source. *(DEWY `2026-08-09-persona-facet-gauntlet`.)*
4. **Mechanize on the second hand-run, not the first.** Counterpart-gauntlet mechanized at N=2; ATG and witness-ingestion deliberately held at N=1. *(night-moves 08-10; ADR-046.)*
5. **Match weight to substance and prefer subtraction.** The best fixes this week removed contradictions and collapsed menus rather than adding content. *(ADR-046; diamond + Yuri redact receipts.)*

---

### This branch's contribution to the pattern
The lab-factory work on `claude/awesome-chebyshev-41e7ef` is a live instance of themes **4 and 6**: the design lesson [[design-for-arriving-cognitive-state]] (match the surface to the arriving System-1 reader — subtraction over front-loaded explanation) and the durability move (scratchpad → `_ARTIFACTS/lab/` + serializable `STATE.json`). The `lab-mint` skill is theme **3** (mechanize the mini-app pattern only after it was hand-built ≥2×).

**Source files:** `_STATE/2026-08-10-session-decisions.dewy.json`, `_STATE/2026-08-11-session-decisions.dewy.json`, `_STATE/witness/2026-08-11.jsonl`, `_STATE/night-moves/2026-08-10.md`, `_DECISIONS/ADR-044…047`, lab commits `063588a` / `6dab72a`.
