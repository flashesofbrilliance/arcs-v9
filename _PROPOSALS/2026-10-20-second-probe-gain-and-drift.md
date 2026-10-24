# Proposal: second_probe_gain and productive vs destructive drift (2026-10-20)

Status: PROPOSAL. Banked from Zach's side chat 2026-10-20. Nothing here is canon or code; nothing
merges without Zach's yes. Canon v1.1 and the Yellow Paper are ask-first, so section 4 is a draft only.

## 1. The atom: `second_probe_gain(pass_1, pass_2)`
- **Definition.** New backed claim units in pass 2, divided by all claim units in pass 2.
- **Claim unit.** The Op 25 v1 claim unit (`runtime/specs/operator-25-shavasana-v0.md`, "Claim
  unit (v1 CANDIDATE)"): a bullet, numbered item or prose sentence; backed when the unit itself
  holds a ground return (ADR, sha, repo path, script, URL, receipt id, memory link).
- **New.** Backed in pass 2 and not present (same claim, same ground return) in pass 1.
- **Guard.** Count only units that a later step cites. A backed claim nobody uses is not gain.
- **Reading.** The "mantissa between the integers": the integers are the passes; the gain is what
  the second probe adds that the first could not. Golden Inchworm aliases point here (LEGEND row
  `Golden Inchworm`) and stay METAPHOR until this atom earns its place.
- **Where it sits.** Beside the domino line in the shared-intention proposal
  (`_PROPOSALS/2026-10-20-shared-intention-before-snap.md`, PR 1691); cross-link there once one
  seed has a receipt (pollinate last).

### Earning conditions (all three, or it is composted)
1. **Worked example** on the side-chat session it came from: pass 1 and pass 2 of the same material,
   both counted by hand, the number reported with every unit listed.
2. **Downstream consumer.** A scheduled second probe after each domino reads the number and acts on
   it (for example, stop probing when gain falls under a pre-registered floor).
3. **Survives a Loki attack.** A Loki pass (Op 23, or the chief-loki agent) tries the cheapest thing
   that breaks it (inflating gain by splitting sentences, citing to self, re-citing pass-1 sources)
   and the guard holds.

## 2. Drift: productive vs destructive
- **Productive drift.** DRIFT mode is declared and the motion prints an artifact or opens a new span.
- **Destructive drift.** CHRONOS is declared and nothing is printed.
- `_CANON/book-ii/part-v-the-accumulation-protocol.md` §5.5 covers only the destructive kind
  (court drift against its axioms). LEGEND row `drift (productive / destructive)` records the split.
- **Classifier (gap).** Inputs: declared mode, printed within N turns, forked span. Backlog row
  `drift-classifier-productive-destructive`. It waits on the atom above, since it uses the same
  claim units. N and the labels are pre-registered before any count.

## 3. Seeds (numbered by `scripts/oracle.py next seed`)
- 17 `seed-second-probe-gain`
- 18 `seed-drift-productive-vs-destructive`
- `claim-index-sme` was not planted: the claim-index session already exists (PR 1696) and owns it.

## 4. Yellow Paper section (DRAFT, ask-first, not applied)
Proposed for `_CANON/ARCS-YellowPaper.md`, after it cites a code file that exists:
> **Second probes and drift.** A pass over material earns a second pass only by what the second
> adds: second_probe_gain counts new backed claim units that a later step cites, over all claim
> units in the second pass. Drift is not failure by itself: declared drift that prints is how new
> spans open; undeclared drift under a linear clock that prints nothing is the failure the
> constitutional court guards against (Book II §5.5).
The citation to the implementing file is added only once that file exists.

## 5. Claim-index ordering (for the claim-index session, PR 1696)
Index first; then its drift check ranks what is stale by surface and audience; then reword in one
pass. The two Concourse "3,500 commits" lines come out of that pass, not before it.

## 6. Not done here, and why
- Cold molt, spawn order and pollination belong to the side-chat session itself: a session molts
  its own state. Its fragment's Open section must name the four open D0 decisions.
- The idiom order (germinate, seed, sprout, pollinate) is not treated as law: memory marks the
  mapping unverified against `_SEEDS/index.jsonl`.
