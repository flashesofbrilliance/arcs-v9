# Format tests: Word, PDF, text, Markdown, track changes and legal features (2026-11-04)

Internal. Follows `2026-11-04-e2e-qa.md`. All test files are invented and built by `formats/bin/build.py`. Rerun
with `formats/bin/check.py`, `mixed.py` and `legal.py`. Public engine head 3fdfb59, no model, $0. Nothing was sent or
committed.

**Verdict:** the engine reads one thing: plain `.txt` in its own numbering style. Everything else needs a
conversion step, and the conversion is where the real risk sits. It can silently pick which version of a redline
you read, drop clause numbers, or never load a file at all. One result needs fixing before any client work: **a
Word amendment next to a text LPA is skipped without a word, and the engine then answers the old 2.0% fee as
current, with no warning.** Every other failure was either refused or detectable with a cheap check.

## 1. Raw files dropped into the document folder

| File | What the engine did |
|---|---|
| `.txt` in its numbering style | Loaded, 3 clauses |
| `.txt` in LPA style ("ARTICLE VIII", "Section 8.1") | Refused as unreadable. Safe |
| `.md` (any), `.docx`, `.pdf` | **Skipped silently.** The loader only opens `.txt`. No error, no log line |
| Same `.docx`/`.pdf` bytes renamed to `.txt` | Refused as unreadable. Safe |

The silent skip only bites when it sits next to a file that loads. A folder of nothing but skipped files gives "no
readable document", which is safe. The mixed case is not:

| Folder | Question | Answer |
|---|---|---|
| `lpa.txt` (fee 2.0%) + `lpa_amendment_1.docx` (fee cut to 1.75%) | "What is the management fee?" | **answered: 2.0%**, cites 8.1, no notes. The amendment never loaded (`formats/bin/mixed.py`) |

This is the "latest amendment wins" rule failing quietly because of a file extension. Fix: the loader must list
every file in the folder and refuse to answer while any file is unread. Fix opened as
https://github.com/flashesofbrilliance/rfp-engine/pull/2 (10 lines plus 5 tests; merged 2026-11-04 as c340f0b). With it, this folder
returns an error naming the `.docx` instead of an answer.

## 2. Conversions, then the engine's parser

| Source | Converter | Clauses | Clause 8.1 fee | Problems |
|---|---|---|---|---|
| Word, typed numbers ("8.1 ...") | textutil, pandoc | 8.1, 8.2, 8.3 | 2.0% | None |
| **Word, automatic numbering** (numbers come from Word's list feature, as in most real LPAs) | textutil | **0, refused** | n/a | Numbers became bullets: every clause number lost |
| Word, automatic numbering | pandoc | **0, refused** | n/a | Became "8." and "1.", "2.", "3.": the "8.1" ids are gone |
| Markdown, plain text saved as `.md` | none needed | 3 | 2.0% | Only the extension stops it loading |
| Markdown, written as Markdown (`## Section 8`, `**8.1**`) | as is, or pandoc | 0, refused | n/a | Heading marks and bold break the numbering match |
| Text PDF (running header, page number, a clause split over a page break) | pdftotext, pdftotext -layout, pypdf | 3 | 2.0% | The split clause joins back up, but **"Page 41 CONFIDENTIAL ..." lands inside clause 8.2's text**, and "Page 42" inside 8.3. A page number can then "trace" a memo figure |
| Scanned PDF (image only) | all three | 0, refused | n/a | No text layer. Needs text recognition (OCR) first. Refused, which is safe |
| Term sheet as a Word table | textutil, pandoc | 0, refused | n/a | Table rows have no clause numbers. Term sheets need their own reader |

## 3. Track changes, comments, footnotes and redlines

Test file `07_lpa_tracked_changes.docx`. Clause 8.1 has a tracked change, deleting 2.0% and inserting 1.75%. Counsel's comment on the
change says "Investor A side letter caps this at 1.50%". A footnote says "Reduced to 1.25% after the fifth
anniversary". Clause 8.3 has a manual redline (red strikethrough on $1,500,000, blue underline on $2,000,000, no
tracking).

