# LORE — the book of stories with their verdicts

> GENERATED from `runtime/specs/lore.jsonl` by `scripts/lore.py render` — do not hand-edit.
> LEGEND's uncle: LEGEND says what a word means; LORE says what we believe and why, including
> what we stopped believing. A story is never deleted when its verdict flips; a new row is
> added and the old one points forward. `undecided` may be told but not cited.

Rows: 12 · durable-myth: 5 · inspiration: 3 · old-wives-tale: 1 · true: 3

## lore-001 · ✖ DURABLE MYTH

**Story.** Old window panes are thicker at the bottom because glass is a slow liquid and gravity has pulled it down over the centuries.

- **Told where:** physics textbooks, museum guides, this session (Zach, 2026-09-27)
- **Observation (real):** Many old panes really are thicker at the bottom.
- **Mechanism claimed:** Room-temperature glass flows under gravity on a scale of centuries.
- **Test that decided:** Zanotto, Am. J. Phys. 1998: relaxation time from measured viscosity ~1e32 years; panes thicker at the top and sides exist; crown-glass process documented to make uneven sheets.
- **Teaches:** A real observation plus a plausible mechanism can carry a false binding for a century; the falsifying calculation cost one afternoon nobody spent. Apparent drift may be a birth defect.
- **Date:** 2026-09-27 · **Refs:** `_STATE/source-trust-events.jsonl`, `runtime/specs/LEGEND.md`

## lore-002 · ✖ DURABLE MYTH

**Story.** An external audit crawled the repo and mapped ARCS Operators 1 through 19 to specific files at 'Full Production' status.

- **Told where:** Perplexity, 'Job to Be Done.md', 2026-09-27
- **Observation (real):** The named files exist and the operator names are in the canon.
- **Mechanism claimed:** Each numbered operator is implemented by the file listed.
- **Test that decided:** grep sweep: 0 hits for shavasana/hyperstition/accountant/sycophancy; five named files implement something else; the 1-19 numbering was the document's own (periodic table has Folksonomy=20, Librarian=21).
- **Teaches:** Real files, plausible mapping, wrong binding: the exact shape the integrity gate exists for. A hand-written map lies silently; a generated one that greps cannot.
- **Date:** 2026-09-27 · **Refs:** `F40`, `operators/OPERATOR-REGISTRY.json`, `scripts/operator_registry_emit.py`

## lore-003 · ✖ DURABLE MYTH

**Story.** In the vacuum of space there is no hot; heat instantly diffuses away.

- **Told where:** this session (Zach, offered as a premise, 2026-09-27); common belief
- **Observation (real):** Space is cold; objects in shadow get very cold.
- **Mechanism claimed:** Absence of a medium makes heat leave instantly.
- **Test that decided:** A vacuum blocks conduction and convection; the only loss channel is radiation, which is slow. A thermos works by vacuum. Spacecraft struggle to dump heat.
- **Teaches:** The corrected mechanism was the better lesson: the vacuum is where nothing can be handed off, and the only loss is slow, invisible, toward the background.
- **Date:** 2026-09-27 · **Refs:** `forensic-quality-bar-correct-premise-name-loss-channel`, `_STATE/2026-09-27-forensic-recoil.md`

## lore-004 · ✖ OLD WIVES' TALE

**Story.** A clean room needs a vacuum.

- **Told where:** this session (Zach, 2026-09-27)
- **Observation (real):** Clean rooms have sealed doors and airlocks.
- **Mechanism claimed:** Cleanliness comes from removing the air.
- **Test that decided:** Clean rooms run at positive pressure with continuous HEPA-filtered laminar flow; negative pressure is for containment labs.
- **Teaches:** Clean because nothing stays, not because nothing enters. ARCS is the second kind: the corpus is supposed to breathe.
- **Date:** 2026-09-27 · **Refs:** `_STATE/2026-09-27-forensic-recoil.md`

## lore-005 · ✖ DURABLE MYTH

**Story.** Operator 20 (the folksonomy cultivator) has an import bug and is starved of real receipts; it is gated vaporware.

- **Told where:** handoffs and AGENTS.md before 2026-08-28
- **Observation (real):** An import error was observed when op20 was invoked.
- **Mechanism claimed:** The operator's code is broken.
- **Test that decided:** Full-fidelity op20 run over 247 real prod receipts via a faithful adapter: 17 archetypes at silhouette 0.765. The error was a harness error; the missing piece was a field adapter.
- **Teaches:** The observed error was real; the diagnosis was not. Test the operator, not the story about it.
- **Date:** 2026-08-28 · **Refs:** `F36`, `operators/prod_receipt_to_op20_seed.py`

## lore-006 · ✖ DURABLE MYTH

**Story.** Hermes never did any arcs-v9 work; its sessions table shows zero.

- **Told where:** cross-harness reconciliation, 2026-09-13
- **Observation (real):** The state.db sessions table has no arcs-v9 rows.
- **Mechanism claimed:** Absence in the table means absence of work.
- **Test that decided:** session_search (FTS) surfaced real repo-committing Hermes sessions from 2026-09-11, including the handoff push at 6c19ec6f.
- **Teaches:** A SQL-table absence is not proof of absence; the index you queried may not be the one that records the thing.
- **Date:** 2026-09-13 · **Refs:** `AGENTS.md#gotchas 14a`

