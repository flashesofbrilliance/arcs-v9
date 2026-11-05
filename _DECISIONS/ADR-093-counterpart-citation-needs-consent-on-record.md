# ADR-093: Counterpart citation needs consent on record

> **Status:** PROPOSED (2026-11-04). Not decided; needs Zach's ruling.
> **Date:** 2026-11-04
> **Author:** Claude Opus 5.5, from the Brooks proposal session (the deep thread recoil of 2026-11-04, ADR candidate 2; local to that session, not committed)
> **Oracle:** number allocated via `python3 scripts/oracle.py next adr` (93); `_SEEDS/_oracle.json` committed with this file.

---

## D: The decision

**Sharp question:** May a counterpart-facing artifact cite the counterpart's call (quoted lines, line or timestamp references, "src: call" tags) when no consent to the notetaker is on record?

**Proposed answer:** No. Without consent on record, the artifact paraphrases and owns it as the author's understanding ("as I understood it, mine to confirm with you"). The transcript stays internal ground truth for fact-checking; it never shows on the page.

---

## E: Entity / system

- Every counterpart-facing surface: proposal pages, one-pagers, follow-up emails, recoil-ship projections, pitch video scripts.
- The pre-send checks: `scripts/page_gate.py --counterpart`, the counterpart gauntlet workflow, `scripts/attribution_provenance_lint.py`.
- Internal surfaces (SSOTs, recoil ledgers, war rooms) are out of scope: they may cite transcripts freely, behind the air gap (ADR-050).

---

## W: Window

**Horizon:** YEAR
**Revisit trigger:** a counterpart asks to see the record; recording consent becomes a standard opener captured in the transcript; or a send is blocked where consent was in fact given but not findable.

---

## Context

On 2026-11-04 the Brooks Thomas audit page tagged each "You said" row "src: Sep 15 call" to show active listening. Zach asked whether he had asked Brooks to use the notetaker. A search of the transcript, the email thread and the pre-call prep found no consent. Zach's bar for the page: show active listening, not surveillance. The tags came off and the deck now reads "as I understood it, and mine to confirm with you at kickoff."

This sits between two existing rules:
- ADR-044 (temporal provenance) governs when a claim was true. This ADR governs whether the source may be shown at all.
- ADR-050 (air gap) keeps one counterpart's material out of another's view. This ADR keeps a counterpart's own recorded words from being shown back to them without consent.

Memory `fact-check-final-pass-vs-transcript` already says a recording announced plus an offer received is not the same as an explicit grant. Memory `counterpart-citation-needs-notetaker-consent` holds the working rule until this is decided.

---

## Options considered

### Option A: consent on record, else paraphrase (proposed)
- Citations allowed only when consent is findable in the transcript, the thread or the prep notes, with the location noted in the internal SSOT.
- Pros: the counterpart never learns from the page that they were recorded; the listening still shows through accurate paraphrase.
- Cons: loses the "here's exactly what you said" trust signal with counterparts who did consent but whose consent was not captured.

### Option B: always paraphrase in counterpart copy
- Simpler; no consent lookup.
- Cons: throws away a strong signal with counterparts who explicitly agreed, such as rigor-oriented reviewers who value the trace.

### Option C: status quo (author's judgment)
- Cons: the Brooks tags passed every existing gate; judgment alone did not catch it.

---

## Decision

**Proposed:** Option A.

**Rationale:** it keeps the trace where it was earned and removes it where it would read as surveillance. The cost is one lookup per send.

**Trade-offs accepted:** a counterpart who consented off the record gets paraphrase until the consent is written down somewhere findable.

---

## Y: Conviction

**Polarity:** YELLOW
**Conviction:** MEDIUM
**Stability:** SHIFTING (one incident; no counterpart reaction observed yet)

**Loki test:** One near-miss, caught by Zach before any send, is thin ground for a rule. Paraphrase is also where ventriloquy (ADR-033, speaker coordinate) breeds: a softened quote drifts more easily than a verbatim one. The answer: paraphrase in copy, verbatim match in the internal check (`attribution_provenance_lint.py` still runs against the transcript before the send).

---

## Consequences

- A pre-send grep for `src:`, call line numbers, timestamps and quoted call lines, with a consent lookup when any are found. First home: the counterpart gauntlet's provenance facet; a mechanical check in `page_gate.py --counterpart` if it recurs (the Frustration Gate rule, AGENTS.md gotcha 15).
- Recoil SSOTs gain a `consent_on_record` field (location, or null) so the check has something to read.
- Unblocked next: ADR-033 amendment 2026-11-04 (agreement in interleaved transcripts), filed alongside this one.

**Implementation pointer:** memory `counterpart-citation-needs-notetaker-consent`. The case material (the Brooks page notes and its kintsugi log, the thread recoil) is local to the contract-work session and not committed: it carries counterpart material.
