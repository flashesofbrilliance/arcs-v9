# PRL — Recoil close, Todd x Zach 1-1 (2026-09-01, 2:00 PM)

> Source: Granola meeting `35b35eff-de06-4672-8d55-8248162b5ecb` (transcript + AI summary).
> T-plus close for the pre-call catch-up (prl.arcs.care/status/catchup).

## Ex-ante vs actual

| Pre-registered (catch-up) | Actual | Verdict |
|---|---|---|
| The decision is "1.3 now vs after the 1.2 loose ends" | Todd's real move: **go live with what works NOW, then 1.3.** ~$6,200 spent, wants a provable live win first. | **MISS on decision-shape.** We framed it as a 1.3 gate; Todd reframed to go-live-first. This was PREDICTABLE from his known "small provable win THEN the doors" pattern — the catch-up should have led with go-live-first as the likely path. |
| Overhead (coordination, not build) explains the 1.2 overrun | Landed. Todd reviewed the receipt, accepted the overhead framing (Sugar/Tidio/vendor chasing + tracking-template overhead). | **HIT.** The honest overhead example worked. |
| Custom code is revenue-side; no Sugar PS needed | Held. Zach to consult Tidio support + Sugar PS *before* touching routing, and get the W-Systems doc ZIP from Bill to de-risk. | **HIT (with caution retained).** |
| Territory routing is a "confirm with Bill" item | Surfaced as the **primary blocker**: ~49% of states mismatch the list, **6 states get no rep at all** (blank owner). Concrete evidence (`/status/crm` SSOT, 43-state sweep): **Dan Damas + Tim Mulcahy are live owners on several states but are NOT on Todd's list** (reps moved in, the list never updated); "Distribution" states mostly route to Bill or a named rep, not nobody. Todd wanted to leave Sugar geo-map as-is and route in Tidio; **Zach pushed back — attribution must be 1:1 or leads fall through unattributed.** NOTE: on the call Zach misstated this as "49 states" and "6 reps" — the SSOT number is ~49% of states and 6 states; correct with Todd. | Sharper than pre-registered; now a live design fork. |
| Dedup e2e proof pending (HITL) | Live demo ran and **worked**: Todd chatted (Norelle / UL V0 / CT) → lead in Tidio unassigned → correctly geo-mapped to **Lynn Winston** in the sandbox. Duplicate case not explicitly re-run. | Delivery + geo-routing proven live; dedup case still not visually confirmed. |

## New signal surfaced on the call (not pre-registered)
- **Lero (Tidio AI) synopsis gap:** the AI blurb + transcript are NOT yet mapped into Sugar's notes field. Todd confirmed the blurb is *exactly* what a rep needs to prep. **Goal: pipe transcript/AI blurb → Sugar lead notes via Zapier.** (New build item.)
- **Notifications not configured:** Todd is not receiving Tidio alerts anywhere; sandbox test lead routes to Zach, not info@prlresins.com.
- **Bill confirmed as the W-Systems build contact** (matches the earlier hunch). Kim's Aug-7 handoff referenced more docs not received.
- **Rep reality locked:** reps 55+, non-technical; new platforms are a non-starter. **Lead→account/opportunity conversion stays fully manual, handled by Bill.** Reps need only contact info + reason for inquiry. Per-rep Tidio operator accounts (unlimited, no extra cost) could push email to reps without any login.
- **CS does not field inbound leads** (admin/order-takers only) — so CS is a fallback dissemination path, not an owner.

## Action items — Zach (before go-live)
1. **Map the Lero synopsis + chatbot transcript into the Sugar lead notes field** (via Zapier). New zap step on 376827315.
2. **Assign Todd's PRL account in the sandbox** so he can run the full chatbot→Sugar flow end to end himself.
3. **Wire Tidio notifications** to the right inbox (info@prlresins.com + rep email), and fix the sandbox-routes-to-Zach issue.
4. **Build the unassigned-lead fallback**: catch-all to Bill + a new-lead digest (daily or 4-hour) to Bill/sales — the zap-kit task3 (4-hour nudge, draft Zap 376815688) + task9 (unassigned sweep) already drafted; publish once territory is decided.
5. **Consult Tidio support + Sugar PS before touching routing logic**; use Bill's doc ZIP to de-risk.
6. **Prep go-live**: Tidio plugin on the LIVE WordPress site, pointed at PRODUCTION Sugar + real notification inbox (see config table below).
7. **ZoomInfo**: once Todd confirms the plan, assess radius-based rep assignment + dedup/appending.

## Jobs to be done — Todd
1. **Get the Sugar handoff docs (ZIP) from Bill** — all W-Systems ("W Service") build documentation, to de-risk any routing/attribution change.
2. **Reconcile the territory list with Bill** — correct rep-to-state mapping + decide the catch-all for the 49% mismatch, before routing is finalized.
3. **Confirm the ZoomInfo plan** — tier, lookup limits, and the internal contact.

## Go-live configuration: staging vs the real site
| Piece | Staging (now) | Live go-live |
|---|---|---|
| Site | dev WordPress (staging) | Tidio plugin on the **live prlresins.com** WordPress |
| CRM target | **sandbox** (prlresinstest) | **production** Sugar |
| Notifications | routes to Zach's inbox | **info@prlresins.com** + assigned-rep email |
| Routing | sandbox geo-map (Lynn Winston proven) | resolved territory (or catch-all to Bill) + fallback digest |
| Lead notes | Lero blurb NOT mapped | Lero blurb + transcript **piped into Sugar notes** |
| Delivery zap | paused between tests | ON, verified live (HITL sanity check) |

## Sequence
Pre-launch (Zach items 1-3 + Todd JTBD 1-2) → e2e test with Todd's account assigned → **go live on the real site** → gather internal feedback → web forms (1.3 on-ramp) → 1.3 (recognition + attribution analytics + landing-page personas) → 1.4 (chatbot object, full source attribution).

## Belief updates
- **Lead with go-live-first for Todd, not a phase-gate decision.** His revealed pattern (small provable win, then the doors) predicted this; the catch-up over-indexed on the 1.3 decision.
- Todd will trade attribution purity for speed-to-live (wanted to route in Tidio, leave Sugar as-is); Zach's 1:1-attribution pushback is the tension to hold — resolve via the Bill territory reconcile, not by forking routing.
- The rep-reality constraint (55+, manual conversion via Bill, per-rep Tidio email) is now a hard design boundary for every routing/notification choice.
