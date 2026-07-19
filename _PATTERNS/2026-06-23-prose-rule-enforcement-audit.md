# Prose-Rule Enforcement Audit (Task #5) — 2026-06-23

> **UPDATE 2026-07-19 (token-efficiency audit follow-up):** Finding #1's live violations have since
> been **remediated**, not disproven — the audit was accurate on 2026-06-23. As of today:
> `src/document/patterns/ScenarioStack.tsx` (the `className="fadein"` site) no longer exists, and
> `src/app/layout.tsx` now carries the **single sanctioned** `className` — the next/font CSS-variable
> classes on `<html>` (documented inline, AGENTS.md Gotcha #2 / SKILL.md Domain #4), not the Tailwind
> utility classes it flagged. A repo-wide grep now returns exactly **1** `className` in `src/`, and it
> is allowed. The *enforcement* gap (no ESLint/CI rule forbids `className`) is still real; the
> *instances* are gone.

> Scope: `SKILL.md` only, per the execution plan's narrowed scope decision
> (`_PATTERNS/2026-06-23-s-tier-execution-plan.md` #5). Extension to `AGENTS.md`/
> `CLAUDE.md`/`WORLD.md` is *not* done exhaustively here — two findings below
> (Tailwind, the commit-message format) cross-reference those files because the
> SKILL.md pass surfaced them as the same rule restated, not because the other
> three files were independently audited end-to-end. That generalization call is
> recorded inline at each finding, not assumed up front.

## Method

For every "must"/"must not"/"always"/"never"/hard-constraint sentence in
`SKILL.md`, three checks, in order:
1. Is there a mechanism today that would catch a violation? (lint/CI/test/hook)
2. If not, is the rule already broken in the live repo? (grep, not assumption)
3. If not broken, how cheap would a mechanism be to add?

Evidence is cited per rule — this is the same discipline the governance roadmap
names as missing elsewhere (`ALTITUDE_MISMATCH`'s own caveat: don't opine before
verifying, even when the premise feels obviously right).

---

## Rule-by-rule findings

### 1. "Inline styles only — no CSS files, no Tailwind, no className" (Skill Domain #4)

**Classification: DISCIPLINE-ONLY — and already broken.**

Evidence:
- `package.json` has `tailwindcss: ^4` and `@tailwindcss/postcss: ^4` as real
  dependencies (not devDependencies-only cruft — `tailwindcss` is a peer of
  `postcss.config.mjs`, which exists and wires `@tailwindcss/postcss` as its only
  plugin).
- `src/app/layout.tsx:48-51` uses `className` with literal Tailwind utility
  classes: `className="min-h-full flex flex-col bg-obsidian-950 text-ivory-100
  antialiased"`.
- `src/document/patterns/ScenarioStack.tsx:38` also has a stray `className="fadein"`
  alongside an inline `style={}` object on the same element — a hybrid, not pure
  inline.
- `git log --oneline --all -- postcss.config.mjs` shows exactly one commit:
  `"Day 1 scaffold: Next.js 16 + Prisma 7 + Auth.js v5 magic link"`. This violation
  has existed since the literal first commit of the repo and was never caught or
  removed — the rule was written into `AGENTS.md`/`CLAUDE.md`/`SKILL.md`
  *after* the scaffold already contradicted it, and nothing has reconciled the two
  since.
- No ESLint rule, no CI step, no test forbids `className` or Tailwind imports.
  `eslint.config.mjs` only loads `eslint-config-next/core-web-vitals` +
  `eslint-config-next/typescript` — neither enforces a no-Tailwind policy.

This is the highest-severity finding in the audit: not an unenforced rule, but a
rule the codebase has been silently violating at its root layout since inception.
Three files state it (`CLAUDE.md`, `AGENTS.md`, `SKILL.md`) — worth generalizing
across all three on this one point, since it's the same sentence repeated
verbatim, not three independent claims.

**Recommendation:** Either (a) remove the Day-1 Tailwind scaffold remnants
(`tailwind.config`-equivalent via `postcss.config.mjs`, the two deps, the
`className` usages) to make the rule true again, or (b) if Tailwind is now
intentionally in use for `layout.tsx`/global shell only, narrow the rule's wording
to say so explicitly instead of stating an absolute that's been false for the
life of the project. Either fix is cheap; the dangerous third option is leaving
the rule's text unchanged while reality diverges further.

---

### 2. "No new dependencies without asking" (Skill Domain #4; mirrored in `AGENTS.md`/`CLAUDE.md`)

**Classification: DISCIPLINE-ONLY.**

Evidence:
- No `package.json` diff gate exists in CI (`ci.yml` runs lint/type-check/build
  only — no dependency-diff check, no `npm ls` allowlist, no Renovate/Dependabot
  config found).
- `git log -p -- package.json` shows the dependency list grew from a Day-1 set to
  the current 20 deps / 11 devDeps with no commit message or PR referencing "asked
  Zach" — consistent with the rule being followed via in-session conversation
  (invisible to git), but there is no artifact that would catch a future violation
  if a session simply forgot to ask.
- Tailwind's addition (see finding #1) is itself evidence this rule and the
  no-Tailwind rule are the same failure event — a dependency was added that
  directly contradicts a separate hard rule, and nothing caught either.

**Recommendation:** Cheaply enforceable as a *soft* check, not a hard gate (since
"asking" is a conversational act CI can't verify): add a CI step that fails if
`package.json` dependencies changed in a PR without a corresponding line in the
PR body/commit message (e.g., grep commit messages in the PR for `deps:` or
`NCI:`). This only catches the silent case, not a bad-faith one — still worth
having given finding #1's evidence that the unenforced version already failed.

---

### 3. "`npx next build` for typecheck (not `tsc --noEmit`)" — stated in `CLAUDE.md`/`AGENTS.md`, **absent from `SKILL.md`**

**Classification: Not a SKILL.md rule at all — flagged because checking it surfaced a contradiction worth recording.**

Evidence:
- `SKILL.md` never states this rule. `CLAUDE.md`'s "Token-saving rules" section
  does: *"`npx next build` for typecheck (not `tsc --noEmit` — false positives on
  baseUrl)."*
- `package.json`'s own `scripts.type-check` is literally `"tsc --noEmit"` — the
  exact command the rule says not to use for typecheck — and **CI's hard gate
  calls it directly**: `.github/workflows/ci.yml` step `"Type-check"` runs
  `npm run type-check`, i.e. `tsc --noEmit`, as one of the two non-advisory gates
  blocking merge.

This is a rule that is not just unenforced — the enforcement mechanism that
exists (CI) actively does the thing the rule says not to do. Worth surfacing to
`CLAUDE.md`/`AGENTS.md` maintainers even though it's outside today's SKILL.md
scope, because it's the sharpest instance found of "documented rule contradicted
by the actual enforced check," not merely lacking one.

**Recommendation:** Either change `ci.yml`'s type-check step to `npx next build`
(absorbing it into the existing build step, since build already typechecks) and
delete the redundant `tsc --noEmit` script, or correct the prose rule if `tsc
--noEmit` turns out to be fine for CI's pinned TS/baseUrl config and the original
caution was a local-environment-specific issue. Don't leave the contradiction
written down on both sides.

---

### 4. Spec front-matter: "version, status (DRAFT/REVIEW/ROM), depends-on, blocks" (Skill Domain #1)

**Classification: DISCIPLINE-ONLY, and partially already broken.**

Evidence: checked all `runtime/specs/*.md` files for the four required
front-matter fields.
- `runtime/specs/dewy-receipt-schema-v1.md` — has all four (`version: "0.1.0"`,
  `status: REVIEW`, `depends-on:`, `blocks:`). Compliant.
- `runtime/specs/ARCS-Vector-Collision-Engine-v2-delta.md` — has `version: 2.0`
  and `status: Production-Grade Specification` (not one of the three allowed
  status values DRAFT/REVIEW/ROM — a silent enum drift of its own), no
  `depends-on`/`blocks`.
- `runtime/specs/README.md` — has `version: 1.0.0` only.
- `runtime/specs/ARCS-Vector-Collision-Engine-v1.md`,
  `ARCS-v9-ROM.md`, `ARCS_Question_Compass_Signal_Receipts_Spec.md`,
  `arcs-v9-consolidated-design-v1.md`, `arcs-v9-engineering-spec-v1.md` — **none**
  have any of the four fields.

5 of 8 spec files in `runtime/specs/` are non-compliant with a rule stated as a
required schema, including one file using a `status` value outside the three
named in the rule. No mechanism checks this — no JSON-Schema validation of
front-matter, no CI step, no lint rule for Markdown front-matter shape.

**Recommendation:** Cheaply enforceable: a 20-line script (`scripts/check-spec-frontmatter.py`,
consistent with the stdlib-only convention already used elsewhere) that parses
front-matter from every file in `runtime/specs/*.md` and fails if `version`/
`status`/`depends-on`/`blocks` are missing or `status` isn't one of
DRAFT/REVIEW/ROM. Could run as an advisory (not hard-gating) CI step, mirroring
the existing advisory-lint pattern in `ci.yml`.

---

### 5. Python scan suite — "Zero external dependencies (Python 3.8+ stdlib only)" (Skill Domain #5)

**Classification: Already broken, not generically enforceable cheaply (see below).**

Evidence: grepped every `scripts/*scan*.py` import block.
- `scripts/network_scan.py:17` — `import anthropic` (Anthropic Python SDK, a real
  external dependency, contradicts "zero external dependencies" directly).
- `scripts/archetype_scan.py:16-17` — `import plotly.graph_objects as go`,
  `import networkx as nx` (both external, both heavyweight).
- `scripts/calendar_scan.py`, `scripts/listening_scan.py`, `scripts/reader_scan.py`,
  `scripts/forensic_scan.py`, `scripts/network_scan_full.py` — stdlib-only,
  compliant.

2 of 7 scanner files violate the rule outright; this is not hypothetical risk, it
is present-tense violation in committed code.

**Recommendation:** Cheaply enforceable in principle (`pip-licenses`/AST-walk a
script's imports against the Python 3.8 stdlib module list, fail if anything
else appears), but given two files are *already* non-compliant, adding the check
now would immediately break CI on existing code — sequence the fix (rewrite or
relabel the two offending scanners) before adding the gate, not the other way.
Flagging as discipline-only for *today's* state; cheaply-enforceable only after
the existing violations are resolved or the rule is scoped to exclude
`network_scan.py`/`archetype_scan.py` explicitly (e.g., a documented "visualization
scanners are exempt" carve-out, since plotly/networkx are for graph rendering,
not the core gauntlet).

---

### 6. "Every new scanner must implement the gauntlet interface: `strand_a`, `strand_b`, `helix_composite`, `l2_bayesian`, `triune_classify`, `run_gauntlet`" (Skill Domain #5)

**Classification: Already broken — 0 of 7 scanners comply.**

Evidence: grepped every file in `scripts/*scan*.py` for `def strand_a`,
`def strand_b`, `def helix_composite`, `def l2_bayesian`, `def triune_classify`,
`def run_gauntlet`. Zero matches across `calendar_scan.py`, `listening_scan.py`,
`reader_scan.py`, `archetype_scan.py`, `forensic_scan.py`, `network_scan.py`,
`network_scan_full.py`. Only `scripts/arcs_core.py` (the shared kernel itself, not
a scanner) and `scripts/network_scan_full.py` had any hits when checked broadly
for the underlying gauntlet machinery, and `network_scan_full.py`'s hits did not
match the exact six function names — manual spot-check confirms the interface
functions live in `arcs_core.py` as shared/inherited logic, and individual
scanners call into the kernel rather than each defining their own
`strand_a`/`run_gauntlet`. So the rule as literally written ("every new scanner
must implement") describes an interface that doesn't exist as scanner-level
methods anywhere — either the architecture changed (composition over the literal
interface) without the rule being updated, or the rule was aspirational from the
start and never implemented as stated.

This is the single clearest case in the audit of a rule whose plain reading does
not match the actual architecture, with zero enforcement and zero compliance —
worth flagging above the others because it's not "nobody checks, but it mostly
holds" (the Tailwind/className case) — it's "the rule as written has never been
true."

**Recommendation:** Don't build a checker for an interface that may be
intentionally obsolete. First confirm with whoever owns `scripts/arcs_core.py`'s
architecture whether "implements the gauntlet interface" now means "calls into
`arcs_core`'s shared implementation" (composition) rather than "defines these six
methods itself" (literal). Rewrite the SKILL.md rule to match whichever is true,
*then* decide if a cheap AST-based "does this scanner call `arcs_core.run_gauntlet`"
check is worth adding.

---

### 7. Commit message format: `type(scope): imperative [NCI:XX]` + Co-Authored-By trailer — **stated in `AGENTS.md`/`CLAUDE.md`, NOT in `SKILL.md`**

**Classification: Checked because the execution plan predicted this would surface as "exhibit A" — prediction does NOT hold as stated, with a sharper finding underneath.**

The execution plan (`_PATTERNS/2026-06-23-s-tier-execution-plan.md` #5) predicted
the SKILL.md audit would surface the commit-format rule as the clearest unenforced
convention. Verified directly rather than taken on faith, per the task's own
instruction:

- **The commit-format rule does not appear in `SKILL.md` at all.** It lives in
  `AGENTS.md` ("Gotchas" #7: `type(scope): imperative [NCI:XX]` + Co-Authored-By)
  and the user's global `~/.claude/CLAUDE.md`. Since this audit is scoped to
  SKILL.md, this rule is technically out of scope — the prediction assumed it
  would be *in* SKILL.md and it isn't.
- Checked anyway, since the entanglement claim (`#5 ↔ #6`) is explicitly about
  this rule regardless of which file states it, and the task brief asked to
  verify the prediction, not just record whether the literal text exists in
  SKILL.md.
- `git log --oneline -30` confirms the rule **is** followed in practice with high
  consistency — every recent commit matches `type(scope): description [NCI:XX]`
  or `[NCI:SKIP]`/`[NCI:CANONICAL]`/`[RC-OPS-001]` tag variants. No raw "wip" or
  unstructured commit messages found in the sample.
- **No mechanism enforces it** — no `commit-msg` git hook exists
  (`.git/hooks/commit-msg` absent, confirmed via `ls`), no CI step validates
  commit message shape, no `commitlint` config anywhere in the repo.
- So the prediction's *spirit* holds (this is a real unenforced convention,
  exhibit-A-shaped) but its *letter* doesn't (it's not a SKILL.md finding, and the
  rule is currently being followed faithfully by discipline alone, not
  "silently rotting" yet — there's no evidence of drift in the sample checked).

**Sharper finding, found instead:** SKILL.md's *own* internal token-budget
contract self-contradicts. Skill Domain #7 states *"Token budget contract: ...
`/handoff-pickup` reads at most 3 files"* — but `.claude/commands/handoff-pickup.md`
itself, the file that contract is describing, says *"Reads at most 5 files"* two
lines later in its own body (lines 40-44 list `_STATE/snapshot.json`,
`.claude/arcs-session-state.md`, plus 3 more). This is the same shape as the
BAR/KKL canon collision from earlier this session — two documents disagreeing on
a number, found only by reading both rather than trusting either's restatement —
except this time it's SKILL.md disagreeing with the very command file it
describes, not two peer canon files. Genuinely "exhibit A" in spirit: a rule
restated in two places, already silently diverged, caught only by direct
cross-check.

**Recommendation:** (1) Decide which number is correct (5, matching the actual
`handoff-pickup.md` body, or 3, matching SKILL.md's summary) and fix the other.
(2) Separately, the actual commit-format rule (`AGENTS.md`) is cheaply
enforceable: a `commit-msg` hook or CI step with a regex
(`^(feat|fix|docs|chore|refactor|perf|test)\([a-z-]+\): .+\[NCI:`) would catch
format drift before it compounds — currently zero mechanism exists for a
convention that, per task #6 in the roadmap, is about to gain even more
structure (ADR-Ref/Y-Gate trailers) with still nothing checking the base format
it builds on.

---

### 8. HOLD/REJECT validation gate — "every invocation/input passes through a three-state gate" (Skill Domain #6 + dedicated section)

**Classification: DISCIPLINE-ONLY, and not actually implemented anywhere in code.**

Evidence:
- Grepped `src/` and `scripts/` for `validation_state`, `blocking_question`,
  `ARCS-INV-` (the receipt ID prefix the spec defines) — zero matches anywhere in
  the codebase.
- `src/app/api/compass/route.ts` (the actual L0-L5 pipeline entry point this gate
  is supposed to sit in front of) has no PASS/HOLD/REJECT gate logic. Its only
  PASS-adjacent string is `reasoning.court`'s verdict field
  (`"PASS"|"TENSION"|"BLOCK"`), which is a different three-state enum, for a
  different purpose (Court reasoning verdicts inside the Claude-generated output,
  not input validation before the pipeline runs), and the two are easy to
  conflate on a skim.

This rule describes a complete validation layer with a receipt schema, gate
order, and trigger taxonomy, none of which exists as code. It's the most
elaborately specified rule in SKILL.md (two full sections) and has zero footprint
in the implementation. This is a different failure mode from the others above
(a *spec describing unbuilt work*, the same shape as the Tribune Intelligence
Layer's "fully specced, entirely unbuilt" status noted in the execution plan,
rather than a *behavioral rule nobody checks*) — worth distinguishing from true
discipline-only rules, since there's no behavior to maintain discipline over yet.

**Recommendation:** Not a "build a checker" item — there's nothing to check
against. Recommend SKILL.md mark this section `STATUS: SPECCED, NOT IMPLEMENTED`
explicitly (the same convention `runtime/specs/*.md` front-matter already uses
for DRAFT/REVIEW/ROM) so a future reader doesn't mistake the detailed spec for a
description of running code — that mistake is exactly the
described-as-settled-vs-actually-built pattern this session's roadmap already
named as a recurring pathogen (`v9 ROM Candidates` in `RECOIL-PROTOCOL.pdf`).

---

## Summary

| # | Rule | Classification |
|---|---|---|
| 1 | Inline styles only / no Tailwind / no className | Discipline-only — **already broken** (Day-1 scaffold) |
| 2 | No new deps without asking | Discipline-only |
| 3 | `npx next build` not `tsc --noEmit` for typecheck | (out of SKILL.md scope) — CI's actual gate **does the forbidden thing** |
| 4 | Spec front-matter (version/status/depends-on/blocks) | Discipline-only — 5/8 files non-compliant |
| 5 | Python scan suite stdlib-only | Discipline-only — **already broken** (2/7 scanners) |
| 6 | Scanner gauntlet interface (6 named methods) | Discipline-only — **0/7 scanners comply as literally written**; likely an architecture/rule mismatch, not pure neglect |
| 7 | Commit message format | (out of SKILL.md scope) — followed in practice, zero mechanism; real finding is SKILL.md's own 5-vs-3-files self-contradiction |
| 8 | HOLD/REJECT validation gate | Discipline-only — **fully specced, zero implementation** (different failure shape: nothing built yet, not behavior drifting) |

**Count (rules actually in SKILL.md's stated scope, #1/#2/#4/#5/#6/#8 — six rules):**
- **Enforced: 0**
- **Cheaply enforceable: 2** (#4 front-matter checker; #5's stdlib check, once existing violations are resolved first)
- **Discipline-only: 4** (#1, #2, #6, #8 — though #1 and #6 are also already-broken, and #8 is unbuilt rather than undisciplined)

Two additional out-of-scope findings surfaced and are recorded above because the
task brief asked to verify, not assume, the entanglement prediction with #6: the
`tsc --noEmit` CI contradiction (#3) and SKILL.md's internal 5-vs-3-files
self-contradiction (#7). Neither is counted in the six above since neither rule
exists in SKILL.md itself.

**Zero of the six in-scope SKILL.md rules have an actual enforcement mechanism today.**

## Single highest-value discipline-only rule to fix first

**Rule #1 — "Inline styles only — no Tailwind, no className."** Not because it's
the most elaborate (#8 is) or the most architecturally confused (#6 is), but
because it is simultaneously: (a) stated in **three separate files** as a hard
constitutional constraint, (b) **already violated at the application root**
(`layout.tsx`, the one file every page passes through), (c) **violated since the
literal first commit**, meaning every session since has either not noticed or
noticed and not fixed it, and (d) cheap to either fix or formally narrow — this
is not a six-method interface redesign or an unbuilt validation layer, it's
removing two deps and rewriting one `className` string, or alternatively just
correcting three files' prose to admit Tailwind is in scoped use. Left alone,
this is the rule most likely to be cited confidently by a future session ("no
Tailwind, per CLAUDE.md") while writing code in a part of the repo that already
contradicts that exact claim — the precise shape of `TOPOLOGY_INVERSION` from
this session's own pathogen catalog, applied to a style rule instead of a domain
map.
