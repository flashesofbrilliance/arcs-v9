# JTBD Orchestration Map

> One row per recurring job. Each carries a dependency graph, an orchestration
> shape, a per-node **model tier**, and a **token budget** — so every run is
> costed and reproducible instead of improvised. This is the blueprint the
> `Workflow` tool executes against.
>
> Version 0.1.0 · 2026-07-19 · on-demand doc (NOT auto-loaded)

---

## 1. Model-delegation policy — assign by effort × difficulty

The rule: **cheap + parallel at the leaves, expensive + adversarial at the root.**
Spend the strong models only where judgment or refutation actually happens.

| Tier | Model | Use for | Effort |
|------|-------|---------|--------|
| **Grunt** | `claude-haiku-4-5` | mechanical extraction, gathering, formatting, single-fact lookups, fan-out leaves | low |
| **Analyst** | `claude-sonnet-5` | synthesis, drafting, multi-lens analysis, most build/edit work | medium |
| **Judge** | `claude-opus-4-8` | adversarial verification, final synthesis, architecture calls, anything where being wrong is expensive | high / xhigh |
| **Wide/creative** | `claude-fable-5` | divergent generation, many-angle ideation when breadth matters more than rigor | medium |

Delegation heuristics:
- A node that **reads a lot and decides little** → Grunt. (repo scans, log reads, signal gathering)
- A node that **transforms or drafts** → Analyst.
- A node that **must refute, rank, or ratify** → Judge. Never cheap out here — this is the stage that catches the errors the whole workflow exists to prevent.
- **Isolation:** any node doing a messy/large read runs in a subagent so the mess stays out of the main context (proven pattern: the `_ARCHIVE` scan commit).

## 2. Token-budget policy

- Every job has a **target budget**; the `Workflow` tool enforces it as a hard ceiling via `budget.remaining()`.
- Budgets are **per-run**, shared across the whole fan-out (main loop + all subagents).
- Loop-until-dry / loop-until-count jobs guard on `budget.total &&
  budget.remaining() > <reserve>` so they converge instead of running to the
  1000-agent backstop.
- **No silent caps:** if a run bounds coverage (top-N, sampling, no-retry), it
  must `log()` what it dropped.

---

## 3. JTBD registry

| Job | Trigger today | Orchestration | Shape | Budget | Verdict |
|-----|---------------|---------------|-------|--------|---------|
| **recoil-report** | `/recoil-report` skill | **Workflow** | gather→profile→lens→verify→synth | ~350k | convert — highest ROI |
| **review-gate** | `/ultrareview` + `/dual-bar-raiser` | **Workflow** | dims→find→adversarial-verify | ~120k | convert |
| **patent-triage** | ad-hoc (this session) | **Workflow** | per-candidate: prior-art‖§101‖novelty → rank | ~150k | convert |
| **deep-research** | `/deep-research` skill | already agentic | sweep→fetch→verify→synth | ~200k | keep, formalize budget |
| **log-consolidation** | manual | single-agent | linear reconcile | ~40k | keep single-agent |
| **handoff / dewy-stub / init-state-sync** | skills/hooks | single-agent | mechanical | <15k | keep single-agent — do NOT orchestrate |

Orchestration criterion (when to fan out): the job **decomposes into independent
parallel work**, needs **adversarial verification**, or **exceeds one context**.
Mechanical jobs fail all three → single-agent.

---

## 4. recoil-report — detailed dependency map

The most-invoked job over 90 days, and the one whose manual corrections
("stated vs revealed", "scanner vs human", over-flags) are exactly what an
adversarial-verify stage removes automatically.

```
[gather:gmail]  [gather:granola]  [gather:calendar]  [gather:git]  [gather:linkedin]   ← Grunt ×5, parallel roots
        \            \                |                /              /
                       ── profile synthesis ──                                          ← Analyst (barrier: needs all signals)
                                  |
        ┌──────────────┬──────────┴────────┬──────────────┐
   [lens:LAB]     [lens:BAR]          [lens:SAGE]    [lens:CURATOR]                     ← Analyst ×4, parallel
        └──────────────┴──────────┬────────┴──────────────┘
                                  |  (per claim)
                   [verify ×N skeptics, refute-mode]                                    ← Judge, parallel per claim
                                  |
                        synthesize report                                               ← Judge (provenance-graded)
```

