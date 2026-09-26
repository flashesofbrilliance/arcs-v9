# cold-recon — cold-reconstruction incident report CLI

A self-contained, parameterized CLI for the ARCS **cold-reconstruction** post-mortem method:
given an incident (a git commit range, or a `--since/--until` time window), gather the durable
committed artifacts it touched, hand them to a **zero-transcript cold agent**, and audit what
that agent could and could not reconstruct.

Think of it as a microservice with a file-based contract: **git in → evidence pack → (cold
agent) → reconstruction JSON → leak map + report out.** Same division of labor as
`tools/recoil-report`: this package owns everything deterministic; the single non-deterministic
step (the reconstruction) is done by a fresh Claude Code session whose only context is the pack.

## Why cold

The participant is the worst narrator of their own incident: hindsight and the pull toward a
coherent story bend the account. A **memoryless reader of the contemporaneous committed record
cannot spin** — it can only report what the record shows. Coldness is a deliberate debiasing
control. It corrects narrator / hindsight bias **exactly to the degree the record was committed
contemporaneously**, which is why the leak map (below) is a second product, not a byproduct.

The security framing is the same mechanism turned outward: an unspinnable, artifact-grounded
forensic post-mortem is what incident review wants — the participant cannot retrofit the breach
story; the cold agent reports only what the logs / commits / receipts show. **Blue-team:** the
leak map is your logging/detection gap. **Red-team:** "is this incident reconstructable from the
evidence trail?" is a control test. Reconstructability-from-evidence becomes a measurable property.

## Honest constraints (carry these)

- **Not claimed patentable, not hyped.** Prior art is dense: event sourcing / WAL replay, git
  bisect, blameless post-mortems (Google SRE), blinded review, and retrieval-grounded
  cite-or-abstain LLM generation. The fresh part is the **framing** (coldness-as-debiasing-control
  + leak-map-as-observability-audit) — a good methodology, not a patent. Novelty is a legal call
  for an attorney with a prior-art search, not for this README.
- **It is only as good as your pre-commit / commit-as-you-go discipline.** A thread that dies
  uncommitted is invisible to a cold reader by construction. The method's payoff is highest when
  the receipt is a *gate before the action* (esp. irreversible / outbound), so the record is
  complete ex-ante and hindsight-immune by timestamp.
- **It corrects narrator/hindsight bias in the report, conditional on a contemporaneous commit.**
  It does not "solve hindsight bias." State the limit; do not overclaim it.

## Deps

- **`python3` only** (>= 3.8) — pure standard library. **No third-party packages, no install
  step, no network.**
- **`git`** for the gather stage.
- `bash` for the entrypoint (or call `cold_recon.py` directly with any `python3`).

## Layout (everything travels together)

```
tools/cold-recon/
├── cold-recon                          # bash entrypoint (zero-dep runner; prints help with no args)
├── cold_recon.py                       # the CLI (argparse; all logic; stdlib only)
├── schema/reconstruction.schema.json   # bundled JSON Schema (draft-07 subset) — the contract
├── prompts/cold-agent.md               # the zero-transcript prompt template (fills {{PACK}}/{{SCHEMA}})
├── sample/sample-reconstruction.json   # a valid, annotated reconstruction (schema exemplar)
└── README.md                           # this manifest
```

## The loop (subcommands)

| Command | Args | Does |
|---|---|---|
| `gather` | `<range>` or `--since/--until`, `--repo`, `--durable-glob`, `--all-files`, `--redact`, `--redact-file`, `--out` | **Deterministic, zero transcript.** git + tracked files only → an evidence pack JSON: commits (with trailers + NCI), merges, files touched, and the content of durable artifacts. `--redact` scrubs PII at the source (see air-gap below). |
| `prompt` | `<pack>` `--out` | Emits the exact cold-agent prompt (pack + coldness contract + schema embedded) to hand a fresh agent. |
| `validate` | `<reconstruction>` | Checks the agent's reconstruction against the bundled schema. Exit 1 on failure. |
| `leakmap` | `<pack> <reconstruction>` `--out` `--min-rate` | **Deterministic.** Diffs the reconstruction's evidence trail against the pack's anchors → `{reconstructed, partial, leaked}` + a reconstructability ratio. The observability audit. |
| `render` | `<reconstruction>` `--leakmap` `--set` `--redact` `--redact-file` `--no-validate` `--out` | **Deterministic.** Standalone `noindex` HTML incident report, per-section confidence bars + leak-map panel. Em-dash-0 **by construction**; `--redact` produces the public artifact. |
| `selftest` | (none) | Runs the frustration-gate proofs (em-dash + redaction, each fails-on-bad **and** passes-on-good). Exit 1 if any check fails. |

