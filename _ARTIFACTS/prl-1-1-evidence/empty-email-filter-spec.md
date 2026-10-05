# Empty-email dedup filter — Zapier co-pilot spec + go-live test addition (2026-09-08)

> **Why this exists (the keel).** The live delivery Zap (376827315) de-duplicates leads by searching
> Sugar on `email1`. When a submission has an EMPTY email, the search matches an arbitrary existing
> record and Path A (UPDATE) overwrites it. This already corrupted a real 2021 lead (Roger A Lamarre,
> `ea77a7d2-1b0b-11ec-...`) in the sandbox — repaired by hand, but the PREVENTION was never shipped.
> GO-LIVE-FIRST points this at PRODUCTION Sugar, where the same path overwrites a real customer record
> that 55+ manual-conversion reps would not notice. This is a blocking go-live pre-condition, not a
> loose end. Bar-raiser protocol: co-pilot implements, Zach verifies by reading the Sugar record back
> directly — never trust the co-pilot's step-test echo.

---

## PART 1 — Zapier co-pilot prompt (paste into the co-pilot)

> Work only on Zap **376827315** on the **sandbox** connection (`prlresinstest.sugarondemand.com`,
> connection 65663180). Do not touch prod. Do not publish until I confirm.

**Task: add a guard so the dedup search never runs on an empty email.**

1. **Insert a Filter step** immediately AFTER the Code/parse step that produces the email, and BEFORE
   the "Find Record in SugarCRM" (dedup search) step.
2. Filter condition: **`email` (the parsed lead email) — "(Text) Exists" AND "(Text) Does not contain" a blank** —
   i.e. only continue if a non-empty, syntactically plausible email is present. If your Filter UI
   offers it, also require it "(Text) Contains" `@`. Trim whitespace first if a Formatter/Code step is
   easier than relying on the raw value.
3. **Decide the no-email branch — do NOT silently drop the lead.** A chatbot lead with no email is
   still a real lead. Route the "email is empty" case to the **unassigned-lead safety net** (the
   catch-all to Bill + digest, drafted in zap-kit task3 / Zap 376815688) as a CREATE-only path:
   create a fresh Sugar lead with whatever fields we do have, `lead_source` unchanged, and a
   `description` note `"NO EMAIL ON SUBMISSION — dedup skipped, routed to catch-all"`. It must NEVER
   enter the Find-Record → Path A (UPDATE) branch.
4. Leave Path A / Path B for the normal (non-empty email) flow exactly as they are.

**After you build it, tell me the exact filter condition text and which step number the filter sits at.
Do not publish. I will verify against Sugar directly before we publish.**

---

## PART 2 — Zach's independent verification (before publish; do not skip)

Run these against the sandbox via the Zapier MCP raw request (`/rest/v11_5/Leads`), NOT the co-pilot's
step-test:

1. **Empty-email submission** → confirm NO existing record was modified. Query the record the old bug
   hit (Roger `ea77a7d2-...`) and 2-3 other arbitrary leads; confirm `date_modified` unchanged.
   Confirm a NEW catch-all lead was created with the `NO EMAIL ON SUBMISSION` description note.
2. **Valid-email new visitor** → normal Path B CREATE still works, correct field map, `location_c`
   parsed, `lead_source: "Chatbot"`.
3. **Valid-email repeat visitor** (same email as an existing lead) → Path A UPDATE still de-dupes
   correctly (this is the legitimate dedup we want to keep).
4. Harden Path A field mapping so it only writes the intended **4** fields and cannot clobber others:
   `description`, `title`, `hint_account_industry`, `account_description` (the bug wrote 4, not the 3
   the original brief listed).

Only after 1-4 pass on a direct read: publish.

---

## PART 3 — Go-live test addition (fixes the gate that can't catch this)

The Sep-1 recap defined the green light as *"run a chat as a fresh visitor and watch the lead land."*
A fresh visitor with a valid email CANNOT trigger the empty-email path, so that test green-lights over
the bug. Add two cases to the go-live test Todd runs with his own account:

- **Empty-email case:** start a chat, reach the lead step, submit with the email field left blank →
  confirm no existing Sugar record changed AND a catch-all lead was created.
- **Repeat-visitor case:** run a second chat with the SAME email as the first → confirm it updates the
  same lead (legit dedup), not a new duplicate.

Green light to go live = happy path + BOTH failure-mode cases pass. Not before.
