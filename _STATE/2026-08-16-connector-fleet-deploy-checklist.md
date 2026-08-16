# Connector Fleet — Deploy Checklist (ADR-056) · 2026-08-16

> STOP-gated. Everything below is **owner-approval required**. This branch is built and
> local-pixel-verified only. NO push to main, NO Vercel deploy, NO subdomain attach has been done.
> Approve, then run as a single batched deploy.

## What's in the branch
- Renderer: `scripts/connector_render.py` (stdlib-only; SSOT-driven; honesty-gated on `live:true`).
- Data block: `_SEEDS/connectors.json` (per-tool copy, grounded in each repo's real README).
- Pages: `public/<tool>.html` for the 7 LIVE public goods (below). Excluded repos have **no** page.
- Rewrites: 7 `beforeFiles` entries in `next.config.ts`, one per `<tool>.arcs.care`, mirroring the
  existing `resume-tailor.arcs.care` block.

## Fleet (all registry `live:true`)
| Tool / subdomain | Page | Live channels rendered |
|---|---|---|
| rosetta-shell.arcs.care | public/rosetta-shell.html | npm, homebrew |
| germinate.arcs.care | public/germinate.html | npm, homebrew |
| rca-skill.arcs.care | public/rca-skill.html | github (skill) |
| state-sync-skill.arcs.care | public/state-sync-skill.html | github (skill) |
| token-savings-bank.arcs.care | public/token-savings-bank.html | github (skill) |
| fix-toolbar-comments-skill.arcs.care | public/fix-toolbar-comments-skill.html | github (skill) |
| arcs-field-scan.arcs.care | public/arcs-field-scan.html | github (web app) |

EXCLUDED (registry `live:false`, no page, no subdomain): `arcs-claude-project-scaffold`,
`linkedin-connections-toolkit`, `blindsat`. Do not attach these until published.

## Deploy order (batched, after approval)
1. **Merge/push** this branch to `main` (canon + tooling + `public/*.html` + `next.config.ts`).
2. **Deploy** arcs-v9 to Vercel production (the rewrites only take effect on a new deploy).
3. **Attach each subdomain** to the arcs-v9 Vercel project (one call per row below), then verify DNS
   + a `200` on each `<tool>.arcs.care`. Attaching before the deploy lands would 404 until step 2.

## Subdomain attach — one `POST` per subdomain
Resolve `{projectId}` first (arcs-v9 project): `.vercel/project.json` in the main checkout, or
`get_project` for `arcs-v9`. Then, for each subdomain:

```
POST /v10/projects/{projectId}/domains
Content-Type: application/json
Authorization: Bearer $VERCEL_TOKEN

{ "name": "<subdomain>" }
```

Subdomains to attach (in order):
- [ ] `rosetta-shell.arcs.care`
- [ ] `germinate.arcs.care`
- [ ] `rca-skill.arcs.care`
- [ ] `state-sync-skill.arcs.care`
- [ ] `token-savings-bank.arcs.care`
- [ ] `fix-toolbar-comments-skill.arcs.care`
- [ ] `arcs-field-scan.arcs.care`

DNS: `arcs.care` is on Vercel, so each `*.arcs.care` host resolves via the existing wildcard/apex
setup used by the other connector subdomains (forge, resume-tailor). If a `CNAME` is required per
subdomain, add `<tool> CNAME cname.vercel-dns.com` alongside the attach.

## Post-attach verification
- [ ] `get_deployment(idOrUrl: "<tool>.arcs.care")` returns the arcs-v9 deployment (per verify-live rule).
- [ ] `curl -sI https://<tool>.arcs.care` → `200`, and the page is the connector (not the app shell).
- [ ] Update `_SEEDS/distribution.jsonl`: add a `connector{url,live:true,verified_at,verify}` field to
      each rendered row (mirror the resume-tailor row) once the 200 is confirmed. Do NOT mark
      `live:true` before the curl passes.

## Cost note
7 live tools → 1 renderer + 7 data blocks + 1 batched deploy. Re-render is `python3
scripts/connector_render.py`; no per-page hand-editing, no per-page debug push.
