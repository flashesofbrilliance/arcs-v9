# monday.com take-home prep: what monday publishes, how good its evals are, and where ARCS fits

Scope and limits: this is built only from the supplied static crawl (2026-10-08), three skeptic passes, and the specialist lenses. Nothing was cloned, installed or run, and I did not re-open primary sources. "Verified" means a reader saw it in source or docs. It does not mean anyone executed it. "Inferred" means reasoned from verified facts. The crawl's developer-docs section and the architect lens were cut off mid-sentence in the input, and so was the last skeptic block. Any corrections in the lost text are not reflected here. The take-home prompt itself was not in the inputs.

## 1) What monday actually publishes

**GitHub (org `mondaycom`)**

| Artifact | What it is | Confidence | Evidence path |
|---|---|---|---|
| `mondaycom/mcp` | MIT monorepo, created 2025-04-06, 427 stars, 53 open issues, last push 2026-10-08. Packages: `@mondaydotcomorg/agent-toolkit` v5.73.0 and `@mondaydotcomorg/monday-api-mcp` v3.3.1. MCP (Model Context Protocol) is the standard for exposing tools to AI agents. | verified | `gh api repos/mondaycom/mcp`; `packages/*/package.json` |
| Tool surface | At least about 90 named tools (about 33 read, 54 write, 2 raw-API). This is a floor, because the regex missed some. The README table lists only about 14 early tools. | inferred | `packages/agent-toolkit/src/core/tools/**`; README "Available Tools" |
| Hosted MCP server | `mcp.monday.com/mcp` is the recommended path, but its source is not in any reviewed repo. OAuth, scoping and limits on the hosted side cannot be audited from public code. | inferred | README "Hosted MCP"; `server.json`; tree grep found no server or OAuth code |
| Local server auth | Personal API token via env or flag. No OAuth locally. Modes: default, apps, atp. `--read-only` is a tool-registration filter. | verified | `packages/monday-api-mcp/src/index.ts`; `tools-filtering.utils.ts` |
| Apps mode | Can set app env vars, promote an app to live, and export storage. | verified | `core/tools/monday-apps-tools/**` |
| Tests in `mcp` | Jest, mock-based, 78 `*.test.ts` files (the crawl said about 84; the skeptic counted the tree). No live-account, agent-behavior, tool-selection or injection tests. | verified | git tree; `.github/workflows/pull_request.yml` |
| Open issues | #501 (failed writes returned as success), #496 (relation, mirror and dependency column writes look failed but succeed), #508 (a search tool with 8 required fields breaks GPT-5.5 in Copilot Studio), #218 (oversized board-info output). | verified | `gh api repos/mondaycom/mcp/issues` |
| `agentic-monday` | Claude Code plugin marketplace with 3 plugins (monday-api, monday-code, vibe). Its one eval has 13 skill-trigger prompts (7 should-trigger, 6 should-not), scored 13/13 with model "sonnet". | verified | `plugins-official/monday-api/evals/monday-oauth-migrate/{evals.json,eval-results.json}` |
| Eval provenance | The results file cites PR 729 and run 25730947850. Both return 404 in public repos, so the harness is not published. | verified | `gh api` on pulls/729 and actions/runs/25730947850 |
| `skills`, `monday-claude-cowork-plugin`, `ai-skills-examples` | Five near-duplicate Agent Skills (procedural prompts, no tests) running over hosted OAuth MCP; a sample app showing how a monday AI "sidekick" skill runs a workflow block. | verified | each repo's README and tree |
| `agent-tool-protocol` (ATP) | Code-first alternative to tool-calling. The model writes JS that runs in an `isolated-vm` V8 sandbox. MIT, 101 stars, v0.26.0, 2 main authors. It layers on MCP and has a monday GraphQL example. | verified | ATP README; `packages/server/package.json`; `examples/monday-graphql` |
| ATP defaults | Provenance (taint tracking) is off by default. Approvals fail closed when no handler is set. A hard-coded default JWT secret is used if none is set. | verified | `create-server.ts` line 99; `client-sessions.ts` line 13; `runtime/src/approval/index.ts` |
| Platform tooling | `apps-sdk`, `monday-apps-cli` (`mapps`), `monday-code-quickstarts`, `welcome-apps`, `vibe` (design system, with its own `@vibe/mcp` server), `mcli`. | verified | each repo's README |
| `n8n-nodes-monday-models` | Empty repository (no commits). | verified | `gh api` returns 409 "empty" |

