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
- **Trust-of-input override (ADR-032 P6):** tier = `difficulty × trust-of-input × blast-radius`, risk-calibrated, never blanket. Bump to a robust model **only** where *untrusted* input meets an egress channel or real consequence; keep the cheapest model where input is trusted **or** blast-radius is bounded (interior no-tools reasoners can't exfil even if poisoned). Worked example (`recoil-report` gather): email + web → Sonnet; calendar/transcripts/git → Haiku; interior reasoners stay quality-tiered. Security budget concentrates at the 2 real trust boundaries — compute efficiency preserved.

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

## 8c. Approved backlog — ATG-generated, ratified 2026-07-19

Generated by running ATG over this session's own second/third-order effects;
all six approved by the operator. Owner "human" = needs a person, not a session.

| ID | JTBD | Tributary | Owner | Model / budget | Status |
|----|------|-----------|-------|----------------|--------|
| **J1** | Sanitize external-surface telemetry (chan shows counts+deploy only; status full) | need-to-hear | session | Sonnet / ~5k | **DONE 2026-07-19** |
| **J6** | Secrets inventory + rotation ADR | meta-question | session→human | Sonnet / ~10k | doc landed → `_DECISIONS/ADR-031` |
| **J2** | Public-repo exposure audit (named dossiers + IP in a public repo) | meta-question | session→human | Opus / ~20k | audit landed → `_PATTERNS/public-repo-exposure-audit.md`; remediation = human call |
| **J4** | Workflow cost ledger (actual vs projected spend) | adjacent primitive | session | Haiku / ~5k | ledger seeded → `_PATTERNS/workflow-cost-ledger.md` |
| **J5** | Concurrent-session merge guard (pre-push drift check + branch protection) | need-to-hear | session→human | Sonnet / ~30k | **QUEUED** — plan below |
| **J3** | Falsifiability harness (make the eval matrix runnable, OSF-preregistered) | adjacent primitive | session | Sonnet+Opus / ~120k | **QUEUED** — plan below |

**J5 plan:** a `pre-push` git hook that (a) fetches `origin/main` and refuses to
push if local `main` is behind (forces rebase, kills silent clobbers), (b) checks
`_STATE/snapshot.json` head matches HEAD. Plus repo branch-protection on `main`
(require PR, no direct push) — the human half. Root cause: multiple sessions on
`main` is the "3 logs disagree" pathogen's structural source.

### Post-validation additions (ATG over the recoil-report run, 2026-07-19)

| ID | JTBD | Source | Status |
|----|------|--------|--------|
| **J7** | Cap verify fan-out (top-N claims/lens by confidence) | run blew budget: 31 claims → 93 Opus verifiers | **DONE** — `MAX_CLAIMS_PER_LENS=5` |
| **J8** | Reasoning agents truly no-tools (`recoil-reason tools: []`) | run bled other people's dossiers into the report | **DONE** — validate empty-tools on next run |
| **J10** | MCP connectivity preflight (warn + `thin` flag) | gather built on 2 of 5 sources silently | **DONE** — preflight warning + `thin` in result |

**Downstream backlog (recommended next paths, not yet started):**
- **J11** — `/ultrareview` enforces the ADR-032 conformance checklist (makes the doctrine self-enforcing, not aspirational). meta. ~med.
- **J12** — Wire the Skeptic Sentinel to `pathogen_log` / `immune_sessions` (close the anti-fragile loop — each caught form primes the next). adjacent. ~med.
- **J13** — Dual-control handshake in code (agent↔agent HMAC on a different model; human via magic-link step-up). From ADR-032 pattern. ~med.
- **J14** — Global write-lock serializability (the yoav question): branch-protection *trigger* + pre-push *hook* for `main`; a lease *worker* only if the yoav store needs pessimistic locking. Read `operators/arcs_yoav_store.py`, then ADR. Supersedes/absorbs J5. ~med.
- **J15** — Verify cost, deeper: Sonnet first-pass refutation, Opus only on survivors (further bounds the driver J7 capped). adjacent. ~low.
- **J16** — Recoil-report gather robustness: reconcile the CURATOR's cross-file reads as an *explicit, consented* input list (per-subject allowlist) rather than filesystem wandering — makes multi-artifact synthesis safe under J8. adjacent. ~med.
- **J17** — **Fork Lineage** (rebrand `init-state-sync`). Two moves: (a) make snapshot-sync a mandatory step 0 of `/handoff` — the semantic fields (session_summary/next_action/blocking/open_adrs) don't auto-refresh like the git fields do, so they silently drift (2 days stale at this handoff; operator caught it, the process didn't). (b) **Reframe the snapshot from a mutable current-state blob into a fork-lineage provenance record**: each session/worktree stamps the state it *forked from* (parent HEAD + fork timestamp + session id) and its *merge-back*, yielding a session-provenance DAG. This is the receipts/provenance ethos applied to the session topology itself, and it's the observability layer J5/J14 (write-lock serializability) need to make concurrent-session drift legible rather than a mystery — and it ties into the archaeology/immune-ledger themes. meta/process → architecture. ~med.

