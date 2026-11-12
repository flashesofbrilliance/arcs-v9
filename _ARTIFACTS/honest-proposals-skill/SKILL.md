---
name: honest-proposals
description: Turn a client's ask (an email, call notes or an RFP) into an honest proposal from one engagement record. It renders the reply, a plain-language agreement with Exhibit A and an internal five-altitude page, and refuses to send a number without a source, a quote where a range belongs, a sharing ban, or a task-level price list before the paid step. Use when a consultant is writing a small fixed-fee proposal. It stops before anything is sent.
---

# honest-proposals (v0.1, staging copy)

> Staging copy inside arcs-v9 for later extraction to a public repo. Nothing here is public yet.
> v0.1 supports one engagement type: **a fixed-fee paid first step for a private client who asked by email or
> call, with later steps shown as ranges.** Formal RFP responses come later.

Most proposal tools optimize for winning. This one is for proposals the client can trust after they sign:
every number has a source, later work is a range with written assumptions, and what has not been proven
is said out loud. The sibling skill `resume-tailor` does the same for a resume.

## What you need

- The client's own words: the email thread or call notes. Quote their questions; do not paraphrase them into
  questions they did not ask.
- Your rate, the hours for the first step, and your judgment on the later ranges.
- `scripts/engagement_render.py` and `scripts/proposal_lint.py` (Python 3.9+, standard library only).

## The rules this skill enforces

| Rule | Enforced by |
|---|---|
| Every number cites a source or is labeled judgment | renderer (every field has `source`), lint 1 (no typed figures) |
| The first step is a fixed fee; later steps are ranges with written assumptions, never a quote | renderer |
| A reliance disclaimer instead of a sharing ban | renderer (needs a `reliance` term), lint 2 |
| No task-level bid sheet or full-build figure before the paid step | lint 3 |
| "Opinion, not legal or compliance advice" and "as is", stated plainly; a lawyer reads the agreement once per template version | lint 2, send gate (`counsel_review`) |
| A prediction of the reply, with odds and their basis, scored after the reply | send gate (`ex_ante`), then `close` |
| A pre-send review from the client's seats | send gate (`gauntlet`) |
| What is not proven yet is said out loud | renderer (`not_proven[]` non-empty) |
| A change after sending is shown, never silent | renderer (change seam once `last_sent` is set) |
| Plain language, first person singular, no em-dashes | lint 4 |

## Workflow

1. **Intake.** Copy `example-fictional/` to `_ARTIFACTS/engagements/<slug>/`. List the client's questions in
   `asks[]`, each with its source (who, when). Ask the person what they are unsure about; that goes in
   `not_proven[]` and `assumptions[]`, each assumption with the test that would decide it.
2. **Fill the record.** Every value is a field with `kind`, `value`, `label` and `source {kind, ref, date}`.
   Source kinds: sent, email, doc, decision, judgment, call. A guess is `judgment`; never dress it up.
   Fees that follow from others are `derive`d (for example hours times rate). Set `leak.ceiling_usd` just above
   the largest figure you are willing to show before the first step is paid.
3. **Write the templates.** Change wording only where this client differs. Every figure in a template is a
   `{{field}}` cite. Write as "I" to "you".
4. **Render and lint.**
   ```
   python3 scripts/engagement_render.py --dir _ARTIFACTS/engagements/<slug>
   python3 scripts/proposal_lint.py --dir _ARTIFACTS/engagements/<slug>
   ```
   Fix the record or the template, never the output.
5. **Pre-send review.** Read every client output from five seats, at a high burden of proof, and record the
   result as `gauntlet {date, ref, open_findings}`:
   - **Founder:** does this answer what I asked, in my words? What would make me stop reading?
   - **Finance:** can I tell what I pay, when, and what could make it more?
   - **Counsel:** what in the agreement is unclear, one-sided or missing for my state?
   - **Skeptic:** which claim is not backed by anything in the record? What is oversold?
   - **Busy reader:** after thirty seconds, do I know the price, the date and the next step?
   Fix each real finding, then set `open_findings` to the number still open.
6. **Predict the reply.** Write `ex_ante {expect, p, basis {kind, text}, date}`. The basis kind is stated,
   measured or judgment; a judgment says so.
7. **Send gate.** `python3 scripts/proposal_lint.py --send-ready --dir <slug>` must pass: outputs fresh, a lawyer
   review recorded (`counsel_review {date, by_role, template_version}`), the review clean, the prediction written.
   Then set `meta.last_sent`. The person sends; this skill never does.
8. **After the reply.** Write `close {what_happened, held, date}`. Changes after sending show as a visible seam.

## What it will not do

- Price the whole job before the first step is paid.
- Turn a client's question into a sales pitch.
- Give legal advice. The agreement template is a plain-language starting draft that follows one US state's
  habits; a lawyer reads it before first use.

## Not proven yet

- That honest proposals win more often than ordinary ones. The `ex_ante` and `close` fields exist to find out.
- That the record fits engagement types other than the one above.
- Numbers written as words pass the typed-figure lint.
