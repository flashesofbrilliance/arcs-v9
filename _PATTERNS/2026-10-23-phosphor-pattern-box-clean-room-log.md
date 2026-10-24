# Phosphor pattern box: clean-room log

Rule: the parser is written from the documents listed here only. Strudel source code (any file under codeberg.org/uzu/strudel or the npm packages, including krill.pegjs) is not read, opened, pasted or summarised by the implementer. Append a dated row for every document read before writing parser code. A row missing here means the document was not read.

| Date | Who | Document | Kind | Source code? |
|---|---|---|---|---|
| 2026-10-23 | Claude (design session) | `_PATTERNS/2026-10-23-strudel-for-phosphor-research-brief.md` section 5 (mini-notation reference, written by a research subagent from the public docs page and a prose summary; no grammar text copied) | second-hand brief | No |
| 2026-10-23 | Claude (design session) | `runtime/specs/phosphor-adopt-vs-build.md`, `_PATTERNS/2026-10-15-phosphor-visualizer-prereg.md` | our own docs | No |

Not read, by design: any Strudel repository file, npm package content, or Codeberg page. The design session did not fetch strudel.cc or Codeberg itself.

Caveat: the subagent that wrote the brief says it read a prose summary of krill.pegjs. That is upstream of this log and is a residual risk for the derivative-work question; Zach and counsel should weigh it (decision note, question 3). The implementer may use only the brief's section 5, never the grammar.

Note (2026-10-23): the prereg amendment for this feature is number 70 (69 went to release checkpoint 7 on main while this was in review).

Build record (2026-10-23): the parser in `_ARTIFACTS/phosphor-src/app.js` (`patParse`, `patCells`) was written from the brief's section 5 and amendment 70 only. No document beyond the rows above was read; no Strudel source, package or web page was opened by the implementer. The euclid rule and the `?` hash are our own design (amendment 71). Check P10 greps the parser for Strudel identifiers.
