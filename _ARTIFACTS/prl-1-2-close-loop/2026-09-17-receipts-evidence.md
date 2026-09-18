# PRL / Todd — 2026-09-17 receipts + evidence pack

_Internal. Every claim below links to a reproducible receipt or a primary source. Built after the 2026-09-17 2:00pm walkthrough (Granola cd30a239). Companion to the Todd recap email DRAFT + the progress-page update this session._

## Green receipts (reproducible, exit 0)

| Claim | Receipt (command) | Result |
|---|---|---|
| The investigation pre-work gate (P-1) is cleared on evidence, not rubber-stamped | `python3 _ARTIFACTS/prl-1-2-close-loop/prl_depmap_check.py` | Was **HARD FAIL** (gate "in-progress"); now **PASS (exit 0)**. Only INFO left: P4 (Todd-owned priority/transition), P3-12 invoice. |
| The acceptance-test logic fails-on-bad and passes-on-good | `python3 _ARTIFACTS/prl-1-2-close-loop/prl_uat_harness.py --self-test` | **SELF-TEST PASS** — good fixtures 0 FAIL, bad fixture 7 FAIL, assertions OK. |

Gate-clear evidence (both named reconciliation items verified against artifacts):
- **Dossier/audit → UAT schema:** `prl_uat_harness.py` encodes exactly the 6 required Sugar Leads fields (`account_name, first_name, last_name, phone_work, lead_source, location_c`) with inline provenance to `prl-lyro/STATE-OF-SUGAR-2026-08-11.md` (§2, 100/100 phone_work) + `prl-lyro/INTEGRATION-DOSSIER.md` (§B/§D4).
- **Email next-steps in-repo:** `prl-lyro/2026-08-11-sugar-case-589806-reply.md`, `2026-08-03-todd-vision-serialization.md`, `2026-09-01-nextsteps-email-DRAFT.md`, `2026-08-26-three-scenario-email-DRAFT.md` all present.
- Full receipt block: `prl-dependency-map.json` → `investigation_prework.reconciliation_receipt`.

## What the 9-17 walkthrough actually showed (primary source: Granola cd30a239, verified against transcript lines)

**Proved live on the call (evidence backs the claim):**
- Region routing: Connecticut lead → rep Lynn; "rep in Nebraska" → Steve Fabricius / Central & South Central territory (transcript ~L443–466).
- ZoomInfo enrichment fired (company/title/industry) on the live lead (~L452).
- Baseline audit: 24 months, 942 leads, 4,238 opps, ~40% no lead source (~L136).

**Evidence did NOT back the happy-path claim — open items found in live testing (this is the honest delta):**
- New lead came in status **"dead" not "new"** — Zach: "it's flagging it as dead for the status. That might be a bug." (L428, L439, L576). Field-mapping/routing-rule quirk, under investigation.
- A **second test lead lagged / did not appear** in Sugar during the call (Zapier push timing / ZoomInfo hold / nudge-rule gating) (L530–531, L576).
- **New-lead email notification did not reach Todd** (L582–584); notifications are still an "easy workaround right now" (L132).
- **info@prlresins.com has no CRM user record** to receive a routed lead (L588–592).
- Regional mapping is **partial** ("the 52% that works," L476); catch-all drops attribution.

**Decision (answers open belief P4):** NOT going live yet; Todd wants **knowledge-base enrichment (phase 1.3)** so the bot answers alternative-resin questions before go-live — "Which we will do. We'll do that in the next phase here." (L102). This is a **retained multi-phase engagement, not a clean handoff.** No Friday go-live (Zach, L297). No hard deadline set by Todd.

## Deliverables produced this session
- **Progress page updated to Sep-17 truth** (`public/prl-status-progress.html`): re-dated, new "Latest · after the Sep 17 walkthrough" block (proved-live / in-test / go-live-sequenced), honest status pills. `scripts/artifact_wrap_lint.py` → **clean**; verified desktop + 375px mobile; em-dashes swept to 0 (was 13 pre-existing). **NOT yet deployed** — awaiting review before pushing to live.
- **Todd recap email DRAFT** (`2026-09-17-todd-recap-email-DRAFT.md`): the config-summary Zach committed to on the call (L614–615). Air-gapped, plain-language, honest about the open items Todd saw live. **NOT sent** — draft for review.
- **Visual documentation:** live-page screenshots (progress, atlas, runbook) + updated-progress render at desktop and mobile.

## Honest blocked residue — canNOT be looped to "done" by an autonomous session
These are gated on live-system HITL, irreversible cutover, or Todd/PRL, per `prl-dependency-map.json` + the induced-backlog:
- **Investigate the 3 live-test issues** (dead-status, delivery timing, notification) — needs live Tidio/Zapier/Sugar access, HITL via Chrome; Zach's own actions.
- **Swap notification/assignment email to Todd's account; create "Chatbot" lead source in prod** — live-system, Zach.
- **Publish drafted zaps (task3/task9); sandbox e2e test lead** — live Zapier/Sugar, HITL.
- **Production cutover + WP plugin install** — BAR/COURT irreversible; explicitly Opus + human, do not run blind.
- **info@ fix + Barracuda allow-list** (PRL IT), **written sandbox approval** (Todd), **territory reconcile / Bill docs** (Todd+Bill), **1.3 knowledge enrichment content** (Todd domain input), **P4 priority answer** — now partially answered (retained phase-2).
