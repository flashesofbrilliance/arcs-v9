# STATE OF SUGAR — consolidated pre-work brief

_2026-08-11 · The single walk-in document for the 3:00 PM ET Long Ngo / SugarAI call and for the whole
1.1-close / 1.2-delivery push. Consolidates: the live CRM config audit (artifact 5fc2e7ac), the Aug-11 call
prep, the Aug-10 recoil-close, the go-live test plan, the UX pre-mortem, and the 1.2 sprint SSOT. Nothing
here is new analysis; it is the scattered truth pulled into one place so the call runs on facts, not memory._

**Sources (all in `runtime/recoil/generated/`):** `prl-lyro/SUGAR-call-prep-2026-08-11.md` ·
`2026-08-10-todd-recoil-close.md` · `prl-lyro/TEST-PLAN-go-live.md` · `prl-lyro/PREMORTEM-user-experience.md` ·
`prl-lyro/SPRINT-2-1.2-kickoff.md` · `2026-08-04-sugar-deep-dive-clarifications.md` · SugarCRM config audit
(claude.ai artifact `5fc2e7ac`).

---

## 0. The one thing

This sandbox is the gate for **1.1's 5th layer** (verify a real test lead is received, complete, in Sugar)
and **all of 1.2 delivery**. Once we have current data copied down + a login + admin/API access, wiring the
lead delivery and running UAT is a matter of days. **The call's job: get Todd's verbal yes and a named
technical contact, and choose refresh-vs-new.** Everything else is confirmable on our side.

Two Todd-owned unblocks gate go-live, and neither is technical work on our side:
1. **Written sandbox approval** (admin + API + prod copy-down) — verbal to Long today, then in writing.
2. **info@prlresins.com fixed** so leads can be received — **IN MOTION** (Jorge/IT looped with Tidio support).

---

## 1. The call today

- **Polymer Resources / SugarAI**, Tue Aug 11, **3:00–3:30 PM ET**. Zoom `https://sugarcrm.zoom.us/j/91777967025`,
  ID **917 7796 7025**, passcode **335846**.
