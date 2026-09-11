# Hermes Operationalization — Shared Ground Truth

> **Single reference page for both harnesses** (Claude Code Terminal + Hermes-orchestrator)
> working the Hermes production-readiness thread under the dual-bar-raiser protocol
> (`.claude/arcs-dual-bar-raiser.md`). The human is the relay; **git is the write-lock**.
> Nothing here is true until it is committed on the right base. Last updated: 2026-08-30 (+ §5.1 sequencing/serialization).

---

## 0. The naming split (resolve this first, every time)

"Hermes harness" is **two different systems**. Do not conflate them.

| Name | What it is | Where | Role |
|---|---|---|---|
| **Hermes-orchestrator** | The `~/.hermes/` CLI agent runtime (v0.20.6): kanban, a2a, sessions, spawn-ledger, MCP, platform adapters | `~/.hermes/`, bin `~/.local/bin/hermes` | The counterpart in this dual-bar-raiser; one leg of the Hermes / Claude Code / QuaDriver triad |
| **Hermes-harness** | The `operators/audit_service/` FastAPI sidecar that runs the 4 Python operators (SAGE/LAB/BAR/KINTSUGI) against compass receipts | `operators/audit_service/` in arcs-v9 | The thing being built; subject of JTBD-A..F |

**JTBD-A..F below is the HARNESS.** The gate sheet (§4) is the ORCHESTRATOR.

---

## 1. Canonical branch

**`feat/audit-service`** — off current `main`, PR-able, additive (zero deletions).

```
cfbd1200  wire record_coverage into main.py — Approach D coverage now fires
60fa95c3  audit-service baseline on main — Task 18 recovered, scaffolding pruned
```

Contents: 16 runtime files (`operators/audit_service/*` + `src/lib/audit-*.ts` + `docs/audit-translator-validation.md`).
Verified in-commit: all `*.py` py_compile; service loads as package (`operators.audit_service.main`);
`play_instrument.py` exit 0; Task-18 API present; `record_coverage` fires once per receipt and
`operator_coverage` reaches `store_benchmark_fragment`.

**Retired:** `claude/hermes-production-readiness` — deleted on origin (2026-08-30). It sat 1739 commits
behind main on the `feat/resume-pwa-theming` lineage (merge-base 2026-05-25) and carried the wrong,
pre-Task-18 `persistence.py`. A stale **local** ref may still exist in the main checkout
(`/Users/zharris/arcs-v9`) because that checkout is parked on it — Hermes clears it with
`git checkout main && git branch -D claude/hermes-production-readiness`.

---

## 2. The recovery record (KINTSUGI — show the break and the gold)

Task 18's `persistence.py` (655 lines: `compute_csm`, `fidelity_weight`, `_WEIGHTS`, `weighted_csm`,
`weighted_csm_by_operator`, `print_weighted_store`) was **verified in a working tree but never committed**.
A `git add` caught only untracked files; a branch checkout then reverted the tracked files. The verified
655-line version survived only as **dangling blob `ac455d1d`** and was restored from it into 60fa95c3.
`store_benchmark_fragment` in this version accepts `operator_coverage=` (coverage-aware).

Unrecoverable: an earlier 419-line `audit-translator.ts` measurement — no blob exists. **396 is canonical**
unless Hermes recalls specific lost content (e.g. a HORIZON_MAP / somaticPrompt addition).

---

## 3. The failure class (why this thread cost three rounds)

Same failure three times, each caught by diffing working-tree against git:
1. Harness files RAM-only (uncommitted) — would vanish on branch switch.
2. Force-push onto a 3-month-stale base — 756 unrelated commits, unmergeable diff.
3. The commit captured *older* tracked files; the verified newer ones were discarded (Task 18 loss).

**Invariants (banked):**
- **One tree, one write-lock.** Never fix the same file in two working trees. The canonical branch is the only place edits land.
- **Verify in git, not RAM.** A claim ("36/36 pass", "wired", "N lines") is only real of the *committed* tree. Re-run against disk before asserting.
- **Diff-stat vs origin/main before any PR.** Blast radius must be the intended files, zero surprise deletions.
- **Oracle-first numbering** for any ADR/seed/receipt (`python3 scripts/oracle.py next <ns>`).

---

## 4. Gate sheet — Hermes-ORCHESTRATOR operationalization

Done = all provable, not asserted. Sequence: G1 → G2 → G4 → G3 → G5.

| Gate | Provable when | Status |
|---|---|---|
| G1 Reliable inference | `fallback_model` set in `~/.hermes/config.yaml`; kill primary mid-run, task still completes | ❌ commented out |
| G2 One real inbox | ≥1 platform `enabled:true` + `channel_directory` non-empty; a task assigned to `arcs` pings the human | ❌ empty |
| G3 Live LLM path | `llm_client` wired into CIS pipeline so `adr_audit.py --model X` changes the envelope | ❌ inert (ADR-073) |
| G4 Shared write-lock | oracle pre-commit hook installed in Hermes cwd; duplicate-ADR commit rejected | 🟡 armed, uninstalled |
| G5 Round-trip JTBD | Hermes pulls one `_QUEUE/induced-backlog.jsonl` item, does it, opens PR, closes loop — unattended | ❌ not run |

QuaDriver = **cua-driver** (cua.ai, MIT). RESOLVED 2026-08-30. An open-source computer-use driver
(macOS/Windows/Linux) that sends input to **specific windows without moving the system cursor** —
background operation, agent drives app A while human works in app B. Exposes **MCP** (window snapshots +
input tools) + CLI (`cua-driver serve|call|mcp`); Claude-Code-compatible; honors a "no-foreground
contract". **Hermes already consumes it.**

