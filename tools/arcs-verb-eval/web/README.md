# Web: the checks in a browser

- `arcs-verb-eval.js` is the machine checks ported to plain JavaScript, gate for gate. Load it and call `AVE.evaluate(verb, text, upstreamReport)` or `AVE.fromNotebook(ipynbText, name)`.
- `index.html` is the single-file page: the five steps, a playground that runs the checks in the page, and copy-paste snippets. Nothing is uploaded.
- `playground.js` and `build_page.py` are the sources `index.html` is built from.

Parity with the Python engine was checked in a browser on 2026-09-29: all 23 self-test cases (5 good, 18 broken) failed the same checks in both. Three checks need a file system or a repo script, so they run in the CLI only: the slop lint at Synthesis, and the "file exists" half of the two receipt checks at Recapitulation. The page says so where it applies.

## Explainer video (`video/`)

- `honest-explainer.mp4` (H.264) and `honest-explainer.webm` (VP9): the 65-second captioned explainer, 1920x1080, silent so it works with muted autoplay. `player.html` plays whichever the browser supports.
- `explainer.html` is the source: every frame is drawn by `renderAt(t)`, so the render is deterministic. Edit a caption or timing there, then run `node capture.js` (Playwright) to write `frames/`, and join them:
  `ffmpeg -framerate 30 -i frames/%05d.jpg -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart honest-explainer.mp4`
- `node capture.js 3.5,15.8` renders stills at those seconds, for checking layout before a full render.
