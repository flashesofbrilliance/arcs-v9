# Copy-paste snippets

Paths assume the tool lives at `tools/arcs-verb-eval/`. Change them if you vendored it elsewhere.

## Analysis by ARCS

**Shell**

```bash
tools/arcs-verb-eval/arcs-verb-eval analysis teardown.html --ledger evidence.jsonl --out prints/analysis.json
```

**Python**

```python
import json, sys
sys.path.insert(0, "tools/arcs-verb-eval")
from arcs_verb_eval import evaluate, load_ledger

upstream = None
report = evaluate("analysis", open("teardown.html").read(), upstream=upstream, ledger=load_ledger("evidence.jsonl"))
json.dump(report, open("prints/analysis.json", "w"), indent=2)

print(report["fate"])            # sourced
if not report["ok"]:
    sys.exit("stopped by: " + ", ".join(report["failed"]))
```

**GitHub Actions**

```yaml
- name: Analysis by ARCS
  run: tools/arcs-verb-eval/arcs-verb-eval analysis teardown.html --ledger evidence.jsonl --out prints/analysis.json

- name: Keep the paper
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: analysis-print
    path: prints/analysis.json
```

**pre-commit**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: analysis-by-arcs
        name: Analysis by ARCS
        entry: tools/arcs-verb-eval/arcs-verb-eval analysis teardown.html --ledger evidence.jsonl
        language: system
        files: '\.html$'
        pass_filenames: false
```

## Assessment by ARCS

**Shell**

```bash
tools/arcs-verb-eval/arcs-verb-eval assessment report.html --upstream prints/analysis.json --out prints/assessment.json
```

**Python**

```python
import json, sys
sys.path.insert(0, "tools/arcs-verb-eval")
from arcs_verb_eval import evaluate

upstream = json.load(open("prints/analysis.json"))
report = evaluate("assessment", open("report.html").read(), upstream=upstream)
json.dump(report, open("prints/assessment.json", "w"), indent=2)

print(report["fate"])            # the step's go/stop stamp
if not report["ok"]:
    sys.exit("stopped by: " + ", ".join(report["failed"]))
```

**GitHub Actions**

```yaml
- name: Assessment by ARCS
  run: tools/arcs-verb-eval/arcs-verb-eval assessment report.html --upstream prints/analysis.json --out prints/assessment.json

- name: Keep the paper
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: assessment-print
    path: prints/assessment.json
```

**pre-commit**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: assessment-by-arcs
        name: Assessment by ARCS
        entry: tools/arcs-verb-eval/arcs-verb-eval assessment report.html --upstream prints/analysis.json
        language: system
        files: '\.html$'
        pass_filenames: false
```

## Evaluation by ARCS

**Shell**

```bash
tools/arcs-verb-eval/arcs-verb-eval evaluation lenses.json --upstream prints/assessment.json --set min_lenses=4 --out prints/evaluation.json
```

**Python**

```python
import json, sys
sys.path.insert(0, "tools/arcs-verb-eval")
from arcs_verb_eval import evaluate

upstream = json.load(open("prints/assessment.json"))
report = evaluate("evaluation", open("lenses.json").read(), upstream=upstream, min_lenses=4)
json.dump(report, open("prints/evaluation.json", "w"), indent=2)

print(report["fate"])            # the step's go/stop stamp
if not report["ok"]:
    sys.exit("stopped by: " + ", ".join(report["failed"]))
```

**GitHub Actions**

```yaml
- name: Evaluation by ARCS
  run: tools/arcs-verb-eval/arcs-verb-eval evaluation lenses.json --upstream prints/assessment.json --set min_lenses=4 --out prints/evaluation.json

- name: Keep the paper
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: evaluation-print
    path: prints/evaluation.json
```

**pre-commit**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: evaluation-by-arcs
        name: Evaluation by ARCS
        entry: tools/arcs-verb-eval/arcs-verb-eval evaluation lenses.json --upstream prints/assessment.json --set min_lenses=4
        language: system
        files: 'lenses.*\.json$'
        pass_filenames: false
```

## Synthesis by ARCS

**Shell**

```bash
tools/arcs-verb-eval/arcs-verb-eval synthesis surface.html --upstream prints/evaluation.json --out prints/synthesis.json
```

**Python**

```python
import json, sys
sys.path.insert(0, "tools/arcs-verb-eval")
from arcs_verb_eval import evaluate

upstream = json.load(open("prints/evaluation.json"))
report = evaluate("synthesis", open("surface.html").read(), upstream=upstream)
json.dump(report, open("prints/synthesis.json", "w"), indent=2)

print(report["fate"])            # the step's go/stop stamp
if not report["ok"]:
    sys.exit("stopped by: " + ", ".join(report["failed"]))
```

**GitHub Actions**

```yaml
- name: Synthesis by ARCS
  run: tools/arcs-verb-eval/arcs-verb-eval synthesis surface.html --upstream prints/evaluation.json --out prints/synthesis.json

- name: Keep the paper
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: synthesis-print
    path: prints/synthesis.json
```

**pre-commit**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: synthesis-by-arcs
        name: Synthesis by ARCS
        entry: tools/arcs-verb-eval/arcs-verb-eval synthesis surface.html --upstream prints/evaluation.json
        language: system
        files: '\.html$'
        pass_filenames: false
```

## Recapitulation by ARCS

**Shell**

```bash
tools/arcs-verb-eval/arcs-verb-eval recapitulation note.md --upstream prints/synthesis.json --out prints/recapitulation.json
```

**Python**

```python
import json, sys
sys.path.insert(0, "tools/arcs-verb-eval")
from arcs_verb_eval import evaluate

upstream = json.load(open("prints/synthesis.json"))
report = evaluate("recapitulation", open("note.md").read(), upstream=upstream)
json.dump(report, open("prints/recapitulation.json", "w"), indent=2)

print(report["fate"])            # the step's go/stop stamp
if not report["ok"]:
    sys.exit("stopped by: " + ", ".join(report["failed"]))
```

**GitHub Actions**

```yaml
- name: Recapitulation by ARCS
  run: tools/arcs-verb-eval/arcs-verb-eval recapitulation note.md --upstream prints/synthesis.json --out prints/recapitulation.json

- name: Keep the paper
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: recapitulation-print
    path: prints/recapitulation.json
```

**pre-commit**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: recapitulation-by-arcs
        name: Recapitulation by ARCS
        entry: tools/arcs-verb-eval/arcs-verb-eval recapitulation note.md --upstream prints/synthesis.json
        language: system
        files: 'note.*\.md$'
        pass_filenames: false
```

## The whole thing as one workflow

```yaml
# .github/workflows/check-before-you-say-it.yml
name: check-before-you-say-it
on: [pull_request]
jobs:
  five-steps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Self-test (the checks check themselves)
        run: tools/arcs-verb-eval/arcs-verb-eval --self-test
      - name: All five steps
        run: tools/arcs-verb-eval/arcs-verb-eval pipeline --config arc.json
      - name: Report
        if: always()
        run: |
          tools/arcs-verb-eval/arcs-verb-eval export prints --format md >> "$GITHUB_STEP_SUMMARY"
          tools/arcs-verb-eval/arcs-verb-eval export prints --format junit --out prints/junit.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: five-step-prints
          path: prints/
```
