# Receipt-Save Nudge Spec - v1 (consent surface, not a capture fix)

**Status: BUILT BEHIND FLAG (default OFF). Trigger was NOT met on 2026-09-27 (spec-only); it flipped on 2026-09-28 when PR #586 merged the funnel split to origin/main, and §6.2 + §6.3 were built the same day in PR #595. §6.1 (Vercel Web Analytics toggle) remains Zach's.**
**Date:** 2026-09-27, amended 2026-09-28
**Backlog row:** `notomation-receipt-save-nudge` (rank 6, GitHub issue #583), blocked by `outcome-capture-rate-keel-gap`
**ADR references:** ADR-016 Option C (anonymous compass), ADR-049 (opt-in save, trust contract v1.2), ADR-068 (print schedule)
**Verified against:** origin/main `e36084f4`, sibling branch `claude/accountant-keel-funnel` (PR #586, open), Vercel project `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`

---

## 0. Trigger check (the gate this chip waits on)

| Condition | Result 2026-09-27 |
|---|---|
| A funnel split JSON exists under `_STATE/` on **origin/main** | **NO.** `git ls-tree origin/main _STATE/` has no funnel/split/cohort file. |
| The split exists somewhere | Yes, but on a branch: `_STATE/outcome-funnel/2026-09-27.json` on `claude/accountant-keel-funnel`, PR #586, unmerged. |
| Building now would collide | Yes. PR #586 also edits `src/app/dashboard/page.tsx` (adds `?horizon=`). A second dashboard edit before it lands is a merge conflict by construction. |

Per the route ("LEVEL TRIGGER: do not build until a funnel split JSON exists under `_STATE/` on origin/main"), this session reads, specs, and stops. The build branch of this spec (section 6) is executable the day PR #586 merges.

The split itself, read from the branch so the spec is shaped by real numbers:

| segment | receipts | users | ephemeral saves | debrief sent | closed | last receipt | last 30d |
|---|---|---|---|---|---|---|---|
| external | 10 | 4 | 0 | 6 | 0 | 2026-07-10 | 0 |
| founder | 196 | 1 | 1 | 135 | 3 | 2026-09-27 | 7 |
| anonymous (legacy, pre 2026-07-13) | 48 | 0 | 0 | 0 | 0 | 2026-07-13 | 0 |

Read: there has been no external receipt in 79 days. A nudge shown to nobody measures nothing. The upstream move is distribution (PR #586 links the `/fears` page into the compass); this nudge is downstream of that inflow.

---

## 1. Premise correction (read before anything else)

The chip's JTBD says "build a consent-gated nudge on the dashboard after a compass run that offers to keep the receipt." Two parts of that premise are wrong against source:

1. **The nudge already exists and has been live since 2026-07-13** (ADR-049 Phase 2, commit `750d2872`). End to end:
   - `src/app/receipt/[receiptId]/page.tsx` renders, for any `eph_` id, a gold NOT STORED banner with a "Sign in & save" button.
   - The button stashes the bearing in `localStorage["arcs_pending_save"]` (7-day TTL; localStorage, not sessionStorage, because a magic-link click opens a new tab) and routes to `/compass` (the sign-in page).
   - `src/components/ClaimAnonymousReceipts.tsx`, mounted in the root layout so it fires on whatever page the magic link lands, checks the session, POSTs the pending bearing to `POST /api/receipts/save`, clears the stash, and hard-navigates to the new `/receipt/<id>`.
   - `src/app/api/receipts/save/route.ts` writes only post-auth, recomputes the Y gate server-side, clamps every field, marks the row `surface: "EPHEMERAL_SAVE"`, and sets `reminderDate` so the row enters the same debrief cron as pipeline-minted receipts (`src/app/api/cron/debrief/route.ts` selects on `userId not null` + `reminderDate`, not on surface).
   - `src/app/brief/share/page.tsx` reuses the same stash for a one-time shared bearing.
   - A save route with "no caller" was my own first read and it was wrong: the grep filtered its own match. Corrected here so the next session does not repeat it.

2. **The dashboard is the wrong surface.** After a run, `runCompassWith` in `src/app/dashboard/page.tsx` immediately `router.push()`es to `/receipt/<id>` (persisted) or `/receipt/eph_<uuid>` (anonymous, bearing in sessionStorage). Nothing post-run is ever seen on the dashboard. The post-run surface is the receipt page, and that is where the existing nudge lives.

3. **`PATCH /api/receipts/claim` is legacy, not the nudge's path.** It reassigns pre-2026-07-13 anonymous rows (the 48 retained under ADR-049) by `sessionId`. New anonymous runs persist nothing, so for any new visitor it is a no-op. It stays because the retained rows remain claimable.

So the honest scope of "chip 6" is not "build the nudge." It is: (a) measure the nudge that exists, (b) close the small recovery holes in it, (c) decide from evidence whether any second touch is warranted.

---

## 2. Evidence of use (what the existing nudge has done)

| Signal | Value | Source |
|---|---|---|
| `EPHEMERAL_SAVE` rows, all time | 1 (2026-07-21, signed-in founder test) | `_STATE/2026-09-27-receipt-outcome-export.json` on origin/main |
| External ephemeral saves | 0 | funnel split, PR #586 |
| `receipt_save_clicked` / `_completed` / `_failed` counts | **unmeasurable** | Vercel API returns `404 Web Analytics not found` for project `arcs-v9` (checked 2026-09-27 via `count_events` and `aggregate_events`) |

The third row is the finding. The `<Analytics />` component is mounted in `src/app/layout.tsx` and `track()` is called at three points, but Web Analytics is not enabled on the Vercel project, so every event is dropped at the edge. The instrument is described, not wired (memory `control-integrity-described-vs-wired`). The cheapest real work item in this whole chip is a dashboard toggle, not code.

---

## 3. Where the nudge appears

**v1 (already live):** the ephemeral receipt page only, inside the NOT STORED banner, directly under the header rule and above the Decision block. One instance per bearing. It appears because the visitor is looking at a result that will vanish when the tab closes; that is the only moment the consent question is honest.

**Never:** on the dashboard (nothing post-run renders there), on `/`, on the sign-in page, in email, as a modal, as an exit-intent interstitial, or on a persisted receipt (there is nothing to save).

**Secondary (already live):** the ephemeral error card ("This bearing didn't travel here") offers "Sign in to keep bearings" for the next run. Keep.

---

## 4. What it says

Current copy (live since July, unblessed in the draft-first sense but shipped under ADR-049):

> NOT STORED. This bearing lives only in this browser tab, per the trust contract. Save it to your ledger by signing in.
> [Sign in & save]

Proposed v1.1 copy (DRAFT, Zach blesses before any change; the only edit is to name the cost and the exchange plainly):

> NOT STORED. This bearing lives only in this tab and is gone when you close it. Keep it: sign in with a magic link and it lands in your ledger, with a check-in at the horizon you chose.
> [Keep this bearing] [Let it go]

Rules for the copy, whichever version ships:
- Names what is true now (not stored), what the visitor gives (an email, one click), and what they get (the row plus the horizon check-in). No urgency words, no counters, no "don't lose."
- "Let it go" is a real dismiss that hides the banner for this bearing only (state in sessionStorage keyed by the `eph_` id). Dismiss is never remembered across bearings; the next run is a new consent moment.
- Tone per WORLD.md: calm, precise, an instrument, not onboarding confetti.

---

## 5. What it never does (the NOTOMATION and trust-contract floor)

1. **Never writes before auth.** The only write path is `POST /api/receipts/save`, which 401s without a session. `/trust` §1 and `/privacy` ("no auth = no write path") hold to the letter. A pre-auth counter of clicks would be request metadata, which the trust page permits, but it is not needed: Web Analytics covers it once enabled.
2. **Never auto-saves.** The human clicks. Landing on the site signed-in does not save an ephemeral bearing unless the stash exists from a click.
3. **Never emails on its own.** Sign-in sends the magic link the visitor asked for. The horizon check-in email follows only because the saved row enters the existing debrief pipeline, gated by `debriefOptIn` after the first send. The nudge adds no send path.
4. **Never re-runs the compass.** Per memory `client-fetch-failure-is-not-persistence-failure`: a client error after a run is not proof the bearing was lost. For signed-in runs, the dashboard already polls history by `sessionId` and routes to the recovered receipt. For anonymous runs nothing was persisted, so there is nothing to recover server-side; the recovery target is the browser stash (section 6.2), never a second Anthropic call.
5. **Never infers.** No matched, no regret, no outcome is derived from the save. The save is a consent record for a bearing the visitor already saw.
6. **Never nags.** One banner per bearing. Dismiss is honored. No second touch on the next visit, no "you have N unsaved bearings."
7. **Never gates the result.** The bearing, the tributaries, and the one-time share all render whether or not the visitor saves.
8. **Never sets the legacy `arcs_session_id` claim cookie** (removed 2026-07-13; the comment in the compass route is the record).

---

## 6. Build branch (executable only when the trigger holds)

Order is by evidence-per-line-of-code. Each step is independently shippable and reversible.

### 6.1 Turn the instrument on (zero code, Zach's toggle)
Enable Web Analytics on Vercel project `arcs-v9`. The three existing events then measure clicked, completed, failed. Until this is on, no copy change can be evaluated and steps 6.3 onward must not ship.

### 6.2 Close the two recovery holes (small, no flag needed, no copy change)
- In `ClaimAnonymousReceipts.tsx`, the outer `catch` around the pending save removes `arcs_pending_save` on any exception, including a dropped network request. Change: remove the stash only on JSON parse failure or TTL expiry; keep it on a network exception so the next page load retries. A failed POST already keeps it (the `!r.ok` branch does not remove), so this aligns the two failure shapes.
- In `receipt/[receiptId]/page.tsx`, the ephemeral error card fires when `sessionStorage` has no entry for the `eph_` id. Before erroring, check `localStorage["arcs_pending_save"]`; if its bearing exists and is unexpired, render it with the banner instead of the error. This is the case "clicked save, magic link opened in a new tab, came back to the old tab URL": the bearing is not lost, it is one storage layer over.

### 6.3 Copy v1.1 behind a flag (only after 6.1 and after Zach blesses the copy)
- Flag: `NEXT_PUBLIC_RECEIPT_SAVE_NUDGE_V11 === "true"` on the client, mirrored as `receiptSaveNudgeV11` in `src/lib/flags.ts`, following the exact `NEXT_PUBLIC_OUTCOME_NUDGE` pattern already in the dashboard. Default OFF. Off renders the current banner unchanged.
- Add the dismiss ("Let it go"), sessionStorage-scoped to the `eph_` id.
- Track `receipt_save_dismissed` alongside the three existing events so the ratio clicked : dismissed : ignored is visible.
- Inline styles only, `Button` primitive, existing tokens (`signal.gold`, `text.secondary`, `border.subtle`). No new molecule, no new dep.
- `npm run build` (never bare `next build`), then `privacy-review` on the diff because it touches the trust-contract surface.

### 6.4 Do NOT build
- A dashboard banner: nothing post-run renders there.
- A count-based nudge ("you've run 3, sign in to see them"): ADR-016 mentions it as the history gate; it is a different surface and needs the history page, not the receipt page.
- Any server-side record of anonymous clicks.
- Any change that makes the banner louder before 6.1 shows the quiet one is being ignored rather than unseen.

---

## 7. Measurement (what "it worked" means)

Read weekly from two places, founder and external always separate (per `scripts/outcome_funnel.py` in PR #586):

| Metric | Source | Baseline 2026-09-27 |
|---|---|---|
| `receipt_save_clicked` / ephemeral views | Vercel Web Analytics (after 6.1) | unmeasured |
| `receipt_save_completed` / `receipt_save_clicked` | Vercel Web Analytics | unmeasured |
| `EPHEMERAL_SAVE` rows by segment | `outcome_funnel.py --ingest` (`ephemeral_saves`) | founder 1, external 0 |
| `EPHEMERAL_SAVE` rows that later close an Outcome | same join as the Accountant (Op 19) report | 0 |

The nudge is judged on the second row (did the consent it gathered complete) and the fourth (did a kept bearing ever close). It is not judged on raw saves; a saved receipt that is never closed is one more open position on the scoreboard.

---

## 8. Backlog status append (to apply to the row once commit `4d18717e` reaches origin/main)

The row `notomation-receipt-save-nudge` is not on origin/main yet (it lives in `4d18717e` on `claude/fanout-ranks-2-7`), so this PR does not touch `_QUEUE/induced-backlog.jsonl`. Text to append to its `status`, verbatim, once the row lands:

> 2026-09-27: TRIGGER NOT MET (no funnel split under `_STATE/` on origin/main; the split sits in PR #586, which also edits dashboard/page.tsx). Spec written: `_SPECS/receipt-save-nudge-v1.md`. PREMISE CORRECTED: the consent-gated save nudge already exists since 2026-07-13 (ADR-049 Phase 2, `750d2872`) on the ephemeral receipt page, not the dashboard; the dashboard navigates away post-run. Evidence of use: 1 EPHEMERAL_SAVE row (founder), 0 external. INSTRUMENT GAP: Vercel Web Analytics is not enabled on `arcs-v9` (API 404), so the three `receipt_save_*` events are dropped; step 1 is a toggle, not code. Next: enable analytics, close two recovery holes (spec 6.2), copy v1.1 behind `NEXT_PUBLIC_RECEIPT_SAVE_NUDGE_V11` only after Zach blesses copy and PR #586 merges.

---

## 9. What is unconfirmed

- Whether Web Analytics was ever enabled and later disabled (the API answers only about now).
- Whether the single `EPHEMERAL_SAVE` row was a deliberate test or a real save (it is the founder's, dated 2026-07-21, eight days after ship).
- Whether the founder identity in the split equals prod `ADMIN_EMAILS` (carried from PR #586's own unconfirmed list).
- Whether any visitor has ever reached an `eph_` receipt page from outside the founder's browsers. With analytics off there is no way to know.
