# DEPLOY — arcs-v9 production rules

> One Vercel project (`arcs-v9`, `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9`) serves **~70 arcs.care
> domains** — `arcs.care`, `app.arcs.care`, `resume.arcs.care`, `status.arcs.care`,
> `prl.arcs.care`, and every `<name>.arcs.care` — from one deployment via `next.config.ts`
> rewrites + `src/proxy.ts`. **A bad production deploy blanks all of them at once.** Treat every
> production promotion as a blast-radius event.

## The incident this file exists to prevent (2026-08-28)

An agent (`hermes-agent`) ran `vercel --prod` from a **dirty working tree** on a feature branch
(`feat/resume-pwa-theming`). A PWA-install commit had dropped the `selectedNode`/`selectedClient`
state that the résumé's `Resume()` component still passed to `<SharpResume>`, so the client-rendered
React app threw `ReferenceError: selectedNode is not defined` at mount → **black screen, HTTP 200**.
resume.arcs.care (linked from LinkedIn) was down and no status-code check would have caught it.

## Rules

1. **Production = `main` only.** Feature-branch git pushes create **preview** deployments — never
   production. (Verified: a push to `feat/resume-pwa-theming` produced a `target: null` preview.)
   Do not change the project's production branch away from `main`.
2. **Never `vercel --prod` from a feature branch or a dirty tree.** Production promotion is a
   deliberate, human-reviewed act from a clean `main`. `gitDirty:1` on a production deployment is a
   defect, not a convenience.
3. **Deploy agents must hold preview-only Vercel tokens.** The CLI `--prod` hole cannot be closed by
   a project setting — it is closed by *not giving automation a production-capable token*.
   **Action (Vercel dashboard, human):** Team → Settings → Tokens / Access — ensure any token an
   agent uses cannot promote to production; keep production promotion to the dashboard or a
   named human.
4. **Run the render smoke-gate before every promote — it must PASS.**
   ```bash
   node scripts/deploy-smoke.mjs https://<preview-deployment-url>   # gate a preview
   node scripts/deploy-smoke.mjs                                    # gate live production
   ```
   It loads the résumé + homepage in a real browser and fails if a page mounts blank/black or throws
   at mount. Client-rendered pages (`public/resume.html`) fail *invisibly* to status checks — this
   gate is the only thing that catches them. **Never promote on a FAIL.**

## Promote (only when authorized, from clean `main`, after the gate passes)

```bash
vercel --prod --yes --archive=tgz
```
`--archive=tgz` is **required** — the repo has ~48k files (nested worktrees), over Vercel's 15k
per-file upload cap; a plain `vercel --prod` fails with `missing_archive`.

## Rollback (instant restore to a known-good main deployment)

```bash
vercel promote <last-good-main-deployment-url>      # re-points all production aliases
```
Find the last healthy one: `list_deployments` → newest with `target:"production"` **and**
`githubCommitRef:"main"` **and** `state:"READY"`. Rolling back to `main` reverts any
feature-branch-only work that was live, so confirm that trade before using it.

## Coordinating with other agents

There is no live channel to `hermes-agent` or other deploy automation. **This file and the Vercel
project settings are the coordination channel** — agents that read repo conventions follow them.
Keep this file on `main` so it is authoritative.
