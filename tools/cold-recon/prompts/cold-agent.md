# Cold-reconstruction task (ZERO TRANSCRIPT)

You are a **fresh, memoryless reader**. You did not participate in the incident below and
you have no conversation history about it. Your only context is the EVIDENCE PACK at the
end of this prompt: the committed record (git commits + tracked artifact files) for one
incident in repo `{{REPO}}`, range `{{RANGE}}`.

This coldness is deliberate. A participant is the worst narrator of their own incident:
hindsight and the pull toward a coherent story bend the account. You cannot spin what you
never lived. Report **only what the committed record shows.** Where the record is thin,
say so plainly rather than filling the gap with a plausible story.

## Counts in this pack
```
{{COUNTS}}
```

## What to produce

Return a single JSON object conforming to the schema below. Rules:

1. **Ground every claim in the pack.** Cite the artifact path or short commit sha in each
   section's `evidence` array. If you cannot cite it, it does not go in `sections`.
2. **Per-section confidence is about the RECORD, not your fluency.** A section you can
   write beautifully but only weakly ground gets a LOW confidence. Confidence measures how
   well the committed record supports the claim.
3. **`could_not_verify` is a first-class output, not an apology.** List every claim you can
   describe but not confirm from the record -- e.g. "the RCA says the send tool is denied at
   the tool layer, but the settings file is not in this pack, so I cannot confirm the deny
   is live." Omitting this list is a failure; a rich list is the point.
4. **`root_invariant` is the durable principle, not the surface event.** Name what the
   incident turned on that would generalize to another domain.
5. Do not invent dates, names, numbers, or file contents. Redact people to roles.

## Schema
```json
{{SCHEMA}}
```

## Evidence pack
```json
{{PACK}}
```
