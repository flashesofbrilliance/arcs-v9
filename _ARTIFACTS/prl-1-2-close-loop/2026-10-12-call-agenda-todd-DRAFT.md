DRAFT, not sent. For Zach to edit and send.

Subject: Agenda for Monday's Phase 1.2 wrap-up (10:00 ET)

Todd,

Short version: I found why Roger Lamarre's lead kept getting changed, and the fix is ready but not live. I'd like us to switch it on together Monday so you see every step.

1. What went wrong (5 min)
Your Sep 17 test chat didn't come in "dead" because of a missing email. The chatbot found the right record (your test lead), but the update step was locked onto Roger's record from an August test. So any returning visitor would have updated Roger instead of themselves.

2. The fix (10 min, screen share)
I've prepared an unpublished draft. The update step now uses whatever record the search finds, and it no longer overwrites notes, title or industry with filler text. Nothing has changed in your live setup yet.

3. Switch it on together (15 min)
- One quick test in the sandbox to confirm an update leaves empty fields alone rather than wiping them.
- Publish the draft.
- Restore Roger's record.
- Run two test chats: a repeat visitor should update their own lead, and Roger should stay untouched.

4. Correction on the "lagging lead" (2 min)
I'd thought your Zapier plan was holding this automation's runs until Nov 12. It isn't: the held run is from a different automation (Covestro Unbounce). Your chatbot runs are going through.

5. Still needed from PRL before going live on production Sugar (10 min)
- Add "Chatbot" to the Lead Source list in live Sugar.
- A dedicated Sugar user for the automation, not an SSO login.
- WordPress access to install the Tidio plugin.
- Allow-list the alert sender with IT, and confirm each rep's Sugar email.
- Territory list: 12 states still route to no rep; for now they go to Bill.

6. Next steps and owners (3 min)

Zach
