# Fortnight retrospective — 2026-07-31 → 08-13

**Status:** RECORD · 14 days · ~500 commits (all branches) · 20 ADRs · ~24 net-new tools · ~20 memories
**Shareable artifact:** https://claude.ai/code/artifact/795dbd1e-9bf2-4514-9f5f-9ccb2126d3a4 (ARCS field-log render)
**Method:** token-efficient git sweep (`git log --all --since="14 days ago"`) + ADR/tool/memory inventory — no transcripts.

> Two weeks that moved on three fronts at once — **money-facing** (client surfaces), **trust-facing**
> (governance substrate), **ruin-facing** (security). The structural win underneath: the shift from
> hand-crafted artifacts to **rendered families from a single source of truth**.

## Activity trace (commits/day, all branches)
```
07-31  57   ████████████████████
08-01  42   ███████████████
08-02   6   ██
08-03  30   ███████████
08-04  27   ██████████
08-05  55   ████████████████████
08-06  20   ███████
08-07  87   ███████████████████████████████  ← peak (forge/omakase crest)
08-08   9   ███
08-09  39   ██████████████
08-10  53   ███████████████████
08-11  39   ██████████████
08-12   0        (quiet day)
08-13  32   ████████████
```

## 1. Engagement surfaces — revenue-facing (forge · louisville · omakase · ahmed)
- **[major] Counterpart-forge became a product** — parameterized `forge_counterpart.py` CLI, the 5-surface
  family (onedoor · receipt · codex · diamond · profile), gate-hardened into one canonical pipeline.
  Robin = platinum master, Yuri = acceptance test. Published `forge.arcs.care` + `forge-cut.arcs.care`.
- **[major] Louisville universe end-to-end** — `louisville.arcs.care` pitch suite, The Board cast, tiered
  Offer, present mode, **Phase-2 persistence** (SessionReceipt + receipts/agenda API + Studio wiring),
  least-privilege `louisville_app` DB role.
- **[major] Omakase pipeline generalized (instance→class)** — jeben → omakase → louisville; coursed
  L1/L2/L3, the atom story, the guest's-course live receipt + take-home gift.
- [minor] Ahmed reconnect — omakase 3-surface `ahmed-ext` + the 60-second chronograph onramp (the
  consumability fix), per-section reaction capture. Rayan/Periscope one-door (pw-gated).

## 2. Product & canon — thesis-facing (arcs.care family · Tao · pricing · OSS)
- **[major] Public federated family on arcs.care** — playground + monolith + 4 performers, two-layer
  air-gap (ADR-050).
- **[major] Tao / pricing / OSS-family canon** — dormant-seed doctrine (ADR-053), free-to-hold/metered-to-fire
  (ADR-054), two-tier conformance (ADR-055), connector pattern (ADR-056; forge.arcs.care as reference),
  the `_SEEDS` bank, the germinate open↔private boundary.
- [minor] lab-mint factory + serializable state; Rosetta operational-definitions registry.
- [minor] Positioning sharpened — honest resonance engine (not propaganda); magnetic best-fit / simulated annealing.

## 3. Infrastructure & governance — trust-facing (oracle · gauntlets · gates · inchworms)
- **[major] The sequence oracle** (ADR-057) — a git-serialized ID authority. `oracle next adr` — no session
  hand-guesses a number again.
- **[major] Forensic ADR reconciliation** — 4 auditors traced ~43 refs to ground truth; colliding namespace
  (024/025/031/032) fixed at forensic grade (→ 058/059/048/049).
- [minor] Drift machinery — drift-receipt gate (ADR-051), lattice inchworm (ADR-052), seedbank inchworm,
  `surface_watch`, `adr_dewy_watch`.
- [minor] Quality gates — temporal-provenance (ADR-044), model-tier routing (ADR-047), hypercube gauntlet +
  sampler wired to real models, `serialize_grade.py` two-pass fidelity grader. Deploy cost guardrail
  versioned as `vercel.json ignoreCommand` (ADR-039); night-moves (ADR-045); witness (ADR-046).

## 4. Security — ruin-facing (quietly some of the biggest wins)
- **[major] Closed multiple RUIN-class leaks** — jeben thread book, omakase appendix, recoil canvas/philosophy,
  `canon-manifest.json` were all **world-readable**; pulled off public surfaces.
- **[major] CISO/SRE hardening** — Studio (append-only guard, 405s, logging) + Louisville anon receipt API;
  tenant-wide agenda read gated.
- [minor] Restored a witness receipt clobbered in a merge (lost-update fix); private-repo receipts for chan/status.

## 5. Meta-capability — compounding
- **[major] Instance → class proved repeatable** — forge and omakase each went one-off → parameterized family.
  The template is now the deliverable.
- [minor] ~20 durable memories (fork-when-dense · mechanical-pass-first · git-is-the-write-lock ·
  render-fidelity-is-two-way-imprint), 20 ADRs, ~24 tools — substrate compounding, not just shipping.

## The through-line
Money-facing (forge/louisville/omakase/ahmed) · trust-facing (gauntlets/gates/oracle/inchworms) ·
ruin-facing (leak closures). The single largest **structural** win is the move from hand-crafted artifacts
to **rendered families from SSOT** — the same shift that made the sequence oracle and the OSS-family seed
bank possible in one session at the close of the fortnight.