**Hugging Face.** There is no monday.com organization, model, dataset or Space. The HF API returned 404 or empty lists for nine name variants. The handle `monday` is an unrelated personal user. No Hugging Face usage was found in mondaycom code, but code search can miss things, so this is strong absence rather than proof. Confidence: verified for the HF API results, inferred for the code search. (`huggingface.co/api/organizations/<name>/overview`; `gh search code --owner mondaycom huggingface`)

**Developer docs.**
- **Machine-readable:** `.md` suffix on pages, plus `/api-reference/llms.txt` and `/apps/llms.txt`. Verified.
- **MCP calls consume the API budget:** MCP calls run as GraphQL, so they count against the daily limit (1,000 on Free/Standard/Basic, 10,000 on Pro, 25,000 on Enterprise). Per-minute limits are 1,000, 2,500 and 5,000. Concurrency limits are 40, 100 and 250. Verified. (`rate-limits.md`)
- **MCP security page:** It says MCP actions run under the user's own permissions. It assigns prompt-injection and output validation to the customer or AI client. It says self-service export of detailed MCP or API audit logs is not available. Verified. (`monday-mcp-security-overview.md`)
- **Models API:** An OpenAI-compatible gateway at `api.monday.com/platform-ai-gateway/openai/v1`. Upstreams are OpenAI and Anthropic only. Billing is in "monday AI tokens", with a per-call `x-monday-credits-used` header. No numeric rates or gateway rate limits were found. Verified. (`changelog/consume-ai-models-through-monday`; `getting-started-with-the-models-api.md`)
- **Bring-your-own model:** Unsupported, per search summaries of monday's FAQ that nobody read directly. Inferred.

## 2) Verdict on Sensei and the other off-the-shelf evals

**Sensei (`mondaycom/sensei`) is a demo-grade smoke harness, not a qualification standard.**

Why it should not be treated as monday's standard:
- Created 2026-03-15, last push 2026-03-22, v0.0.3, 20 stars, 7 issues and PRs ever.
- Commits trace to AgentTalent.ai and "Nymeria", with early multi-agent AI build messages.
- `SECURITY.md` routes reports to a personal Gmail address.
- monday's docs index never mentions it.
- Verified for the facts above; the "AI-built and adopted" reading is inferred. (`gh api repos/mondaycom/sensei`; `SECURITY.md`; `developer.monday.com/api-reference/llms.txt`)

What it does well (verified):
- Clean YAML suite schema, with Zod (a schema validation library) checking suites at load.
- Transparent scoring math: KPI to scenario to layer, weighted 50/30/20, with badge cutoffs at 90, 75 and 60.
- Deterministic KPI primitives: contains, regex, json-schema, json-parse, numeric-range, word-count.
- Seeded scenario pools.
- A `multi_judge` option (several judge calls, median score) reachable from suite YAML.
- An HTML report and `duration_ms` timings.
- (`packages/engine/src/{scorer,types,schema,loader}.ts`)