### Em-dash normalization is by construction (not a post-process)

`render` inherits em-dashes from commit subjects embedded in the pack / leak-map anchor
lists (e.g. a commit `NFTT — 'forge'...`). The repo's wrap gate
(`scripts/artifact_wrap_lint.py`) **fails any published HTML with an em-dash**, so the
render output is normalized on the way out — `—`/`–` → ` - `, `−` → `-` (surrounding
spaces collapsed). A rendered report clears the gate with em-dash 0 with no hand
post-process. (The pack from `gather` is faithful JSON data, not published HTML, so its
dashes are left intact — normalization is render-only.)

### In-tool redaction — the internal/external air-gap

PII scrubbing lives **in the tool**, not in a hand-written post-process redactor. The
**un-redacted** render is the internal record (private repo); the **redacted** render is
the public artifact. Supply redactions two ways (combinable, repeatable):

```bash
# inline PATTERN=REPLACEMENT (repeatable)
$T render recon.json --leakmap lm.json \
   --redact 'Robert Lycett=the recruiter' --redact 'Fun.xyz=the company' --out public.html

# or a JSON map { "pattern": "replacement", ... }
$T render recon.json --leakmap lm.json --redact-file redactions.json --out public.html
```

Redactions apply **case-insensitively, longest-pattern-first**, so
`zach.harris@gmail.com` is scrubbed before the shorter `Zach` can partially match inside
it. `gather --redact` / `--redact-file` scrub at the source, so the cold agent never sees
the PII. Verify the public artifact with the same grep used at publish
(`lycett|riskpod|fun\.xyz|robert|zach|@gmail`, case-insensitive) — it must come back clean.

### Coldness is enforced structurally

`gather` only ever touches **git history and tracked files**. It never reads a conversation
transcript, the (gitignored) `_STATE/handoff-progress.*` warm-narrator log, or a scratchpad. So a
reconstruction built from a pack is cold by construction — and any contemporaneous artifact that
was *never committed* (an untracked RCA, an uncommitted witness stub) is invisible to the cold
reader, which the leak map then surfaces as a serialization gap. That is the point, not a bug.

## The leak map is a second product

`leakmap` treats every durable artifact path and every commit sha in the pack as a claim-anchor,
then checks whether the reconstruction's evidence trail references it: `reconstructed` (cited),
`partial` (basename stem referenced, exact path not), or `leaked` (absent). A leaked anchor means
**the durable record did not carry enough for a cold reader to surface it** — a telemetry /
serialization gap or a thread that died uncommitted. `--min-rate` turns reconstructability into a
gate (exit 1 below threshold) for CI use.

## End-to-end example

```bash
T=tools/cold-recon/cold-recon

# 1. gather an incident (deterministic, zero transcript)
$T gather 'A~1..B' --repo /path/to/repo --out /tmp/pack.json
#    or a time window:
$T gather --since 2026-09-24 --until 2026-09-25 --repo /path/to/repo --out /tmp/pack.json

# 2. emit the cold-agent prompt, hand it to a FRESH session with no other context
$T prompt /tmp/pack.json --out /tmp/cold-agent-prompt.md
#    -> the agent returns reconstruction.json conforming to the schema

# 3. validate + audit
$T validate /tmp/reconstruction.json
$T leakmap /tmp/pack.json /tmp/reconstruction.json --out /tmp/leakmap.json --min-rate 0.6

# 4a. render the INTERNAL record (un-redacted, private repo)
$T render /tmp/reconstruction.json --leakmap /tmp/leakmap.json --out /tmp/report.html

# 4b. render the PUBLIC artifact (PII scrubbed to roles — the air-gap)
$T render /tmp/reconstruction.json --leakmap /tmp/leakmap.json \
   --redact-file /tmp/redactions.json --out /tmp/report.public.html
#    em-dash 0 by construction; clears scripts/artifact_wrap_lint.py

# (any time) run the gate proofs
$T selftest
```

## Exit codes

`0` ok · `1` validation / leak-threshold failed · `2` usage / IO error · `127` python3 missing.

## Provenance

Extracted from the 2026-09-24/25 Fun.xyz autosend post-mortem, where a cold general-purpose agent
reconstructed a whole session spine from committed artifacts alone and correctly flagged its own
gaps ("described != wired; could not confirm the deny is live"). That run is the proof of concept.
Public-good writeup: `good.arcs.care/blog/nftt/the-cold-reconstruction` (method + redacted run).
