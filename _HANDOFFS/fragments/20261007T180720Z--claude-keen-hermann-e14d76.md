<!--
session: claude-keen-hermann-e14d76
branch: claude/keen-hermann-e14d76
head: cc85c8b4
created_at: 2026-10-07T18:07:20Z
-->
## Changed
- #1068 merged (`d5a831ff`, `--merge`, 2026-10-07T18:01:31Z): decision-geometry explorer over real receipts (`public/pf-decision-geometry.html`, served at `/decision-geometry` on app.arcs.care and playground.arcs.care via `next.config.ts` rewrites), `GET /api/geometry` feed with server-decided fidelity (admin, owner, text-free public), `tests/decision-geometry.spec.ts`, dopeness eval v0.
- Production `dpl_BxoqpbitCdKKbpGk2wsys7Z9GAG1` READY for `d5a831ff`, aliased to app.arcs.care and playground.arcs.care (Vercel get_deployment).
- Verified live by this session (`claude/keen-hermann-e14d76`): app.arcs.care signed in reads fidelity admin, receipts 269/269, sessions 161, users 5, phase SUPERIONIC; projections A polar, B ziggurat, C hypercube render on M; drawer for receipt i=142 shows 25 cells, PULL TRACES and MAGNETIC SNAP. playground.arcs.care banner reads "Public fidelity"; `curl /api/geometry` has 0 `q`/`tn`/`id` keys and 269 of 269 `t` values day-granular. Playwright spec against playground: 7 passed.
- Screenshots: `_ARTIFACTS/decision-geometry-verify-2026-10-07/` (6 jpg).
- Receipt `2026-10-07--decision-geometry-explorer-verify-pr1068--ZH` (decision_receipt).

## State
- Specs are DRAFT: `runtime/specs/dopeness-eval-v0.md`, `runtime/specs/decision-geometry-cells-v0.json`, `_STATE/2026-10-07-tool-cluster-jtbd-map.json`. The adversarial verifier workflow (14 agents, output kept at the originating session's task path `w7oi2kc36.output`) recorded corrections that are NOT yet folded into the specs:
  - Cells: 12 of 46 claims refuted, 3 unverifiable. Key refutations: DELTA has two triggers (parent nci band shift as well as hasRed, `ygate.ts:170-180`); sessionVersion is parent.version + 1, not a count of session rows; driftState DRIFTING is outcome-driven (matched false) not version-driven; PrepSession.stakes/horizon equal Receipt.stakes/window by assignment so they carry no independent evidence; confidence = 1 is a ygate input so independence holds only for 2 to 5; inline prep can leave prepId null on a calibrated receipt; `observatory/page.tsx:30-36` already defines an L1 to L5 altitude rung map (off by one from the model's); the contract altitude sample uses a U+2013 en-dash so the `L(\d)-L(\d)` parse returns lo=hi=1 on the contract's own sample; "5R: no field" is false (ScanSignal.networkResonance exists, still unmappable to a receipt cell); D1 coverage L2 must read ~267 since coherencePct presence was not measured; the "0 of 267 by code path" for six columns rests on a route grep, not SQL.
  - Clusters: 4 of 16 spot checks refuted: `arcs_no_go_inventory.py` and `arcs_seed_bar.py` are not decision-lens members (post-hoc failure catalog; BAR there means Belief-Action-Rationale templates); `sugar_bulk.py` is a PRL CRM payload builder, not counterpart-facing; `fates.py` is the fate registry, not page authoring. The map also double-books 11 tools as both members and orphans.
  - Critic: `src/app/api/tribune/route.ts:205` writes batonId (so "no write path" is wrong for that column); `provenance` is client-settable by any signed-in caller; the founder userId is unrecorded so the founder cohort split is assumed; COURT and ONE_WAY are one predicate in `compass/route.ts` (same 96 rows by construction); the shipped `parseKairos` differs from the cell model's parse; ladder tier A's GREEN clause is not SHARP (CONTESTED renders DEGRADED); ladder fields use pseudo-paths not prisma names; the day-counting unit differs between tier D (sessionId) and tier B (userId).
- Admin fidelity shows no banner by design (only public and owner set one); the fidelity statement lives in the stats line.

## Decisions
- Merge handled by the originating session; this session verified only and did not merge.
- Receipt logged in the fixed form with the JS-dispatched drawer open listed as unconfirmed rather than claimed as a click.

## Open
1. Zach: pick the landing projection (A polar is the default today).
2. Preview env `DATABASE_URL` is rejected by Postgres (P1000); previews cannot reach the DB, so preview checks of the feed return 503.
3. Three kintsugi detector all-caps-label findings on the new page.
4. Fold the verifier corrections above into the three DRAFT specs (batonId and provenance first; they change the eval's judgment rules), align ladder field names to prisma names, and re-run the two unrun modalities (staged Playwright spec now passes on prod; the Vercel event cross-check is still unrun).
5. Drawer open was proven by dispatching pointer events and `openDrawer()` from JS; a human click on the canvas was not observed. Stray slider state changes (time, resolution, lomo) appeared during the Chrome session and were not diagnosed.
6. `provenance` is client-settable on the compass body; decide whether the server should ignore it for non-admin callers.

## Next action
Fold the verifier corrections into `runtime/specs/dopeness-eval-v0.md` and `decision-geometry-cells-v0.json` (start with batonId write path and client-settable provenance), then mark them past DRAFT.

## Cold-start
- Page: `public/pf-decision-geometry.html`; feed: `src/app/api/geometry/route.ts`; rewrites: `next.config.ts` lines 92 to 96 (playground) and 205 to 208 (app).
- Gate: `SMOKE_BASE_URL=https://playground.arcs.care npx playwright test tests/decision-geometry.spec.ts --reporter=line`.
- Feed shape check: `curl -s https://playground.arcs.care/api/geometry | head -c 600` must show no `"q":` and only `"t":"YYYY-MM-DD"`.
- Receipt: `2026-10-07--decision-geometry-explorer-verify-pr1068--ZH`.

## Lessons
- Claude in Chrome clicks on a canvas can land on neighbouring controls; prove a pick by dispatching the page's own pointer events and reading the drawer state, and record it as a dispatch, not a click.
