# 11 Tally setup notes (INTERNAL, for Zach; do not publish)

Status 2026-10-08: no Tally connector exists in this session and no form has been created. Nothing was submitted anywhere.

**Plan.** One Tally form built from `10-intake-forms-spec.md`: a first question "Which part are you answering?" (the four sections), logic that shows only that section, and a hidden field for the stage. The proposal page (`proposal-view.html`) embeds it with a plain iframe once a form id is set in `build_proposal_view.py` (`TALLY_FORM_ID`). Until then the page shows the question list as a read-only preview, so nothing leaves the page.

**Unverified, check in Tally before relying on it:** that the embed URL form is `https://tally.so/embed/<id>`; which plan allows file upload, hidden fields and logic; where Tally stores responses and its data terms; whether it has a built-in way to create a form from a prompt; export and deletion controls. Tally is another vendor in the data-flow map (P0.A4), so it goes on the vendor register.

**Rules for the form.** Links, file names and short descriptions only. No file upload until the NDA is signed and counsel agrees. No children's information, no credentials. Turn off any setting that emails answers to people outside your team. After the NDA, decide whether answers go to a sheet you own and who can see them.

**To go live:** create the form in your Tally account (the app is yours to log into; I will not sign in), set `TALLY_FORM_ID`, rebuild the page, run the page gate, read it aloud to one non-technical person, then decide whether to send.
