# Dreaming pass 8 (nightly, 2026-11-11)

Proposals only. Nothing here is applied; Zach rules each row ACCEPT, AMEND or REJECT.

## Header

- Worktree: /tmp/dream-2026-11-11 at origin/main 2a2a19c9.
- Quiet-night check: 66 commits across all refs in the last 26h; 0 files changed under ~/Downloads/gauntlet-2026-11-06/ in 26h.
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 36 transcripts, 10 error clusters (>= 2 sessions), 10 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1363 docs, 137 dead cites, 113 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 41 orphans, 7 cited, 0 unregistered, 0 awaiting a fate.
- `python3 scripts/memory_index_sync.py --check`: "memory-sync: 1-1 OK".
- Slice: dropped everything in `_PROPOSALS/*-dreaming-*.md` on main (passes 1 to 3) and in open draft PRs #2061 (pass 4), #2071 (pass 5), #2085 (pass 6), #2111 (pass 7). RESIDUE-for-dream-2026-11-06.md is already cited by passes 4 to 7; not re-used.
- KINTSUGI.md not re-read this pass; ranking is by evidence strength, not rows prevented.
- Under 40 items: judged inline, no scouts. 9 of 10 clusters and all 10 corrections were already covered by passes 4 to 7.

## Proposals

| id | pattern | prevalence | existing guard | proposal | file it would edit | risk |
|----|---------|-----------|----------------|----------|--------------------|------|
| J1 | Browser probes of the token tuner run `document.querySelector('[data-arcs-token-tuner]').shadowRoot` and get null, so the next `.querySelectorAll` throws "Cannot read properties of null (reading 'querySelectorAll')". | 2 sessions, both 2026-11-10: d6dcefa4 14:35:09Z (worktree agitated-nightingale-d1cdcc) and c2139dd4 21:28:15Z (worktree optimistic-leakey-d2316e). Both failing inputs read from the transcripts this pass; both use the same selector. | None found. Cause, read from src/ui-kit/token-tuner.js this pass: the same attribute is set on `<style>` tags appended to `<head>` (line 154 value `dbl`, line 318 and 542 `wrap`, line 581 `edit`) and on the shadow host (line 365, value empty). querySelector returns the first match in document order, a head `<style>` with no shadowRoot. Unverified: where the host is appended (body assumed; not read). | Give the host its own hook: `host.setAttribute('data-arcs-token-tuner', 'host')` and set `window.__arcsTunerHost = host`; add one line to the header comment: "probe with `window.__arcsTunerHost.shadowRoot`, not `[data-arcs-token-tuner]`". The `closest('[data-arcs-token-tuner]')` exclusions keep working, since they match any value. Mirror the change in src/ui-kit/recoil-report/40-token-tuner.html (it carries the same code at line 391). | src/ui-kit/token-tuner.js; src/ui-kit/recoil-report/40-token-tuner.html | Low. No caller outside these two files selects the host (grep across the repo this pass). A probe written as `[data-arcs-token-tuner=""]` would stop matching; none found. |

## Evidence updates to proposals still open (not new proposals)

- Pass 7 I1 (memory index over budget): resolved for now. MEMORY.md is 24,543 bytes (mtime 2026-11-10 09:25), under the 24,576 budget; memory_index_sync --check reports OK. Headroom 33 bytes, so the optional `--append` refusal in I1 still stands; the consolidation half can be closed.
- Pass 7 I3 (hardcoded preview ports in .claude/launch.json): now 3 sessions (adds c2139dd4 2026-11-10 21:27Z). launch.json unchanged on main since 93b35eeb (2026-10-07); still 6 configs with ports in argv.
- Pass 5 F1 (bash 3.2.57 harness refusal, exit 126): now 24 hits in 10 sessions (pass 7: 18 in 10). Still the strongest unruled item.
- Pass 5 F3 (`ValueError: substring not found`): 4 hits in 3 sessions, no new hits.
- Pass 5 F5 (write hook blocks writes into another worktree): 2 sessions, no new hits.
- Pass 7 I2 (worktree branch tracks origin/main, bare push fails): 2 sessions, no new hits. This pass's own step 1 used the same `worktree add -b ... origin/main`; pushed with `git push origin HEAD:<branch>` to avoid it.

## Not proposed

- `JSONDecodeError: Expecting value` (2 sessions, 22d2d282 2026-11-07 and 7757e3eb 2026-11-09): covered in pass 6.
- 10 corrections: same set judged in pass 7 (client scope, tone, tax; no repo behavior). Watch items from pass 7 ("stop number" jargon, .docx render check) got no second session.
- Corpus: 137 dead cites (pass 7: 137), 113 stale verifications (pass 7: 111). Classes ruled in pass 3; new items not isolated. Unverified.

## False-positive shapes to drop from the scan

- User tool rejections (13 sessions this window): consent, not an error. Fifth pass in a row; exclude "The user doesn't want to proceed" in dream_mine.py.
- `[resize_window] Viewport emulation cleared`: informational (repeat).
- `head: illegal line count -- 0` inside the "book the seam" cluster: repeat.
