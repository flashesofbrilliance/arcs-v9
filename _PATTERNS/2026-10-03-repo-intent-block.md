# Repo intent block (pattern, 2026-10-03)

**Problem.** Sessions in Claude Code, Hermes, and cloud containers open a repo and load whatever
its CLAUDE.md says. Across the 24-repo fleet (audit 2026-10-03): no repo stated its intent; three
root `SPEC.md` files were three different kinds of document (germinate: normative; arcs-care:
historical, for a site no domain serves; refraction-engine: ROM candidate); two repos still named a
May 2026 arc as "active". The missing piece is not two more files per repo. It is a short,
dated statement of *why this repo exists*, in the file every harness reads.

**Decision.** One fenced block at the top of `AGENTS.md` (the cross-harness file; Codex, Cursor and
others read it). `CLAUDE.md` imports it with `@AGENTS.md`, since Claude Code auto-loads CLAUDE.md
only. No separate `intent.md`: a new file is one more surface to drift. `SPEC.md` only where there
is a contract other code must conform to (germinate is the model: RFC 2119 text + schemas +
fixtures), and every root `SPEC.md` gets a declared standing.

**Gate.** `tools/intent_lint.py <repo> [...]` (canonical copy in the public `flashesofbrilliance/arcs-skills`, run in every repo by its reusable `intent-lint` workflow: push, PR, and weekly) fails on: no block, an empty field, an unknown
status, a verified date older than 90 days or with no "how", an unvouched root `SPEC.md`, or a
CLAUDE.md that does not import AGENTS.md. Archived repos skip the age check. `--self-test` proves fail-on-bad and pass-on-good.

## Template (copy verbatim, fill every field)

```markdown
<!-- intent:begin -->
## Intent
- **Why:** one or two sentences: the job this repo does, for whom.
- **Done looks like:** the observable state at which this repo needs no more work (or "n/a: dormant").
- **Not this:** what a session might wrongly assume this repo is or does.
- **Status:** live | active | dormant | archived (then a short reason)
- **Last verified:** YYYY-MM-DD (how: the command, tool call, or read that confirmed Status)
- **Spec:** none | SPEC.md (normative | historical | candidate, plus one clause)
<!-- intent:end -->
```

**Status vocabulary.** `live`: serves users now (verify against Vercel/npm, not memory).
`active`: being built, not yet serving. `dormant`: kept, not worked on, may revive.
`archived`: done; read-only.

**Rule of thumb.** If you cannot fill `Last verified` with a real check, write what you could
verify and put the rest in `Why`/`Status` as "unconfirmed". Never date a guess.

## Monorepo rule (Zach, 2026-10-03)

**arcs-v9 is the canonical monorepo.** Private ARCS content belongs here; a dormant repo's content
is folded in under `runtime/` with an `IMPORTED-FROM.md` naming the source repo and commit, and the
source repo's intent block flips to `archived` once a `diff -rq` shows nothing is left behind.
Exception: a distributable package with its own public identity (npm, Homebrew, a plugin
marketplace) keeps its own repo, because consumers install from it: germinate, rosetta-shell,
arcs-skills and its plugin repos.

Done so far: `runtime/specs/field-os/specs/` (arcs-field-os, the only copy of the ATG spec) and
`runtime/memory-export/` (arcs-memory-export). arcs-memory-pipeline is a de-identified extraction,
not a twin; publishing or archiving it is a separate decision.
