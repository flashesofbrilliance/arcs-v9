# Manual wiring steps — 1.1/1.2 delivery leg (do these yourself, staging/sandbox only)

## #1 — Zapier Catch Hook (one-time, Zapier web UI)
1. New Zap. Trigger app: **Webhooks by Zapier** → event **Catch Hook**. Copy the generated
   webhook URL — this is what Tidio will POST to.
2. Action app: **SugarCRM** (the `SugarAI` app / `zapier.chatbot` sandbox connection already
   used 2026-08-13) → action **Create Record** → module **Leads**.
3. Map fields from the webhook payload keys (name them exactly this, so step #2 below matches):
   `account_name, first_name, last_name, lead_source (hardcode "Chatbot"), location_c, phone_work, email1`
4. Turn the Zap **on**. That's the whole Zapier side — no code, no MCP needed for this part.

## #2 — Tidio flow edit (Tidio flow editor, staging site's chatbot)
**Graft onto Flow B — "PRL Resins - AI Handoff (lead delivery bridge)" (the draft), not the
live Flow A.** Reasoning already logged in `leg1-tidio-flow-map.md` §"Comparative verdict":
Flow B is linear, has an open terminal "+" slot, and needs the same two fixes either way —
Flow A's live traffic/branching makes it the riskier graft target for the same amount of work.

Two fixes, in order:
1. **Bind variables.** On each of Flow B's 6 question nodes, toggle "Save the answer as a
   contact property" ON, naming each to match the field it feeds:
   `need` → (not sent to Sugar, informational only) · `contact_name` → splits to
   `first_name`/`last_name` · `email` → `email1` · `phone` → `phone_work` ·
   `company` → `account_name` · `state` → `location_c` (see note below).
2. **Add the delivery action** at the open "+" slot: Action → **Send data to Zapier / Webhook**
   (whichever Tidio's action palette actually offers — confirm on the day, may be named
   differently) → POST → paste the Catch Hook URL from #1 → body = the 6 bound variables above.

**Trigger conflict — resolve before activating.** Flow B currently shares `onFirstVisit` with
live Flow A ("Flow overload" banner). Do not activate Flow B as-is. Recommended: change Flow
B's trigger from `onFirstVisit` to a manual/internal trigger fired from within Flow A's own
decision tree at whichever of the 4 terminal branches (nodes 5/17/21/27) represents a
qualified lead — turning Flow B into the actual "bridge" its name already implies, rather than
a competing first-visit flow. If Tidio's editor doesn't support that hand-off pattern
directly, the fallback is deactivating Flow A and promoting Flow B's questions into a single
flow — flag which one you hit and I'll adjust the plan same-session, cheaply, since it's a
config decision, not new build.

**`location_c` note:** the "What state or region are you in?" question is free text today.
Sugar's `location_c` is a strict 2-letter enum. A full transform (fuzzy-match free text →
abbreviation) is out of scope for this pass — for now, send the raw text through as-is and
let it land in Sugar even if unmapped (better than losing the lead); a proper normalizer is
future work, not a 1.1/1.2 blocker.

## #3 — Staging test
Run a real chat on the WP staging site through to a qualified-lead terminal branch. Then ping
me — I'll do one cheap read-only check (Zapier MCP → list recent sandbox Sugar Leads) to
confirm it landed, rather than you needing to open Sugar yourself.
