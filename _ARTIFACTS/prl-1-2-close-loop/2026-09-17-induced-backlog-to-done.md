# PRL / Todd Hotes — Induced Backlog to "Done" + completeness audit

_Internal war-room. Built 2026-09-17 for the 2:00pm ET walkthrough. Sources: 2026-09-15-todd-prl.json (recoil-close), 2026-07-30 MASTER-HANDOFF, 2026-09-01 recoil-close + golive-premortem, 2026-08-26 chase-list, prl-zap-kit README, 2026-08-03 lyro-ai-layer-v2. Not counterpart-facing._

## The ask for the 2pm call (what "landing the plane" actually needs)
Two things must come back from Todd, and one honest correction must go to him:
1. **Force the P4 answer**: how time-sensitive is this, and is the transition a clean handoff-and-done or a retained phase-2? (belief P4, still OPEN)
2. **Collect the PRL-owed admin inputs** (the list below) or explicitly park them, because a clean go-live is gated on them, not on more build.
3. **Correct the record**: the 9-15 "just 3 steps and it should just work" story was true for the happy path, but it under-counted real dependencies. Better Todd hears the full list now than discovers it mid-cutover while Zach is post-op.

---

## COMPLETENESS AUDIT — did the 9-15 outline to Todd get them all right?

**What Zach DID surface on 9-15 (correct, and correctly framed):**
- Go-live = 3-step happy path: repoint Zapier→Sugar connector sandbox→prod, add the `lead_source` "Chatbot" value in live Sugar, install Tidio WP plugin on the live site with the same creds. ✅
- Ticket enrichment: full Tidio conversation + spec-code / competitor cross-reference into the assigned ticket. ✅
- Routing interim: all mis-routed geo emails → one central inbox (Bill) until volume forces a finer rule. ✅ (deliberate, receipted)
- Handoff: Todd has edit access to Tidio + Zapier; Copilot can modify flows. ✅

**What was UNDER-SURFACED or MISSING on 9-15 (the honest gap):**
| Gap | Why it matters | Owner | Surface at 2pm? |
|---|---|---|---|
| **Lyro/"Lero" blurb → Zapier → Sugar Notes mapping** — feasibility unconfirmed | Called a must-have in the 09-01 close; if it can't write to Notes, the enriched-ticket promise degrades to raw transcript | Zach (verify w/ Tidio+Sugar) | YES — flag as the one real build unknown |
| **Notification wiring blocked on `info@prlresins.com` fix by PRL IT** | Rep alerts / lead emails may not land until IT completes this | PRL IT | YES — it's a PRL dependency, not a Zach task |
| **Barracuda allow-list for the Zapier mail sender** | Quarantine risk — real leads silently held | PRL IT | YES — pair with the info@ item as "two IT asks" |
| **Territory admin inputs**: 6 blank-owner states, NY/PA split default, Rob/Pat/Dan/Tim Sugar usernames, reconcile the 49% mismatch with Bill | The Bill-interim only holds until volume; the real fix needs these from PRL and has **no owner/trigger assigned** | Todd + Bill | YES — name an owner + a volume trigger |
| **Written sandbox approval** (verbal given, email outstanding) | Paper trail before any prod touch | Todd | YES — 30-second ask |
| **Bill's Sugar build-doc ZIP (W-Systems docs)** | Needed to mirror prod mapping cleanly; Bill-bandwidth risk | Todd/Bill | YES |
| **Anti-ICP / negative-keyword list** | Improves routing + ticket quality | Todd | Optional at 2pm |
| **1.2-A web-forms invoice #NYQRTJPQ-0004 ($2,070)** | Payment-gated scope; unpaid | PRL (payment) | Only if natural — do not lead with money on a handoff call |
| **Internal loose ends**: publish the drafted task3/task9 zaps, clean ~8 synthetic test leads, Roger Lamarre lead repair, empty-email Tidio validation root cause, confirm Zapier tz = America/New_York | Block a clean "done" but are Zach's, need no Todd input | Zach/Claude | NO — do silently before/after |

