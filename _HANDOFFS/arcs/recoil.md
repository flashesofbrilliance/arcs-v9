# Arc: recoil (reconstructed 2026-10-06)

> Recoil is the counterpart engagement machine: one SSOT JSON per counterpart, a gated internal war room, a
> sanitized external twin, and an ex-ante receipt that gets scored against reality after the call. It began in
> July 2026 as hand-built pages for Todd Hotes (PRL Resins), matured into four composable skills
> (recoil-new / prep / close / ship) by v3.17.0, was IP-hardened after `public/` was found world-readable
> (v3.18.0), spawned sibling classes (omakase pipeline for Louisville, teardown factory for Wing, the
> counterpart forge for Yuri), and carried the only paid engagement (PRL, $6,052.51 paid to date) through
> phases 1.1 and 1.2. By October the work is mostly close-loops (Schriner/Vico, Lyndon) and a shared
> "Ahmed order" vocabulary that receipts, briefs and the ledger now render through.

## Goal
Every counterpart conversation runs through the same loop: prep with an honest ex-ante receipt, hold the call,
close the loop by scoring the receipt against the transcript, and ship only a counterpart-safe projection.
Internal and external artifacts never cross the air gap; every claim is transcript-grounded.

## What changed
- **v3.4.0 to v3.12.0 (Jul 2-20):** PRL Phase 1 proposal for Todd Hotes; plain-English call and teardown pages,
  live Stripe pay button, Tidio branch-logic tree. chan.arcs.care built in one session (v3.7.0).
- **v3.13.0 (Jul 22):** ROM primitive "Exogenous Forge" inscribed; `/thread-recoil` skill.
- **v3.16.0 (Jul 22):** Ahmed Elsamadisi (Polyform) reconnect loop: internal `ahmed.arcs.care` war room plus
  external `ahmed-ext.arcs.care`; air gap mechanized from SSOT `runtime/recoil/generated/2026-07-22-elsamadisi.json`.
- **v3.17.0 (Jul 23):** recoil becomes a system: 4 skills over one SSOT, 6-tab template
  `runtime/recoil/templates/war-room-6tab.template.json`; first live run on Yuri Kleban (Google).
- **v3.18.0 (Jul 24):** IP-leak hardening: 9 internal docs moved from `public/` to `runtime/warroom/`,
  analytics added to 34 counterpart pages, generator provenance comment removed.
- **v3.19.0 to v3.20.0 (Jul 31 to Aug 1):** Louisville Brands universe (louisville / omakase / atom), `jeben.html`
  RUIN leak closed, `omakase-pipeline` skill codified, follow-up sent.
- **v3.23.0 to v3.29.0 (Aug 5-10):** counterpart forge CLI and Robin-standard family; Yuri family transcript-healed
  and shipped. Client-side first-name pw gates on Yuri pages REMOVED by Zach's call (v3.27.0), not migrated.
- **v3.35.0 to v3.41.0 (Aug 17-19):** PRL Sugar routing work; chatbot to sandbox Sugar Lead verified end to end
  via Zap 376827315; Todd-facing progress pages.
