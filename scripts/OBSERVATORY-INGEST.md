# Observatory — plug-and-play GitHub event explorer

Point the Observatory at **any GitHub repo**, define **custom events** with a
declarative ruleset, and the dataset drops straight into the live switcher — no
UI rebuild, no redeploy.

## The pieces

| File | Role |
|------|------|
| `scripts/event-rules.json` | **The config you edit.** Maps GitHub signals → Observatory events/risks. |
| `scripts/event_rules.py` | The rule engine (pure, offline-testable). `python3 scripts/event_rules.py` runs a self-test. |
| `scripts/github_ingest.py` | Fetches a repo's commits/releases, applies the ruleset, emits `data.<name>.json` + updates `datasets.json`. |
| `public/observatory/runtime.jsx` | Static UI runtime; `hydrateObservatory(payload)` installs a dataset at runtime. |
| `public/observatory/datasets.json` | Switcher manifest — every dataset the dropdown offers. |

## Quick start

```bash
# 1. Live: ingest any repo (needs a token for private repos / rate limits)
export GITHUB_TOKEN=ghp_...
python3 scripts/github_ingest.py --repo vercel/next.js --name nextjs --include-releases

# 2. Offline / CI: ingest a pre-fetched commits payload (no network)
#    (a GitHub `GET /repos/:owner/:repo/commits` array, or {"commits":[...],"releases":[...]})
python3 scripts/github_ingest.py --repo owner/name --from-json commits.json --name myrepo

# 3. Open /observatory and pick the dataset from the switcher (top-right).
#    ?data=data.myrepo.json deep-links straight to it.
```

## Defining custom events

Edit `scripts/event-rules.json`. The **first matching rule wins**; no match falls to
`default` (kept only if `default.keep`). `drop` short-circuits housekeeping noise.

```json
{
  "event_rules": [
    { "id": "deploy",
      "when": { "subject_matches": "(?i)\\b(deploy|ship|release)\\b" },
      "set":  { "type": "milestone", "alt": "L3", "conf": 90, "peak": true } },

    { "id": "incident-pr",
      "when": { "kind_in": ["pr"], "label_in": ["incident", "sev1"] },
      "set":  { "type": "security", "alt": "L4", "conf": 95, "peak": true } }
  ],
  "risk_rules": [
    { "id": "ci-failure",
      "when": { "kind_in": ["workflow"], "status_in": ["failure"] },
      "set":  { "sev": "MED", "status": "OPEN", "how": "CI red" } }
  ]
}
```

**Match predicates** (all listed must hold; omitted = ignored):
`subject_matches` · `body_matches` (regex) · `prefix_in` · `scope_in` (conventional-commit
type/scope) · `author_in` · `label_in` · `kind_in` (`commit`/`pr`/`release`/`workflow`) · `status_in`.

**`set` fields:** `type`, `alt` (`L5` executive → `L1` surgical), `conf`, `peak` for events;
`sev` (`RUIN`/`HIGH`/`MED`), `status` (`AVERTED`/`MITIGATED`/`OPEN`), `how`, `risk`, `note` for risks.
`label` defaults to the cleaned commit subject.

## Altitudes (the vertical axis)

`L5` EXECUTIVE · `L4` STRATEGIC · `L3` OPERATIONAL · `L2` TACTICAL · `L1` SURGICAL —
audience zoom, not importance. Governance/strategy ride high; surgical fixes ride low.

## What's stubbed (v1 prototype)

- Ingest covers **commits + releases**. PR and workflow-run signals are first-class in the
  engine (`kind_in`, `label_in`, `status_in`) but the live fetchers for them aren't wired yet —
  feed them via `--from-json` for now.
- The altitude **deck (LAYERS)** is auto-derived from classified events (top-N per altitude).
  Repo-specific hand-authored findings (like arcs-v9's) remain a manual payload edit.
