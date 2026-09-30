# Web: the checks in a browser

- `arcs-verb-eval.js` is the machine checks ported to plain JavaScript, gate for gate. Load it and call `AVE.evaluate(verb, text, upstreamReport)` or `AVE.fromNotebook(ipynbText, name)`.
- `index.html` is the single-file page: the five steps, a playground that runs the checks in the page, and copy-paste snippets. Nothing is uploaded.
- `playground.js` and `build_page.py` are the sources `index.html` is built from.

Parity with the Python engine was checked in a browser on 2026-09-29: all 23 self-test cases (5 good, 18 broken) failed the same checks in both. Three checks need a file system or a repo script, so they run in the CLI only: the slop lint at Synthesis, and the "file exists" half of the two receipt checks at Recapitulation. The page says so where it applies.
