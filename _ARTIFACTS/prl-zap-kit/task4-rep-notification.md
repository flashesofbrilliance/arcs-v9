# Task 4: Rep Notification Email (Edit Sheet)

Zap: 376827315 (Tidio to Sugar pipeline). Sandbox only. Estimated time: 10 minutes.

Goal: after the Sugar step in EACH path, add one "Email by Zapier" (Send Outbound Email) step so a notification fires whether the lead was updated (Path A) or created (Path B).

## Steps to add (identical settings in both paths)

Add after "Update Lead" in Path A, and after "Create Lead" in Path B.

| Field | Value |
|---|---|
| To | [rep_email], info@prlresins.com, zach.harris@gmail.com |
| Reply To | info@prlresins.com |
| Subject | New chatbot lead: [name] - [company_display] |
| Body (HTML or Plain) | see below, plain text |

Note: Email by Zapier always sends from noreply@zapiermail.com (not configurable) and is limited to about 10 emails per hour. Fine for pilot traffic; if volume grows past that, notifications will queue or drop and the step should move to a real mail provider.

Subject mapping: name = the parsed full name from the Code step ("Process State and Name Inputs"). company_display is a NEW output key added to that same Code step (do not rename existing keys): the payload account name, trimmed to 80 characters (account names over 255 chars have occurred in test data), or the literal text "Not provided" when blank. Plain field mapping in the email step cannot do a blank fallback; it must be computed upstream.

### rep_email mapping (add to the same Code step)

Map state_code to the assigned rep's email using this table (verified against the sandbox routing sweep 2026-08-26). If state_code is one of the 12 unassigned states (AK, DE, HI, ID, LA, MS, MT, NM, SD, UT, WV, WY), or the lookup misses, output rep_email as empty and the email still goes to info@prlresins.com and zach.harris@gmail.com. Never guess a rep.

| Rep | States |
|---|---|
| Bill Galla | AL, AZ, NV |
| Steve Fabrizius | AR, CO, KS, MO, NE, OK, TX |
| Lynn Winston | CA, CT, MA, ME, NH, OR, RI, VT, WA |
| Howard Altman | FL, NJ |
| Christian Cassel | GA, KY, MD, NC, SC, TN, VA |
| Kathy Brown | IL, WI |
| Tim Mulcahy | IN, MI |
| Dan Damas | IA, MN, ND |
| Robert Spano | NY, OH, PA |

Rep email addresses are not in this doc; pull them from the sandbox user records before wiring, and confirm each with Todd before the first live send.

Body (plain text, map each field from the Code step / ZoomInfo enrich / Sugar step output):

```
Name: [full name]
Company: [company]
Email: [email]
Phone: [phone]
State: [state_code]
State as typed by visitor: [raw state input]
State parse failed: [state_parse_failed]
Job title: [job title]
Industry: [industry]

View in Sugar: https://prlresinstest.sugarondemand.com/#Leads/[id]
```

Why both state lines: the parser falls back to CA when it cannot read the state. Showing only state_code would present that fallback as fact (the same failure class as the Roger Lamarre incident). The raw input plus the state_parse_failed flag lets the reader see when CA is a guess, not data.

Record link mapping: in Path A use the id from the dedup search result (the record that was updated). In Path B use the id returned by the Create Lead step. Do not hardcode; map the id field from the correct Sugar step in each path.

Blank fields: map them anyway. A blank line in the email is fine and honest; do not add filler defaults except the "Not provided" fallback in the subject so the subject never ends in a dangling dash.

## Test

Run one live test through the staging chatbot (or Zap test with a real-shaped payload). Confirm:

1. Email arrives at zach.harris@gmail.com with all fields and a working Sugar link.
2. Reply-to resolves to info@prlresins.com.
3. Both paths fire it: one test that matches an existing lead (Path A) and one that creates a new lead (Path B).
4. One test with an unassigned state (for example WY): email still arrives at info@prlresins.com and zach.harris@gmail.com with no rep address.
5. One test with a garbage state input: email shows State parse failed: true and the raw input, not just "CA".

## Barracuda protocol

Send one test, report the email's ACTUAL fate (inbox vs quarantine) and if quarantined say so plainly, the allow-list fix is on PRL's side, do not work around it. Expect quarantine to be likely: the sender is noreply@zapiermail.com, which PRL's Barracuda has never seen. The address PRL needs to allow-list is noreply@zapiermail.com (or the zapiermail.com domain).