Where it fails as an eval (verified by reading source, not executed):
- **The judge never sees the fixtures.** It gets only the prompt string, so accuracy KPIs such as personalization are scored on plausibility. A fluent fabrication scores like a grounded answer. (`runner.ts` `runScenario`; `cli/src/commands/run.ts`; `judge.ts` `inputContext`)
- **Fixtures are also dropped on two of the four agent adapters.** The `openai-compat` and `langserve` adapters forward only `previous_output` and `feedback`. Only `http` and `stdio` forward the full context. A hosted-model or Ollama run through `openai-compat` scores two models inventing a prospect. (`adapters/openai-compat.ts` 107-120; `adapters/langserve.ts` 88-94; `adapters/http.ts` 67; `adapters/stdio.ts` 145)
- **The agent's model name cannot be set from YAML or the CLI.** `AgentConfig` has no `model` field, so it is always `'default'`. That blocks same-gateway model comparisons through the CLI. The key-stripping step is standard Zod behavior and was not run. (`openai-compat.ts` line 58; `types.ts`; `schema.ts`)
- **Judge controls are minimal:**
  - Single model, default `gpt-4o`, temperature 0.
  - No order randomization, length control or cross-family judge.
  - The judge's confidence value is collected and never used.
  - `parseVerdict` rejects only NaN, with no clamp.
  - A judge outage becomes a KPI score of 0 instead of a failed run.
  - (`judge.ts`; `runner.ts` catch block)
- **`multi_judge` is not a bias fix.** It makes three calls to the same model at temperature 0 and takes the median. The `rate_limit` and `retry` YAML keys are stripped by the schema (inferred, standard Zod behavior).
- **Layers 2 and 3 are weak.**
  - The "interview" is a fresh prompt with the previous output prepended.
  - "Self-improvement" appends a static feedback string.
  - The comparator never interpolates the per-KPI rubric, has no order blinding and has no timeout.
  - (`runner.ts`; `comparator.ts`)
- **Reproducibility fields are partly missing.** Results carry `agent_id`, `timestamp`, `judge_model`, transcripts and durations. They lack run id, seed, judge-prompt version and cost. (`types.ts`)
- **`scenarios_per_layer` is dead.** `pickScenariosByLayer` is called nowhere in the runner or CLI. The shipped suites use no pools and no `multi_judge`.
- **Suite coverage is thin:**
  - Suites are SDR (sales development rep), support, content, and three novelty suites.
  - Only SDR has fixtures.
  - The README's QA, Data Analysis and Developer suites do not exist.
  - (`suites/*/suite.yaml`)
- **Safety surface:** a downloaded marketplace suite can set `agent.command` for the `stdio` adapter and spawn processes. No suite signing was seen (inferred). (`adapters/stdio.ts`; `registry-client.ts`)

Two corrections to claims in the specialist lenses:
- **"Only automated check is word-count"** is true of shipped suites but misleading. The engine has six deterministic primitives. What is missing is labeled data wired to them. The `function` KPI type returns 0 on the CLI path. Some SDR rubrics also name expected facts, which gives the judge a weak coverage check. (`scorer.ts` 38-170; `suites/sdr-qualification/suite.yaml` 51-125)
- **"A catastrophic layer failure can still earn silver or gold"** overstates it. By my arithmetic from the 50/30/20 weights, a zero in a full three-layer suite caps the overall score as follows. This is inferred from `LAYER_WEIGHTS` and `BADGE_THRESHOLDS`.

  | Layer scored zero | Best possible overall | Badge |
  |---|---|---|
  | Reasoning | 70 | bronze |
  | Self-improvement | 80 | silver |
  | Execution | 50 | no badge |

  The real averaging risk is inside a layer (one bad scenario among 1-3) and in layers that are absent, which renormalize. Per-KPI hard-fail gates are still missing.

