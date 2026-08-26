# Task 8: Payload Hardening Spec for Zap 376827315

Edit sheet for the live Tidio to Sugar pipeline Zap (376827315). Applies to BOTH branches: Path A (update existing lead) and Path B (create new lead). Sandbox only: prlresinstest.sugarondemand.com, rest/v11. Production is off limits.

Written so it works as a Zapier co-pilot prompt and as a human checklist. Every step has its own verification. Do the steps in order; each is independently checkable.

House rule: the existing Code step "Process State and Name Inputs" has a fixed output contract. Do not rename `state_code`, `state_parse_failed`, or the raw passthrough keys. New output keys may be added.

---

## Step 0: Preconditions (check before editing anything)

- [ ] You are editing Zap **376827315** (Tidio trigger, then Code "Process State and Name Inputs", then ZoomInfo enrich, then Sugar dedup search by email, then Paths A/B). Confirm the Zap ID in the URL.
- [ ] Draft SLA Zap 376815688 and old series_376761228 are NOT the target. Do not touch them.
- [ ] Get a sandbox API token for the read-back checks in this doc:

```
curl -s -X POST "https://prlresinstest.sugarondemand.com/rest/v11/oauth2/token" \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"password","client_id":"sugar","client_secret":"","username":"<SANDBOX_USER>","password":"<SANDBOX_PW>","platform":"base"}'
```

Save `access_token` from the response. All read-back calls below use header `OAuth-Token: <access_token>`.

---

## Edit 1: Sanitize all payload fields in one Code step (recommended single change)

Rather than adding one Formatter step per field (each Formatter step burns a Zapier task per run), extend the existing Code step "Process State and Name Inputs" with a sanitize block. This is the cheapest and most testable option. A Formatter-only fallback is given in Edit 1b for anyone who prefers no-code.

### 1a. Code step additions (JavaScript, append after the existing state/name logic; do not modify existing outputs)

Placement matters: the existing step ends with an `output = ...` assignment (it does not use `return`). Paste this block AFTER that final assignment so the `Object.assign` below merges into the object the parser already built. If the step is ever refactored to `return`, move this block above the return and merge the keys there instead. After pasting, run the step's built-in test once and confirm `state_code` and `state_parse_failed` still appear in the output alongside the new `*_clean` keys.

```javascript
// ---- Payload hardening (Task 8) ----
// Helper: treat unresolved Tidio template strings and blanks as missing.
function clean(v) {
  if (v === undefined || v === null) return "";
  var s = String(v).trim();
  // Tidio leaves literal {{property_name}} when a property was never set.
  if (s.indexOf("{{") !== -1 || s.indexOf("}}") !== -1) return "";
  return s;
}

// account_name: strip template junk, hard truncate to 255 chars (Sugar column limit).
var accountName = clean(inputData.account_name);
if (accountName.length > 255) {
  accountName = accountName.substring(0, 255);
}

// phone_work: keep only digits, plus sign, hyphen, parentheses, and spaces.
// Trim again after stripping so removed junk cannot leave trailing spaces.
var phoneWork = clean(inputData.phone_work).replace(/[^0-9+\-() ]/g, "").trim();

// email: lowercase, trimmed; empty stays empty. IMPORTANT: every downstream
// empty-email guard (the Roger Lamarre fix) must test email_clean, NOT the
// raw Tidio email. A literal {{email}} template string is non-empty raw but
// empty after clean(), and would slip past a raw-email check straight into
// the dedup search. See the routing guard note under the mapping table.
var emailClean = clean(inputData.email).toLowerCase();

// Two families of keys, on purpose:
//   *_clean       sanitized value, NO invented defaults. Used by Path A (update)
//                 so a sparse chat payload can never overwrite real CRM data
//                 with literals like "Unknown" (the Lamarre damage class).
//   *_for_create  sanitized value WITH the create-time default applied. Used
//                 by Path B (create) only, where Sugar requires last_name and
//                 a stated default is more honest than a rejected create.
output = Object.assign({}, output || {}, {
  account_name_clean: accountName,
  phone_work_clean: phoneWork,
  email_clean: emailClean,
  first_name_clean: clean(inputData.first_name),
  last_name_clean: clean(inputData.last_name),
  title_clean: clean(inputData.title),
  industry_clean: clean(inputData.industry),
  website_clean: clean(inputData.website),
  description_clean: clean(inputData.description),
  account_name_for_create: accountName || "Not provided",
  last_name_for_create: clean(inputData.last_name) || "Unknown",
  description_final: buildDescription()
});

// Compose description here, not in the Zapier field mapping: mappings cannot
// express conditionals, and both the sparse-payload default and the CA-fallback
// flag surfacing below are conditional.
function buildDescription() {
  var d = clean(inputData.description) || "Submitted via chatbot; transcript unavailable";
  // Surface the parser contract's own failure signal instead of hiding it.
  // state_parse_failed is emitted by the existing logic as the string "true"/"false".
  if (String(output && output.state_parse_failed) === "true") {
    d += " | State not confirmed by visitor";
  }
  return d;
}
```