- Organizer **Long Ngo** (long.ngo@sugarcrm.com). Attendees: Zach (accepted), **Todd (needsAction — his yes is the gate)**.
- Support case **589806** ("Sugar reports tracking leads"), status **Pending External Input** (SugarAI awaiting PRL's go).

**People:**

| Who | Role |
|---|---|
| Long Ngo — long.ngo@sugarcrm.com | Today's call · SugarCRM |
| Joseph Dade Hamblin — support@sugarcrm.com | SugarAI support · case handler (offered the two paths) |
| Bika Miltner — bika.miltner@sugarai.com | SugarAI lead (was OOO) |
| Kim Borst — kmiller@sugarai.com | SugarAI · PTO until Aug 17 · sent the scoped solution design |
| Alberto Ruiz Ospina | SugarAI technical support |
| Amy Jaeger (PRL) | Admin on the existing stale sandbox |
| Bill Galla (PRL) | **Runs Sugar** — lead verifier + territory-map owner (NOT Nicole) |

---

## 2. Field truth of the CRM (what the data actually says)

From a **read-only** audit of the live Leads module via Zapier MCP (all 175 fields + 100 real records).
Nothing was created, changed, or deleted.

**Instances:**
- Production: `https://prlresins.sugarondemand.com/`
- Existing sandbox: `https://prlresinstest.sugarondemand.com/` — **stale (~1-2 yrs old; dashboard reads
  "2025 Plan")**, admin appears to be Amy Jaeger. Entitlement: Sugar Sell Advanced allows **2 sandboxes**, so
  a refresh or a 2nd is **no additional charge**.

**Leads schema — the integration surface our chatbot writes through:**
- **6 required fields:** `account_name` (company) · `first_name` · `last_name` · `phone_work` · `lead_source` · `location_c` (state).
- **`phone_work` is REQUIRED**, filled 100/100. The bot must force phone or a lead fails to create → **phone is required in the flow** (decision made).
- **`lead_source` is a fixed picklist with no chatbot value.** Live: "Other" 91/100, "Web Site" 8/100, "AdWord" 1/100. → **add a "Chatbot" value** (needed to ever measure chatbot-sourced pipeline) or fall back to "Web Site".
- **`location_c` stores FULL state names** (Texas, California…) in all 100 live records, even though the API schema *declares* abbreviations. Existing Unbounce→Sugar zaps write full names and are correct. **Write full names.** (This reverses an earlier "use abbreviations" note.)
- **`description` = the Notes field**, filled 100/100 → this is where captured resin/application/requirements go.
- **`opportunity_name` 0/100** → confirms the workflow: bot creates a **Lead**, a human converts to Opportunity manually (Bill's step).
- **92/100 leads assigned to Bill Galla**, status "New" 100/100 → the MVP single-inbox routing design already matches existing practice exactly.
- **All 100 records on team "Global"** → **no record-level privacy exists.** A test lead cannot be hidden → either use the sandbox or one clearly-labeled test record created + deleted with explicit approval.

**The commercial substance (from the Opportunity + Order-History reports, not the Leads snapshot):**
- **$26.56M closed-won revenue has NO lead source** (all "Undefined") → the attribution black hole. Tagging every lead with a source directly attacks this. **This is the number to show the team.**
- **231 opportunities already carry a named competitor grade** mapped to a PRL grade — the commercial cross-reference is **already machine-readable in Sugar** (the spec datasheets are still PDF, but "we make an equivalent to X" can be grounded on these 231 records today).
- **95% of current leads have no email**; the chatbot captures email every time → strongest quotable value proof (but note: real *web* leads do carry email — the 95% is dragged down by a 92-record bulk import, so frame as "captures qualification depth + a clean source tag," not "the site captures no email").
- Scale/margin context for pricing: ~$86.5M shipped since Jan 2025, $10.25M open pipeline next 90 days, ~40% gross margin. One recovered lost deal covers a year of retainer many times over.

**Direct Tidio→Sugar was researched and REJECTED:** Sugar cloud REST supports only OAuth2 password/refresh (1h token, 2-call dance); no static key, no native inbound webhook. **Keep Zapier in the middle** for retry + visible task history — a raw node dropping a 500 loses the lead silently, the exact failure this project exists to prevent.

---

## 3. Stated preference (what we are trying to do)

**JTBD:** never lose a web lead; hand the rep a clean, complete, correctly-routed lead with an email and a
source tag, fast enough to hit Todd's **4-hour callback** number.

**1.1 Definition of Done (the 5th layer):** a real test conversation **down every branch (A/B/C)** produces
a Sugar lead a rep would accept as real — all 6 required fields populated, `lead_source = Chatbot`, correct
territory assignee — notification arrives within seconds, prospect gets an autoresponder, and **nothing on
the plant floor or in any rep's daily tooling changed**. Test in the sandbox; delete test leads after.

**1.2 Definition of Done:** lead lands complete **+ enriched business email** (ZoomInfo); notify +
autoresponder fire within seconds; **time-to-first-touch instrumented** (or documented New→Working proxy);
a **baseline** (volume, close rate, deal size by region + source, incl. the $15K lead-gen line) so net-new
is provable. Plus the **4-hour escalation nudge** in Sugar (second notification if a lead sits unanswered 4h).

**Payment-milestone sequence:** 1.1 (paid 7/24, finishing) → **1.2 $4,500 (paid 8/10, kicking off)** → 1.3
$4,000 (recognition) → 1.4 $6,000 (SEM landers) → 1.5 $3,500 (AI assistant, optional). Each phase gated by
its own payment.

---

## 4. Decide / ask on the call

**Primary asks (in order):**
1. **Refresh vs new** — restore the existing `prlresinstest` to current prod data, or spin a fresh 2nd sandbox? **Lean: latest production copied down** (Joseph offered both, either free).
2. **Access** — get Zach a **login + admin** on the sandbox; confirm current admin (Amy Jaeger); **developer-portal / API access** for the chatbot integration.
3. **A named technical / dev-rel contact** (the top de-risk ask) — someone to go to directly on **schema changes, deprecated fields, and API guidance**, instead of the support-case queue. Who owns technical changes on SugarAI's side; who signs off on customization changes on PRL's side.
4. **Todd's explicit yes** to proceed (he is needsAction; the whole thing is pending it).
5. **Cost** — confirm no charge (2-sandbox allowance on Sugar Sell Advanced).
6. **Timeline** — how long to restore/create + hand over credentials.

**Health-check / drift (we already diffed Kim's scoped as-built design vs the live instance):**
- Does SugarAI have a **health-check / upgrade-readiness scan** (Studio customization diagnostics) to assess the instance against the current platform — flagging drift, deprecated customizations, and what actually needs maintaining? Frame: build the integration on solid ground, not on tech debt.
- Which customizations are **non-standard vs stock**, and which are **at risk on the next upgrade**?
- Any **deprecated fields / modules / API endpoints** not to build on? **Upgrade cadence** — is this instance behind? What breaks mid-project?
- **Sandbox parity** — will the copy-down include all customizations, workflows, and the exact Leads schema?

**Integration surface confirmations:**
- Are any of the 6 required Leads fields changing/deprecated? Confirm `location_c` canonical format (full names).
- **API + auth** (OAuth2 password/refresh) — any planned changes? **Rate limits / quotas**?
- Best-practice way to add a **"Chatbot" `lead_source`** value so it survives upgrades.

**Data-model (feeds the 1.2 CRM Data-Reality session):**
- The **OEM ↔ molder** relationship + **territory** model — how represented, any planned changes?
- Best-practice fields to make **attribution** ($26.5M unattributed) + the **231 competitor-grade deals** hold going forward.

---

## 5. Blockers & gates

| Gate | Owner | State |
|---|---|---|
| **Written sandbox approval** (admin + API + copy-down) | **Todd** | Verbal to Long today → then in writing. THE gate for 1.1 L3 + all 1.2. |
| **info@prlresins.com receiving** | Todd/IT (Jorge) + Tidio | **IN MOTION** — Jorge looped with Tidio support (Aug 10). The more immediate go-live gate. |
| Sandbox provisioning (refresh vs new + creds) | SugarAI | Commercially unblocked (free, 2-allowance). Decide + trigger on the call. |
| Named technical contact | SugarAI | Ask on the call. |
| Negative keywords + garbage-lead examples | Todd | Owed — for the anti-ICP filter. |
| Territory map (rep → states) | Bill | Delivered once (`prl-territory-map.csv`); confirm current + net-new/dedup with Bill. |
| ZoomInfo contact to thread Zach | Todd | Owed — reconnect enrichment (already paid, unused) for 1.3. |

**Not blockers (already resolved, do not re-derive):** sandbox is commercially free (case 589806); Tidio's
flow-level API-call node is native webhook on the current plan (no upgrade needed for delivery); recognizer +
evals + IDES crawl + capture-first flow are **built and verified** (22,500-grid all-pass, 84-case eval);
1.3 ground truth (150 grades) delivered + verified; the Zapier Create-Lead mapping is staged.

---

## 6. Blindspots (what we do not yet know)

- **Sandbox parity is assumed, not confirmed** — a copy-down may or may not carry all customizations/workflows. Confirm on the call; verify the Leads schema in the sandbox before wiring.
- **Instance drift is real but unquantified** — the "2025 Plan" dashboard implies a large ~last-year update. We diffed the as-built design vs live, but we do not have a platform-level health scan. This is the health-check ask.
- **Amy Jaeger** — unknown to Todd; likely the original onboarding admin. Who actually holds admin rights today is unconfirmed.
- **Net-new / dedup logic** — how Sugar handles a person who moves companies (same phone, new email, new account) vs a new person at an existing account vs a new BU. Needed to make "net-new is provable." Clarify with Bill.
- **Lead → Opportunity** — automatic object creation or a manual rep step? (Audit suggests manual; confirm Bill's workflow.)
- **Territory edge cases:** 12 "Distribution" states have no direct rep (route to Nicole? the SM?); NY/PA split by sub-region (Rob=Western, Howard=Eastern) can't resolve at state level alone. Confirm defaults before auto-routing.
- **The 92-record bulk import** skews every rate in the 100-lead snapshot ("Importer Importer" created_by). Real web-era baselines need a clean pull filtered to non-import / `lead_source=Web Site`. Treat all snapshot rates as directional.
- **UL yellow-card data** — the ~$30K/6mo differentiator — is in **no file we have**. Todd-owned; the bot **HARD-routes** cert questions until sourced.

---

## 7. Pre-mortem — how this goes wrong, and the de-risk (ranked)

**Structural (the plan itself):**
1. **[HARD GATE] Broken-promise launch.** If the bot is pointed at real traffic before delivery→Sugar + rep notification are wired, every "we'll be in touch" is a lie and it lands on Todd. → **Do not expose to real visitors until Layer 3 passes and someone owns the inbox.** Staging/testing only.
2. **Building around the gate instead of pushing on it.** The sandbox gate tempts endless side-building. → **No new build until 1.1 ships or the sandbox lands.** Feature ideas go to backlog. Name a date on the call; if it slips, fall back to one Todd-signed labeled test lead.
3. **Anti-fabrication must be a deterministic hard block**, not a hope. Unsourced categories (cert/UL/price) HARD-route; a confidence-threshold off-ramp defers to a human. The eval gates BOTH (0% hallucination = when not grounded + confident, hand off, never invent). **Competitor gating built + verified BEFORE the data touches the live bot.** G/B/B = options to confirm, never a directive.

**Delivery / trust:**
4. **The 4-hour promise made but not met.** → Mailgun instant autoresponder covers the prospect immediately; the metric instruments whether the human 4-hour SLA is kept; the escalation nudge fires if not. Don't promise a time the team can't hold — soften to "shortly" until the SLA is enforced.

**Capture UX (from role-playing real visitors):**
5. **Mid-capture bail leaves no way to reach them.** → **Reorder capture to secure a reachable channel 2nd: name → email → phone → company → state.** (Implementable now.)
6. **The guardrail reads as an unhelpful bot** ("I just want the UL rating and it won't tell me"). → Reframe the route as value + acknowledge the ask: "our specialist confirms the *exact current* number so you're not on a stale spec, and here's the official data sheet." Never "I can't answer that."
7. **Two verifications before go-live:** validation failure must not dead-end and must accept real phone/email formats; and the capture gate must not be bypassable by typing first (Tidio flow-vs-Lyro precedence).
8. **Anti-ICP garbage leads** — people want resin **sheets**; PRL makes **pellets/compounds**. → Keyword trigger + prequal ("we make X, are you sure?"), negative-exclusion lead grading, optional form-factor field, SEO "what we do and don't make." Engine is BUILT (`exclusions.json` + `exclusions.py`, self-test 8/8); needs Todd's keyword list to seed.

**Sugar-specific:**
9. **Schema drift breaks the write on upgrade.** → The health-check + named-contact asks (§4) exist precisely to surface deprecated fields before we build on them.
10. **Test-lead pollution of prod.** No record-level privacy (team Global) → test only in the sandbox, or one labeled record created + deleted together, never against prod.

---

## 8. What passing looks like after the call

- Sandbox path chosen (refresh vs new), triggered, ETA on creds.
- Zach gets login + admin + API access; named technical contact captured.
- Todd's verbal yes on record; written approval to follow.
- Health-check / drift questions answered or a report promised.
- Then: import the capture-first flow to staging → wire delivery to Sugar (Zapier) → run 1.1 UAT (lead lands
  → routing → verify received → Todd + Bill sign off) → flip live in Todd's chosen window. **Days, not weeks,
  once access lands.**
