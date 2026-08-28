# ARCS Session State — sprint snapshot
_Last written: 2026-08-17 19:41 EDT_

## Active sprint: PRL Resins × SugarCRM chatbot (client: Todd Hotes)

**SSOT for pickup:** `_ARTIFACTS/prl-11-oneshot-pickup.md` in worktree
`chatbot-1-1-jtbd-blockers-edda33` — authoritative state, spec, ledger (items 1–11). Read it first.

**Client-facing surfaces (all live on prl.arcs.care, served from origin/main):**
- root (`todd-call.html` = `prl-chatbot.html`) — the reconciled roadmap deck (one SSOT: `_ARTIFACTS/prl-roadmap-deck.html` → vendor artifact fb2878f6). Standing rule: edit SSOT, deploy to BOTH public files, rebuild vendor via `build-vendor-deck.sh`.
- `/status/crm` · `/status/troubleshooting` (now carries a **$2,000 CWO / Addendum 1.2-A** — RECONCILE) · `/status/build` (runbook, artifact 60fbdf00) · `/status/tidio` (E2E-scaffold + UAT + DoD)
- `/status/wp` — stubbed, empty, awaits Josh-leg findings

**Where 1.1 stands:** chatbot→Sugar sandbox create PROVEN (routed to rep by CT abbrev, deleted clean); field spec locked (6 required + `location_c` abbreviation enum; prod picklist still lacks "Chatbot" = cutover gate). Delivery path settled: Tidio native "Send to Zapier" node → Zap → Sugar create (Zapier Pro). **Remaining: the Tidio→Zapier UI wiring (copiloted, Zach's hands) → recorded E2E evidence into /status/tidio → the artifact promised to Todd.**

**Where 1.2 stands:** open ex-ante receipt ($4,500/20h, wrong-if outside 12–30h, check-in Aug 24) — actual tracking HIGH end (slippage 100% in coordination legs, ~1x in build). Baseline captured (928 leads, 42% stuck "New"). Enrichment = reuse ZoomInfo (decided, not built). Web-form leg = **subtract Gravity Forms → Sugar native Web-to-Lead** (Todd confirmed it's the Unbounce/PPC mechanism; approved in principle).

**The gate:** WebToLeadCapture endpoint probe (running in `prl-chatbot-sugarcrm-605dbe-9b`) firms the web-form CWO best case (reuse vs rebuild). A **$2,000 CWO already shipped** — verify it prices the vendor-latency buffer and waited for the probe.

**Blockers narrowed:** Mailgun owner = likely Josh/WFA (not Jorge, not Todd). De-SPOF directive: PRL-owned test mailbox (ask Jorge once) + PRL-held Mailgun key (ask Josh once) → deliverability tests self-serve.

**Comms:** Todd re-engaged, deputized Zach↔Josh direct, started negative-keyword list ("sheet resin" = pellets not sheets). Status email sent (now/next/later). One-pager in shared Drive folder. Staged-but-unsent Josh + Jorge drafts live in the delegate session.

**Delegate sessions:** `prl-chatbot-sugarcrm-605dbe-9b` (W2L probe · WP A–E copilot · Josh/Jorge drafts); a Sonnet subagent built /status/tidio (complete).

**Hygiene carry-forward:** plaintext creds in the "Zach and Todd" Drive doc → rotate + password-manager (flag to Todd in person). Tidio invoice-reconciliation loop with Daniel still open.
