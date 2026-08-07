# PRL 1.1/1.2 build assets: autoresponder + Zap field map
_2026-08-07 · Drop-in assets so the Tidio flow and the Zap are fully built, leaving only the Sugar write for
Todd's go. Plain language, no specs/prices/certs (anti-fabrication holds)._

## 1) Acknowledgment autoresponder (1.2)
Sent instantly on capture (Tidio auto-message, or the flow's email step, or Resend/Mailgun). Keep it short,
human, and specialist-routed. No spec, price, or lead-time promises.

**Subject:** Thanks for reaching out to Polymer Resources

**Body:**
> Hi [First name],
>
> Thanks for getting in touch with Polymer Resources. We have your inquiry and a PRL specialist will follow up
> shortly to help with [application/interest].
>
> If it is easier to talk now, you can reach us at 1-800-243-5176 during business hours.
>
> Talk soon,
> The Polymer Resources team

Notes: `[First name]` and `[application/interest]` are merge fields from the capture form. Do not have it state
a grade, spec, price, or availability. If sent from a domain address, confirm SPF/DKIM before go-live so it
does not spam-filter (a 1.2 deliverability check).

## 2) Zapier Catch Hook -> SugarCRM Create Record field map (1.1)
The Zap: **Catch Hook** (receives the flow payload) -> **SugarCRM Create Record (module: Leads)**. Build it
fully; leave the Create Record step OFF (or pointed at the labelled test lead) until Todd approves the write.

| Catch Hook field (from flow) | Sugar Leads field | Notes |
|---|---|---|
| `first_name` | `first_name` | required |
| `last_name` | `last_name` | required |
| `account_name` | `account_name` | company |
| `phone_work` | `phone_work` | required in Sugar; per Todd's phone decision |
| `email1` | **`email1`** | THE fix: write to `email1`, Sugar maintains the email relationship |
| `description` | `description` | full inquiry text |
| `lead_source` = "Chatbot" | `lead_source` | needs the "Chatbot" dropdown value added (Studio, gated) |
| `status` = "New" | `status` | matches existing convention |
| (assignment) | `assigned_user_id` | sales manager for MVP; territory routing later |
| `market` | `description` (append) or a custom field | MVP: fold into description |
| `source_url`, `captured_at` | `description` (append) | provenance, optional |

Reliability (1.2): set the Zap to **retry**; add a fallback step that **emails the lead to a human** if the
Sugar write errors, so a lead is never silently dropped. Zapier task history is the audit trail.

## Sequence to done
1. Build the flow (see `prl-tidio-capture-flow-spec.md`) + this autoresponder.
2. Verify capture via Tidio email/panel/export (no Sugar needed).
3. Build the Zap up to the Create Record step using the map above.
4. On Todd's go: add the "Chatbot" lead_source value, turn on the Create Record write, run one labelled test
   lead end to end, confirm it lands with `email1` populated, then flip live.
