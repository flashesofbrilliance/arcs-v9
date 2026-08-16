# ADR-061 — Verify every audit/gauntlet flag against the full primary source before applying

**Status:** Accepted · 2026-08-16
**Allocated by:** the oracle (`oracle next adr` → 61), per ADR-057. First falsification: `_STATE/falsification-ledger.jsonl` entry `EXP-2026-08-14-kam-codex-gauntlet`.

## Context
The counterpart-gauntlet (persona facets → adversarial verify → dual-bar-raiser → synthesis) is a strong
falsifier, but it is not self-grounding: it reasons over whatever source it is handed. On the Kam codex
run (17 agents, both bar-raisers HOLD, 13 ranked flags), the gauntlet was fed a **scratchpad transcript
that had been silently abbreviated** and did **not** carry the two LinkedIn profiles. Result: three flags
were false positives — including the synthesis's own **#1 top-fix**, which called a verbatim line
("geometric approach… field state… dyad… triad") a fabrication because the passage had been dropped from
the local copy. Two more ("six million pages" invented; "Kam has no Invisible tie") were refuted by the
profiles. One prescribed fix, if blind-applied, would have **replaced a truth with a new fabrication**
(telling Kam he "almost joined Invisible" — that near-miss was his friend on the tape; Kam actually
co-founded it). A test can be falsified by its own source, and a fix can be worse than the defect.

## Decision
No flag from any audit, gauntlet, skeptic, or bar-raiser pass is applied until it is **re-verified by the
operator against the full primary source** — for a counterpart artifact that is the complete call
transcript (re-pulled authoritative, never a working copy), the counterpart's own profile/comms, and where
a quote cites an external document, a fetch of that document. Concretely:
1. **Ground the grader.** Confirm the source the pass ran on is complete and authoritative before trusting
   any "not in source / fabricated" verdict. A partial source only licenses *true-positive* reasoning, never
   *absence* claims.
2. **Adjudicate each surviving flag** GROUNDED / OVER-FLAG / REAL against the full source, with a written
   reason. Reject over-flags explicitly (they are data — record them in the ledger).
3. **Never blind-apply a prescribed fix.** A fix can introduce a new falsehood; verify the fix's own claim
   before writing it.
4. **Deterministic where possible.** Quote provenance is checked mechanically (`scripts`-side substring
   checker, e.g. the reusable `provcheck.py`): every attributed quote must be verbatim-present in the source
   (elisions marked); only external-sourced or self-labeled paraphrase may be non-verbatim, and each such
   exception is named.

## Consequences
- **Both defect classes are recorded, not just one.** The falsification ledger logs `falsified[]` (real
  defects fixed) AND `over_flags_rejected[]` (where the test itself was proven wrong). The gauntlet's own
  error rate becomes visible over time.
- **NOTOMATION holds:** the machine surfaces and pressure-tests; the operator adjudicates against ground
  truth and owns what ships. A HOLD from a bar-raiser is an input, not an order.
- **Cost note (pre-revenue):** a 17-agent gauntlet (~1.8M tokens) is only worth it when a real source
  exists to verify against — reinforcing the dual-gate (cheap artifact → real ground truth → expensive
  fan-out). Running a gauntlet on thin/partial source manufactures false work.
- **Generalizes** beyond counterparts to any ADR/handoff/canon promoted past a claims-skeptic pass, and to
  the meta-audit.

## Lineage
[[fact-check-final-pass-vs-transcript]] · [[external-artifact-eval-ground-and-skeptic-route]] ·
[[dont-trust-subagent-citation-without-checking]] · [[gauntlet-tuned-to-register-catches-what-detector-cannot]] ·
[[never-merge-on-red-x-verify-check-conclusions]] · [[control-integrity-described-vs-wired]] ·
ADR-044 (temporal-provenance) · ADR-057 (oracle) · `_STATE/falsification-ledger.jsonl`.
