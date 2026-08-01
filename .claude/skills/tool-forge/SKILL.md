---
name: tool-forge
description: Forge a new self-contained CLI tool package (deps · args · passthrough params · resources · schema · README) in the canonical ARCS shape, or promote an existing one-off script instance→class. Use when a concrete artifact/script is about to be repeated and should become a composable, interoperable microservice rather than a copy-paste fork. The class-of-the-class behind tools/recoil-report/.
---

# /tool-forge — instance → class, as a repeatable act

> **Governing decision:** ADR-039 (Instance→Class Self-Promotion Build Loop).
> **Reference instance this class is lifted from:** `tools/recoil-report/` — the Shannon recoil
> report (one instance) promoted into a parameterized package (the class), Aug 2026.
> **Sibling exemplar:** `omakase-pipeline` (jeben→omakase→louisville).

## When to use

- A concrete artifact or ad-hoc script exists and a **second real (or imminent) use** has appeared —
  promote it instead of forking it (ADR-039 step 2).
- You want a new capability to be a **composable, interoperable microservice** from day one: a
  file-based contract, `data in → validated data / rendered output out`, callable from a shell, a
  workflow, or another tool.

**Do NOT use** to package genuinely one-off work. Promotion is a response to repetition, not a
substitute for judging whether repetition exists (ADR-039 honest edge). No second case → leave it an
instance.

## The fixed contract (what "self-contained package" means here)

Every forged tool has the **same six-part contract** — this uniformity is what makes them
interoperable:

1. **Deps** — `python3` stdlib only by default (repo rule: no new deps without asking). Declared
   explicitly in the README. Zero install, zero network.
2. **Args** — one entrypoint, subcommands via `argparse`, documented in a README table.
3. **Passthrough params** — `--set dotted.key=value` (repeatable), with type coercion
   (bool/JSON/number, else string). Lets any field be overridden at run time.
4. **Resources** — bundled, read-only, travel with the package: a machine-checkable `schema/` and an
   annotated `sample/` (which doubles as the `new` scaffold seed).
5. **Runtime files** — what the tool *writes*, named and located explicitly; never written
   implicitly. Distinct from bundled resources.
6. **README manifest** — declares all five above + exit codes, in one file.

## Package layout to reproduce

```
tools/<tool-name>/
├── <tool-name>              # bash entrypoint: zero-dep runner, prints help on no args,
│                            #   resolves its own dir, execs the python module. (copy from recoil-report)
├── <tool_name>.py           # the CLI: argparse subparsers, stdlib only, all logic here
├── schema/<thing>.schema.json  # the contract (draft-07 subset is enough; see recoil_report.py validator)
├── sample/sample-<thing>.json  # valid annotated template + `new` seed
└── README.md                # the six-part manifest
```

## Forge steps

1. **Name + locate.** `tools/<tool-name>/`. Verb-first, kebab-case (`recoil-report`, `precall-brief`).
2. **Copy the skeleton** from `tools/recoil-report/` — it is the canonical shape. Keep the bash
   entrypoint nearly verbatim (only the header comment + module name change). Reuse
   `recoil_report.py`'s pieces wholesale: the minimal stdlib JSON-Schema validator (`validate`),
   `coerce` + `apply_overrides` (the `--set` passthrough), and the `build_parser` pattern.
3. **Write the schema** for the tool's data. Permissive by design (extra keys allowed) but **require
   the load-bearing sections** so a dropped section or typo'd key is caught. Add `enum`s where a
   field has a fixed vocabulary (they become free input validation).
4. **Write the sample** — a valid, annotated instance. It is both the doc and the `new` seed; keep it
   schema-valid (the `new` command refuses to scaffold an invalid file).
5. **Define subcommands** to fit the tool, but default to this spine where it applies:
   `new` (scaffold from sample + `--set`), `validate` (schema-check), `render`/`build` (produce the
   output artifact, validating first unless `--no-validate`), and any deterministic compute the
   domain needs (recoil-report has `segments`). Standalone outputs must be **fully self-contained**
   (inline everything; zero external `http(s)`/`src=`/`<script>` refs).
6. **Write the README manifest** — the six-part contract, an args table, a passthrough section, a
   resources list, a runtime-files list, examples, exit codes.
7. **Prove it.** `chmod +x` the entrypoint + module. Run every subcommand against a real input:
   help-on-no-args, `validate` on a known-good and a known-bad file (must exit 1), `new --out -`,
   `render --out -`, and a `--set` override with a bad enum value (must refuse). Grep the rendered
   output for every section + for zero external references.
8. **Commit** `type(tools): <name> — self-contained CLI package ... [NCI:SKIP]`. Add one line to the
   relevant memory/index if the tool is durable.

## Exit-code convention (uniform across forged tools)

`0` ok · `1` validation failed · `2` usage/IO error · `127` interpreter missing.

## Anti-goals

- No third-party deps without asking (stdlib-only default).
- No hidden writes — every runtime file is named and explicit.
- No premature forging — promote on the second case, not the first (ADR-039).
- No over-strict schema — permissive-but-load-bearing beats brittle; tolerate sibling shapes and
  degrade gracefully rather than reject (see recoil-report's three-shape tolerance).
- No external references in standalone rendered output — self-contained means self-contained.