Wire the Code step inputs so `inputData.account_name`, `inputData.phone_work`, `inputData.email`, etc. map from the Tidio trigger fields. Then remap the Sugar actions. Path A and Path B intentionally differ on two fields:

| Sugar field | Old mapping | Path B create mapping | Path A update mapping |
|---|---|---|---|
| account_name | Tidio raw company | `account_name_for_create` | `account_name_clean` |
| phone_work | Tidio raw phone | `phone_work_clean` | `phone_work_clean` |
| email1 | Tidio raw email | `email_clean` | `email_clean` |
| first_name | Code first name | `first_name_clean` | `first_name_clean` |
| last_name | Code last name | `last_name_for_create` | `last_name_clean` |
| title | Tidio raw title | `title_clean` | `title_clean` |
| industry | Tidio raw industry | `industry_clean` | `industry_clean` |
| website | Tidio raw website | `website_clean` | `website_clean` |
| description | composed text | `description_final` | `description_final` |
| primary_address_state / location_c | `state_code` (unchanged) | `state_code` (unchanged) | `state_code` (unchanged) |

Path A caveat that MUST be sandbox-verified before shipping: confirm what the Sugar update action does with an empty mapped value (skips the field vs clears it). Run a Path A test where title arrives blank against a lead whose title is populated, then read the record back. If the integration CLEARS on blank, remove the optional fields (title, industry, website, first_name, last_name, account_name) from Path A's mapping entirely and update only email, phone, state, and description. An update that erases real CRM data on a sparse chat payload is the Lamarre incident again, just via a different door.

Also point the dedup search step (Find Record by email) at `email_clean`, not the raw Tidio email.

**Routing guard (the Lamarre fix, stated precisely).** Do NOT implement the empty-email guard as a standalone Filter by Zapier step before Find Record: a top-level Filter that fails HALTS the whole run, so an empty-email visitor would produce no lead at all (silent lead loss, the opposite failure). Implement it as Path rules instead:
- Path A (update) rule: Find Record returned a record AND `email_clean` is not empty (Zapier condition: `email_clean` "Exists" / "Is not empty").
- Path B (create) rule: everything else.
- Set Find Record to "continue even if no search results" so a miss does not error the run.

The update action can only fire when a real, non-empty email matched, and empty-email payloads always land in Path B create. Note the guard field is `email_clean`; guarding on the raw Tidio email re-opens the `{{email}}` template hole described in the code comments.

### 1b. Formatter fallback for account_name only (if a no-code edit is required)

Add a step between the Code step and the Sugar actions:
- App: Formatter by Zapier
- Event: Text
- Transform: **Truncate**
- Input: the Tidio company field
- Max Length: **255**
- Append Ellipsis: **No** (an appended "..." would itself push past a clean value and is not real data)

