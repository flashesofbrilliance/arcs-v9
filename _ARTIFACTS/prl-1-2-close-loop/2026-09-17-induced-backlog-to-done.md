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
1. `[NEW]` **Zach**: resolve Lyro/blurb → Zapier → Sugar **Notes** mapping. **RESEARCH RESULT (2026-09-17, docs-crawl SME): CONDITIONAL-FEASIBLE, medium confidence.** Tidio exposes a Lyro-specific webhook event `conversation.solved_by_lyro` (developers.tidio.com/reference/events) that can feed the SAME existing Zapier Catch Hook → Code → Sugar leg; Sugar Notes create+relate (`POST /rest/v11/Notes` with `parent_type`/`parent_id`) is architecturally real. **One open gap:** whether that event's payload carries the transcript or only metadata. **Fallback if metadata-only:** use the event as a trigger, then call Tidio's conversation/messages API in the Code step to pull the transcript before writing the Note (same two-hop pattern already proven). **Close the gap by:** firing a test event and inspecting the raw JSON in Zapier's Catch Hook test step (Tidio support thread `19fddc302ce41ffc` is the backup). *No longer a build-blocker; it is a payload-schema confirmation.*
   - **Belief impact:** this moves belief **P1** anterior→posterior — the enriched-ticket promise is feasible on proven infrastructure, not a blocking unknown. Confidence up; conviction MED→MED-HIGH.
2. `[NEW]` **PRL IT**: fix `info@prlresins.com` delivery + **Barracuda allow-list** the Zapier sender. *Blocker on real lead alerts.*
3. `[T]` **Zach**: publish the drafted routing zaps (task3 SLA nudge, task9 unassigned sweep) + task4/task7/task8 (verified, ship-with-notes); confirm Zapier tz. *Then* the pipe is actually on, not drafted.
4. `[NEW]` **Todd**: written sandbox approval (email). *Paper trail before prod.*

### P1 — the go-live itself (the 9-15 happy path, gated on P0)
5. `[T]` **Zach**: assign Todd's sandbox account; run one controlled end-to-end test lead (lands in Sugar + Notes + alert fires).
6. `[T]` **Zach + Todd**: controlled prod cutover — repoint zaps sandbox→prod, add `lead_source` "Chatbot" live, run ONE test lead, verify. **Do NOT run blind; sandbox-accept first.**
7. `[T]` **Zach/Todd**: install Tidio plugin on live WP (via GTM-WLP9C76 tag or HFCM), pointed at prod; fix the "all reps unavailable" bot line pre-launch.

### P2 — clean handoff (so it survives Zach post-op)
8. `[NEW]` **Todd + Bill**: territory admin inputs — 6 blank-owner states, NY/PA split, Rob/Pat/Dan/Tim usernames, Bill's Sugar build-doc ZIP. **Assign an owner + a volume trigger** for retiring the central-inbox interim.
9. `[T]` **Zach**: exec runbook / how-to page — end-to-end overview + the 3-step go-live for Todd to re-drive solo. **BUILT this session → prl.arcs.care/status/runbook** (client-safe, air-gapped). Optional: screen-record the walkthrough as the reference.
10. `[NEW]` **Zach**: internal cleanup — remove ~8 synthetic test leads, Roger Lamarre repair, empty-email Tidio validation root cause. *Silent, pre-done.*

### Execution channel for the two teed-up Tidio→Sugar sandbox jobs (Task C)
Append the FULL Tidio chat into the assigned Sugar ticket + wire the spec-code / competitor cross-reference. **Staged, not fired.** Per Zach: the relevant Tidio/Zapier/Sugar tabs are open in Comet and Claude has Chrome access, so these get executed **via Chrome on Zach's go, once he actions the specific job** — NOT via blind Zapier-MCP REST writes. Sandbox (central-inbox connection) only; never prod. HITL: Claude drives structure/clicks, Zach types any free-text.

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
- **Tidio preconfigured templates + Audiences (UNEXPLORED)** — Tidio ships flow/automation templates and an Audiences (visitor-segmentation/targeting) layer we have not evaluated. Likely accelerates the personas-per-landing-page + SEM work (1.4) and could replace hand-built flows. *Owner: Zach (explore). Trigger: phase-2 greenlight, or before rebuilding any flow from scratch (reuse-before-invent).*
- **Web-forms on-ramp** (1.2-A / 1.3) — *invoice-gated.*
- **Prettier confirmation emails** — *blocked by current Tidio plan tier; "Powered by Tidio" removal needs Tidio Plus.*

