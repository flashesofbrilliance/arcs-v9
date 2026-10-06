# Doc reconciliation, 2026-10-06

Measure + salvage only. Nothing moved or deleted (Zach, 2026-10-06). Full per-file evidence: `_STATE/2026-10-06-doc-reconciliation.json` (722 rows).

## Scope and honest totals

- **Files:** 722 git-tracked `*.md` at origin/main 735b6afd.
- **Lines in scope: 87,251.** This is total lines in the doc corpus, not lines reconciled. The artifact tile's 90,600 was a group-level estimate of the same thing.
- Every file got a class from the rule below; every class carries per-file evidence.

## Rule (fixed before counting)

- **precedence:** stale > drift > debt > current (pre-registered before counting)
- **stale:** in _ARCHIVE/ or archive/; OR self-declares superseded/deprecated/archived at line start; OR 0 inbound basename refs AND untouched >30d AND >=50% of backticked path refs missing
- **drift:** >=1 backticked repo path ref not in tree (gitignored paths excluded via git check-ignore)
- **debt:** >=3 open markers (unchecked boxes, TODO, TBD, FIXME, not built)
- **current:** none of the above

## Result

| Class | Files | % files | Lines | % lines |
|---|---|---|---|---|
| current | 601 | 83.2% | 61,888 | 70.9% |
| drift | 83 | 11.5% | 12,031 | 13.8% |
| debt | 24 | 3.3% | 3,006 | 3.4% |
| stale | 14 | 1.9% | 10,326 | 11.8% |

The "~40% stale or archive" estimate does not survive measurement: 1.9% of files (11.8% of lines, mostly the two big archive files) meet the stale rule. Drift (11.5%) is the real backlog: docs that cite paths no longer in the tree. Heaviest drift: _PATTERNS (22 of 55), _STATE (21), _DECISIONS (11).

Limits: path refs only count backticked repo paths, so prose-only docs default to current. Inbound refs match by basename, so same-named files (pitch-memo.md, ARCS-YellowPaper.md) share a count. A review list of 38 non-stale files with 0 inbound refs and no edit in 45+ days (3,456 lines) is in the JSON as `dormant_signal`.

## Near-duplicates and the operator suite

Ops 19 (Accountant), 20 (Folksonomy) and 21 (Librarian) are bound and READY in the registry, but none takes documents as input: 19 scores receipt outcomes, 20 clusters receipts as 54-dim seeds (gated at 100), 21 ranks a receipts store. Running them on docs would fake the output, so they were **not run (blocked: input contract mismatch)**. Substitute: 5-word shingle Jaccard >= 0.5 or containment >= 0.8, union-find.

9 clusters, 43 files:

- 2 files, J=1.0: keeper by rule `archive/specs/deprecated-versions/ARCS-YellowPaper.md`; others: `_CANON/ARCS-YellowPaper.md`
- 2 files, J=1.0: keeper by rule `runtime/specs/arcs-v9-engineering-spec-v1.md`; others: `runtime/specs/arcs-v9-engineering-spec.md`
- 27 files, J=0.659: keeper by rule `_STATE/job-search/forge-inputs/prompt-avepoint-forward-deployed-engineer-ai.md`; others: `_STATE/job-search/forge-inputs/prompt-american-express-director-digital-produc.md`, `_STATE/job-search/forge-inputs/prompt-basis-atlas-fde.md`, `_STATE/job-search/forge-inputs/prompt-camunda-ai-process-forward-deployed-engi.md` ...
- 2 files, J=0.962: keeper by rule `_ARTIFACTS/blog/field-notes-self-cataloging-corpus.md`; others: `_ARCHIVE/nftt-threaded-engine/stories/self-cataloging-full.story.md`
- 2 files, J=1.0: keeper by rule `_ARTIFACTS/mercury-bundle/pitch-memo.md`; others: `_ARTIFACTS/mercury-pitch/pitch-memo.md`
- 2 files, J=0.925: keeper by rule `_ARCHIVE/nftt-threaded-engine/stories/germinate-pollinate.story.md`; others: `_ARTIFACTS/blog/field-notes-germinate-pollinate.md`
- 2 files, J=1.0: keeper by rule `_ARTIFACTS/sentilink-bundle/pitch-memo.md`; others: `_ARTIFACTS/sentilink-pitch/pitch-memo.md`
- 2 files, J=0.892: keeper by rule `_ARTIFACTS/blog/field-notes-self-cataloging-corpus-diamond-cut.md`; others: `_ARCHIVE/nftt-threaded-engine/stories/self-cataloging-brief.story.md`
- 2 files, J=0.78: keeper by rule `_ARTIFACTS/blog/field-notes-self-cataloging-corpus-exec.md`; others: `_ARCHIVE/nftt-threaded-engine/stories/self-cataloging-exec.story.md`