### Local→global audit (things we scoped local that are actually a class, 2026-07-19)

Prompted by the chronos-sequencer generalization — same failure mode (fix the instance, miss
the class). Ranked by exposure:

- **J19 (HIGHEST) — Harden `/api/compass`, the real front door.** We spent the session
  hardening an *internal* validation workflow (recoil-report) with untrusted-data wrapping +
  the Skeptic Sentinel, while the **production LLM entry point that takes real, arbitrary user
  input** got none of it. The actual injection surface is unhardened. Apply untrusted-data
  framing + a Sentinel pre-screen to compass. ~med.
- **J20 — Promote the Skeptic Sentinel to a standalone reusable operator** (not embedded in
  recoil-report). Intent/premise screening applies to compass, any workflow, and webhook/PR
  ingestion — it's the general trust-boundary operator, currently trapped in one workflow. ~low.
- **J18 — Rename the scoped agent types to generic primitives** (`recoil-reason` → a no-tools
  reasoner; `recoil-gather-*` → read-only gatherers). The `recoil-` prefix makes *reusable*
  primitives look single-use, so review-gate/patent-triage will re-invent them. ~low.
- **J21 — Default watchdog/stop-rule for every long-running background task**, not per-run.
  We wrote one for the recoil run by hand; every workflow/agent/deploy-wait needs the timeout. ~low.
- **J22 — MCP server identity pinning.** The servers reconnect under *changing* IDs — noted
  as a local annoyance, but it's a supply-chain trust gap (P8/P10): you cannot cryptographically
  pin a server whose identity churns. A changing identity is itself a trust signal. ~med.
- **J23 — Freshness stamps on all derived/cached surfaces** (brief, receipt, observatory), not
  just the Live Pulse — the "data as of" principle is a class, not a one-widget fix. ~low.
- **J24 — External-surface leak policy is a class, not just chan** (J1). Every prospect-facing
  subdomain must not surface internal text; make it a policy + a check, not a per-page fix. ~low.
- **J25 — Recursion/termination audit of self-referential operations.** Each self-triggering or
  self-spawning process needs an explicit terminating condition: state-sync (✓ fixed — gated
  terminal step), **ATG** (needs a stop rule — halt when a round yields no new *class*, not just
  no new item), **Skeptic-on-Skeptic** (depth cap), workflow nesting (harness-capped at 1), and
  the **local→global generalization** itself (bound the altitude climb). Unbounded self-reference
  = liveness bug. Now gated by the ADR-032 checklist item. ~low.

**J3 plan:** per top-3 claim (accuracy-scaling, calibration, beats-experts):
pre-register on OSF → build a time-ordered backtest over the receipt corpus →
report CI-hit / reliability / win-rate against the kill criteria in §Evals. Gated
on ≥100 real receipts (same gate as ADR-023) — until then, harness scaffolding only.

## 8d. Least-privilege agent scoping (standing rule for all workflows)

A complex fan-out must not hand every agent full read/write/shell/MCP/spawn access.
Scope each stage to the minimum via `agentType`:

- **Reasoning stages** (synthesis, lenses, judges, verifiers — usually the *majority*
  of agents) → a **no-tools** agent type (`recoil-reason`: `tools: Read` only). They
  reason over prompt text; they cannot write, run shell, call MCP, reach the network,
  or spawn subagents. This is the biggest, safest surface reduction.
- **Gather / collect stages** that genuinely must touch external systems → the built-in
  **`Explore`** (read-only: keeps Bash/WebFetch/MCP for collecting, but no Write/Edit
  and cannot spawn subagents).
- **Never** run a many-agent workflow on the default `*` agent. Reserve write-capable or
  worktree-isolated agents for stages that actually mutate files, and only those.

Applied in `recoil-report.mjs`: only the 5 gather agents can touch external systems
(read-only); all 8+ reasoning agents (profile, 4 lenses, N verifiers, synth) have
`tools: Read` and nothing else.

## 8. Guardrails

- Strong-model nodes are the minority of node *count* but the majority of
  *budget* — that's correct; don't let grunt work creep onto Opus.
- Re-cost a job here before running it; if a run's shape changed, update the row.
- Single-agent jobs stay single-agent. Orchestrating a 10k mechanical task
  costs more in coordination than it saves.
