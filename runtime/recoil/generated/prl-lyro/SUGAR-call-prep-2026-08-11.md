# SugarCRM sandbox call — prep (Tue Aug 11, 3:00 PM ET · Long Ngo)

_2026-08-10 · Consolidated from Gmail (case 589806) + calendar. This is the sandbox call that unblocks 1.1's
receiving-end proof and all of 1.2 delivery. **Sandbox access is pending Todd's approval.**_

## The meeting
- **"Polymer Resources/SugarAI"** — Tue **Aug 11, 3:00–3:30 PM ET**. Zoom: `https://sugarcrm.zoom.us/j/91777967025`, ID **917 7796 7025**, passcode **335846**.
- Organizer: **Long Ngo** (long.ngo@sugarcrm.com, SugarCRM). Attendees: Zach (accepted), **Todd Hotes (needsAction)**.
- Support case: **589806** ("Sugar reports tracking leads"), status **Pending External Input** (SugarAI awaiting PRL's go).

## State as of Aug 10 (from the case thread)
- **An existing sandbox already exists:** `https://prlresinstest.sugarondemand.com/`
  - It is a **stale copy of production** (~1–2 years old; dashboard reads "2025 Plan").
  - **Instance admin appears to be Amy Jaeger** (PRL side).
- Production instance: `https://prlresins.sugarondemand.com/`
- **Entitlement:** Sugar Sell Advanced allows **2 sandboxes**; one exists, so a refresh or a 2nd is at **no additional charge** (save DB/filesystem usage notes).
- **SugarAI (Joseph Dade Hamblin) offered two paths, either free:**
  1. **Restore-from-parent** the existing `prlresinstest` sandbox to current production data, or
  2. **Create a new** (second) sandbox from the latest production backup.
- **Zach's reply (to Joseph, Aug 10):** yes, want a version with the **latest production data copied down**; asked **who has admin access** and **whether Zach will get access**.
- **Zach forwarded to Todd (Aug 10):** "This is promising. If you're OK with what they're proposing, I think this makes the most sense. Let's ask Long about this tomorrow?" → **the sandbox is pending Todd's approval to proceed.**

## The people
| Who | Email | Role |
|---|---|---|
| Long Ngo | long.ngo@sugarcrm.com | Tomorrow's call · SugarCRM |
| Bika Miltner | bika.miltner@sugarai.com | SugarAI lead (was OOO) |
| Kim Borst | kmiller@sugarai.com | SugarAI · PTO until Aug 17 |
| Joseph Dade Hamblin | (support@sugarcrm.com) | SugarAI support · case handler |
| Alberto Ruiz Ospina | (support) | SugarAI technical support |
| Amy Jaeger | — | Admin on the existing sandbox (PRL) |

## Decide / ask on the call
1. **Refresh vs new:** restore the existing `prlresinstest` to current production data, or spin a fresh 2nd sandbox? (Lean: latest production copied down.)
2. **Access:** get Zach a **login + admin** on the sandbox; confirm who currently holds admin (Amy Jaeger); **developer-portal / API access** for the chatbot integration.
3. **Cost:** confirm no charge (2-sandbox allowance on Sugar Sell Advanced).
4. **Todd's approval:** get his explicit yes to proceed (he is needsAction on the invite; the whole thing is pending it).
5. **Timeline:** how long to restore/create + hand over credentials.

## Why it matters
This sandbox is the gate for **1.1's 5th layer** (verify a test lead is received) and **all of 1.2 delivery**. Once access lands with the current data + a login, wiring the lead delivery and running UAT is a matter of days.
