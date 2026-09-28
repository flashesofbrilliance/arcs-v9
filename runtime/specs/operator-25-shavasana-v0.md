# Operator 25 — ShavasanaSpace · operational definition v0 (CANDIDATE)

> **Status:** CANDIDATE, ethereal stage of the hyperstition pipeline (ethereal → Loki test →
> receipt evaluation → ROM). Nothing here is built. Registry row 25 stays UNBUILT until an
> implementation exists AND has caught one real over-momentum act. Induced 2026-09-27 in session
> `arcs-production-harness-arch-f4f38e` from the breathing/membrane exchange (Zach: "the deep
> shavasana recall is the meditative breath that inhales and exhales until the two are entangled
> into an indistinguishable om"; "this is the carrier signal for that operator 25").
> **Periodic table row:** 25 · Shav · ShavasanaSpace · Wisdom · Contemplative pause · The Meditation.
> **Prior art in-repo (the prototype without the name):** `/thread-recoil`, `/night-moves`, the
> drift sentinel (WORLD.md: five turns without an artifact), the Fun.xyz autosend post-mortem
> (`tao-256`: "a draft is not a verb"), `_STATE/2026-09-27-forensic-recoil.md`.

## Operational definition (one sentence, LEGEND-grade)

**Shavasana is the mandatory do-nothing interval between the last effortful operator and any
irreversible act, in which the system stops generating, audits the session's breath (what came in
by recoil, what went out by hyperstition), releases every claim that does not survive a cold
re-read without its momentum, checks for agreement without dissent, takes the human's felt read,
and emits an integration receipt that contains no new claim, after which the act is released or
returned to the queue.**

Corpse pose: the posture where nothing is done and the practice consolidates because you stop
driving it. Not a timer. A level trigger on conditions.

## What it is NOT (the Loki pre-read)

- Not a sleep. A fixed delay is chronos; Shavasana is kairos. It fires on the shape of the moment
  (a one-way door approaching), not on the clock.
- Not a summary. It adds no claim. A summary that introduces a conclusion is an exhale wearing a
  blanket.
- Not a veto. It cannot refuse the act (NOTOMATION). It can only return it to the queue with the
  integration receipt attached; the human releases.
- Not sycophancy in reverse. Releasing every attachment is as dishonest as keeping every one. The
  release test is "does it survive cold," not "does it feel humble."

## Decomposition (eight components; mechanical vs judgment per the metabolic router)

| # | Component | What it does | Kind | Nearest existing code |
|---|---|---|---|---|
| 1 | **Trigger** | fires on level: pre-send, pre-merge, pre-handoff, pre-write-lock, drift sentinel (N turns no artifact), post-gauntlet. Never on a timer. | mechanical | `scripts/git-hooks/pre-commit` (pre-merge hooks), WORLD.md drift sentinel (prose only) |
| 2 | **Stillness window** | a read-only interval: no mutating tool calls, no new generation of claims. Length scales with stakes × irreversibility (BAR inputs), never with the clock. | mechanical guard | none; nearest is the outbound-send deny (forbidden-fruit guard) |
| 3 | **Breath audit** | runs the inhale ledger (thread-recoil: priors moved by external ground) and the exhale ledger (what was claimed, committed, sent this session). Computes the balance (exhale with no inhale = manifesto; inhale with no exhale = mirror) AND the signed net direction `exhale_n - inhale_n` (Maekawa, LEGEND: a node whose folds balance does not lie flat; asm-009 in `_STATE/assumptions.jsonl` is OPEN on whether balanced sessions leave more loops open, tested across ten handoffs, so the script reports the sign and attaches no verdict). | mechanical counts, judgment on rows | `scripts/shavasana_handoff.py` `breath()`; `/thread-recoil`, `/night-moves` gather |
| 4 | **Attachment release** | each open claim is re-read cold (the cold-reconstruction control: no momentum, no author warmth). Survives → stays at its Y. Does not → downgraded or dropped, logged. | judgment (human, or a LAB pass as pre-score) | `arcs_operators_lab.py` LokiChallenge; NFTT cold-reconstruction post |
| 5 | **Sycophancy check** | agreement ratio across the session's operators vs presence of dissent. Agreement above threshold with no Loki/Detective dissent on record → the act returns to the queue for re-evaluation. (The one net-new mechanic salvaged from the 2026-09-27 external audit, its FR-3.) | mechanical threshold | none built; LAB emits the dissent it would read |
| 6 | **Somatic read** | the human's felt state, asked once: certainty now vs certainty at the prep, given as one number, conviction 0-10 (`--conviction`). The delta is data; the human supplies it (a receipt cannot close itself). Absent → recorded as null; the script does not impute it from anything. | human input | `scripts/shavasana_handoff.py --conviction`; PrepSession fields (`stakes`, `confidence`); `SomaticReading` in `arcs_primitives.py` |
| 7 | **Integration receipt** | emitted with NO new claim: what was released, what stayed, the breath balance and its net direction (`breath_net_direction`, signed), the sycophancy reading, the somatic delta, and the om metric (`confidence`, `conviction`, `om_gap`; contract below). Self-test asserts zero confidence markers by the altitude canary's own regex and at least one ground return. | mechanical emit | `scripts/shavasana_handoff.py` `block()` / `fields()` (`--json`); `CoherenceReceipt`; `decision_receipt` form (`what_confirmed` / `what_unconfirmed`) |
| 8 | **Release or return** | the act proceeds, or goes back to the induced backlog with the receipt attached. Always the human's move. | human | `_QUEUE/induced-backlog.jsonl` |

