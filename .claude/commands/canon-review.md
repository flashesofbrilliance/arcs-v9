---
description: Batch-review the canon-propagation queue — quick yes/no multi-picker over DEROT / ESCALATE / FORK items, then apply the yes'd ones
---

# /canon-review — batch approval for canon propagation

Drive the human-in-the-loop review of `_INBOX/canon-propagation-queue.json` (produced by
`scripts/canon_propagation_check.py`, run nightly by `scripts/canon_propagation_nightly.sh`).

This is the **judgment surface** for a deliberately dumb, deterministic sentinel. The engine only
ever DETECTS and stages; nothing lands on a first-order source of truth without a yes here.

## Steps

1. **Read the queue.** `cat _INBOX/canon-propagation-queue.json`. If it is absent or `items` is
   empty, run `CLAUDE_PROJECT_DIR="$PWD" python3 scripts/canon_propagation_check.py` first to
   regenerate it, then re-read. If still empty, report "nothing staged — canon is in sync" and stop.

2. **Group items by kind** and present them as ONE `AskUserQuestion` multi-select (quick yes/no):
   - `kind: "mechanical"` (DEROT) — default **yes**. A partial-mirror completion; provably safe,
     git-reversible. Label each: "APPLY: <proposal>".
   - `kind: "judgment"` (ESCALATE) — default **no**. A conflict / collision / cross-source mismatch.
     Approving does NOT resolve it — it spawns an escalation stub for a human ruling. Label: "ESCALATE: <proposal>".
   - `kind: "fork"` (gravity-well) — default **no**. A net-new cluster dense enough (mass × gravity)
     to become its own organism. Approving drafts a dedicated spec/ADR/seed stub. Label: "FORK: <title> (<mass> members)".
   Keep the picker to one screen; if >12 items, page by kind (mechanical first).

3. **Apply the yes'd items — by kind, never blur the line:**
   - **mechanical → apply for real.** Run `CLAUDE_PROJECT_DIR="$PWD" python3 scripts/canon_propagation_check.py --regenerate`
     which writes ONLY the mechanical de-rots in place. Show the resulting diff (`git diff`).
     Do this on the current branch (or `git switch -c canon-sync/manual` first if the user wants isolation).
   - **judgment → do NOT edit any canon file.** For each yes, append an escalation stub to
     `_DECISIONS/` (or the relevant collision doc, e.g. `CANON-COLLISION-rom-vocabulary.md`) capturing
     the conflict + options, status `ESCALATED — AWAITING RULING`. The human rules later; you never
     pick the winner (canon-collision-escalate rule).
   - **fork → draft the organism, marked PROPOSED.** Create the dedicated stub (a
     `runtime/specs/ROM-CANDIDATES-<slug>.md` or an ADR draft or a seed entry), pull the cluster's
     members in as provenance, mark `PROPOSED — NOT RATIFIED`, and cross-link back to the folksonomy
     source. Do NOT wire it into constitutional lists. (This is the mechanized version of the manual
     Norse-stack fork.)

4. **Receipt.** Append one line to `_INBOX/canon-propagation.jsonl` recording which item ids were
   approved/applied/deferred, so the loop is auditable. Do NOT auto-push or auto-merge; the user
   merges the review branch when ready.

## Guardrails
- Never resolve a `judgment` conflict by editing canon — only stage an escalation. NOTOMATION + canon-collision-escalate.
- Never auto-apply a `fork` into a ratified list — a fork produces a PROPOSED organism, human ratifies.
- Empty/degenerate picks are fine: applying zero items and reporting "held" is a valid outcome.
