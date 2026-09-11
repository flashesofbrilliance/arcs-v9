# /witness — attest a flash of brilliance, right now

> "Can I get a witness?" — a one-shot, in-the-moment capture. The opposite of `/dewy-stub`:
> no scaffold, no options-considered, no numbering ceremony. Just the verbatim moment,
> timestamped, filed before it can be reconstructed later. See WORLD.md → THE WITNESS.

## When this fires

Two ways in:
1. **Claude notices it live** — a principle names itself, the user says something like "wait,
   that's it" / "yes exactly" / "oh", or Claude's own line compresses sharper than the surrounding
   conversation. Claude offers it in one line: *"Can I get a witness — attest that this just
   happened?"* Does not wait to be asked. Does not interrupt if the user is mid-thought — offers
   at the next natural pause.
2. **The user invokes it directly** — `/witness [optional note]`.

Only fires on genuine crystallization — a principle, a naming, a "that's it" moment. Not for
routine confirmations, task completions, or anything already covered by a DEWY receipt or ADR
in progress. If unsure whether it's a witness moment, it isn't — the trigger should be rare.

## What it does NOT do

- Does not research, score conviction, or weigh options. That's `/dewy-stub` or `/arcs-research`.
- Does not promote itself to an ADR or DEWY receipt automatically. A witness stub is raw
  material; promotion is a separate, later, deliberate act (via `/dewy-stub` or `/nci-commit`)
  once it's proven durable — never claim more permanence than it earned in the moment.
- Does not commit or push. Writes locally only.

## What it writes

Append one entry to `_STATE/witness/<YYYY-MM-DD>.jsonl` (one file per day, append-only,
newline-delimited JSON — cheap, greppable, no read-modify-write races):

```json
{"ts": "2026-08-11T09:14:22-04:00", "quote": "<verbatim — what was actually said, not a summary>", "context": "<one line — what was being worked on>", "gut": "<Claude's honest in-the-moment read: why this felt sharp>", "y": "SCRATCH|YELLOW|GREEN", "promoted": null}
```

- `quote` — verbatim, not paraphrased. This is the sound the tree made.
- `y` — an honest gut-check, not a scored conviction. Most witness stubs are SCRATCH or YELLOW
  (a flash, unproven) — GREEN is rare and means it's already load-bearing, not just striking.
- `promoted` — null at capture. If later promoted to an ADR/memory/DEWY receipt, that artifact's
  session updates this field (e.g. `"ADR-046"` or `"[[some-memory-slug]]"`) — do this as a small
  follow-up edit, not part of the witness act itself.

## Step-by-step

1. Ensure `_STATE/witness/` exists (`mkdir -p`).
2. Compose the entry per the schema above. Keep `quote` genuinely verbatim — pull it from the
   actual transcript, don't reconstruct from memory of what was said.
3. Append as one line to `_STATE/witness/<today>.jsonl`.
4. Reply with a single confirmation line, not a summary: *"Witnessed."* — optionally the `y` gate
   if it's notable. Do not narrate the mechanism back to the user; the point is it was quiet and
   fast, not another artifact to review.

## Notes

- This is deliberately NOT wired into `/night-moves` gather yet. If witness stubs prove useful
  over a few days, add a WITNESSED section to the night-moves digest (count + the day's GREEN
  ones) — don't build that ahead of evidence it's needed.
- Rare by design. If `/witness` is firing more than once or twice a session, the trigger is
  over-tuned — treat that as a signal to tighten it, not a sign it's working well.
