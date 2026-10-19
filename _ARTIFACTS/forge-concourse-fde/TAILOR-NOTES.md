# TAILOR-NOTES · Concourse · Forward Deployed Engineer

Forged 2026-10-19 from the seed, not a full forge (memory forge-cost-edit-from-seed-not-full-forge). Base: conventional one-page template from the OpEx exemplar (resume-tailor-zach). Claims and framing copied from the live pre-reads (public/concourse.html, public/concourse-sara.html, public/concourse-candidate.json) so all three agree: "intake and handoff", scoping to running system, reusable pieces for the next deployment.

## Stages run / skipped
- Ran: seed edit, render (1 page, PNG eyeballed), provenance_lint PASS (11 metrics), slop_lint PASS, public_claim_gate PASS, em-dashes 0.
- Skipped: slop_eval --strict (SKIP, no ANTHROPIC_API_KEY in env); counterpart-gauntlet (not run; time). Claims with no digit are not checked by provenance_lint.

## Choices
- Header is not the JD title (skill rule 6); the req title appears only in `<title>`.
- arcs-v9 stays private: "Live app (app.arcs.care); commit history and traces on request". The 3,500-commit figure cites status.arcs.care, which is public.
- Honest gaps on the live page (no pager, no SOC 2 / TX-RAMP, GovTech is discovery only, solo build) are not contradicted: Axon is worded as discovery and MVP scope; no on-call or audit claim.
- PRL chatbot is stated as sandbox-verified, go-live in progress (same as the Sara brief).
- Titles from the vetted OpEx exemplar; Squat title differs from the live page's "embedded product and solution lead" wording. Zach: confirm which to use.

## Not done
Not published, not linked from concourse.arcs.care, not sent. Zach decides.

## Source HTML not committed (kintsugi seam, booked here)
The pre-commit design detector (impeccable) blocks a NEW `_ARTIFACTS/*.html` on any finding. Fixing 19 tight-leading findings left one ("line-height 1.16x") that would not clear without pushing the resume to two pages; the detector scores a one-page Georgia print resume against the dark screen design system, the same category error the hook already skips for `resume_ats_render.py` output. I did not bypass or waive the gate. The source HTML stays local at `_ARTIFACTS/forge-concourse-fde/resume-concourse-fde-ats.html` (untracked) and the PDF, txt, PNG and ledger are committed. Zach decides: waive print resumes in the hook, or keep sources local.