| Node | Depends on | Model / effort | ~Budget | Notes |
|------|-----------|----------------|---------|-------|
| gather ×5 | — | Haiku / low | 15k ea (75k) | blind, parallel; MCP sources (Gmail/Granola/Calendar) + git telemetry |
| profile synthesis | all gather | Sonnet / med | 40k | **barrier** — merge before lenses |
| lens ×4 (LAB/BAR/SAGE/CURATOR) | profile | Sonnet / high | 30k ea (120k) | the ARCS operators as independent lenses |
| verify ×N per claim | its lens | Opus / high | 20k ea (~60k) | prompted to **refute**; ≥majority-refute kills the claim |
| synthesize | verified claims | Opus / high | 50k | earned-fidelity, provenance-graded |
| **total** | | | **~350k** | strong models only at verify + synth |

Pipeline note: lenses should `pipeline()` into verify (no global barrier) so a
claim verifies as soon as its lens completes — dimension B's verify runs while
dimension A's lens is still going.

---

## 5. review-gate (ultrareview + dual-bar-raiser) → Workflow

```
[dim:correctness] [dim:security] [dim:simplification] [dim:reuse]   ← Analyst ×4, parallel
        \               |              |               /
              per-dimension findings → adversarial verify           ← Judge, ≥2 skeptics/finding, refute-default
                              |
                    ratified findings (dedup)                       ← Analyst
```
Budget ~120k. Dimensions Analyst; verify Judge. Only findings that survive ≥2
refutation attempts are reported.

## 6. patent-triage → Workflow

```
per candidate (×11):  [prior-art search] ‖ [§101 eligibility] ‖ [novelty vs refs]   ← Sonnet ‖ Opus ‖ Sonnet
                                     |
                              per-candidate verdict
                                     |
                        rank all → disclosure-clock check                            ← Opus (barrier: needs all)
```
Budget ~150k. §101 (the killer axis) gets Opus; prior-art/novelty Sonnet with
real USPTO/Google-Patents fetches. Barrier at the end to rank the full set.

---

## 7. Mapping to the `Workflow` tool

- Dependency edges → `pipeline(items, stage1, stage2, …)` (no barrier) or
  `parallel(thunks)` (barrier when a stage needs all prior results).
- Model per node → `agent(prompt, { model: "haiku"|"sonnet"|"opus", effort })`.
- Budget ceiling → the turn's `+Nk` directive; guard loops on `budget.remaining()`.
- Messy reads → `agent(prompt, { isolation: "worktree" })` only if the node
  mutates files in parallel; otherwise a plain subagent keeps the read isolated.
- Adversarial verify → `parallel(Array.from({length:N}, () => () => agent("refute: …")))`
  then keep the claim only if refutations < majority.

## 8b. Off-the-shelf vs bespoke — OSS agent vetting (2026-07-19)

Vetted `wshobson/agents` (203 agents / 94 plugins), `VoltAgent/awesome-claude-code-subagents`
(154+), and the `hesreallyhim/awesome-claude-code` index via a delegated Sonnet subagent.

- **Keep bespoke:** `/ultrareview` + `/dual-bar-raiser` remain the primary review gate.
  Nothing OSS is ARCS-aware — the marketplace agents are generic "elite reviewer"
  personas with no DEWY / Y-gate / NOTOMATION grounding, and would actively suggest
  things CLAUDE.md forbids (new deps, Tailwind, `className`). They do not beat a
  domain-specific ADR/receipt-aware reviewer for this repo.
- **Adopt (different layer, not a replacement):** `anthropics/claude-code-security-review`
  — Anthropic's own GitHub Action that runs semantic vuln detection on the PR diff at
  merge time. ARCS has no automated CI-time security scan today, so this is additive.
  **Gate:** it is explicitly **not** prompt-injection-hardened → only safe on trusted PRs.
  The repo is public, so wire it **only** with "require approval to run workflows for
  outside collaborators" set. Needs `CLAUDE_API_KEY` in GitHub Secrets. Recommendation
  pending human sign-off — do not enable silently.
- **Adapt (convention, not code):** mirror VoltAgent's read-only tool scope for any
  audit-role agent (`Read, Grep, Glob` only — no Write/Bash) in future ARCS agent defs.
- **Skip:** installing either marketplace wholesale (supply-chain surface + generic
  prompts). Test-generation agents are premature — ARCS has no test suite yet; decide a
  testing policy first, then pick tooling.

## 8. Guardrails

- Strong-model nodes are the minority of node *count* but the majority of
  *budget* — that's correct; don't let grunt work creep onto Opus.
- Re-cost a job here before running it; if a run's shape changed, update the row.
- Single-agent jobs stay single-agent. Orchestrating a 10k mechanical task
  costs more in coordination than it saves.