**Verdict:** the 9-15 outline was *directionally right and honestly framed*, but it compressed a ~15-item dependency set into a 4-item story. The compression is fine for warmth; it is not fine as the go-live plan. The list above is the delta.

---

## STACK-RANKED BACKLOG TO DONE

Ranked by critical-path-to-clean-go-live. `[T]` = surfaced to Todd 9-15, `[NEW]` = the audit gap. Owner in **bold**.

### P0 — blocks a safe production cutover (do first)
1. `[NEW]` **Zach**: resolve Lyro/blurb → Zapier → Sugar **Notes** mapping; confirm feasibility with Tidio + Sugar PS. Fallback: land the raw transcript into Notes. *Trigger: before any prod test lead.*
2. `[NEW]` **PRL IT**: fix `info@prlresins.com` delivery + **Barracuda allow-list** the Zapier sender. *Blocker on real lead alerts.*
3. `[T]` **Zach**: publish the drafted routing zaps (task3 SLA nudge, task9 unassigned sweep) + task4/task7/task8 (verified, ship-with-notes); confirm Zapier tz. *Then* the pipe is actually on, not drafted.
4. `[NEW]` **Todd**: written sandbox approval (email). *Paper trail before prod.*

### P1 — the go-live itself (the 9-15 happy path, gated on P0)
5. `[T]` **Zach**: assign Todd's sandbox account; run one controlled end-to-end test lead (lands in Sugar + Notes + alert fires).
6. `[T]` **Zach + Todd**: controlled prod cutover — repoint zaps sandbox→prod, add `lead_source` "Chatbot" live, run ONE test lead, verify. **Do NOT run blind; sandbox-accept first.**
7. `[T]` **Zach/Todd**: install Tidio plugin on live WP (via GTM-WLP9C76 tag or HFCM), pointed at prod; fix the "all reps unavailable" bot line pre-launch.

### P2 — clean handoff (so it survives Zach post-op)
8. `[NEW]` **Todd + Bill**: territory admin inputs — 6 blank-owner states, NY/PA split, Rob/Pat/Dan/Tim usernames, Bill's Sugar build-doc ZIP. **Assign an owner + a volume trigger** for retiring the Bill-catch-all interim.
9. `[T]` **Zach**: written go-live runbook + optional screen recording of the walkthrough, so PRL can re-drive it solo.
10. `[NEW]` **Zach**: internal cleanup — remove ~8 synthetic test leads, Roger Lamarre repair, empty-email Tidio validation root cause. *Silent, pre-done.*

### P3 — decisions, not tasks
11. `[T]` **Todd**: the P4 answer — priority + clean-handoff vs retained phase-2.
12. **Todd**: 1.2-A invoice ($2,070) — surface only if it comes up naturally.

---

## PHASE-2 / FUTURE BACKLOG (deferred — revisit triggers named)
- **Territory auto-routing** (beyond the single-inbox interim) — *trigger: Bill "bogged down" / volume threshold.*
- **Lyro AI layer full activation** (`build_full_ai`, AI-first menu) — *trigger: delivery proven live + economics check out (maps to client-page 1.5).*
- **ZoomInfo radius routing + dedup/append** — *trigger: Todd confirms ZoomInfo plan/tier.*
- **Lead-source attribution analytics** ($43.7M / 2041 opps unattributed) — *trigger: go-live stable, want the before/after number (maps to 1.2/1.3).*
- **Landing-page personas + SEM on-ramp stubs** — *maps to client-page 1.4.*
- **Web-forms on-ramp** (1.2-A / 1.3) — *invoice-gated.*
- **Prettier confirmation emails** — *blocked by current Tidio plan tier; "Powered by Tidio" removal needs Tidio Plus.*

---

## The two open decisions to force at 2pm (from belief P4)
- **Time-sensitivity**: is this a "before Friday" push or a "whenever" workstream? Zach's availability craters after Fri 9-19 surgery for 1-2 weeks — so this answer sets whether to attempt the prod cutover today/tomorrow or explicitly defer it with the runbook.
- **Transition shape**: clean handoff-and-done (complete, honorable stopping point) OR retained phase-2. Do not infer from warmth; get the plain answer.
