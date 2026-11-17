---
name: feedback_count_before_judging_conversation_reads
description: "Reading people from transcripts: count first, pre-register, freeze a test line, two blind coders; lessons from the projection map"
metadata:
  node_type: memory
  type: feedback
---

Zach called judged signature reads "handwavy" (2026-11-16). Ground conversation reads in evidence this way:

- **Count before judging.** Talk share, questions, turn length, uptake are a script over verbatim transcripts (Granola `Microphone` = Zach, `System audio` = others). Fetch with fetch-only helpers and extract from their logs, checked against `total_chars`; never retype a transcript.
- **Pre-register** every test with its threshold and kill rule before computing (`tools/projection-map/PREREGISTRATION-TEMPLATE.md`). A hypothesis found in the data is labelled exploratory.
- **Shuffle within rooms** when pooling audiences, or the room mix fakes a result (Simpson's paradox).
- **Freeze a discovery/test line.** Patterns found in old calls promote only on new calls. Re-running on the same data is one observation, however often it agrees.
- **Judged labels need two blind coders on different models** and an agreement score (Cohen's kappa) before they count as a stream.
- **Never retire a measure on a small pilot.** Counted uptake failed on 15 turns and held on 60.
- **Audit the parser first.** Three parser bugs (named speaker labels, untimed files, duplicate pages) each flipped a verdict before they were caught.
- **A later meeting is not an advance** until the counterpart is verified; an impersonation's fast "next steps" are the hook ([[unverified-inbound-starts-at-bad-faith-reference-class]]).
- **Teleport to terminal:** once transcripts are local, mining them with grep or a script costs almost no tokens; spend agents only on judgment.