- **v3.42.0 (Aug 23):** Sean Wing teardown at wing.arcs.care (#153 to #166), `teardown-page-factory` skill,
  verb x altitude gate matrix (became ADR-068 in v3.43.0).
- **v3.44.0 (Aug 26):** Ahmed 60-Second Read onramp, gauntlet-hardened (#181); re-open note drafted.
- **v3.45.0 to v3.46.0 (Aug 27):** PRL 1.2 close-loop closed; `prl.arcs.care/status/receipt`; Instrument Board
  `scripts/warroom_board.py`; zap kit staged at `_ARTIFACTS/prl-zap-kit/`.
- **v3.52.0 (Sep 2):** recruiter two-tier tear sheet; ammo tier later gated by `src/lib/ammo-gate.ts`.
- **v3.62.0 (Sep 14):** Joe Schriner (Oxenham/Autopilot/Vico) internal recoil receipt `2026-09-14-schriner.json`.
- **v3.64.0 (Sep 17):** PRL wrap: overview with payment history (#475), #469 to #476; receipt
  `2026-09-17--todd-prl-recoil-close-pr463` among 4 filed.
- **v3.66.0 to v3.66.1 (Sep 26):** `tools/cold-recon/` CLI; Ahmed-order re-cut and phone card.
- **v3.79.0 (Oct 5):** `/recoil-close` Schriner on the two Vico calls (#742, `eba6c858`); Lyndon pre-call refreshed
  (#746, `17647913`); `scripts/recoil_brief.py` password gate fixed for blocked sessionStorage. Receipts
  `2026-10-04--schriner-recoil-close-pr742--ZH`, `2026-10-04--lyndon-precall-refresh-pr746--ZH`,
  follow-up `2026-10-05--lyndon-precall-refresh-pr746-followup--ZH`.
- **v3.88.0 (Oct 5):** shared icons excluded from host catch-all rewrites (#824); only 5 of ~95 hosts checked.
- **v3.102.0 (Oct 6):** Ahmed order shared by receipt, brief and ledger: #880 (`28225089`), #885 (`2f3cb294`),
  #890 (`a8fd8358`); receipts `2026-10-06--ahmed-order-vocabulary-pr880--ZH`, `--ahmed-order-receipt-pr885--ZH`,
  `--ahmed-order-brief-pr890--ZH`. #918 made True North the page h1.

## State
- All PRs cited above are MERGED (checked with `gh pr view`); the five SHAs cited are ancestors of origin/main.
- SSOTs live in `runtime/recoil/generated/`; latest is `2026-10-03-oh-vico.json` (Lyndon prep).
- `/recoil*` is gated by Auth.js session plus `ADMIN_EMAILS` (`src/lib/admin.ts`); `RECOIL_PASSWORD` is retired.
  Ammo tier gated by `RECRUITHAUS_AMMO_PASSWORD` (`src/lib/ammo-gate.ts`, exists).
- PRL: 1.1 and 1.2 paid and closed; phase cards 1.2-A/1.3/1.4/1.5 HELD pending 3 decisions; Tidio to Sugar
  pipeline staging-proven, NOT prod-verified (as of v3.64.0; no later evidence, unverified).
- Lyndon call: not scheduled as of v3.79.0 (unverified since).
- Sean Wing and Louisville: let-it-breathe, no reply recorded (unverified).

## Decisions
- Air gap is mechanical: internal SSOT projects into an external twin; leak checks run before ship.
- Gates on consented counterpart pages are friction, not protection: Yuri pages stay ungated (Zach, v3.27.0).
  Truly internal material sits behind server-side auth, never a client-side first-name check.
- Ex-ante receipt is filed before any counterpart send (ADR-068); close-loop when they respond.
- Never send on Zach's behalf: notes are drafted, Zach hand-sends.
- PRL client surfaces carry no provenance footer (client-confidential, v3.60.0).
- Run the prep skill against what already exists before re-prepping (Lyndon ex-ante existed 12h earlier).
- Named founder battle cards are offline files only, never hosted.

## Open
1. Zach: Lyndon call, then `/recoil-close` against `2026-10-03-oh-vico.json`; Autopilot 10-13 nudge; Vico funding question.
2. Zach: PRL phase-card decisions (1.2-A/1.3/1.4/1.5) and the human-gated zap-kit installs; Tidio to Sugar prod cutover.
3. Icon rewrite backstop (#824) verified on only 5 of ~95 hosts; `/:path*` style host rules may still swallow icons.
4. Retro-sweep `runtime/recoil/generated/*.json` through the attribution lambda (v3.51.0), unverified as done.
5. Counterpart pulse: Yuri, Robert, Ahmed note send status (unverified).

## Next action
Check whether the Lyndon call happened (calendar / Granola); if so run `/recoil-close` on `2026-10-03-oh-vico.json`.

## Cold-start
- Skills: `recoil-new`, `recoil-prep`, `recoil-close`, `recoil-ship`, `forge`, `teardown-page-factory`,
  `omakase-pipeline`, `prl-page-factory`, `counterpart-gauntlet`.
- Files: `runtime/recoil/generated/`, `runtime/recoil/templates/war-room-6tab.template.json`, `scripts/recoil_brief.py`,
  `scripts/warroom_board.py`, `_ARTIFACTS/prl-zap-kit/README.md`, `src/lib/admin.ts`, `src/lib/ammo-gate.ts`, `src/proxy.ts`.
- Commands: `git log origin/main --oneline -i --grep=recoil`; `ls runtime/recoil/generated | tail`.
- Tracker: tech-debt artifact `debt` collection, filter recoil/PRL rows.
- Memory: `recoil-brief-ssot-cli`, `comparative-recoil-orthogonal-echo-inward`, `internal-external-artifact-air-gap`,
  `project_todd_hotes_prl_resins`, `project_ahmed_elsamadisi_polyform`, `project_joe_schriner_oxenham_autopilot_vico`,
  `project_yuri_kleban_google`, `confirm-before-outbound-send-even-when-authorized`, `counterpart-forge-pipeline`.
