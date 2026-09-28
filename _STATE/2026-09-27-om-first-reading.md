# Om, first reading (2026-09-27)

The first instrumented reading of the Hypersphere manifold's fifth axis (Flow-State, WORLD.md).
Taken by `scripts/shavasana_handoff.py` (commit f8bd5ec3, branch claude/zen-pasteur-85c635) on
the drafting session's own handoff draft, per spec `runtime/specs/operator-25-shavasana-v0.md`
("The om metric", instrument table) and assumption asm-009 in `_STATE/assumptions.jsonl`.

Conviction was not given: Zach was not present in the session, so `om_gap` is null on this
reading. It is recorded as the zero point of the series, not as a value. The ten-handoff read that
decides asm-009 starts here.

## Fields (`--json`)

```json
{
 "day": "2026-09-27",
 "draft": "/private/tmp/claude-501/-Users-zharris-arcs-v9--claude-worktrees-zen-pasteur-85c635/3bad16f0-2c9c-42d6-bd08-461db81c4cc0/scratchpad/draft-handoff.md",
 "exhale": {
  "commits": 59,
  "merges": 18,
  "receipts_in_digest": 0
 },
 "inhale": {
  "falsification_rows_today": 3,
  "dissent_markers": 16,
  "unconfirmed_markers": 7,
  "agreement_markers": 30
 },
 "breath": {
  "balance": "breathing (both directions)",
  "exhale_n": 59,
  "inhale_n": 26,
  "net_direction": 33,
  "lean": "exhale-leaning"
 },
 "sycophancy": {
  "agreement": 48,
  "dissent": 26,
  "ratio": 1.78,
  "verdict": "OK: dissent present"
 },
 "cold_reread": {
  "verdict": "GROUNDED",
  "alarms": [],
  "thin": []
 },
 "confidence": 0.33,
 "backed_sections": 1,
 "total_sections": 3,
 "conviction": null,
 "om_gap": null,
 "breath_net_direction": 33,
 "new_claims": 0
}
```

## Block as emitted

### Shavasana — handoff pause, 2026-09-27 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 59 commits, 18 merges to main, receipts in digest: 0.
- **Inhale** (what came in): 3 falsification rows today, 16 dissent markers, 7 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Breath net direction** (Maekawa; asm-009 open, read across ten handoffs): exhale 59 minus inhale 26 = +33, exhale-leaning.
- **Sycophancy check**: agreement 48 / dissent 26 (ratio 1.78) → OK: dissent present.
- **Cold re-read (canary on the draft draft-handoff.md)**: GROUNDED; no ground return: none; thin air: none.
- **Om** (Flow-State axis; component 7): confidence 0.33 (1 of 3 sections carry a ground return); conviction: not given (--conviction absent); om_gap: null, not imputed.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today? Give the number as `--conviction 0-10` and re-run.
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._


## How to take the next reading

```bash
python3 scripts/shavasana_handoff.py --draft <draft-handoff.md> --conviction <0-10> --json
```

Append the JSON to this file under a dated heading. The ten-handoff series for asm-009 reads
`breath_net_direction` against the count of open loops the handoff leaves; `om_gap` reads against
whether the release was later returned.
