# PRL go-live pre-mortem (2026-09-01)

> Risk gauntlet on the go-live plan from the Sep-1 Todd 1-1. Sibling to
> `2026-09-01-recoil-close.md`. Decision on the call: launch what works now on the live site
> first, gather internal feedback, then the next phase. This maps what could delay or spoil that.
> Headline: **go-live is not "just add the plugin," and the two biggest delay risks are external
> (Bill's bandwidth, PRL IT), not the build.**

## Risks that could delay or spoil go-live (ranked)

| # | Risk | Likelihood / Impact | Evidence | Mitigation |
|---|---|---|---|---|
| 1 | **Leads route wrong to real reps in production.** Real leads flow through the broken territory config (49% mismatch, 6 blank-owner states, Dan/Tim owning unlisted states) to real 55+ reps. A wrong/sitting lead poisons rep buy-in (the whole game). | HIGH / HIGH | `/status/crm` 43-state sweep; transcript (Todd: reps 55+, non-technical) | Launch with **all-unassigned → Bill catch-all + digest** BEFORE the full reconcile, so nothing lands wrong. |
| 2 | **Notifications reach no one.** Todd: "I'm not getting anything anywhere." No alert = no visible value = negative internal feedback. | HIGH / HIGH | transcript; info@ domain fix stuck on PRL IT for weeks (memory) | Wire alerts to a **working inbox interim**; don't gate go-live on info@ being perfect. |
| 3 | **Lero AI blurb may not be Zapier-accessible** for the Notes mapping (Todd's must-have). | MEDIUM / HIGH | transcript (Todd: "map that blurb into the notes, that's all we need"); unconfirmed whether Zapier payload exposes the Lero synopsis vs only the raw transcript | Resolve FIRST; fallback = raw transcript in Notes. |
| 4 | **Production cutover writes to the live CRM.** Zaps point at sandbox today; cutover re-points at prod Sugar (the business runs on it) + the custom code + broken routing. | MEDIUM / HIGH | zap-kit README (sandbox only); ADR-074 | Cut over, run ONE controlled test lead, verify, then open. |
| 5 | **First-visit-only trigger.** Returning live-site visitors fall past capture to Lyro, no lead. | MEDIUM / MEDIUM | judgment-items ("Lyro races the flow on returning visitors") | Accept for v1; name it so it isn't found as a "bug." |
| 6 | **Sugar docs from Bill incomplete.** Field-defs doc missing; builders (Fred/Amy) gone. | LOW / MEDIUM | Kim sent 2 of N docs; W-Systems dept. | Self-serve field detail from sandbox Studio; Notes mapping is on the lead (standard) side, lower risk. |
| 7 | **ZoomInfo unknown.** Radius routing + dedup depend on it. | LOW (for go-live) | transcript (Todd unsure of plan) | **De-scope** — 1.3 enrichment, not a go-live gate. |
| 8 | **Bot "all reps unavailable" message** reads badly on the live site. | LOW / LOW | transcript (Todd saw it live) | One-line Tidio handoff-config fix pre-launch. |

## The real gates (go-live depends on these three, not the plugin)
1. Can the **AI summary get into the lead Notes** (Zapier path — unknown).
2. Do **reps actually get notified** (Tidio config + the info@ fix).
3. Do leads **route to a right rep or a clean catch-all** so nothing lands wrong.
Everything else (full territory reconcile, ZoomInfo, missing doc) refines but does not gate.

## Timeframe (honest)
- **Safe minimum go-live: ~1 week** — catch-all-to-Bill routing + transcript/blurb in Notes + interim
  notifications + one clean e2e test — assuming Todd + Bill respond in a couple of days.
- **Clean go-live: ~2 weeks** — reconciled routing + Lero blurb + info@ fixed — **gated on Bill's
  bandwidth and PRL IT (both external).** Todd flagged Bill's bandwidth is thin.
- Build work is only a few days; the schedule risk is coordination (the same thing that ran 1.2 long).
  Move: make go-live **safe fast (catch-all), refine after**, rather than wait for the perfect reconcile.

## What testing and feedback actually look like
- **Testing (pre-launch, Zach + Todd):** the e2e green light — Todd runs a chat as a fresh visitor and
  watches the lead land in Sugar WITH the Notes populated and an alert in a real inbox. That single pass
  is go/no-go.
- **Feedback (post-launch, internal per Todd):** low volume at first, so **qualitative, not metrics.**
  The reps + Bill answer: "is the lead routed to the right person, and is the summary enough to prep?"
  **Loop risk:** one wrong-routed or thin lead to a skeptical 55+ rep poisons the well — so the quality
  of the FIRST handful of leads outranks speed (again argues for catch-all + good Notes before launch).

## Prioritized critical path
1. **Confirm the Lero-blurb → Zapier → Sugar Notes path** (must-have + real unknown). Fallback: raw transcript.
2. **Wire the catch-all routing** (unassigned → Bill + digest) — makes go-live safe without waiting on Bill.
3. **Resolve notifications** to a working inbox (interim if info@ isn't fixed).
4. **e2e test with Todd** (his account assigned; watches a lead land with Notes + alert).
5. **Controlled production cutover** (one test lead, verify, then open).

Parallel, non-blocking: Bill's docs · territory reconcile + Dan/Tim · ZoomInfo.
