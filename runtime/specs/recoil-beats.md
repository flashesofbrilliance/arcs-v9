---
version: 1
date: 2026-10-27
---
# Recoil beats: the timeline the recoil player plays

A recoil data file (`runtime/recoil/generated/*.json`) may carry an optional top-level `beats` array.
Files without it render exactly as before.

## One beat

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable id, such as `b07` |
| `t_start`, `t_end` | yes | Seconds from the start of the call. Beats are in order and do not overlap |
| `speaker` | yes | Who holds the floor |
| `summary` | yes | One plain sentence of what happened |
| `evidence` | no | A short verbatim quote that grounds the beat |
| `kairos` | no | `{ "label": "...", "lock": "open" \| "pending" \| "locked" \| "released" }`: a moment that mattered, and its write-lock state |
| `belief_deltas` | no | `[{ "belief": "<beliefs[].id>", "to": 0.0 to 1.0 }]`: confidence after this beat |
| `audience` | no | `both` to show on external projections; anything else is internal only |

## Commands

- `./scripts/recoil --data <file> --check-beats` validates the array (exit 1 on any problem).
- `./scripts/recoil --data <file> --format player` prints beats plus the belief manifold: for each belief,
  `points[0]` is its prior (`confidence[0]`), `points[i]` its confidence after beat i, and `D1` to `D3` from the
  same engine as the brief (`operators/arcs_kinematics.py`, stdlib fallback). dt is one beat.

## Rendering

The player template is `recoil-player` in `src/ui-kit/templates.json`; organisms 34 (manifold) and 35 (backlog
graph) and the shared `src/ui-kit/recoil-report/_player.js`. The demo (`recoil-player.html`) embeds the output of
`--format player` on `runtime/recoil/demo/2026-10-27-player-demo.json` and of
`scripts/backlog_graph.py --file runtime/recoil/demo/backlog-demo.jsonl --today 2026-10-27 --json`. All demo
data is invented.

Tempo: real time plays one call second per second; max recall plays the whole call in about 8 seconds; slow mo
dwells about 6 seconds on each beat and 12 on a kairos beat. Reverse plays at the chosen tempo backwards.
Detail: gist (summary only), beats (speaker, time, belief moves), full recall (plus the evidence quote).
