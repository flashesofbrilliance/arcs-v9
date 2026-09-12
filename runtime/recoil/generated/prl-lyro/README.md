# PRL Lyro agent — setup runbook (SSOT)
_2026-08-07 · The Phase 1.5 Lyro config, authored as repo files (no account/CRM touched). Everything here is
the "build-now" work; anything that enters the Tidio account or writes to SugarCRM is gated (see below).
Derived from `../2026-08-06-lyro-config-plan.md` (v2, post-gauntlet). Load order matters._

## Files (all authored, ready)
| File | What it is | Where it goes |
|---|---|---|
| `guidance-prompt.md` | The Lyro Guidance/persona prompt | Tidio → Lyro → Behavior/Guidance |
| `kb-content/kb-content.md` | The curated, scrubbed KB text | Tidio → Lyro → Knowledge (paste/Q&A) |
| `kb-manifest.md` | Loaded-vs-held-out ledger + scrub checklist | reference / guardrail |
| `conversation-starters.md` | Market-level widget openers | Tidio widget starters |
| `handoff-policy.md` | Escalation + rep-anonymous measurement | Tidio → Configure → handoff |
| `costcap-policy.md` | Hard cost ceiling | Tidio → Lyro billing/limits |
| `firewall-test-prompts.md` | Anti-fabrication acceptance test | Tidio playground, before go-live |

## Setup order (when Tidio account access lands)
1. **Verify the gates first** (in-account, before loading anything):
   (a) Lyro→Flow handoff primitive + tag propagation exist; (b) file-import / paste-text path available;
   (c) Guidance char limit ≥ the prompt (read it back whole); (d) real Lyro quota + overage controls exist.
2. **Paste the Guidance prompt** (`guidance-prompt.md`), read it back to confirm no truncation.
3. **Load the KB** from `kb-content/kb-content.md` (paste/Q&A). Do NOT upload the raw sell-sheet or datasheet
   PDFs. Point any site crawl only at market/capability pages, not the datasheet PDFs.
4. **Set conversation starters** from `conversation-starters.md`.
5. **Configure handoff** (online/offline) per `handoff-policy.md`; hand to a named rep.
6. **Set the cost cap** per `costcap-policy.md` (overage off, quota→Flow fallback, alert-before-spend).
7. **Run `firewall-test-prompts.md`** in the playground. Any leak → fix the KB source, re-test. Clean sweep
   required.
8. **Only then** consider go-live — and only after the 1.2 delivery handoff is proven and the AI-economics
   kill-switch check passes (1.5 is last + optional by contract).

## Blocked-until (not build-now)
- Anything writing to SugarCRM (lead delivery webhook) — Sugar sandbox not secured; that's 1.1/1.2.
- Steps 1-7 above need the live Tidio account / pending support review.
- `phone_work` required-vs-placeholder — Todd's decision.

## Scope reminder (from the gauntlet)
This is **1.5 only**. Competitor recognition is 1.3; OEM/molder persona branching is 1.4; the delivery pipe +
baseline is 1.1/1.2. Do not build those here. The bot stays persona-generic and never states a spec, cert,
price, or lead time — those route to a specialist by construction.