**Slot = application-I/O plane, NOT the inter-agent bus.** It is how *either* harness reaches native
desktop apps, not how Hermes and Claude Code talk to each other (that stays git write-lock + relay; a2a is
the future agent↔agent wire). It removes **cursor contention** — the reason multi-threading on one machine
normally fails — the same way git removes file contention. Triad: **Hermes = orchestration · Claude Code =
judgment · git = file write-lock · cua-driver = input/app write-lock.**

**SECURITY GATE (before wiring cua-driver to Claude Code):** scope it to ARCS-only FIRST, then wire.
macOS TCC (Accessibility, Screen Recording) is granted GLOBALLY to `com.trycua.driver` — the OS cannot
scope per-app. Scoping is done at cua-driver's own `bounded` mode + `cua-capabilities.yaml` manifest
(allowlist; everything outside denied). ARCS is a web app → use **browser-origins mode** (origin-gated
`browser_*` tools; mutually exclusive with generic `click`/`type_text`/`get_window_state`), origins =
app.arcs.care/arcs.care/localhost:3000, files = the repo dir, `desktop.display: false`. Reviewed template:
`docs/cua-capabilities.example.yaml`. Enabled with human `--approve-capability-manifest` (agent cannot
self-grant) + `expires_after`/`idle_timeout`. Caveat: this is cua-driver policy, not a kernel sandbox —
for a hard boundary run it under a dedicated macOS user account or VM.

---

## 5. JTBD-A..F — Hermes-HARNESS productionization

Ownership split (agreed): **Claude Code = doc-heavy design; Hermes = items needing its running service.**

| Item | What | Owner | Status |
|---|---|---|---|
| A Kernel legibility | `operators/README.md` inventory current vs `operators/*.py` | either | partial |
| B Surface composition | `docs/surface-composition.md` — each surface × kernel pieces × voltage/current | **Claude** | ✅ DONE (81384e66) |
| C Seam contracts | `docs/seam-contracts.md` — name/guard each shared-state seam; DB-down policy | **Claude** | ✅ DONE (2529ec56) |
| D De/composability | `ARCS_MODEL` env-var to swap operator impl, or decision record why not | shared | not started |
| E Sovereignty boundary | `docs/sovereignty-boundary.md` — harness-enforced invariants vs surface-declared config | **Claude** | ✅ DONE (2529ec56) |
| F RAG kernel-discovery | `docs/rag-kernel-discovery.md` — design only (impl is P3/GIGI) | either | not started |
| Task 10 | `docs/audit-service-interface.md` — full FastAPI spec | Claude | open |
| Task 17 | `validate_translator.py` — script now, exec blocked on DB | Hermes | open |
| Task 19 | `store_csm_result` persistence + wire | Hermes | ✅ DONE — ratified vs Seam 2, merged 736b67d9 |
| Task 20 | consolidate stores (benchmark_pairs vs audit_traces vs csm_results) + doc | Claude | open — incl. trim redundant `llmOutput` from CSM row (recoverable by join) |
| Task 21 | `docs/monthly-review-template.{md,json}` | Claude | open |
| Task 23 | SQLite/queryable store migration | — | deferred |

### 5.1 Sequencing & serialization (read before writing)

**Ordering principle: contract-defining work LEADS implementation.** The reasoning that defines a
contract (seams, invariants, boundaries) is written first; the implementation conforms to it rather than
defining it by whatever was convenient. This beats file-contention ordering — it's the stronger constraint.
(The axis is contract-vs-implementation, which *mostly* but not perfectly maps to Claude-vs-Hermes:
task 10 is descriptive grunt that's Claude's; task 19 carries real schema judgment.)

**Three phases:**
1. **Contracts lead (parallel, collision-free):** Claude → **E** (sovereignty boundary) + **C** (seam
   contracts, incl. store/DB seam) — these govern how the store must behave. **B** rides along.
   Hermes → **17** (new `validate_translator.py`, zero contention). All new files.
2. **Implementation conforms:** Hermes → **19** (`store_csm_result`) implemented *against* C + E — do NOT
   start until C + E are pushed. This is the `persistence.py`/`service.py` write-lock.
3. **Descriptive/consolidation last:** Claude → **10, 20, 21**, snapshotting the settled code (20 conforms
   to C's store seam; 10 specs the frozen interface).

**File contention map — only `persistence.py`/`service.py` is contended.** Everything else (all docs,
task 17) is parallel-safe. **Hard dependency: 19 → 20** (19 changes store shape; 20 documents/consolidates
it — 20 held until 19 lands).

**Branch model (OPEN — human/Hermes to confirm):** either (a) **private branches off `feat/audit-service`,
merged back in phase order** (no push races — recommended), or (b) **shared `feat/audit-service`, turn-take**
(one write-lock holder at a time). Two harnesses cannot push the same branch concurrently.

---

## 6. Open decisions
- Branch model for the JTBD split: private-branches-merge vs shared-turn-take (§5.1).
- QuaDriver: what is it, and which control-plane slot (§4).
- G-sequence execution once the harness JTBD lands.
- Whether the 396-line `audit-translator.ts` is missing real content (§2).

## 7. Update protocol
Edit this file on `feat/audit-service`, commit (`type(scope): imperative [NCI:..]`), push. Both harnesses
pull before writing. If the two harnesses disagree, the disagreement is logged here, not resolved silently.
