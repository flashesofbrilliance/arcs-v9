# JTBD graph pre-registration, amendment 4 (2026-10-19)

Amends the exclusion list in `_PATTERNS/2026-10-18-jtbd-s1-mined-job-rule.md`. No threshold changes.

## What was seen first
The mined-job rule excluded the pre-registration file and itself by exact name, but not its dated
amendments. Amendments 1 and 2 were mined as jobs and landed as files 15 and 16 of the 30-file label
sample (seed 20261018) that Zach is labelling now.

## Rule
The miner excludes every `_PATTERNS/*-preregistration*.md` and the mined-job rule file, by pattern
(`PAT_EXCLUDE_RE` in `scripts/universe_jtbd_adapter.py`). A self-test fixture fails if an amendment is mined.

## Label sample
The exclusion applies to the mined atom set only. The in-progress sample is frozen as drawn in
`runtime/specs/jtbd-label-sample-20261018.json` (30 ids, including the two amendments) and the adapter
reads it from that file; the gate's 24-of-30 bar and its 30 files do not change. How files 15 and 16
are scored is Zach's call, not this amendment's.
