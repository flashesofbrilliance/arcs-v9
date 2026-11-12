<!-- DRAFT for Zach. Not sent. Counterpart-facing: no client names, no private material. Fill the [BLANKS]. -->

# Every number in the memo, traced before the vote

**A fixed-fee check for investment committees and boards.**

Before your committee or board votes, I check every number in the memo or deck against the documents it came
from: the term sheet, the LPA and its amendments, the side letters, the resolutions. Each number comes back with
the exact clause it rests on, or a plain flag that no clause supports it.

## What you get

A short report, one row per number in the memo:

- **Traced.** The number, the sentence it sits in, and the clause that states that number on the same subject,
  with the clause text quoted.
- **Inputs traced, math not checked.** For a number that is worked out (a fee in dollars, a net return), the
  clauses that feed it. I do not restate or redo the math; your team does.
- **Not covered.** No clause in the set supports the number. These are the ones to look at first.

The report also lists any document I could not read in full, such as a scanned page or a file that still has
tracked changes or comments. For those I ask which version the vote is on rather than picking one, so a gap never
shows up as "not covered".

Where an amendment changed a term, the report shows the current wording and the wording it replaced. Where a side
letter changes a term for one investor, the report names that investor's side letter.

## How it works

The check is built on an engine I wrote and published, which answers questions about long documents with the
exact clause behind each answer, or says "not covered". Its rules are enforced in code, not left to an AI:

- Every answer points to a clause that exists in your documents.
- Every amount, percentage and date matches the clause word for word, or it is flagged.
- If a later document changed a term, the later wording wins, and both are shown.
- It never writes proposal language and never gives a go or no-go verdict. Part of setup is extending that
  refusal to investment questions ("should we invest", "is this term market").

You can read the code and try it yourself: [PUBLIC LINK].

## What it is not

- **Not legal review.** It checks that a number appears in a clause. It does not check that the clause means what
  the memo says, or that a term is enforceable or market. Your counsel still owns that.
- **Not a model of the deal.** It does not check projections, valuations or assumptions.
- **Not proven on fund documents yet.** The engine was built and tested on bid documents. That is why the first
  step below is a dry run on a past memo you choose, before I touch a live one.

## Your documents stay private

By default the check runs with no AI service and no internet connection, on [YOUR MACHINE / MY MACHINE UNDER
NDA]. Nothing is sent to an outside AI provider unless you approve it in writing.

## Scope and price

| | |
|---|---|
| Setup and dry run | I set it up for your document formats and run it on one past, already-decided memo you pick. You see the report and decide whether to go on. [PRICE] fixed, [WEEKS] weeks |
| Each live check | One memo or deck and its document set, report delivered [TURNAROUND] before the vote. [PRICE] fixed |
| Documents covered | [LIST, e.g. term sheet, LPA and amendments, side letters, board resolutions] |
| Not included | Legal review, financial modeling, documents outside the agreed set |

If the dry run does not catch anything your team would have wanted caught, you stop there and [CREDIT / REFUND
TERM].

## Next step

A 30-minute call. Bring one past memo you are comfortable using as the test, and I will tell you on the call
whether your documents fit.

Zach Harris · [EMAIL] · [PHONE]