## The om metric (the entanglement, made countable)

On the claims that survive component 4, measure the gap between **confidence** (what the evidence
supports; the backed fraction) and **conviction** (what the human holds; the somatic read). The
om is the state where the gap is near zero across the surviving set: inhale and exhale at the same
frequency, a standing wave. It is a reading, not a target: a session can be perfectly grounded and
still leave the human unconvinced, and that gap is the most useful line on the receipt. The books
still record which direction each claim arrived by; the om is the felt state, not the bookkeeping.

**Instrument (v0, built 2026-09-27; the first reading of the Hypersphere manifold's fifth axis,
Flow-State, WORLD.md).** Emitted by `scripts/shavasana_handoff.py` on the handoff block and as
`--json` fields:

| Field | Definition | Kind |
|---|---|---|
| `confidence` | backed fraction of the draft: sections with at least one ground return (the cite classes `scripts/altitude_canary.py` counts: ADR, sha, repo path, script name, URL, receipt id, memory link) divided by non-empty sections. Reads the draft as handed; re-run after the cold re-read (component 4) drops claims to read the survivors. Null with no draft. | mechanical |
| `conviction` | the human's felt read, 0-10, from `--conviction` (component 6). Null when absent. Not imputed from PrepSession, from the canary, or from anything else. | human |
| `om_gap` | `abs(confidence - conviction/10)`, rounded to 2 places. Null when either side is null. | mechanical |
| `breath_net_direction` | `exhale_n - inhale_n`, signed. `exhale_n` = commits + receipts in the digest; `inhale_n` = falsification rows + dissent markers + unconfirmed markers. Reported alongside the balance string; no verdict on the sign until asm-009 is decided. | mechanical |

Reading the gap: near zero with a high `confidence` is the om; near zero with a low `confidence` is
shared doubt (also honest); a large gap is the line to talk about before the release. The section
denominator is coarse by design (v0): a finer claim unit (sentence or bullet) is a v1 change to
this table, not a silent reinterpretation of the number. First dated reading:
`_STATE/2026-09-27-om-first-reading.md`.

## Input / output contract (for the eventual `operators/arcs_shavasana.py`)

```
ShavasanaOperator.run(
    session: SessionContext,        # turns, claims, sends, commits, operator outputs
    act: PendingAct,                # the irreversible thing that triggered it (send | merge | lock | handoff)
    somatic: SomaticReading | None, # the human's felt read, if given
    stakes: str, irreversibility: float,
) -> ShavasanaReceipt {
    trigger, window_len, breath_balance {inhale_n, exhale_n, net_direction (signed), verdict},
    released [claim, from_y, to_y, why_cold_failed], kept [claim, y],
    sycophancy {agreement, dissent_present, verdict},
    somatic_delta, confidence (0..1 | null), conviction (0..10 | null, human), om_gap (| null),
    new_claims: 0 (asserted, checked),
    disposition: "released" | "returned"
}
```

Bridge binding when built: registry row 25 → `arcs_shavasana.py` · `ShavasanaOperator` · `run` ·
call kind `callable`. `new_claims` is a hard assertion: a receipt with a new claim fails its own
self-test.

## Graduation criteria (what moves this from CANDIDATE to a READY row, then toward ROM)

1. Implementation exists, self-test proves: (a) it refuses to add a claim, (b) it returns an act
   when agreement is high and dissent is absent, (c) it fires on a pre-send with no timer.
2. It catches **one real over-momentum act** before the act lands (the Fun.xyz autosend class).
   Until then it is a description.
3. Its own receipts pass the altitude canary and the integrity gate (it cannot describe stillness
   in thin air).
4. Ouroboros: it has run on the session that built it and released at least one of its author's
   own claims.

## Lineage

Witness `_STATE/witness/2026-09-27.jsonl` (diamonds; torch) · `tao-257` (cron vs kairos) ·
`seed-service-librarian-retrieval-policy` (the reserve ratio the breath audit reads) ·
[[forensic-quality-bar-correct-premise-name-loss-channel]] · `operators/OPERATOR-REGISTRY.json`
row 25 (UNBUILT, nearest: this spec).