Note: Formatter Truncate does not fix unresolved `{{...}}` strings or phone characters. The Code step in 1a covers everything in one task; prefer it.

---

## Edit 2: Explicit defaults for every mappable field

Rule: no Sugar field mapping may be left pointing at a raw Tidio property that can arrive empty or unresolved. Every field gets exactly one of: a cleaned value, a stated literal default, or a deliberate blank.

| Sugar field | Source | Default when missing | Why |
|---|---|---|---|
| last_name | `last_name_for_create` (Path B) / `last_name_clean` (Path A) | `Unknown` on create only | Sugar requires last_name; a blank rejects the create. On update, never write `Unknown` over a real name |
| first_name | `first_name_clean` | blank | Optional in Sugar; do not invent names |
| email1 | `email_clean` | blank, AND Path A's rule must require `email_clean` non-empty (see the routing guard note in Edit 1) | Empty email caused the Roger Lamarre false match; empties go to Path B create only |
| account_name | `account_name_for_create` (Path B) / `account_name_clean` (Path A) | `Not provided` on create only | Distinguishes "asked, not given" from parser failure; capped at 255. On update, never write `Not provided` over a real company name |
| phone_work | `phone_work_clean` | blank | Never store letters or emoji in a phone field |
| location_c | `state_code` | `CA` fallback per existing parser contract, with `state_parse_failed` true | Contract is locked; routing depends on a valid 2-letter code |
| lead_source | literal | `Chatbot` (literal text, not a Tidio field) | Baseline attribution; 2041 opps already have blank lead_source. lead_source is a Sugar dropdown: before relying on it for reporting, confirm `Chatbot` exists in the sandbox lead_source dropdown list (Admin > Dropdown Editor > lead_source_dom) or add it; REST will store an unlisted value but the UI and dropdown filters will not show it |
| description | `description_final` (composed in the Code step; mappings cannot express conditionals) | `Submitted via chatbot; transcript unavailable` | Keeps an audit trail even on sparse payloads |
| title | `title_clean` | blank | "Not specified" literals polluted the Lamarre record; blank is honest |
| industry | `industry_clean` | blank | Same as title |
| website | `website_clean` | blank | Same as title |

Note on `state_parse_failed`: the parser emits it as the STRING `"true"`/`"false"` (Zapier conditions compare text), so any Zap condition on it must be a text comparison against `true`, not a boolean check. When it is `"true"`, append `State not confirmed by visitor` to description so a human can see the CA fallback fired. That flag is the parser contract's own signal; surface it, do not hide it.

---

## Edit 3: Missing-property test procedure (unresolved template strings)

Purpose: prove that a Tidio conversation which never sets a property cannot write a literal `{{property_name}}` into Sugar.

