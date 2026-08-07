# SugarCRM admin-config runbook for 1.2 / 1.3 (design now, execute when authorized)
_2026-08-07 · Maps each 1.2/1.3 config need to the Sugar admin Developer Tool that does it. **Every item here
is a WRITE/CONFIG change to Todd's LIVE PRODUCTION Sugar** — so all of it is gated behind Todd's explicit
approval, sandbox-first where possible. This doc is the plan; it is not a licence to change his system.
Tool names from general Sugar Developer Tools (Studio / Module Builder / SugarBPM); confirm exact menu paths
against Todd's actual version/edition (schema pulled was 25.2 ent; docs shared were Sell 26.1)._

## The high-value realization: the 4-hour number without turf-stepping
**SugarBPM (Process Definitions) can measure and enforce the 4-hour SLA natively** — a process starts on lead
create, waits, and if the lead has not changed status / been actioned within 4 hours, it flags/alerts. That is
the **automated proxy** we wanted: it times first-response from system events (create → first status change /
assignment action), so **reps never have to log calls** (the hard guardrail holds). This is a better 4-hour
mechanism than parsing `calls_leads`, and it doubles as the alert that improves response time. Design it as a
non-intrusive, alert-only process first (watch, don't nag).

## Config map (need → tool → gated write)
| # | Need (JTBD) | Admin tool | Change |
|---|---|---|---|
| 1 | `lead_source` has no "Chatbot" value | **Studio → Dropdown Editor** (`lead_source_dom`) | Add "Chatbot" option |
| 2 | Carry the audience tag (molder/OEM) | **Studio → Leads → Fields** | Add custom `audience_c` dropdown |
| 3 | Confirm email capture path | **Studio → Leads** (email is a standard relate, not a field) | Verify layout/API writes email to the email relationship, not a text field |
| 4 | `phone_work` required | **Studio → Leads → Fields / Layouts** (or enforce in the Flow form) | Keep required; decide required-vs-placeholder with Todd |
| 5 | Instant acknowledgment autoresponder | **SugarBPM → Process Email Templates + Process Definition** | On lead create (source=Chatbot) → send acknowledgment |
| 6 | 4-hour SLA metric + alert | **SugarBPM (Process Definitions)** | Timer process, alert if untouched >4h (the proxy above) |
| 7 | Territory auto-routing | **SugarBPM / Assignment** | Route by region to the right rep (switch on later; audit routing first) |
| 8 | First-touch auditability | **Studio → Audit** on key Leads fields | Enable audit so status/assignment changes are timestamped |
| 9 | Attribution reporting (won/lost by source) | **Reports module** (not dev tools) | Opportunities by `lead_source` × region |

## Sequencing + safety
- **Read-only audit FIRST** (via the connected Zapier MCP, or CData MCP once wired): confirm current
  `lead_source` values, whether email is populated via the relationship, whether OEM↔molder links + activities
  exist, and whether any 4-hour/SLA process already runs. Change nothing.
- **Then, with Todd's sign-off, sandbox or one labelled test lead**: apply items 1-3 minimally, prove one lead
  end-to-end (including the email relationship fix), before any SLA/routing automation.
- **No admin config on live prod without Todd's explicit go.** Admin tools are powerful and changes to a
  production CRM are outward-facing and hard to reverse. Design here; execute on his authorization.

## Credential handling
Zach/Todd wire the MCP + login; the agent does not enter or store Todd's admin credentials. Once the MCP is
connected, the agent drives it **read-only first**, writes only after explicit per-change approval.