| Converter | Clause 8.1 reads | Comment | Footnote | Manual redline in 8.3 |
|---|---|---|---|---|
| textutil (macOS) | 1.75% only: **change accepted silently** | Dropped | **Dropped** | Both figures, no marking: "$1,500,000 $2,000,000" |
| pandoc (default) | 1.75% only: accepted silently | Dropped | Kept, but **attached to clause 8.3** (it lands after the last clause) | Both, struck one marked `~~$1,500,000~~` |
| pandoc, reject changes | 2.0% only | Dropped | Same misplacement | Same |
| pandoc, show all | "...Investor A side letter caps this at 1.50%; confirm before signing.2.0%1.75% of..." | **Comment text pasted into the clause** | Same misplacement | Same |

What this means:

- **The converter decides which version you are checking, and says nothing.** An unaccepted tracked change means
  the document is still a draft. If the memo quotes 1.75% and the vote is on the executed LPA at 2.0%, a converter
  that accepts changes makes the memo look right. The engine never learns there were changes.
- **Comments can become clause text.** In "show all" mode, a lawyer's note with its own figure (1.50%) becomes part
  of 8.1 and would "trace" a memo line.
- **Footnotes move.** A fee step-down in a footnote on 8.1 was cited as part of 8.3.
- **Manual redlines and compare PDFs are invisible as redlines.** The compare-style PDF (struck 2.0% in red, 1.75%
  underlined in blue) extracted as "2.0% 1.75%" in all three PDF readers. The strike is a drawn line, not text. Both
  figures then trace to 8.1.

**What is cheap to catch.** Inside a Word file, all of these are visible in the XML before conversion. A scan of the
test files counted insertions, deletions, strikethrough, automatic numbering and tables correctly
(`<w:ins`, `<w:del`, `<w:strike`, `<w:numPr`, `<w:tbl>`). Comments need a count of `<w:comment` elements, not
just a check that the part exists: Word and pandoc write the comments part even when it is empty. So a pre-ingest
gate can refuse, or ask "which version is the vote on?", for any Word file with live changes, comments or manual
strikethrough. A PDF has no such marker in its text. A compare PDF has to be treated as unreadable for figures, or
read from the Word original.

## 4. Legal drafting features (text restyled to the engine's format)

| Feature | Result |
|---|---|
| Defined term: "Management Fee Rate" means 1.75% (1.1), used in 8.1 without the number | Memo "1.75% fee" traces to 1.1. The engine's own answer cites 1.1 only, not the operative 8.1. Workable, but the report should show both |
| Sub-clauses 8.3(a), (b)(i), (b)(ii) on their own lines | Folded into one clause 8.3. Citation is "8.3", never "8.3(b)(ii)" |
| A conditional figure: cap rises to $2,000,000 "if the Final Closing is after December 31, 2026" | Memo "$1,500,000 cap" and memo "$2,000,000 cap" **both trace to 8.3**. The condition is lost. Numbers, not meaning, as the fit check says |
| Cross reference ("the cap in Section 8.3(a)") | Not followed. Kept as text |
| LPA headings ("ARTICLE VIII", "Section 8.1") | Refused until restyled (as before) |

## What this changes

**Readers to build (setup fee):**

1. Load every file in the folder, or refuse. Never skip one silently.
2. Read Word from its XML, not from a converter, so that:
   - automatic clause numbers are kept
   - tracked changes, comments and manual redlines are detected and stopped at the door
   - footnotes stay with their clause
3. Strip page headers, footers and page numbers from PDFs. Refuse scans until they have been through OCR. Refuse
   compare PDFs for figures.
4. Cite sub-clauses as 8.3(b)(ii).
5. Write a term sheet table reader.

**Questions for the client before any run:**

- Is the vote on the executed documents or on a draft?
- Are there any documents with live tracked changes?

## Not tested

- Real Word files from Word itself. These were hand-built Word XML plus pandoc output, and Word adds fields,
  bookmarks and styles that may convert differently.
- Pages, Google Docs exports, `.doc` (the old Word format), `.rtf`.
- OCR quality on a real scan.
- Two-column PDFs, and PDFs with tables.
- Excel.
- Redlines made with dedicated compare software, or Word's own compare feature.
