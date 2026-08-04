# Phase 1.1 — Go Live (the chatbot itself)
_Todd-safe · NOW · 2026-08-04. Burn-down to landing the plane._

## Where this sits
**NOW.** This is the phase in flight. Everything else (1.2–1.5) is next/later and overlaps only as
parallel gathering, never as work you pay for before you greenlight it.

## What "done" looks like (definition of done)
A test conversation down every path produces a clean lead in SugarCRM, tagged Chatbot, routed to your
sales manager, and it goes live on the real site in a window you pick, with nothing changed on the
plant floor or in any rep's daily routine.

## Burn-down (what is left to land it)
- [x] Bot built, branded, tested on a private copy of the site.
- [x] Phone required + "Chatbot" label decided.
- [ ] **Sandboxed copy of SugarCRM** — the one thing on the critical path. Prove lead-creation safely
      before touching live production.
- [ ] Wire lead delivery (Tidio → Zapier → Sugar) + the Mailgun notification.
- [ ] 30-minute session with your SM + reports person.
- [ ] Flip live via the controlled go-live switch, in your chosen window.

## Best / Base / Worst
| | Time to live | What drives it |
|---|---|---|
| **Best** | ~2-3 days | Sandbox access lands this week; session booked fast. |
| **Base** | ~1 week | Normal back-and-forth on access + one scheduling round. |
| **Worst** | 2-3 weeks | Access stalls (the 1.1 pattern so far), or a holiday/work-trip window. |

## Dependencies & what could delay it
- **Blocking:** SugarCRM sandbox access. This gates the safe test.
- **Coordination overhead:** scheduling the SM/reports session; IT/agency for the go-live switch.
- **Calendar risk:** a holiday or an unplanned work trip in the window shifts the date, not the scope.
- **Out-of-scope:** any change to how leads are captured beyond the agreed fields is a separate note,
  not silently absorbed.

## Payment
**Already paid.** Phase 1.1 was the original engagement ($1,552, paid Jul 24). Nothing further owed to
finish it.

## Contingency
- **Min-cost path:** if sandbox access is slow, we prove everything against a single, clearly-labelled
  test lead you approve, then delete it — no new spend, no live-data risk.
- **Where it could bubble:** only if the CRM setup turns out to differ materially from what we audited
  (unlikely) would there be added work, and that would be a named change order, not a surprise.
- **Safety net:** sandbox-first, one-toggle kill switch, full rollback. You are never exposed.

## Appendix (deep supporting material)
- Go-live gate + acceptance criteria: `2026-08-04-todd-phase-map-1.1-to-1.5.md` (Phase 1.1).
- Safeguards / kill-switch / rollback: `2026-08-04-todd-safeguards-killswitch-rollback.md`.
- The bot conversation design + flow generator: `2026-07-20-todd-chatbot-branch-logic-v1.md`,
  `prl_tidio_flow_gen.py`.
