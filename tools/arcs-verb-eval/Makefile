# Every target uses only python3. Override the runtime with PYTHON=/path/to/python3.
PYTHON ?= python3
RUN = PYTHON=$(PYTHON) ./arcs-verb-eval

.PHONY: test demo notebook-demo export clean
test:            ## prove fails-on-bad AND passes-on-good for every gate
	$(PYTHON) -m unittest discover -s tests -v
demo:            ## run the whole sample arc
	$(RUN) pipeline --config sample/arc.json
notebook-demo:   ## data in from a notebook, then analysis + assessment on it
	$(RUN) ingest examples/training-run.ipynb --outdir build/nb --mutate 2
	$(RUN) analysis build/nb/analysis.html --ledger build/nb/evidence.jsonl --out build/nb/prints/analysis.json
	-$(RUN) assessment build/nb/assessment.html --upstream build/nb/prints/analysis.json --out build/nb/prints/assessment.json
export: demo     ## data out in every format
	mkdir -p build/export
	for f in jsonl csv md junit receipt; do $(RUN) export sample/prints --format $$f --out build/export/report.$$f; done
clean:
	rm -rf build sample/prints
