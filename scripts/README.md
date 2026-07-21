# ARCS Scripts - Connections Scanner Suite & CLI

Forensic analysis tools for a LinkedIn connections export, plus the ARCS
5-verb reasoning pipeline (`arcs_cli.py`) that runs over their JSON output.

The scanners read a `Connections.csv` export, score every contact through the
ARCS lenses, and write JSON + Markdown receipts. `arcs_cli.py` then consumes
those JSON envelopes and produces a combined decision receipt.

> Note on data: these tools operate on your own contact export. The subject
> name and network size in `score_me.py` are generic placeholders
> (`SUBJECT_NAME`, `NETWORK_SIZE`) - set them to your own values if you want a
> personalized receipt. No personal data is hard-coded.

---

## Requirements

- **Python 3.8+** (stdlib only for most scripts).
- Optional, per script:
  - `network_scan.py` needs **`anthropic`** and a valid `ANTHROPIC_API_KEY`.
  - `archetype_scan.py` needs **`plotly`** and **`networkx`** (renders an
    interactive HTML graph).

Install the optional deps only if you run those scripts:

```bash
pip install anthropic          # for network_scan.py
pip install plotly networkx    # for archetype_scan.py
```

`score_me.py`, `forensic_scan.py`, `export_apollo.py`, and `arcs_cli.py`
require no third-party packages.

---

## Input data

Export your connections from LinkedIn
(Settings -> Data privacy -> Get a copy of your data -> Connections) and unzip
to get `Connections.csv`. The file has a few preamble lines before the header
row; the scanners skip them automatically.

Point the scanners at the file with the `CONNECTIONS_CSV` environment variable.
If unset, they default to `Connections.csv` in the current directory.

```bash
export CONNECTIONS_CSV="/path/to/Connections.csv"
```

---

## Scanners

Run each from the `scripts/` directory. Outputs are written one level up
(repo root) unless noted.

### `forensic_scan.py`

Five detection lenses (Detective, Curator, Librarian, Sentry, Accountant).
Final verdict = contacts surfacing in 3 or more lenses.

```bash
CONNECTIONS_CSV=/path/to/Connections.csv python3 forensic_scan.py
```

- **Args:** none.
- **Env:** `CONNECTIONS_CSV`.
- **Writes:** `../forensic_scan.md`, `../forensic_scan.json`, `../exports/`.

### `archetype_scan.py`

Classifies each connection into the 8 ARCS archetypes, scores resonance
against the subject stack, and renders a force-directed Plotly graph.

```bash
CONNECTIONS_CSV=/path/to/Connections.csv python3 archetype_scan.py
```

- **Args:** none.
- **Env:** `CONNECTIONS_CSV`.
- **Deps:** `plotly`, `networkx`.
- **Writes:** `../network_archetype_viz.html`, `../network_archetype.json`,
  `../network_archetype.md`.

### `network_scan.py`

Topology scan applying Triune Logic (OM / UNDEFINED / NULL) to the graph.
Uses Claude for classification, so an API key is required.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
CONNECTIONS_CSV=/path/to/Connections.csv python3 network_scan.py
```

- **Args:** none.
- **Env:** `CONNECTIONS_CSV`, `ANTHROPIC_API_KEY`.
- **Deps:** `anthropic`.
- **Writes:** `../network_scan.json`, `../network_scan.md`.

### `export_apollo.py`

Exports the top-N contacts by NCI score as an Apollo.io People CSV.

```bash
CONNECTIONS_CSV=/path/to/Connections.csv python3 export_apollo.py 1000 recent
```

- **Args (positional):**
  - `top_n` - how many contacts to export (default `500`).
  - `mode` - `all` (default) or `recent` (recent connections only).
- **Env:** `CONNECTIONS_CSV`.
- **Writes:** `../exports/`.

### `score_me.py`

Scores a single hypothetical contact and prints a receipt. Does not read the
CSV - it scores against the subject constants at the top of the file.

```bash
python3 score_me.py "Jane Doe" "VP of Partnerships" "Acme Corp" 2025
```

- **Args (positional):** `name title company year`
  (all optional; each falls back to a built-in example default).
- **Subject constants:** edit `SUBJECT_NAME`, `SUBJECT_STACK`, `NETWORK_SIZE`
  near the top of the file to personalize the receipt.

---

## `arcs_cli.py` - the 5-verb pipeline

A self-sovereign CLI that reasons over the scanner JSON output. Stdlib only,
Python 3.8+, no dependency on the scanners themselves - it reads any JSON that
conforms to the open envelope contract documented at the top of `arcs_cli.py`.

### Verbs

Each verb runs standalone; none requires another to have run first.

| Verb | What it does |
|------|--------------|
| `analyze` | First-pass read of the input envelopes |
| `assess` | Risk / boundary assessment |
| `evaluate` | Resonance evaluation against the subject `--stack` |
| `synthesize` | Cross-input synthesis |
| `recapitulate` | Final DEWY decision receipt |
| `run` | All five verbs in sequence, writes a versioned apex receipt |

### Passthrough parameters (common to every verb)

| Flag | Alias | Default | Purpose |
|------|-------|---------|---------|
| `--inputs` | `-i` | (required unless piped) | One or more scan JSON files |
| `--stack` | `-s` | `Builder,Navigator,Chartist` | Subject archetype stack |
| `--md` | | off | Print Markdown to stdout |
| `--out` | `-o` | none | Write Markdown receipt to a file (implies `--md`) |
| `--pipe` | | off | Emit pipeline JSON to stdout for chaining |

### Usage

Standalone verb:

```bash
python3 arcs_cli.py evaluate --inputs network_scan.json --stack "Navigator,Chartist" --md
```

Chained pipeline (stdout of one verb becomes stdin of the next):

```bash
python3 arcs_cli.py analyze --inputs *.json | python3 arcs_cli.py synthesize --md
```

All-in-one:

```bash
python3 arcs_cli.py run --inputs *.json --stack "Builder,Navigator,Chartist" --out dewy_receipt.md
```

With no arguments, `arcs_cli.py` prints full help.

---

## Environment variables

| Variable | Used by | Purpose |
|----------|---------|---------|
| `CONNECTIONS_CSV` | all scanners | Path to `Connections.csv` (default `Connections.csv`) |
| `ANTHROPIC_API_KEY` | `network_scan.py` | Claude API access for classification |

---

## Typical run

```bash
cd scripts
export CONNECTIONS_CSV="/path/to/Connections.csv"

# 1. Generate scans
python3 forensic_scan.py
python3 archetype_scan.py          # needs plotly + networkx

# 2. Reason over the JSON output
python3 arcs_cli.py run --inputs ../forensic_scan.json ../network_archetype.json \
  --stack "Builder,Navigator,Chartist" --out ../dewy_receipt.md
```

---

## Other scripts in this directory

This directory also holds the ARCS core kernel (`arcs_core.py`), additional
domain scanners (`calendar_scan.py`, `reader_scan.py`, `listening_scan.py`,
`network_scan_full.py`), the observability simulation harness (`lattice_sim.py`),
and various internal tools. Those carry their own module docstrings and
`--help` output; see the file header for each. This README covers the
Connections scanner suite and the `arcs_cli.py` pipeline.
