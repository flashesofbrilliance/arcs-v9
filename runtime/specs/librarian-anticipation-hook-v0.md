# Librarian anticipation hook, v0 (SPEC ONLY, no build)

Status: DRAFT, proposed 2026-10-15. Number ADR-088 allocated via `python3 scripts/oracle.py next adr`; promote this spec to `_DECISIONS/ADR-088-*.md` only if Zach approves.
Prior art: `operators/arcs_librarian.py` (already has `recommend(q, budget)` with expected-value retrieval, so the registry's "store/retrieve only" row is understated; reconcile separately), `scripts/prior_art.py`, the `/echo-scan` skill, `scripts/provenance_lint.py`, AGENTS.md gotchas 11 and 15.

## Why

2026-10-15 VICO prep: unsourced canon numbers and a definition split surfaced only after Zach said he was "looking in vs looking out"; /echo-scan was suggested late and reactively. Intent: the Librarian anticipates, and every scan compounds into a lookup that costs nothing next time.

## Triggers (any one; deterministic regex, no model call)

| id | fires when | example |
|---|---|---|
| T1 novelty/efficacy word | `novel`, `first`, `proves`, `efficacy`, `unprecedented`, `no one else` within 80 chars of a number or capability claim, in text written to a tracked file or a counterpart-facing draft | "first system to ... 87%" |
| T2 uncovered metric | a `provenance_lint.METRIC` or `canon_claims_report.EXTRA` match in an enrolled file with no covering evidence.jsonl entry | 76% with no ledger line |
| T3 new term | a capitalized or hyphenated term newly added under `_CANON/**` or a counterpart universe (read only; the hook never edits there) that is absent from `_CANON/ordinals/ARCS-Glossary-v0.1.md` and from `runtime/echo/rosetta.jsonl` | "Chrono-Kairos" |

## Behavior

1. Cheap pass (free, deterministic): `prior_art.py <term or claim>` top 3, plus a lookup in `runtime/echo/echo-ledger.jsonl` and `runtime/echo/rosetta.jsonl` by normalized term. On a ledger hit, print it (their term, ARCS term, MECHANISM or METAPHOR, delta, receipt id) and STOP. This is the compounding step.
2. On a miss, emit exactly one line, e.g. `Librarian: "novel" next to 87% (T1+T2). No echo-ledger entry. /echo-scan claim-check costs ~15-25k tokens; adding the number to evidence.jsonl is free. Run? (offer only)`
3. Never auto-run /echo-scan. Never edit text. NOTOMATION: it scaffolds the decision; Zach decides.
4. Filing: a scan that runs appends one receipt row to `runtime/echo/echo-ledger.jsonl` (id, date, source, verdict, kill condition, backlog ids) and each isomorphism as a Rosetta row in `runtime/echo/rosetta.jsonl`: `{their_term, arcs_term, kind: MECHANISM|METAPHOR, delta, source_receipt, universe}`. Append-only; a correction is a new row pointing at the old (Kintsugi). `universe` is a read-only reference to the counterpart universe; the hook never writes under `_STATE/job-search/universe/`.

## Rate limit and stakes

- Max 1 suggestion per trigger id per session, 3 per session total. None during a send-prep or call window unless T2 touches a counterpart-facing file.
- Stakes gate: low (internal scratch) only T2; medium adds T1; high (counterpart-facing, public, resume, canon) all three.
- A declined suggestion mutes that term for 14 days.
- A suggestion must show its cost; one without a cost estimate is a bug.

## Pre-registered kill condition (written 2026-10-15, before any build)

Measured over the first 10 sessions in which the hook fires, from `runtime/echo/suggestion-log.jsonl` (one row per suggestion: trigger, term, accepted|declined|ignored, cost shown):

- K1 acceptance: accepted / suggestions < 1/3 over those 10 sessions => throttle to stakes high and T2 only for the next 10 sessions.
- K2 noise: 5 or more declined+ignored within any 3 consecutive sessions => mute T1 until re-registered.
- K3 value: fewer than 2 accepted scans changed a decision (a canon edit, ledger entry, strike or backlog item) by session 10 => delete the hook, keep only the ledger lookup.
- K4 compounding: no ledger hit ever reused by session 10 => the Rosetta design failed; drop T3.
- Review after the 10th firing session; Zach decides, not the hook. Changing thresholds after build needs a new dated entry (moving goalposts otherwise).

## Frustration Gate (gotcha 15) for the build

Every check ships with a known-bad and a known-good fixture in `--self-test`, wired to pre-commit: T1 fires on "first system ... 87%" and not on "first of the month"; T2 fires on an uncovered 76% and not on a covered one; T3 fires on a term absent from glossary and rosetta and not on one present; a ledger hit suppresses the suggestion; the rate limit suppresses the 4th. The report generator already follows this: `python3 scripts/canon_claims_report.py --self-test`.

## Open questions for Zach

1. Where does it run? Recommendation: pre-commit warning for T2 and T3 (deterministic, file-scoped), `/prior-art` for T1 (the text is in conversation, not yet in a file).
2. The NCI definition split (primitives CoherenceReceipt vs product-level) and the Litepaper acronym mismatch are definitional drift, outside the numeric triggers. A glossary-diff check could catch the acronym, not the formula.
3. Which uncovered tokens to keep, cite or strike: `_STATE/2026-10-15-canon-uncovered-claims-report.md`.
