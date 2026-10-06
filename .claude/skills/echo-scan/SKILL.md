---
name: echo-scan
description: Turn an outside field of research (a paper, a viral post, a screenshot, a domain name like "stopped light" or "mycorrhizal networks") into ARCS design rules - claim-check the source, survey the state of the art plus adjacent and orthogonal work, map isomorphisms to real ARCS files labelled MECHANISM or METAPHOR, rank inventions each with a pre-registered kill condition, and queue the top ones in the induced backlog. The working form of ROM primitive 5 (Orthogonal Echo Detector). Use whenever Zach shares an article, LinkedIn post, paper or screenshot and asks what ARCS can learn, steal, adapt or invent from it, asks for "isomorphisms", "cross-domain echoes", "state of the art adjacent to this", or "what's the analog in ARCS", even if he never says "scan". Also use `/echo-scan claim-check <source>` alone to verify an outside post or article before trusting it.
---

# /echo-scan: an outside field, read as an ARCS design manual

ROM primitive 5 says ARCS surfaces cross-domain kinematic isomorphisms. Until this skill there
was no procedure for doing it, so each attempt re-derived the method and the failure modes
(trusting the source, pattern-matching on vocabulary, inventing ideas nobody can kill). The
reference run is 2026-10-03: a LinkedIn post on Lene Hau's stopped light became
`_PATTERNS/2026-10-03-stopped-light-quantum-memory-isomorphisms.md`, three backlog rows, an
artifact page, and an NFTT draft. Read that note once if you want to see a finished output.

## Modes

| Invocation | Runs |
|---|---|
| `/echo-scan <source or field>` | all six stages |
| `/echo-scan claim-check <source>` | stage 1 only, the nested claim-check module |
| `/echo-scan --no-queue <source>` | stages 1 to 5, writes the note, skips backlog rows |

## The six stages

Each stage prints an artifact. A stage that leaves nothing behind happened only in
conversation and will be re-derived at full cost (WORLD.md, the print schedule).

### 1. Claim-check the source (nested module)
Read `references/claim-check.md` and run it. It is self-contained: inputs, verdict scale,
arithmetic checks, provenance, stop rule. Its output table opens the note. Do this before any
research, because a survey built on an unverified source inherits its errors and its missing
co-authors. If the module's stop rule fires (the core claim is false), say so and stop unless
Zach wants the field scanned anyway.

### 2. Survey the field
Search the core results first, then the frontier, then two rings out:
- **Core:** the original papers the source cites, with venue, year, and authors.
- **State of the art:** current records on every axis the field measures. Fields score
  themselves on several axes at once; collect the vector, never a single "best".
- **Adjacent:** same physics or mechanism, different application.
- **Orthogonal:** a different field that solves the same structural problem.
Prefer primary sources (journals, arXiv, lab pages) over news. Keep every URL for the source
list. Parallel `WebSearch` calls in one message are fine and fast.

### 3. Ground in the repo before mapping
List the ARCS surfaces the field might touch, by real path: ROM primitives (CLAUDE.md), the
operators table (AGENTS.md), seeds and ADR candidates (`_SEEDS/`), open backlog
(`_QUEUE/induced-backlog.jsonl`), known gaps (for example outcome capture, 2/247). An
isomorphism with no real file on the ARCS side is a metaphor at best.

Read-only means read-only. Never call a counter or allocator to "see" a number:
`python3 scripts/oracle.py peek <ns>` or `next <ns> --dry-run` look; `next <ns>` allocates and
stamps the pulse. If any tool writes when you meant to look, revert the write and any side
effect (heartbeats included) before going on, and record it in the note's session log.

### 4. Map isomorphisms, labelled
Read `references/isomorphism-ledger.md` for the row schema and the labelling test. Every row is
MECHANISM (same rule, a design lesson transfers) or METAPHOR (a lens, nothing is built on it).
Label honestly; a metaphor dressed as a mechanism is the failure this skill exists to prevent.
Aim for breadth first (10 to 15 rows), then cut rows that are only shared vocabulary.

### 5. Rank inventions with kill conditions
From the MECHANISM rows only, derive 3 to 5 inventions. Each one carries:
- what it is, in one or two sentences, attached to a real ARCS file or gap;
- why it is new (what ARCS lacks today);
- a **kill condition written now**: an observable result that withdraws the idea, runnable by
  someone other than the author (the `falsifiable-test` skill's standard). No kill condition,
  no invention.
Rank by evidence per effort, not by how good it sounds.

Close the note with a short "what not to take" section: no field vocabulary in product copy,
no claims the source does not support.

### 6. Seal and queue
- Write the note to `_PATTERNS/<YYYY-MM-DD>-<slug>-isomorphisms.md` with front-matter
  (`title`, `version: 0.1.0`, `date`, `status: research (no build decided)`, `source`).
  Zero em-dashes.
- Append the top 3 inventions to `_QUEUE/induced-backlog.jsonl` (skip with `--no-queue`). Use
  the existing row shape: `id`, `jtbd`, `route` (`tool` = note path + `INV-n`, `verified` = today),
  `gates` (first gate is the kill condition), `trigger`, `cost_prior`, `fates`, `status: "OPEN"`,
  `depends_on`, `unblocks`, `order`, `gh_sync: false`. Append with Python `json.dumps`, then parse
  every line back to prove the file is still valid JSONL.
- Stage only the files you wrote (`git add <paths>`, never `git add -A`); hooks or other
  sessions may have touched state files you did not author. Check `git config core.hooksPath`
  is `scripts/git-hooks` so the pre-commit gates actually run.
- Commit `docs(research): ...` with an NCI tag, push to the session branch. A branch push is not
  a merge or deploy, so no decision receipt is owed until it merges.

Then offer, in one line each, the two downstream surfaces: a shareable artifact page of the
note, and an NFTT essay via `nftt-story-factory` (draft-first, Zach blesses before routing).

## Report back

In `claim-check` mode, the module's own Output section is the whole report. For a full scan,
lead with the one-sentence thesis of the field, then the claim-check verdict, the top
isomorphisms (mechanisms first), the ranked inventions with their kill conditions, and anything
that went wrong in the session. Explain jargon on first use; Zach reads these to learn the
field, not only to file it.