## lore-007 · ✓ TRUE

**Story.** An end user, mid-call, said he was 'smelling arcs' while reaching for a word for how the conversation felt.

- **Told where:** Jeben x Zach call, 2026-04-21 (transcript); _CANON/great-moments.jsonl
- **Observation (real):** Verbatim line in the saved transcript, disfluencies preserved.
- **Mechanism claimed:** ARCS is perceptible from the outside as a sensation before it is a feature.
- **Test that decided:** Verbatim transcript on file; fact-checked 2026-08-23 against the source (attribution corrected).
- **Teaches:** The first recorded instance of the product being felt rather than described. Lore of the pre-witness era, recovered by generative recoil.
- **Date:** 2026-08-23 · **Refs:** `_CANON/great-moments.jsonl`, `ADR-066`

## lore-008 · ◇ INSPIRATION

**Story.** Trust is an outcome of a successful earned opinion.

- **Told where:** Zach, iMessage to Scott Witt, 2026-08-21; _CANON/great-moments.jsonl
- **Observation (real):** A one-line text, verbatim from screenshot.
- **Mechanism claimed:** Trust is not requested or asserted; it is the residue of opinions that were earned.
- **Test that decided:** (a mood board: cite as aspiration, never as fact)
- **Teaches:** Mood board for the source-trust ledger built 2026-09-27: tiers are derived from the record, never claimed. The text-register proverb became a generated table five weeks later.
- **Date:** 2026-08-23 · **Refs:** `_CANON/great-moments.jsonl`, `runtime/specs/source-trust.json`

## lore-009 · ✓ TRUE

**Story.** A flash of brilliance mid-conversation needs a scribe: 'can I get a witness' that the tree did fall and this is the sound it made.

- **Told where:** Zach, session night-moves-work-digest, 2026-08-11 (transcript, turn found by the backfill scout)
- **Observation (real):** The verbatim request exists in the transcript.
- **Mechanism claimed:** Naming moments evaporate unless attested at the moment, not at handoff.
- **Test that decided:** The witness register exists: 16 daily files since 2026-08-11, the /witness skill, the backfill scout (141 candidates) built 2026-09-27.
- **Teaches:** Lore that became mechanism: the request was itself the first witness-shaped moment, and the scout found it.
- **Date:** 2026-08-11 · **Refs:** `_STATE/witness/`, `scripts/witness_backfill_scout.py`

## lore-010 · ✓ TRUE

**Story.** The Claude Code harness loads only the first ~24KB of the memory index and silently drops the rest.

- **Told where:** global-session-start.sh comment, 2026-09-26; measured 2026-09-27
- **Observation (real):** An 80KB index produced a session that saw only the top sections.
- **Mechanism claimed:** A fixed read cap applied at a line boundary.
- **Test that decided:** Spawned session stoic-chandrasekhar-96414f: 144 of 382 lines injected, 25,284 bytes / 24,907 chars, warning appended. Cap sits in [24,907, 25,159] chars.
- **Teaches:** Measure the constant instead of repeating it. The earlier '~24.4KB' note was the same number, unverified until a session was spent on it.
- **Date:** 2026-09-27 · **Refs:** `memory-index-load-cap-observed`

## lore-011 · ◇ INSPIRATION

**Story.** ARCS should hold an Olympics: primitives, operators, ordinals and invariants compete under load, and the ones with unknown use cases are exalted. The torch is the flame's chain of custody, lit from one source, never from a lighter.

- **Told where:** Zach + Claude, session arcs-production-harness-arch, 2026-09-27 (witness stub)
- **Observation (real):** The graduation gate (RC-OPS-001) exists with four criteria and no ceremony.
- **Mechanism claimed:** A ceremony around the gate would make graduation legible and exalt cross-domain wins first.
- **Test that decided:** (a mood board: cite as aspiration, never as fact)
- **Teaches:** Mood board for the graduation ceremony: gauntlets as events, Loki and the Detective as judges, provenance as the drug test, write-lock as the truce. Kept as aspiration until a first games is held.
- **Date:** 2026-09-27 · **Refs:** `_STATE/witness/2026-09-27.jsonl`, `operators/RC-REGISTRY.json`

## lore-012 · ◇ INSPIRATION

**Story.** A song called Ephemeral Beauty, written the same day the membrane started breathing differently, embodies the mono no aware moment ARCS keeps circling: holding what fades.

- **Told where:** Zach, iCloud, 2026-09-27; lyrics embedded in the file (not reproduced here)
- **Observation (real):** 3:00, verse/chorus/verse/chorus/outro; the outro thins and quiets at 162s; the verb for letting appears five times.
- **Mechanism claimed:** Ephemeral RAM as a nod to mono no aware can spark a real ROM candidate (the 2026-08-01 line the scout surfaced).
- **Test that decided:** (a mood board: cite as aspiration, never as fact)
- **Teaches:** Mood board for the ephemeral-to-durable etch: the song releases rather than resolves, which is what the witness register does to a moment.
- **Date:** 2026-09-27 · **Refs:** `_INBOX/witness-backfill-candidates.jsonl (candidate 2026-08-01T06:10)`
