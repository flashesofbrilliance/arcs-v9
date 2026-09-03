# Cold-Reader Rubric — Source Survey

Compiled to ground ADR-075 (pull-not-push legibility gate) against established, citable
best practices in data-driven storytelling, information hierarchy, typography, and
accessibility. Every row below is corroborated by a live web source (fetched 2026-09-03);
nothing here is invented. Counterpart quotes are the verbatim feedback lines supplied in
the task brief.

## 1. Table of principles

| Source | One-line principle | Numeric/structural rule | URL | Corroborates counterpart line |
|---|---|---|---|---|
| Barbara Minto — Pyramid Principle / SCQA | Lead with the answer; think bottom-up, communicate top-down | Situation → Complication → Question → Answer, then MECE-grouped supporting points | [Think Insights: SCQA Logic](https://thinkinsights.net/strategy/scqa-logic) | "here is my goal... here's how I fix it... supporting evidence" |
| BLUF (US Army AR 25-50) | State the conclusion/decision before any supporting detail | Purpose sentence → bottom line → then background/evidence/caveats | [Animalz: BLUF](https://www.animalz.co/blog/bottom-line-up-front) | "takeaway up front, supporting evidence, takeaway" |
| Nielsen Norman Group — F-pattern | Users scan top and left edge of a page, not the whole surface | Heavy fixation on first line(s), decaying attention below | [NN/g: F-Pattern video](https://www.nngroup.com/videos/f-pattern-reading-digital-content/) | "nobody wants depth front"; "a little eye I can click for more" |
| NN/g — Progressive disclosure | Defer secondary/advanced info to a click, not the main view | Primary screen shows minimal set; "Show details" reveals the rest | [Wikipedia: Progressive disclosure](https://en.wikipedia.org/wiki/Progressive_disclosure) | "a little eye I can click for more" |
| NN/g — Inverted pyramid for web | Most important info first; users rarely scroll to the bottom | Lead paragraph = conclusion; supporting detail descends in priority | [NN/g: Inverted Pyramid](https://www.nngroup.com/articles/inverted-pyramid/) | "takeaway up front, supporting evidence, takeaway" |
| WCAG 2.2 SC 1.4.3 | Text must be readable against its background | Contrast ≥ 4.5:1 normal text, ≥ 3:1 for large/bold text (AA) | [W3C: Understanding 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html) | Readability substrate for all of the above |
| WCAG 2.2 SC 1.4.8 (AAA) | Line width and spacing must be user-adjustable and bounded | Line length ≤ 80 characters; line spacing ≥ 1.5×; paragraph spacing ≥ 1.5× line spacing | [Make Things Accessible: WCAG 2.2 AA contrast](https://www.makethingsaccessible.com/guides/contrast-requirements-for-wcag-2-2-level-aa/) | Scannability substrate |
| WCAG 2.1 SC 1.4.12 (AA) | Text spacing must not clip content when a user increases it | Line height ≥ 1.5×, paragraph spacing ≥ 2× font size, letter spacing ≥ 0.12×, word spacing ≥ 0.16× | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Scannability substrate |
| Butterick's Practical Typography | Measure (line length) governs how easily the eye returns to the next line | 45–90 characters per line; line spacing 120–145% of point size | [Butterick: Line length](https://practicaltypography.com/line-length.html) | Scannability / "an hour to consume it" |
| Cole Nussbaumer Knaflic — Storytelling with Data | Declutter before you add; maximize signal-to-ink | A dedicated "declutter" pass removes any element that doesn't aid understanding | [SWD: Storytelling with Data](https://www.storytellingwithdata.com/books) | "maximum one plot, one big number" |
| Edward Tufte — data-ink ratio / chartjunk | Maximize the ratio of ink devoted to data over total ink; strip chartjunk | Data-ink ratio = data-ink ÷ total ink, maximized | [GeeksforGeeks: Tufte's Principles](https://www.geeksforgeeks.org/data-visualization/mastering-tuftes-data-visualization-principles/) | "maximum one plot" |
| Tufte — small multiples | Repeat one simple chart form across categories instead of one complex chart | Series of same-scale, same-design panels for comparison | [GeeksforGeeks: Tufte's Principles](https://www.geeksforgeeks.org/data-visualization/mastering-tuftes-data-visualization-principles/) | Tension point — see §2 |
| Stephen Few — dashboard design | A dashboard is a single screen scannable at a glance, updated regularly | Fits on one screen, no scrolling, designed for brief glances | [Perceptual Edge: Dashboard Design course](https://www.perceptualedge.com/files/Dashboard_Design_Course.pdf) | "maximum one plot, one big number" |
| Nancy Duarte — Resonate / Sparkline | Great narrative oscillates between "what is" and "what could be" before landing the new bliss | Sparkline notation charts the oscillation across a talk's duration | [Duarte: Sparklines for strategic conversations](https://www.duarte.com/blog/creating-moments-of-impact-using-sparklines-for-strategic-conversations/) | "here is my goal... here's how I fix it" (gap → resolution arc) |
| Steve Krug — Don't Make Me Think | Design so the user never has to stop and puzzle it out; test with real users cheaply | 3–5 test users per round is sufficient to surface key usability problems | [Wikipedia: Don't Make Me Think](https://en.wikipedia.org/wiki/Don%27t_Make_Me_Think) | "nobody wants depth front" |
| Five-second test (UX research method) | First impression / recall test: show a design for 5 seconds, ask what was retained | 5-second exposure, then recall/comprehension questions | [fivesecondtest.com](https://fivesecondtest.com/) | "the first 3 questions I'm gonna have and 3 simple answers" |
| Gestalt principles of grouping (proximity, similarity, common region) | Visually group related items so hierarchy reads without labels | Elements placed closer together / styled alike are perceived as one unit | [NN/g: F-Pattern video](https://www.nngroup.com/videos/f-pattern-reading-digital-content/) (NN/g applies Gestalt throughout its scanning research) | "3 reasons why I should care... then drill down" |
| Amazon 6-pager (Bezos narrative memo) | Full prose argument, read silently in full, before any discussion | 6 pages max, no bullet slides, 20–30 min silent read-in at meeting start | [CNBC: Bezos 6-page memos](https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html) | Tension point — see §2 |
| Sequoia Capital pitch deck order | Problem is established before solution; narrative order is fixed | 10 sections, Problem precedes Solution, both precede Market/Product/Team/Financials | [MyPitchDecks: Sequoia framework](https://mypitchdecks.com/case-studies/sequoia-pitch-deck-template) | "a VC doesn't care about your innovation before they care about the problem" |
| McKinsey action titles / "so what" | Every slide title is a complete-sentence claim (the takeaway), not a topic label | Governing thought stated as a claim; titles alone must read as one coherent argument | [Slideworks: Action titles like McKinsey](https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey) | "3 reasons why I should care" (each reason = an action title) |

## 2. Where sources disagree

- **Tufte's density vs. Knaflic/Few's restraint.** Tufte's small-multiples and high
  data-ink-ratio ethos tolerates (even rewards) a dense grid of many small charts read
  together — it assumes an engaged, expert reader. Knaflic and Few both push toward a
  *single* focal chart per view for a first-glance audience. The counterpart's "maximum
  one plot, one big number" sides explicitly with Knaflic/Few over Tufte's density; Tufte's
  small-multiples approach is legitimate but belongs *behind* the "eye I can click for
  more," not on the front layer.
- **Amazon's 6-pager vs. "more like a deck versus a long PDF."** The 6-pager is full
  prose, deliberately unskimmable-by-design (it forces a slow, complete read-in before
  discussion). This is the closest thing in the survey to a source that *disagrees* with
  the counterpart's explicit ask. It is not wrong — it optimizes for a different
  situation (an internal decision meeting with a captive, silent-reading audience) — but
  it contradicts "nobody wants depth front" for an external, cold-open surface. Treat the
  full prose narrative as a tier-2/gated artifact (e.g. an appendix), never the entry
  layer.
- **Minto/BLUF/McKinsey (answer-first) vs. Duarte (earned arc).** Minto, BLUF, and
  McKinsey all say: state the conclusion immediately, prove it after. Duarte's sparkline
  implies a *build* — oscillating between problem and vision before the resolution lands.
  These aren't fully contradictory: Duarte's arc operates at the scale of a full narrative
  performance (a talk), while BLUF/Minto operate at the scale of a single document's
  opening move. The resolution used in this rubric: BLUF the take, then let supporting
  evidence *reprise* Duarte's is/could-be tension underneath — arc inside the drill-down,
  not in the headline.
- **WCAG 1.4.8's 80-character line cap (AAA, advisory) vs. Butterick's 45–90.** These
  overlap but aren't identical: WCAG's is a hard *maximum* for AAA conformance; Butterick's
  is a *design range* for readability, not an accessibility conformance target. Both point
  the same direction (short-to-medium lines), so no real conflict — but don't cite WCAG
  1.4.8 as an AA requirement; it's AAA (aspirational), unlike 1.4.3 and 1.4.12 which are AA.

## 3. Consolidated checklist (12 items max, mechanically checkable where possible)

1. **Verdict is the first thing on the page.** A single-sentence claim/answer appears
   above the fold, before any evidence. *(Minto SCQA; BLUF; NN/g inverted pyramid)*
2. **One primary chart, one number, on the entry layer.** Count `<canvas>`/chart
   containers and headline numeric callouts in the above-the-fold region; flag if >1 of
   each. *(Knaflic — declutter; Few — dashboard-at-a-glance)*
3. **Every heading is an action title, not a label.** Grep section headings for a verb +
   claim structure ("X is up 12%" not "Revenue"); flag noun-phrase-only headings.
   *(McKinsey action titles)*
4. **Problem precedes solution in document order.** The first content block after the
   verdict names the problem/gap; the fix/recommendation follows it, not the reverse.
   *(Sequoia deck order; Minto Complication→Answer)*
5. **Exactly 3 top-level reasons/questions at the summary layer.** Count list items in
   the "why this matters" or FAQ-style block; flag if count ≠ 3. *(Counterpart's own
   "3 reasons... 3 simple answers"; Gestalt grouping — 3 is a stable chunk size)*
6. **Depth is opt-in via a visible affordance, not inline.** Any paragraph beyond the
   summary layer must sit behind a click/expand/disclosure control (`<details>`, a
   "more"/eye icon, a modal), never rendered open by default. *(NN/g progressive
   disclosure; counterpart's "little eye I can click for more")*
7. **Line measure stays in range.** Body text column width renders 45–90 characters per
   line (WCAG AAA hard cap: 80). Measurable via computed column width ÷ average glyph
   width. *(Butterick; WCAG 1.4.8)*
8. **Line and paragraph spacing meet the text-spacing floor.** Line height ≥ 1.5×;
   paragraph spacing ≥ 1.5–2× line spacing. Grep computed CSS `line-height` and
   paragraph `margin`. *(WCAG 1.4.12; Butterick line-spacing)*
9. **Text contrast passes AA.** Foreground/background contrast ≥ 4.5:1 (normal text),
   ≥ 3:1 (large/bold ≥18pt or ≥14pt bold). Run any WCAG contrast checker against the
   rendered color pairs. *(WCAG 1.4.3)*
10. **Chart ink is data-only.** No gridline/gradient/3D/decorative element on the
    primary chart that doesn't encode a data value. Manual audit against a checklist of
    common chartjunk (3D bevels, drop shadows on bars, redundant legends).
    *(Tufte — data-ink ratio)*
11. **Full-depth narrative is demoted to an appendix/second surface, never the landing
    view.** Any content resembling a full prose memo (>1 page equivalent, no headings)
    must live behind a link/tab, not inline on the entry page. *(Amazon 6-pager tension
    — see §2; counterpart's "more like a deck versus a long PDF")*
12. **Five-second recall check.** A first-time reader shown the page for 5 seconds can
    state the verdict and one supporting reason unprompted. Run as a manual pre-send
    gate (peer or gauntlet persona), not automatable. *(Five-second test method; Krug —
    "don't make me think")*

Path: `_SPECS/cold-reader-rubric-sources.md` (155 lines).
