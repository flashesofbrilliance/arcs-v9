# arcs-verb-eval

Five small evals, one per stage of a research-to-message arc. Each stage produces an artifact, the artifact goes through a gate, and the gate assigns it a fate. If a stage doesn't produce anything, it happened only in conversation. If an artifact skips its gate, it's just decoration.

| Tool | Checks | Fates |
|---|---|---|
| **Analysis by ARCS** | a raw teardown: every claim cites a checkable source | sourced / unsourced |
| **Assessment by ARCS** | claim against record: each claim gets a verdict and a severity | pass / fail (claims: verified / gap / unresolved) |
| **Evaluation by ARCS** | a gauntlet of named lenses, at least one of which dissents | pass / conditional pass / fail |
| **Synthesis by ARCS** | the finished surface: no new claims, conditions honored, render matches verdict | ship / hold |
| **Recapitulation by ARCS** | the draft note: still a draft, receipts filed, not sycophantic | parked / blocked |

Each tool has two halves:

- **Mechanical.** Hard gates. Any failure exits 1.
- **Judgment.** A 0 to 2 rubric that a human or model fills in. The tool never scores judgment itself.

Each stage reads the previous stage's JSON output through `--upstream`. That means "verified must have been sourced", "no new claims" and "the note only says what the surface says" are all checked mechanically, not taken on trust.

Everything uses the Python standard library only, with nothing to install. JSON config works on any Python 3; TOML config needs Python 3.11 or later.

**New here? Read [docs/HOWTO.md](docs/HOWTO.md) first.** Copy-paste Shell, Python, GitHub Actions and pre-commit snippets for every step are in [docs/SNIPPETS.md](docs/SNIPPETS.md).

## Quick start

```bash
./arcs-verb-eval --self-test                       # proves every gate passes good input AND fails bad input
./arcs-verb-eval pipeline --config sample/arc.json # runs the whole sample arc, writing prints to sample/prints/
```

## One verb at a time

```bash
./arcs-verb-eval analysis     teardown.html --ledger evidence.jsonl --out p/analysis.json
./arcs-verb-eval assessment   report.html   --upstream p/analysis.json   --out p/assessment.json
./arcs-verb-eval evaluation   gauntlet.json --upstream p/assessment.json --out p/evaluation.json
./arcs-verb-eval synthesis    surface.html  --upstream p/evaluation.json --out p/synthesis.json
./arcs-verb-eval recapitulation note.md     --upstream p/synthesis.json
```

Each verb also has its own entry point in `bin/`, for example `bin/analysis-by-arcs teardown.html`.

## Parameters, pass-through, config, runtime

Settings are applied in this order, lowest to highest precedence:

1. built-in defaults
2. the config file (`--config` or `$ARCS_VERB_EVAL_CONFIG`)
3. environment variables (`ARCS_VERB_EVAL_<KEY>` applies to all verbs; `ARCS_VERB_EVAL_<VERB>__<KEY>` applies to one)
4. `--set key=value` or `--set verb.key=value`

| Knob | Where | Effect |
|---|---|---|
| `min_lenses` | evaluation | Minimum number of lenses in the gauntlet (default 4) |
| `ledger` | analysis | Every `data-src` must appear in this evidence.jsonl |
| `public` | synthesis | Waives the noindex gate |
| `slop` / `slop_lint` / `slop_args` | synthesis | Turns the slop-lint layer on or off, points it at a different linter, or passes arguments through to it (`--slop-arg`) |
| `skip_gates` / `--skip-gate ID` | any | Waives a gate. It is still recorded as SKIPPED in the output, never silently dropped |
| `PYTHON=` | runner | Chooses the interpreter (the runtime environment) |

`arcs-verb-eval env` prints the resolved runtime, dependencies (none from third parties), source paths and the effective options for every verb.

## Artifact conventions

- **HTML claims** use the `teardown_eval.py` claim-span convention: `<span class="claim" data-id="c1" data-src="url1,url2" data-stakes="high" data-verdict="gap" data-severity="high" data-render="degraded">`.
- **Assessment summary:** the assessment carries `data-summary="verified/gap/unresolved"` counts, which must match its rows.
- **Gauntlet:** a JSON file of the form `{"lenses": [{"name", "result": "pass|fail|dissent", "reason"}], "verdict", "conditions": [{"id", "claim", "action": "drop|degrade"}]}`.
- **Note:** front matter of `status: DRAFT`, `ex_ante: <path>` and `gauntlet: <path>`, with claims cited inline as `[claim:c1]`.

Working examples of all of these are in `sample/`.

## Anti-sycophancy

This is the Operator 25 Shavasana check: it counts agreement markers against dissent markers. It returns RETURN when there are 5 or more agreements and no dissent, and THIN when the ratio is above 4. It is report-only at Analysis, Assessment and Synthesis, and blocks at Evaluation and Recapitulation, where agreement pressure costs the most. The Evaluation gate also has a **dissent floor**: if no lens dissented, it wasn't a real gauntlet.

## Data in and out

- `ingest` reads a notebook (`.ipynb`) or a claims table (`.csv`/`.jsonl`) and writes the step inputs, plus deliberately broken copies with `--mutate N`.
- `export` writes your saved step outputs as `jsonl`, `csv`, `md`, `junit` or `receipt`.

## Surfaces

- CLI (`arcs-verb-eval`, plus the per-verb entry points in `bin/`)
- Python module (`from arcs_verb_eval import evaluate`)
- HTTP (`arcs-verb-eval serve --port 8787`, then `POST /eval/<verb>` with the body `{"artifact": "...", "upstream": {...}}`)

Exit codes: 0 means every gate passed, 1 means a gate failed, 2 means a usage error.
