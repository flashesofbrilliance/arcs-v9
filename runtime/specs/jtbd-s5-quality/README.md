# JTBD s5 quality rerun pool (EARLY/INTERIM, prepared 2026-11-01, day 12 of 28)

**This run informs but does not replace the official check dated 2026-11-17 (backlog row `jtbd-graph-s5-feedback`).** Pass rule is fixed by `_PATTERNS/2026-10-20-jtbd-s5-preregistration.md` (Tests, Quality): graph passes >= 16 of 18 AND mean essential recall >= 0.89. Pool rules: amendment 7. Per-query pass: at least one essential item and wrong items <= half the system's items.

## Files
- `queries-rows-1-18.json`: the same 18 job statements as s4 (labels not copied).
- `graph-raw.json`: `python3 operators/jtbd_query.py "<job>"` per job at sha `5864abda`.
- `catalog-raw.json`: fresh subagent, read only `.claude/commands/catalog.md` and `runtime/specs/tool-catalog.json` (plus the job-text file), one shot per row. Step 0 of the command (graph lookup, added after s4) was skipped so this is the catalog baseline, not the graph in disguise. The catalog now holds more tools than at the s4 start sha (disclosed; it is the catalog as it exists today).
- `source-mapping.json`, `pool-key.json`: system labels. **Sealed. Never show to the judge.**
- `pool-sealed.json`, `JUDGE.md`: the blind pool (shuffle `random.Random(20261020 + row)` over the sorted union).
- `score.json`: written by the scorer after judging.

Prepared by a session other than the s5 builder. This session did not judge and has not seen marks.

## Handing JUDGE.md to the judge
Give the judge ONLY `runtime/specs/jtbd-s5-quality/JUDGE.md` (copy it out as a standalone file, or paste it). Do not give the repo, the key, `pool-sealed.json`'s directory, or any other file in this folder. The judge writes E, U or W after each arrow and may fill the `Missing:` line. Judge = Zach, or a fresh session with no repo access that sees only that file.

## Scoring (opens the key; run only after marks are in)
```bash
python3 scripts/jtbd_s5_quality_pool.py score path/to/filled-JUDGE.md
```
Prints the verdict and writes `score.json`. `python3 scripts/jtbd_s5_quality_pool.py --self-test` re-scores the s4 marks and must give graph 16/18, recall 0.89, catalog 6/18. `pool` regenerates everything from the raw files.

## Caveats
Same known weakness as amendment 7: five-item graph lists vs a one-item catalog answer. The graph has also had 12 days of new edges/receipts since s4, so a different result is expected and meaningful either way.
