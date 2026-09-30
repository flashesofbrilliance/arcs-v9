# How to use arcs-verb-eval

## The idea in one breath

Before you tell someone something, check it in five steps. Each step leaves a paper behind, and each paper gets a stamp: go or stop.

1. **Analysis.** Write down every fact, and where you found it.
2. **Assessment.** Check each fact against where you found it.
3. **Evaluation.** Let someone try to poke holes in it.
4. **Synthesis.** Write the short version, with nothing new added.
5. **Recapitulation.** Write the note. Don't send it. A person sends it.

A step only reads the paper from the step before it. So nothing can sneak in halfway.

## 1. Try it (one minute)

```bash
cd tools/arcs-verb-eval
make test    # proves every check catches a bad paper and passes a good one
make demo    # runs all five steps on a sample
```

You should see:

```
arc: analysis:sourced  ->  assessment:pass  ->  evaluation:conditional pass  ->  synthesis:ship  ->  recapitulation:parked
```

## 2. Put your data in

**From a notebook** (TensorFlow, PyTorch, anything; it's only a file):

```bash
./arcs-verb-eval ingest my-notebook.ipynb --outdir work/ --mutate 2
```

Every sentence in your notes that says a number becomes a fact to check. If that number shows up in a cell's output, the fact is marked verified. If it doesn't, it's marked as a gap. `--mutate 2` also makes two broken copies, so you can see the checks catch them.

**From a spreadsheet** (CSV or JSONL with columns `id,text,src,stakes,verdict,severity`):

```bash
./arcs-verb-eval ingest examples/claims.csv --outdir work/
```

Either way you get `work/analysis.html`, `work/assessment.html` and `work/evidence.jsonl`.

**By hand:** mark facts in any HTML page like this:

```html
<span class="claim" data-id="c1" data-src="https://where-i-found-it">The fact.</span>
```

## 3. Run the steps

One at a time. Each step saves its paper with `--out`, and the next step reads it with `--upstream`:

```bash
./arcs-verb-eval analysis   work/analysis.html   --ledger work/evidence.jsonl --out work/p/analysis.json
./arcs-verb-eval assessment work/assessment.html --upstream work/p/analysis.json --out work/p/assessment.json
```

Or all at once from a config file (copy `sample/arc.json` and change the paths):

```bash
./arcs-verb-eval pipeline --config my-arc.json
```

Exit code 0 means go. Exit code 1 means a check said stop, and the report says which one and why.

## 4. Get your data out

```bash
./arcs-verb-eval export work/p --format md       # a readable report
./arcs-verb-eval export work/p --format csv      # a spreadsheet
./arcs-verb-eval export work/p --format jsonl    # one row per check, for pandas or a database
./arcs-verb-eval export work/p --format junit    # CI shows each check as a test
./arcs-verb-eval export work/p --format receipt  # a decision receipt: what passed, what didn't
```

## 5. Change the rules

| You want to | Do this |
|---|---|
| Require more hole-pokers | `--set evaluation.min_lenses=6` |
| Keep settings in a file | `--config my.json` (or `.toml` on Python 3.11+) |
| Set it for your whole shell | `export ARCS_VERB_EVAL_EVALUATION__MIN_LENSES=6` |
| Waive one check, on the record | `--skip-gate noindex` (it still shows as SKIPPED) |
| Use a different Python | `PYTHON=/path/to/python3 ./arcs-verb-eval ...` |
| See what's in effect | `./arcs-verb-eval env` |

## 6. Use it from code or over the web

```python
from arcs_verb_eval import evaluate
report = evaluate("analysis", open("work/analysis.html").read())
print(report["fate"], report["failed"])
```

```bash
./arcs-verb-eval serve --port 8787
curl -s localhost:8787/eval/analysis -d '{"artifact": "<span class=\"claim\" data-src=\"x\">A fact.</span>"}'
```

## What the tool will never do

- **Grade the judgment half for you.** Rubric rows stay blank until a person or a model fills them in with `--scores`.
- **Send anything.** The last step can only say "parked, ready for a person to send."
