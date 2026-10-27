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

## Decision and flip (optional, top level)

| Field | Meaning |
|---|---|
| `decision.move` | The next move, one plain sentence (required if `decision` is present) |
| `decision.confidence` | 0 to 1: how likely the move is right |
| `decision.conviction` | `LOW`, `MEDIUM` or `HIGH`: how settled that confidence is |
| `decision.hinges_on` | The belief id the move rests on |
| `flip.belief` | The belief that would change the move |
| `flip.delta_pts` | Signed whole points it would need to move (not zero) |
| `flip.would_need` | What you would need to hear for that to happen |

The player draws these as the decision block above the answer cards. Without them the block stays hidden.

## Commands

- `./scripts/recoil --data <file> --check-beats` validates the array (exit 1 on any problem).
- `./scripts/recoil --data <file> --format player` prints beats plus the belief manifold: for each belief,
  `points[0]` is its prior (`confidence[0]`), `points[i]` its confidence after beat i, and `D1` to `D3` from the
  same engine as the brief (`operators/arcs_kinematics.py`, stdlib fallback). dt is one beat.

## Rendering

The page answers first: one card per belief (before, after, and the moment that moved it most; click to jump
there). On load it plays the call once at max recall and rests at the end; with reduced motion it starts at rest
and Play steps one moment at a time. Space plays or pauses, the arrow keys step. The backlog graph is a cascade:
press a row to mark it done and whatever it unlocks turns "Ready now".

A belief whose direction changes mid-call carries a Reversed breadcrumb on its card (the two times and values) and a Reversal breadcrumb on the moment where it turned. Every change is a signed point delta from one helper, `pts()`; `scripts/delta_encoding_gate.py` (pre-commit, scoped to src/ui-kit) refuses a change shown by colour alone.


The player template is `recoil-player` in `src/ui-kit/templates.json`; organisms 34 (manifold) and 35 (backlog
graph) and the shared `src/ui-kit/recoil-report/_player.js`. The demo (`recoil-player.html`) embeds the output of
`--format player` on `runtime/recoil/demo/2026-10-27-player-demo.json` and of
`scripts/backlog_graph.py --file runtime/recoil/demo/backlog-demo.jsonl --today 2026-10-27 --json`. All demo
data is invented.

Tempo has two stages. Direction: Reverse or Forward; Play follows it. Speed: real time plays one call second
per second; max recall plays the whole call in about 8 seconds; slow mo dwells about 6 seconds on each beat and 12
on a kairos beat. Detail has five levels, each adding to the one before: 1 Gist (summary), 2 Moments (kairos and
lock state), 3 Beats (speaker, time, belief moves), 4 Motion (the D1 to D3 table), 5 Full recall (the evidence quote).
