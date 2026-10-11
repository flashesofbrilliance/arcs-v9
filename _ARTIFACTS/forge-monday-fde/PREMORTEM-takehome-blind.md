# Blind pre-mortem: monday.com take-home (written before opening the link)
Private. "Blind" means: written without seeing the assignment, from the role, the call, public research and patterns at other companies. Update after the forensic research lands and again after you read the assignment.

Frame: it is two weeks from now and you did not advance. Why? Ranked by likelihood times damage.

| # | Failure story | Likelihood | Damage | Pre-work now | In-the-moment guard |
| --- | --- | --- | --- | --- | --- |
| 1 | You answered the wrong question: built something clever instead of what the brief asked, or sprawled past what you can finish | High | High | Write the acceptance criteria and a hard "not doing" list in the log first | Re-read the brief at each milestone; cut, don't add |
| 2 | It read as an engineering demo, not a customer outcome. Stefan is a customer-success leader | High | High | Outcome-first skeleton ready: goal and OKR, success measure, rollout, adoption, risks, next steps | Open the deliverable with the business outcome, then the build |
| 3 | You could not defend part of it in the walkthrough (AI-written code or reasoning you did not own) | Medium | Very high (also breaks their AI policy) | Decide an AI-use rule now: disclose every use in the log; build only what you can explain | Rehearse the walkthrough out loud; say "I", name tradeoffs and what you rejected |
| 4 | Platform fluency gap: misused monday concepts (boards, automations, apps framework, agents, MCP) | Medium | High | Hands-on practice in a free sandbox before the clock starts; read their docs and open repos | Name unknowns and test them, never bluff |
| 5 | Unsupported or inconsistent claims: numbers that disagree with your resume, the case study or the public pages | Medium | High | Reuse the consistency sheet; every number cites a source | Run the provenance and slop gates before submitting |
| 6 | Process failure on a one-time link: closed tab, lost session, no autosave, wrong format, missed deadline | Medium | Very high | Ask what happens if the link is lost; test your setup; plan a quiet, uninterrupted block; know the submission mechanics | Draft locally, keep the tab open, never refresh, screenshot each step |
| 7 | The ARCS "constitutional court wrapper" read as thirsty, jargon-heavy or off-brief | Medium | Medium | Keep it plain; position it as how you would qualify agents for a regulated client, only if the brief invites it | Put it in an appendix; lead with the asked deliverable |
| 8 | IP and confidentiality slip: private ARCS code or data in the deliverable, or the assignment text shared publicly | Low | High | Ask Sam about ownership and retention; build self-contained work on public or deliberately released code | Keep the assignment text private; no client names or PII |
| 9 | Overpromised the frontier or local-model angle (said Qwen, did not run it) | Medium | Medium | Decide now what you will actually run; Ollama has Llama models pulled, Qwen not | Say "I compared N cases" only if you did |
| 10 | Ambiguity handled silently: hidden assumptions, no questions to Sam or Stefan | Medium | Medium | Write your clarifying questions in advance | State assumptions in the deliverable |
| 11 | Fatigue and scheduling: started late at night, rushed the last third | Medium | Medium | Block the time; sleep; family logistics settled | Stop at the time cap and submit |
| 12 | Governance missing where it mattered, or overdone where it did not | Low | Medium | Prepare a short regulated-delivery checklist (evidence, PII, audit, change control, one-way doors) | Use it only if the scenario touches it |

## Quiet signals to design for
- They may weigh how you handle ambiguity and communication as much as the output.
- Engineer peers will read the build; the hiring manager will read the narrative. Serve both in one document.
- A reviewer who sees "worked fast with AI, cannot explain it" will mark it down faster than a modest but fully owned result.

## Right level of pre-work (do this, not that)
- **Do:** scaffolding: the log, a deliverable skeleton, an evidence ledger, a rehearsal plan, a sandbox for monday fluency, and your clarifying questions.
- **Do not:** pre-solve a problem you have not seen, or pre-build the answer. If the brief forbids prior work or AI, you need to know first.

## Questions to ask Sam before you open the link
1. Is there a time limit once the link is opened, and what happens if the browser session is lost?
2. What is the expected time commitment, deadline and submission format (deck, doc, video, working build)?
3. Is AI allowed for the assignment, and what disclosure do they want?
4. Who is the audience for the review, and what are they scoring?
5. Will I work in a trial account, and what tools or models may I use?
6. How is take-home work stored and who owns it afterward?

## Go / no-go to open the link
- [ ] Question answers received, or the unknowns accepted
- [ ] A protected block of time and a stable connection
- [ ] Log started and the AI-use rule written
- [ ] Sandbox practice done; deliverable skeleton ready
- [ ] Confidentiality rule understood
- [ ] A time cap decided, with a plan to submit at the cap

## To add after the forensic research
Findings from monday's open-source repos and docs (what sensei really does, MCP details, local-model support) will become additional checks here.


## Update: mechanics from the invitation (Oct 8)
- **The deadline is fixed: Thursday Oct 15, 5pm ET.** The session stays open until submission, revocation or the deadline, so activation does not start a personal timer. That argues for activating soon, to see the real brief and still have days to ask questions.
- **One-time link (credential):** activate once, in the browser and device you will finish on, with the exact invited email. Bookmark the dashboard. No incognito, no clearing cookies, no switching browsers, no forwarding. Decide the browser now and check that no extension clears cookies.
- **Deliverable:** one ZIP under 10 MB with non-empty source/ and presentation/ folders. That limit rules out a large video; plan a compact deck or a small recording. A packaging and size-check script is ready at takehome-workspace/package.sh.
- **Required steps:** watch the whole intro video, review the pre-read and materials, complete every checklist item. Budget time for these before building.
- **Still unknown (behind the link):** the problem itself, the AI policy for the assignment, and the scoring.


## Update from the forensic research (Oct 8)
Read-only static research on monday's GitHub, Hugging Face and developer docs is in research/monday-oss-forensics-report.md, with a completeness critic. New failure modes:
- **FM14 (High damage): criticizing monday's own repo.** Sensei is a mondaycom repo; the hiring manager or the take-home author may care about it. Frame gaps as "what an eval needs next," never "what is broken," and do not name third parties.
- **FM15 (High damage): stating unrun findings as fact.** The defect claims were read in source, not executed. Reproduce them or label them. A claim that fails to reproduce in front of a reviewer costs more than not making it.
- **FM16 (Medium): stale counts.** Stars, versions, issue states and tool counts drift daily. Re-pull before quoting.
- **FM17 (Medium): heavy ARCS vocabulary or a pivot to self-promotion.** Your own outcome-capture numbers undercut a calibration pitch if raised. Present ARCS as a discipline, not a proof.
- **Responsible disclosure:** the research flagged a default JWT secret in a protocol repo. If it is real, treat it as a private maintainer matter, not interview material.
Rubric gates H11 and H12 now cover these.