1. Open the Tidio staging widget on the WP staging site. Start a fresh conversation (incognito window so no prior visitor properties exist).
2. Complete the flow but deliberately skip or leave blank at least one optional property (for example company). If the flow forces all fields, temporarily mark that question optional (or skippable) in the Tidio flow editor, run the test, then restore it. Do not rely on editing the trigger sample inside the Zap editor; Zapier does not let you hand-edit a trigger payload for a full end-to-end run (the Code step's own test panel does allow edited inputs, but that exercises only the Code step, not the Sugar write).
3. In Zapier, open Zap History for 376827315 and inspect the trigger payload of that run. Note whether the skipped property arrived as empty, absent, or as a literal `{{...}}` string. Record which of the three it was; this is the ground truth for the `clean()` guard.
4. Note the Sugar record id from the Path B create step output.
5. Read the record back (see Verification, call V3) and check every text field for the substrings `{{` and `}}`.
6. Pass condition: no field contains `{{` or `}}`; skipped fields hold their stated defaults from the Edit 2 table (account_name = `Not provided`, title blank, and so on).
7. Delete the test lead afterward:

```
curl -s -X DELETE "https://prlresinstest.sugarondemand.com/rest/v11/Leads/<test_id>" \
  -H "OAuth-Token: <access_token>"
```

Repeat once with a second skipped property (phone) to confirm the guard is generic, not field-specific.

---

## Edit 4: Oversize and hostile-input tests

1. **account_name over 255.** Run a test with a 300-character company string (account_name >255 has occurred in real test data). Pass: Sugar record's account_name is exactly the first 255 characters, and the create call did not error.
2. **phone with junk.** Submit phone `+1 (860) 555-0134 ext.9 :)`. Pass: stored phone_work is exactly `+1 (860) 555-0134 9 )`. Walk it through the regex to see why: letters, the dot, and the colon are stripped, but the closing parenthesis in `:)` is an ALLOWED character and survives, as does the `9` and the internal spaces; the final trim removes only edge spaces. The general rule: only digits, plus, hyphen, parentheses, and internal spaces remain. `ext.` letters are removed by design; if extensions matter later, that is a parser change, not a bug here. If the surviving stray `)` offends, the fix is a stricter allowlist (drop parentheses too), which is a deliberate contract change, not part of this edit.
3. **Empty email.** Submit with no email. Pass: run routes to Path B (create), never Path A (update); no pre-existing lead is modified. This re-proves the Lamarre fix under the new mappings.

---

## Verification checklist (exact read-back calls)

All calls: sandbox only, header `OAuth-Token: <access_token>` from Step 0.

- [ ] **V1. Truncation proof.** After the 300-char test:

```
curl -s "https://prlresinstest.sugarondemand.com/rest/v11/Leads/<id>?fields=account_name" \
  -H "OAuth-Token: <access_token>"
```

Check: `account_name` length is 255 (`| jq -r '.account_name | length'` prints 255).

- [ ] **V2. Phone sanitize proof.**

```
curl -s "https://prlresinstest.sugarondemand.com/rest/v11/Leads/<id>?fields=phone_work" \
  -H "OAuth-Token: <access_token>"
```

Check: value matches `^[0-9+\-() ]*$` and nothing else.

- [ ] **V3. No unresolved templates.**

```
curl -s "https://prlresinstest.sugarondemand.com/rest/v11/Leads/<id>?fields=first_name,last_name,email1,account_name,phone_work,title,industry,website,description,location_c,lead_source" \
  -H "OAuth-Token: <access_token>"
```

Check: response contains no `{{` and no `}}` (`| grep -c '{{'` prints 0); every skipped field shows its Edit 2 default.

- [ ] **V4. Defaults and routing fields.** Same call as V3. Check: `last_name` is never empty; `lead_source` = `Chatbot`; `location_c` is a valid 2-letter code (one of the 50 states); if the visitor gave no state, description contains `State not confirmed by visitor`.

- [ ] **V5. Empty-email path.** In Zap History, confirm the empty-email run took Path B. Then search Sugar by the test name to confirm exactly one new record and zero modified old records:

```
curl -s "https://prlresinstest.sugarondemand.com/rest/v11/Leads?filter[0][last_name]=<TestLastName>&fields=id,date_modified,email1" \
  -H "OAuth-Token: <access_token>"
```

- [ ] **V6. Contract intact.** In the Zap's Code step test output, confirm `state_code` and `state_parse_failed` still exist with unchanged names, and both full state names ("California") and codes ("CA") still normalize to `CA` (historical data holds both forms).

- [ ] **V7. Cleanup.** DELETE every test lead created above (call in Edit 3 step 7). List anything you could not delete in the test-lead cleanup ledger.

- [ ] **V8. Record link spot check.** Open one surviving-during-test record at `https://prlresinstest.sugarondemand.com/#Leads/<id>` and eyeball the fields once. Mechanical pass first, human look last.

---

## Rollback

Every edit here is additive (new Code outputs, remapped fields). To roll back: repoint the Path A/B field mappings to their previous sources and republish. The Code step contract keys were never touched, so the parser and routing are unaffected by a rollback.