---

## Execution orchestration + tool-fit pressure test (post-greenlight)

Metabolic-router split: mechanical → terminal/Haiku, judgment → Sonnet, irreversible/COURT → Opus + human. Most items are gated on Todd/PRL-IT, so sessions spin **when items are actioned**, not now.

| # (backlog) | JTBD | Right tool (TOOL-FIT) | Tool-fit confidence + falsifier | Tier | Est budget |
|---|---|---|---|---|---|
| P0-1 | Lyro/blurb → Sugar Notes | **VERIFY-FIRST via docs-crawl SME agent** over Tidio + Sugar self-service docs + received emails (their *support* is garbage; their *docs* aren't), then Zapier map | **LOW — the one real residue.** Falsifier: "Lyro data isn't exposed to Zapier/webhook" → fallback: land the raw structured transcript into a Note | Sonnet (research SME) | low |
| P0-2 | info@ fix + Barracuda allow-list | PRL-IT (external) | HIGH (not our tool) | n/a (PRL) | 0 |
| P0-3 | Publish drafted task3/task9 zaps + tz | Chrome/Comet HITL + Zapier | HIGH — proven on this engagement | terminal/Chrome HITL | low |
| P1-5 | Sandbox e2e test lead | Chrome HITL + Sugar read-back (the eval) | HIGH | Sonnet + human | low |
| P1-6/7 | Prod cutover + WP plugin | Chrome HITL + Sugar read | HIGH tool-fit, **BAR/COURT gate (irreversible)** | **Opus + human** | low tokens, high care |
| C (Task C) | Full chat into ticket + spec-code cross-ref | Chrome/Comet HITL (tabs open) | HIGH | Sonnet + human | low |
| P2-8 | Territory reconcile | blocked on Bill inputs | n/a (external inputs) | Sonnet (synth) | low |
| P2-10 | Internal cleanup (test leads, Roger, empty-email RCA) | terminal / Sugar reads | HIGH | Haiku/terminal | minimal |

**Cross-orchestration edges (what gates what):**
- `P0-2 (PRL-IT)` + `P0-1 (Lyro verify)` + `P0-4 (written approval)` → **gate** `P1-6 prod cutover`. Do not cut over until all three clear.
- `P0-3 publish zaps` → gate `P1-5 e2e test`.
- `P2-9 runbook` = DONE (shipped this session).
- Shared anchor for parallel sessions = `_QUEUE/induced-backlog.jsonl`; refetch-before-write (append-only), worktree-isolated per session.

**Recommendation:** hold all sessions until post-call. The only pre-execution de-risk worth doing before you're back at full bandwidth is the **Lyro→Notes verify** (a support question, not a build). Spin one Sonnet session on it when you want; the cutover session (Opus + you) waits on its three gates.

## The two open decisions to force at 2pm (from belief P4)
- **Time-sensitivity**: is this a "before Friday" push or a "whenever" workstream? Zach's availability craters after Fri 9-19 surgery for 1-2 weeks — so this answer sets whether to attempt the prod cutover today/tomorrow or explicitly defer it with the runbook.
- **Transition shape**: clean handoff-and-done (complete, honorable stopping point) OR retained phase-2. Do not infer from warmth; get the plain answer.

## Prior-art scan (2026-09-17): open-source analogs to our Tidio->Zapier->Sugar stack
Verdict: our stack is the **sanctioned commercial pattern**, not a hack — Tidio ships a native "Send to Zapier" flow action and Zapier's SugarCRM app has Create-Lead/Contact/Note steps (zapier.com/apps/tidio/integrations/sugarcrm7). No exact drop-in OSS repo replicates this specific proprietary-SaaS chain.
- **Closest open-source analog = n8n** (self-hosted, no per-execution fee): webhook trigger + HTTP Request node to any REST API + native AI/chatbot nodes + firmographic lead-routing patterns. Templates to crib from: github.com/enescingoz/awesome-n8n-templates (280+, incl. CRM + RAG-chatbot + lead routing).
- **Open-source CRM leg = SuiteCRM** (the community fork of SugarCRM): REST API + webhook modules — so a fully-OSS version of our pipe = chatbot -> n8n webhook -> dedup/enrich -> SuiteCRM/Sugar REST.
- **Implication for PRL:** no change now (validates the current path). File as a **future option only** — if PRL ever wants to own/de-SaaS the whole pipe for cost/control, n8n + the existing Sugar REST is the migration target. Not a go-live item.
