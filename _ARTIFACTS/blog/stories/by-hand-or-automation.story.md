---story---
{
  "slug": "by-hand-or-automation",
  "tier": "full",
  "title": "By hand or with automation",
  "description": "Notes from the trenches: a data founder asked one operational question I never answered. The answer is three commands, one JSON per account, and a human who reviews instead of executes.",
  "eyebrow": "NOTES FROM THE TRENCHES // BUILDING IN PUBLIC: ARCS // FIELD OS EDITION",
  "threads": [
    {"id": "red",  "hex": "#FF4D6D", "name": "red · asks",     "shape": "diamond"},
    {"id": "gold", "hex": "#FFD700", "name": "gold · commands", "shape": "circle"},
    {"id": "verm", "hex": "#FF6B2C", "name": "vermillion · seams", "shape": "square"}
  ],
  "arc": {"caption": "from hand to pipeline", "stops": [
    {"label": "the question", "thread": "red"},
    {"label": "the wrong answer", "thread": "verm"},
    {"label": "one JSON per account", "thread": "gold"},
    {"label": "score the bet", "thread": "gold"},
    {"label": "render, then review", "thread": "gold"},
    {"label": "his format, not mine", "thread": "red"}
  ]}
}
---/story---

# NOTES FROM THE TRENCHES // BUILDING IN PUBLIC: ARCS // FIELD OS EDITION
## By hand or with automation

*A founder who runs a data team asked me, on a call in July, one plain question about how the work gets done. I answered with a philosophy. Six weeks and two "hard to follow" emails later, this is the answer I owed him. Three threads: **red** is what he actually asked, in his words. **Gold** is the commands that answer it. **Vermillion** is the seam where a thing done by hand became a thing a machine can repeat.*

## The question

— *Red: "I don't know if you do it by hand or with automation."*

That is the whole ask. He was not asking about my method. He was asking what a partner needs to know before he offers something to his own customers: what does he hand over, what happens to it, how long does it take, and what comes back.

— *Verm: I answered with the word notation and a metaphor about a human on a bike. He said "all right, that makes sense," which is what a polite person says when it does not.*

*In plain terms: when someone asks whether a thing is manual or automated, they are asking whether they can resell it. Answer that.*

## The wrong answer, kept

I could quietly delete the bad answer and write the good one. The record says otherwise, so the bad one stays. The recoil report I sent him after the call had a chart of my own beliefs moving over the length of our conversation. He wrote back: "It has lots of information but hard to follow." I rebuilt the page. He wrote back again: "I honestly think I am still so lost in your offering and the page."

— *Red: "time series per customer is really helpful and the aggregation is also really helpful."*

He had told me his format on the call. Rows over time, per customer, then a roll-up. I sent him curves and a dial. Twice.

>> The bet is filed before. The transcript is filed as it happens. Neither can be edited after. That is what makes the score checkable, and it is also what lets a machine do most of the work.

## One JSON per account

Here is the honest answer to his question. The state of any relationship I track is one file.

> runtime/recoil/generated/DATE-ACCOUNT.json

It holds the pre-call bet with a number on each line, the beliefs, and every update with the quoted line that moved it. A new call is a new row. Nothing in it is typed twice.

— *Gold: python3 scripts/recoil_brief.py --data runtime/recoil/generated/DATE-ACCOUNT.json --audience external --format html*

One flag decides who is allowed to see what. The internal audience gets conviction scores and the war-game tabs. The external audience gets the rows and the quotes. Same file, two renders, and the leak check runs on the external one before it leaves.

The seam is the --set flag. It takes key.path=value and overrides one field without opening the file. That is the difference between a template and a form letter: the shape holds, the values pass through.

## Score the bet

After the call, the transcript comes in from the recorder. The bet already exists, so scoring is subtraction, not storytelling.

— *Gold: python3 scripts/gen_receipt_close.py --recoil runtime/recoil/generated/DATE-ACCOUNT.json --ex-ante runtime/recoil/generated/DATE-ACCOUNT.json --out _STATE/receipt-close.json*

The output is a scaffold with one row per belief: the number before, the number after, the line that moved it. On our call, one of my beliefs went from seventy to twenty-five percent when he said his media proposal was a side project. That row is the most useful thing in the file, and no one wrote it by hand.

*In plain terms: the human does not score the call. The human reads the score and decides what to do Monday.*

## Render, then review

— *Gold: python3 scripts/forge_counterpart.py --surface receipt --data _STATE/receipt-close.json --out public/customer-receipt.html*

The forge is a factory. It has stamped four different people's pages from the same template with different data. The surface flag picks the shape: a receipt, a codex, a one-door decision page. The verify-only flag runs the honesty gates on an existing file without rendering anything, which is how a page gets checked before it is sent.

— *Verm: this is the seam his question was really about. Automation runs the three steps. A person reviews the output once, at the end, and sends it by hand. He described his own company the same way on the call: "the human being is often doing the review, not the execution." Same shape. I should have said so.*

[[ARC]]

## His format, not mine

The last command is the one that keeps me honest about the rest.

— *Gold: python3 scripts/tool_catalog_emit.py*

It emits every tool in the repo with the one job it does, harvested from the tool's own declaration, never inferred. As of this week it opens with a named family: the receipt loop, in stage order. Before, the bet. During, the transcript. After, the score. Share, the gauntlet and the page. Compounds, the account record that gets one row longer every call.

He asked what he hands over and what comes back. He hands over an export of a customer's sales calls, one row per call. What comes back is a table per deal, rows over time, then a roll-up across the book. His format. It was always his format; the commands were built for it. I just kept showing him the chart instead of the rows.

>> A question you did not answer is a row in the account record with a red number next to it. Keep it. It is the most useful row you have.

## The braid, for the record

Two asks, verbatim, both answerable in a sentence. Five commands that already existed when he asked. One seam, the flag that passes a value through a fixed shape. That is what turns by hand into mechanical without turning the person into a bystander.

*Every quoted line above is verbatim from the recorded call or the email thread, checked against the raw transcript on the day this was written. Anything not in quotation marks is my read.*
