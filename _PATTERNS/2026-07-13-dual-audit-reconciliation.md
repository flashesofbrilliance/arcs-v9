# Dual-Audit Reconciliation — Architect × Implementer — 2026-07-13

> **What this is:** The same Operator 20 excavation prompt was run twice, independently,
> on two different corpora:
> - **Architect audit** (Perplexity Space, ~50-file corpus: arcs-rom-manifest, field-os-init,
>   session transcripts, canon docs) — delivered 2026-07-13 as
>   `~/Downloads/# INIT ARCS — OPERATOR 20 GOD MODE_## Mode_ Relic.md`
> - **Implementer audit** (this repo, arcs-v9) — 2026-07-11,
>   `_PATTERNS/2026-07-11-operator20-archaeology.md`
>
> Neither audit could see the other's corpus. This document cross-examines them.
> Convergent findings from two blind methods are genuine Orthogonal Echoes (the
> RECOIL-PROTOCOL precedent). Divergences are routed to the write-lock sheet, not
> resolved unilaterally, per the canon-collision discipline.

---

## §1 Headline: bidirectional blindness

Each audit flagged as "missing" what the other side already has.

**The Architect's "missing dependencies" that arcs-v9 already built:**

| Architect claim | Repo reality (verified 2026-07-13) |
|---|---|
| "Decision Receipt: no standardized schema exists; every session produces a different format — cannot be a ROM atom without a fixed schema" | `runtime/specs/dewy-receipt-schema-v1.json` (JSON Schema Draft 07), Prisma-wired, ~184 production receipts through it |
| "One-Way/Two-Way gate: add as mandatory field" (ROM candidate #3) | Already live: `doorClass ONE_WAY\|TWO_WAY` computed in `src/app/api/compass/route.ts:31`, persisted on every Receipt (`prisma/schema.prisma:119`) |
| "Question Compass — run 3 cold users through it" | Live at app.arcs.care/dashboard with real receipt volume |
| Architect's #1 next action: "Fix the Decision Receipt schema to exactly 9 fields" | The schema exists; the correct action is *reconciling* their 9 fields against DEWY v1 (§4), not writing a new one |

**The Architect's findings that hold against the repo too (gaps on BOTH sides):**

| Finding | Repo check |
|---|---|
| No stop-loss field/template anywhere, despite Time-QA governance requiring stop-loss declaration | Confirmed: zero matches for stop_loss in `prisma/schema.prisma`, `dewy-receipt-schema-v1.json`, compass route |
| No human write-lock field on the receipt | Confirmed: zero matches |
| NCI scale inconsistency | Worse than either audit saw alone — see Collision C1 |

The standing memory says "the port lags the corpus" (arcs-v9 ≈ 20% of canon). This
reconciliation shows the inverse is also true: **the corpus lags the port on runtime
primitives.** Both audits were right about their own blind spots.

---

## §2 Echo-confirmed convergences (two blind methods, same finding)

| Finding | Architect | Implementer | Combined status |
|---|---|---|---|
| Decision Receipt = #1 load-bearing atom | R01, ROM | R03 (DEWY schema), ROM promotion | **Strongest joint candidate** — see §4 mapping |
| Vector Collision Engine = metaphor posing as tech | R22, COMPOST ("Contradiction Scan") | R24, COMPOST (paths-over-probabilities lesson already live as `paths[]`) | Compost confirmed twice; both extracted lessons kept |
| Mythic language costs paying clients ~1 onboarding session | Collision section | Collision #13 | Confirmed; annotation work queued |
| Loki pre-mortem needs a standardized 5-question card | R13, RAM | Kit A/C molecule | Write the card once, share across kits |
| Pre-call/preflight scan is THE revenue pattern | R21 (Millionways/Northly evidence) | R01 call-brief + R07 `receipt_lookup.py` (Todd/Kelly/LaBella/Fanatics evidence) | Same pattern found via different clients — highest-confidence product primitive in the whole corpus |
| Outcome loop is open (post-decision learning never closes) | R23 Outcome Recoil, RAM | Collision #11 (Outcome table: 3 index scans) | Their 48h-recoil scheduling + repo ADR-026 step 3 are the same fix |
| The three MVA kits | Founder Pilot Selection / Client Decision Room / Canon Court | Pilot Court / Shared Terrain Session / Relic Court | **Near-identical architectures from blind runs** — the kit shape is validated; merge the best of each (their stop-loss declarations + single yes/no write-lock question; my two-tier ledger gates + measured promotion gates) |
| Ghost/gapped numbering systems create false completeness | Operators 1–16, 18 undefined | Two ADR-025s, no ADR-021; four "atomic design" taxonomies | Same pathogen, different instances |

---

## §3 Inter-audit collisions (new — created BETWEEN the two audits)

**C1 — NCI is now a four-way name collision.** Architect: A/B/C vs 1–5 vs "speculative"
used interchangeably in the corpus. Implementer: `nci_score` 0–100 in the live schema/UI
vs the `[NCI:XX]` commit counter. Four scales share one name. The Architect's proposed fix
("standardize to A/B/C only; retire all numeric scales") **would break the live product**
(0–100 renders on the homepage today). Needs a naming ruling, not adoption as-is.

**C2 — "Hyperstition" compost vs. constitutional text.** Architect: COMPOST the name,
keep the process as Canon Promotion Court ("a literary term that confuses paying
clients"). Repo: HYPERSTITION PIPELINE is **ROM primitive #3** in `SKILL.md:151` and
`CLAUDE.md:49`. Renaming a ROM primitive is exactly the class of change that requires
explicit human write-lock. Routed, not resolved.

**C3 — Drift Sentinel evidence-standard mismatch.** Architect grades it ROM, evidence B,
"deployed in field-os-init." But that deployment is *prompt text*, not enforcement — the
repo's own audit discipline (2026-06-23) classifies prompt-only rules as
`UNENFORCED_CONVENTION`, and the repo's drift-sensor is unbuilt backlog #4. The deeper
question routed to court: **which evidence standard governs ROM promotion — the corpus's
("stated in an active prompt") or the repo's ("mechanically enforced or live in prod")?**
This single ruling re-grades several rows in both registries.

**C4 — Clarity Modes (SIMPLE/RICH/DEEP).** Architect: ROM, "deployed and confirmed."
Repo: partial analogs only (`decision_mode` QUICKMOVE/PLAN/COURT, render fidelity) — no
SIMPLE/RICH/DEEP surface exists in the product. Same shape as C3: prompt-level vs
product-level deployment.

**C5 — NOTOMATION violations in corpus session artifacts** (ARCS "drafting" outreach,
decks, search strings). The repo already encodes the fix — `call-brief-hooks-v1.md`'s
rule that hooks never auto-create external pages, notify-only. The violating artifacts
predate the rule. Disposition: annotate the corpus sessions as pre-rule LEGACY, don't
retrofit them.

---

## §4 Receipt schema mapping — Architect's 9 fields ↔ DEWY v1

| Architect field | DEWY v1 / live pipeline | Status |
|---|---|---|
| Question | `D` (sharpened question) | ✅ exists |
| Horizon | `W` / prep horizon | ✅ exists |
| Stakes | prep `stakes` | ✅ exists |
| Options | `reasoning.paths[]` | ✅ exists |
| NCI per option | `nci_score` (whole-receipt, 0–100) | ⚠️ exists at receipt level, not per-option; scale collision C1 |
| Gate | `doorClass ONE_WAY\|TWO_WAY` | ✅ exists, persisted |
| Recommended move / why | `true_north`, `why[]` | ✅ exists |
| **Stop-loss** | — | ❌ **genuine gap, both corpora** (3 independent signals now: their Kits A/B, my Kit A, Time-QA governance) |
| **Human write-lock** | — | ❌ **genuine gap** (no field records that a human signed before an irreversible move) |

Proposed (subject to write-lock Q2 below): additive v1.1 amendment adding `stop_loss`
and `write_lock` — no renames, no removals, consistent with "freeze v1 additive-only."

---

## §5 Unified write-lock sheet (one court session, both dockets merged)

Grouped; ★ = convergent (both audits independently arrived here).

**Schema court**
1. ★ Freeze DEWY receipt schema v1 as canonical, additive-only from here?
2. ★ Add `stop_loss` + `write_lock` fields as a v1.1 additive amendment?
3. ★ NCI ruling: `nci_score` 0–100 stays the product coherence score; A/B/C becomes a
   *separately named* evidence-grade atom; 1–5 retired; commit-tag counter renamed?

**Naming court**
4. Hyperstition Pipeline: keep the constitutional name, or rename to Canon Promotion
   Court (Architect's compost) — a ROM-primitive rename?
5. L0–L5 triple-meaning ruling (pipeline stages vs abstraction layers vs design levels).
6. Operator numbering: retire numbers for function names (Adversarial, Accountant,
   Folksonomy…)? Architect's recommendation; repo's 34-file library makes it actionable.

**Evidence-standards court**
7. **The C3 ruling** — what counts as "deployed" for ROM evidence: prompt text, or
   enforcement/production? (Re-grades Drift Sentinel, Clarity Modes, HOLD/REJECT gate.)

**Engagement/protocol court** (carried from the Implementer docket, unchanged)
8. Call-brief hooks DRAFT→ROM; ratify "hooks never auto-create external pages."
9. Pathogen taxonomy: closed-world or open (can sessions add #11 without court)?
10. Y-gate: code enum canonical; RED is a severity, not a polarity?
11. ADR closing ceremony: `Closes: ADR-XXX` trailer required (mechanically checked) or advisory?

**Product court** (from the Architect docket)
12. Adopt SIMPLE-as-default output contract (1 move + ≤3 bullets; RICH/DEEP on explicit
    request) in the arcs-v9 UI?

---

## §6 Composite next action

The two audits' recommended 30-minute experiments are complementary, not competing:

- **Architect's:** run the fixed receipt against the single most likely paid-pilot
  prospect. Repo knowledge makes this concrete: **Todd Hotes / PRL Resins** — a $1,500
  Phase 1 proposal is already live at todd-call.arcs.care awaiting yes/no, and
  **Kelly Mullaney / Juniper Square** is the second live thread. Run Kit A (Pilot Court)
  on the Todd decision itself: stop-loss, review date, falsifiers, receipt.
- **Implementer's:** run the Gini/Zipf corpus baseline over the ~184 live receipts —
  one script run converts three silently-cleared gates (ADR-023, ADR-020, RC-OPS-002)
  into measured numbers.

One advances revenue; one unblocks governance. Both fit in an hour combined.

---

*Reconciliation produced 2026-07-13. Nothing here mutates canon — every disposition
above is a recommendation pending the §5 write-lock sheet. Uncommitted pending review.*