Reading: 6 exact or near-exact copies (YellowPaper archive vs canon, engineering-spec vs -v1, mercury/sentilink bundle vs pitch pitch-memo, 4 blog field-notes vs archived NFTT stories). The 27-file cluster is `_STATE/job-search/forge-inputs/prompt-*.md`: generated from one template, by design, not dedup candidates.

## Salvage pass (stale docs only)

Mechanical: decision-like lines whose 6-word shingles appear in <20% of the rest of the repo + memory. 257 candidates across 14 stale files; residue judged by one agent (handoffs, memory-archive) and by hand (the rest). Burden of proof on UNIQUE.

| File | Candidates | Verdict |
|---|---|---|
| `_ARCHIVE/handoffs.md` | 202 | 1 unique, 25 recorded, 5 superseded, 171 ephemeral |
| `_ARCHIVE/memory-archive.md` | 37 | 0 unique, 9 recorded, 6 superseded, 22 ephemeral |
| `_STATE/2026-08-13-umbrella-dunford-positioning-canvas.md` | 9 | **unique as a whole doc** |
| `_ARCHIVE/nftt-threaded-engine/stories/take-home-trap.story.md` | 6 | recorded (shipped NFTT post + memory) |
| `_ARCHIVE/nftt-threaded-engine/README.md` | 2 | recorded (nftt-story-factory skill) |
| `archive/specs/deprecated-versions/ARCS-YellowPaper-v1-1.md` | 1 | ephemeral |
| 8 other stale files | 0 | nothing to salvage |

### Unique material not recorded elsewhere (2 items)

1. **CI cancel-in-progress on main leaves only the newest commit's run as the verdict** (from `_ARCHIVE/handoffs.md`). `ci.yml`, `security.yml` and `intent.yml` cancel in-progress runs on new pushes to main, so when PRs merge in quick succession the earlier merge commits never get a finished CI run. The setting exists; no memory, pattern or ADR states the consequence. It bears directly on v3.110 open item 4 ("post-merge CI on main never observed"). Suggested home: a memory or `_PATTERNS/durable-gotchas.md` line.
2. **The umbrella positioning canvas (April Dunford method)**, `_STATE/2026-08-13-umbrella-dunford-positioning-canvas.md`. The only record of the competitive alternatives, the auditability/provenance attribute set, and the framing rule "lead with the category, trend only after it lands". "dunford" greps nowhere else in repo or memory besides a passing mention in `public/wing.html`. It is classed stale (0 inbound refs, 54 days untouched, its one path ref gone) but must not be archived without promoting it first.

## Archive proposal: Zach's decision, nothing done

- The 13 files already in `_ARCHIVE/` and `archive/` stay where they are; nothing to move.
- The 6 duplicate pairs above could each collapse to their keeper. Proposal only.
- The umbrella canvas: promote (to `_PATTERNS/` or a memory) or leave as is. Do not archive unpromoted.
- Drift (83 files) is repair work, not archive work: each file needs its dead path refs fixed or annotated.

## Reproduce

Scripts were run from the session scratchpad (classify, dups, salvage). The rule above is complete enough to re-implement; ask to land them as `scripts/doc_reconcile.py` if this should become a repeatable gate.
