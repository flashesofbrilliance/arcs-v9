# LinkedIn pipeline — ported from `arcs_cfa`

Ported into `arcs-v9` per Zach's call on 2026-06-24 (ADR-028 open question #3:
"port the logic into arcs-v9" — not "keep arcs_cfa as the pipeline's home").

| File | Source | Purpose |
|---|---|---|
| `linkedin_export.py` | `arcs_cfa/arcs_cfa/linkedin_export.py` @ `fd6ea07` | Parses a LinkedIn personal-data-export ZIP into structured fields: positions (with fixed date parsing — bare-year/"Mon YYYY" previously silently failed via a bare `except:`), `skills_full`, `endorsements_total`, `platform_inferences` (LinkedIn's own ad-targeting model of the user), `articles` (38 authored long-form pieces, HTML-stripped via `bs4`). |
| `primitives.py` | `arcs_cfa/arcs_cfa/primitives.py` @ `fd6ea07` | `DeceleratorAtom`, `TrendSurfingMolecule`, and the new `ThirdDerivativeAtom` (jerk) + `pre_peak_warning()` — validated against real Creator Analytics data with ~1-day lead time over the prior acceleration-only signal (n=2 peaks; treat as directional, not a stable constant). |

## Requirements

Both files need **Python ≥ 3.10** (`str | Path` union syntax). `linkedin_export.py`'s
article parsing additionally needs `bs4` (falls back to a regex tag-strip if absent).
The system default `python3` on most machines is older and lacks `bs4` — use a 3.11+
venv, same constraint that applied in `arcs_cfa`.

## Status

This is the parser/primitive layer only — **not yet wired into any arcs-v9 route or
script**. Feeds the Profile Scan DEEP-tier generation pipeline once that spec
(`runtime/flows/profile-scan-flow-v0.1.md`) is written; see ADR-028.

`arcs_cfa`'s own copies are left as-is (not deleted) — this is a port, not a move, until
the generation pipeline confirms arcs-v9 is the only consumer.