**Other evals:**
- **`agentic-monday` routing eval:** a 13-case smoke test of which skill fires, not task outcome.
  - 13/13 on 13 cases means the true pass rate could plausibly sit near 75% (my reading of the data scientist's exact interval: 0.025^(1/13) is about 0.75, a two-sided 95% bound).
  - The authors wrote the prompts, it ran once on one model, and the pipeline is not public.
- **`mcp` Jest suite:** tests each tool contract against mocks. It cannot see cross-model or live-account failures such as #501, #496 and #508.
- **ATP tests:** real LLM-in-the-loop approval, resume and security tests run against local Ollama models (`qwen2.5-coder:7b` or `gpt-oss:20b`). They are not in CI: `test.yml` runs unit and one OpenTelemetry integration test only, and lint is `|| true`. (`agent-tool-protocol/.github/workflows/test.yml`; `__tests__/e2e/test-config.ts`)

## 3) Gap map by job-to-be-done shape (after skeptic corrections)

| # | Shape | Rating | Reusable off the shelf | Corrections applied |
|---|---|---|---|---|
| 1 | Connect monday to CRM, ERP or ticketing | Gap | `mcp` mock tests as a contract smoke tier; the GraphQL codegen drift check | Test count is 78 files. The one eval has 7 trigger and 6 negative cases and an unpublished harness. |
| 2 | Agents that do work (SDR, triage, reporting) and need qualifying | Partial, closer to demo-grade | Sensei suites, scoring math, deterministic primitives | Judge blind to fixtures. Primitives exist, but labels and wiring do not. No triage or reporting suite. |
| 3 | Governed AI in cautious or regulated enterprises | Gap | Own-OAuth-app scope cap; ATP approvals and tool rules | See below. |
| 4 | Adoption and ROI after launch | Gap | API analytics dashboard (call volume only) | Cost telemetry exists at the gateway: credits header, qualitative metering. Outcome telemetry does not. |
| 5 | PII or private-model constraints | Gap (downgraded from partial) | None demonstrated | Config path is plausible but untested. Every engine test mocks the model. The LLM client throws without `OPENAI_API_KEY` unless `api_key` is in YAML. Fixture-dropping and the fixed `'default'` model name also block it. |
| 6 | Comparing models or agents | Gap via the CLI; possible via SDK, `http` or `stdio` only | Same YAML across `http`/`stdio` endpoints | Fixtures dropped on `openai-compat`. Model name fixed. `multi_judge` and pools are YAML-reachable but unused. Latency exists; cost does not. |
| 7 | Reusable assets and product feedback | Partial | Skills repos, plugin dirs, registry entries, suite marketplace | Plumbing exists. No evals on skills, no visible CI, no signing, no run metadata. |
| 8 | Long-horizon workflows with human checkpoints | Gap | ATP approval and resume mechanics | Not scored by any eval. ATP's LLM-in-loop HITL tests exist but are ungated. A server-side-stateful agent can leak state across Sensei scenarios (the adapter sends a stable `user` key per run, with 5 scenarios in parallel). |

Shape 3 corrections: the platform is better than "no controls".
- **Own OAuth app route:** an org can cap scopes (for example `boards:read`), restrict users and client, and rotate the secret to revoke everyone. The docs say you get your own audit trail of authorized users and activity.
- **Dynamic connectors:** these are early access. Tokens can keep working up to 24 hours after revocation, and admins get no email about requests.
- **Undo and annotations:** `undo_action` and `get_board_activity` exist, but undo uses the unstable dev API version. Tools carry `readOnlyHint` and `destructiveHint` annotations.
- **What still holds:** no self-service per-tool-call audit export, and no untrusted-content tagging.
- **Unverified:** "no per-board scope" is an absence nobody confirmed either way.
- Evidence: `control-mcp-access-with-oauth-app.md`; `mcp-dynamic-connectors.md`; `undo-action-tool.ts`.

## 4) Divergent expert perspectives

- **Data scientist (validity):** The scores have no demonstrated meaning. The sample is tiny (n of 1-3 per layer), there is no variance, the judge is unvalidated and the KPIs are mostly opinion. Fix first: ground-truth KPIs, then calibration.
- **ML engineer (operations):** The practical blockers are determinism, silent-zero failures, missing cost and run metadata, and weak local-model support. Advice: lead with the smallest fix for an observed flaw, not a rebuild.
- **RL and agents researcher (trajectory):** Text-in/text-out cannot score tool use, credit assignment, long-horizon recovery, or whether "self-improvement" is real. Proposes counterfactual replay, learning curves with held-out sibling tasks, fault-injected sandbox episodes, and indirect-injection scenarios scored on obedience.
- **Systems architect (deployment):** The larger risks sit on the platform side, not in Sensei:
  - no per-call audit export;
  - unsanitized returned data next to write tools, which is the "lethal trifecta" shape (untrusted content, private data, write or exfiltration ability);
  - read-only being a registration filter;
  - apps mode able to promote an app;
  - failed writes returned as success (#501) next to a daily call cap.
  - The fixes are customer-side: gateway audit sink, low-privilege service users, read-after-write checks, dedupe ledger, quota allocator.

Disagreements and how they resolve:
1. **Is `multi_judge` reachable?** The RL lens and the crawl said no. The skeptic showed it is reachable through YAML and simply unused. It is still not a bias control.
2. **Do the badges launder catastrophic failure?** The data scientist and RL lenses said yes. The arithmetic above says only partly: a reasoning zero caps at bronze, a self-improvement zero still earns silver.
3. **Scope.** The ML engineer says start small, while the RL lens lists nine proposals. Treat the RL list as a menu, not a plan. The sequencing in section 5 follows the ML engineer.
4. **Local models.** The architect and ML engineer said "partial". The skeptic found fixture-dropping, the fixed model name, the key requirement and fully mocked tests, and downgraded to gap.
5. **Wasted JSON-parse retries at temperature 0** are the ML engineer's inference. Nobody tested them.
6. **Sensei's status.** The architect rated it "partial". The skeptic's provenance evidence points to "unadopted side project".

## 5) ARCS plug plan with honest status

These ARCS claims come from the plug input and the repo's own docs. I did not re-verify them. None has been run against a monday agent, and everything below is a proposal until built. ARCS is the user's own decision-intelligence system. Its Y-gate is a state check that can force a RED result. Its Kintsugi rule means a failure is shown, never silently patched. WRITE-LOCK means a one-way action requires an explicit declaration first.

| Shape | ARCS piece | Honest status | What to build |
|---|---|---|---|
| 1 | Append-only operator ledger; `arcs-verb-eval` assessment verdicts; Kintsugi "show the break" | Partial: the ledger covers ARCS operator calls only. The integration eval is not built. | Sandbox monday account driven through the real MCP server with tool-call capture; a deterministic board-state diff against a golden end state; read-after-write checks for #496-class columns; an `isError` mismatch scorer for #501; fault injection (429, partial write, stale ID). |
| 2 | Accountant (reports `sufficiency=insufficient` with n below 30 closed per cohort); verb-eval judge that cannot change a gate; five-lens high-stakes gate; `provenance_lint.py` | Partial: the mechanical gates are built and used on ARCS's own artifacts. Calibration is unproven because outcome capture is low (2 of 247 per AGENTS.md; the Accountant docstring notes a later cohort correction). | Pass fixtures to both agent and judge; wire labeled ground truth into existing contains/regex/json-schema checks; per-KPI receipts with a confidence that is actually used; k trials with pass^k; hard-fail KPIs; fail the run on judge error; skeptic pass on the judge. |
| 3 | WRITE-LOCK primitive; BAR/COURT lens probes; `ygate.ts` RED state | Partial: lens gate and ledger built. WRITE-LOCK is declared as a primitive but not proven as an enforced gate over external tools. | A test that one-way tools (`promote_app`, `set_environment_variable`, bulk delete) fail without a lock declaration; an indirect-injection scenario pack on the customer's boards; a gateway-side audit sink; an annotation-vs-behavior test. |
| 4 | Accountant; outcome route; `receipt_outcome_resolver.py` | Built for ARCS's own receipts; calibration not claimed. No monday adapter. | Join the credits header and API analytics to receipts; fix outcome capture first; store run id, seed, judge-prompt hash and cost per run for drift. |
| 5 | Stdlib-only offline rules lane; model registry (`claude-models.ts`) | Partial: offline gates work. No local judge, PII canaries or residency KPI. | Judge adapter for any OpenAI-compatible `base_url`; judge-agreement check before trusting a small local judge; planted-identifier PII canaries. Fix the upstream fixture and model-name defects first. |
| 6 | `ygate.ts` FORK, PARADOX and DRIFT vocabulary; judge/gate separation; seeded RNG | Partial: vocabulary and separation exist. No intervals, k-trial harness or cross-family judging. | k trials with bootstrapped intervals; cross-family, position-swapped judge; cost and latency per receipt; emit FORK when intervals overlap rather than forcing a winner. |
| 7 | "Receipts or it didn't happen" template; verb chain with `--upstream`; packaged `arcs-verb-eval` | Built for ARCS merges and artifacts; unproven for customer feedback. | One receipt per FDE (forward-deployed engineer) engagement; promote a skill or suite only after a falsification pass; sign suites; feedback-record schema with provenance. |
| 8 | Golden Inchworm multi-pass; pipeline runner; WRITE-LOCK window in Kairos | Partial: sequencing built. Long-horizon scoring not built. Drift Sentinel not verified as running code. | Multi-turn sandbox episodes; checkpoint KPIs (asked when warranted, did not act before approval, resumed intact); pass^k. Re-verify ATP's approval runtime, since its tests are ungated. |

Recommended order (my sequencing, following the ML engineer's advice):
1. Fix fixture pass-through, clamping and fail-on-judge-error.
2. Add the per-run receipt: run id, seed, judge-prompt hash, model and cost.
3. Wire labeled ground-truth checks.
4. Add trace capture and the board-state diff.
5. Add hard-fail gates.
6. Add trials and intervals.

## 6) Risks and what NOT to claim

Do not claim:
- That Sensei is monday's evaluation standard, adopted, or maintained. It is dormant with no commits after 2026-03-22.
- That the tool count is exactly 90, or that the README tool list is current. 90 is a floor from a regex.
- That monday's hosted MCP server enforces or lacks any control. Its source is not public.
- That monday has no audit at all. Say instead that there is no self-service per-tool-call export. Security-event audit logs exist, and the OAuth route offers some tracking.
- That monday has a Hugging Face presence, or that its hosted AI supports open weights or bring-your-own models.
- That ARCS calibration is proven. Outcome capture is low, so present it as a discipline.
- That any code, test or eval was run. This is a static read, and counts are grep-based.
- That ATP is part of monday's official MCP stack, or that its injection defense is on by default. Provenance defaults to off and no injection benchmark is published.
- That the 13/13 skill-routing result shows task quality.

Interview-day risks:
- Presenting a gap list as criticism of named maintainers. Frame it as "what an eval needs next", not "what is broken".
- Overscoping. A take-home rewards one flaw found, reproduced and fixed, not the nine-item menu.
- Counts and issue states drift daily. Re-pull them before quoting.
- Confidence in the sources:
  - Verified items were read by one reader, and some skeptic claims also rest on a single read.
  - Search-summary claims about monday AI data retention and the FAQ are second-hand. Do not repeat them as fact.

## 7) What to read or test first

Read, in this order (about 90 minutes):
1. `monday-mcp-security-overview.md`, then `control-mcp-access-with-oauth-app.md`. These set what the customer owns.
2. `mondaycom/mcp` issues #501, #496 and #508, plus `tools-filtering.utils.ts` and `undo-action-tool.ts`. These are the concrete failure modes.
3. Sensei's `runner.ts`, `judge.ts`, `cli/src/commands/run.ts`, `adapters/openai-compat.ts` and `scorer.ts`. These contain every verified defect above.
4. `rate-limits.md` and `getting-started-with-the-models-api.md`, for the cost and quota facts.

Test first (each is a falsification of a claim that was only read, not run; about 2 hours):
1. Run one Sensei suite with the judge prompt logged. Confirm the fixtures are absent from it.
2. Point it at an `openai-compat` stub and confirm the fixtures never reach the agent. Then try `http`.
3. Return a judge score of 15 on a 10-point scale and a malformed JSON reply. Confirm there is no clamp and that the KPI becomes 0.
4. Try a `model:` key in agent YAML and see whether it is stripped.
5. Set `multi_judge: true` in YAML and confirm it takes effect, so you do not repeat the "unreachable" error.
6. If the take-home arrives as a repo or archive from a recruiter, scan it with the `sbom-payload-scan` skill before opening or installing anything.

Anything that fails to reproduce should be struck from the story before it is told.