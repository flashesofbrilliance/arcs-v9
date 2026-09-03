# Ahmed's explicit asks, verbatim, and what each one gets

Source: raw Granola transcript `e8648395` (Jul 22) and the Gmail thread (Jul 28, Sep 2). Every line in
quotes is verbatim. This is the spine of the bundle: his asks are the sections, in his order.
Lesson applied from Robin: listen, then give them exactly what they asked to see, evidence-based,
traceable, scored, serializable. Nothing they did not ask for.

| # | He asked (verbatim) | When | What he gets in the bundle | Evidence it traces to |
|---|---|---|---|---|
| 1 | "with arcs who are you working with, what kind of stages of companies you're seeing that benefit from this?" | Jul 22 | One table: persona, stage, what they got, LIVE or DEMO flag. No names without consent. | tools-by-persona map, honesty flags |
| 2 | "I should really connect you" (Robert) / "For Rob, can you send me a blurb and I can forward it" | Jul 22, Sep 2 | The two-line blurb, ready to forward. Sent today regardless of the call. | talk track, Rob blurb section |
| 3 | "I think this is a lot really really cool but I think I need like a little demo" | Jul 22 | The demo, small: one customer-shaped table, one deal, five rows, per-call over time. Not our call. | one-table page, re-cut for a customer |
| 4 | "look at everyone who had a sales call and let's grab their timeline, let's give it to your system and let's do that analysis and I don't know if it works well with one or multiple" | Jul 22 | The input spec: what a timeline export looks like (columns, one row per call), and the honest answer: one deal is proven on advisors; multiple is the pilot. | SSOT schema, kinematic_series |
| 5 | "if you can send me over like a small demo of anything that can be helpful for me to just kind of wrap my head around it" | Jul 22 | Same as 3. Small is the spec. One screen. | |
| 6 | "how much you charge for this by the way" | Jul 22 | One sentence, one number when we pick who: first report free, then a fixed per-customer fee. Nothing else. | pricing story, single version |
| 7 | "I don't know if you do it by hand or with automation" | Jul 22 | The delivery mechanics, plainly: what he hands over (an export), what happens (automated pass, one human review), how long (state it), what comes back (the table). This was never answered. | recoil-close, gen_receipt_close.py |
| 8 | "a sponsored presentation with your information on it" / "a free trial you only get to run once per company and once you do it you can talk to Zach for more" | Jul 22 | His funnel, as he designed it, written back to him as the offer. One page with a Polyform-branded slot. | his words, unchanged |
| 9 | "time series per customer is really helpful and the aggregation is also really helpful" | Jul 22 | The output in that exact shape: per customer over time, then the roll-up. Tables, not curves. | his format spec |
| 10 | "I think I will need you to explain to me how to consume this" | Jul 28 | A two-minute prep card in the saul.arcs.care PREP schema: what to say to a customer, three things to land, two questions, watch-outs. Read for two minutes, then talk. | saul.html template |
| 11 | "I honestly think I am still so lost in your offering and the page" | Sep 2 | The offering in three sentences at the top of the bundle, before anything else. Who it is for, what they get, what they do Monday. | talk track |

## Bundle shape (after the call, through the defined path)

Self-contained, one URL, atlas-style: a table of contents that IS this list, eleven sections, each
one screen, each headed by his verbatim ask. Data-driven from one object (the saul PREP pattern),
so the same template stamps the customer-facing version with the customer's asks instead of his.

Build path, no improvisation: `/recoil-close` on today's transcript first (his asks from today get
appended to this table) → stamp from saul PREP schema → `counterpart-gauntlet` → fact-check every
quote against the raw transcript → then Zach sees it → Zach sends by hand.

## What this changes for the 1:30 call

Open with #11 (three sentences), answer #7 (hand vs automation, never answered), confirm #2 (blurb
going today), then ask him to pick the customer for #3 and #8. Everything else is in the bundle.
