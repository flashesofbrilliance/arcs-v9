# recoil-report — self-contained CLI package

Parameterized, reusable CLI for the ARCS **recoil-report** artifact pipeline: scaffold, validate,
compute cadence, and render a post-call recoil report. Extracted from the ad-hoc
`scripts/gen_recoil_artifact.py` into a clean, composable package.

Think of it as a microservice with a file-based contract: **JSON in → validated JSON / HTML out.**
The reasoning passes (Reverse Listening, Deep Recall) are done by a Claude Code session and produce
the JSON; this package owns everything deterministic around it.

## Deps

- **`python3` only** (>= 3.8). Pure standard library — `json`, `argparse`, `html`, `math`, `os`,
  `re`, `sys`. **No third-party packages, no install step, no network.**
- `bash` for the entrypoint (or call `recoil_report.py` directly with any `python3`).

## Layout (everything travels together)

```
tools/recoil-report/
├── recoil-report            # bash entrypoint (zero-dep runner; prints help with no args)
├── recoil_report.py         # the CLI (argparse; all logic; stdlib only)
├── schema/report.schema.json# bundled JSON Schema (draft-07 subset) — the contract
├── sample/sample-report.json# bundled scaffold template (also the `new` seed)
└── README.md                # this manifest
```

## Args (subcommands)

| Command | Args | Does |
|---|---|---|
| `segments` | `<minutes>` | Prints `max(3, round(sqrt(minutes)))` — the `recoil-modes-v1` cadence. |
| `validate` | `<file>` | Checks a report JSON against `schema/report.schema.json`. Exit 1 on failure. |
| `new` | `<slug>` `[--out PATH\|-]` `[--set k=v ...]` `[--force]` | Scaffolds a schema-valid report from the sample. Default out: `runtime/recoil/generated/<slug>.json`. |
| `render` | `<file>` `[--out PATH\|-]` `[--set k=v ...]` `[--no-validate]` | Renders a standalone, self-contained, `noindex` HTML page. Validates first unless `--no-validate`. |

## Passthrough params

`--set dotted.key=value` (repeatable) overrides any key at generation/render time. Values are
coerced: `true`/`false` → bool, anything that parses as JSON (`72`, `3.5`, `["a","b"]`) → that type,
otherwise kept as a string. Examples:

```bash
recoil-report new 2026-08-01-smith --set meta.callTitle="Smith x Zach" --set cover.nci=61
recoil-report render report.json --set cover.yGate=GREEN --set notice="" --out -
```

## Resources (bundled, read-only)

- `schema/report.schema.json` — the canonical contract. Permissive by design (extra keys allowed)
  but requires the load-bearing sections (`cover`, `loadBearingQuote`, `callWalk`, `signalThreads`,
  `scenarios`, `riskFlags`, `protocol`) so a dropped section or typo'd key is caught.
- `sample/sample-report.json` — a valid, annotated template; the seed for `new`.

## Runtime files (written by the tool, not part of the package)

- `runtime/recoil/generated/<slug>.json` — the report artifacts. Committed to git (real artifacts,
  not build output). The default landing zone for `new`.
- HTML from `render` goes wherever `--out` points (or stdout). Nothing is written implicitly.

## Shape note (why the schema is permissive)

The repo carries three drifted "recoil report" JSON shapes: the `delaney` shape
(`cover.badges` + `kinematics`, rendered by the legacy `scripts/gen_recoil_artifact.py`); the
`criley`/`shannon` richer shape (this package's canonical target); and the simpler
`RecoilReportData` TS interface used by `src/document/screens/RecoilReport.tsx`. The schema
canonicalizes on the richer shape but tolerates the badge variant, and the renderer degrades
gracefully across all three (falls back `headline`→`title`, `summary`→`body`, array-or-object
`scenarios`/`protocol`).

## Also renders via the app

The Next.js route `/recoil/[reportId]` reads the same `runtime/recoil/generated/<slug>.json` and
renders it through the design system. This package's `render` is the **standalone** path (publish /
share / offline); the route is the **in-app** path. Same JSON feeds both.

## Examples

```bash
# cadence for a 43-minute call
tools/recoil-report/recoil-report segments 43        # -> 7

# validate tonight's report
tools/recoil-report/recoil-report validate runtime/recoil/generated/2026-07-31-shannon.json

# scaffold a new one, pre-filling a couple of fields
tools/recoil-report/recoil-report new 2026-08-02-jones \
  --set meta.callTitle="Jones x Zach // Intro" --set meta.callDate=2026-08-02

# render to a shareable page
tools/recoil-report/recoil-report render runtime/recoil/generated/2026-07-31-shannon.json \
  --out /tmp/shannon-recoil.html
```

## Exit codes

`0` ok · `1` validation failed · `2` usage / IO error · `127` python3 missing.
