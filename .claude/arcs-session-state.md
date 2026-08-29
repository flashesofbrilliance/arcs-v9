# ARCS session state — 2026-08-28 (v3.47.0)

**Branch:** `claude/zachharris-website-design-bcb738` @ 588af273 (tangential; core résumé work on `feat/resume-pwa-theming`, not merged to main).

## This session, in one breath
Shipped the zachharris.xyz consulting site; fixed + guarded the resume.arcs.care production blackout;
built the ARCS job-search pipeline (target-role scan HUD, LinkedIn alert catcher, retargeted alerts);
rewrote the LinkedIn About dual-audience; ran a brand-coherence audit.

## Next unblocked
1. Re-run the LinkedIn alert catcher + rubric scoring once the 4 retargeted alerts populate (~2026-08-31);
   tailor `_ARTIFACTS/resume-<target>/` for the top PURSUE. **Background task `task_57c6b286` is running.**
2. Merge `feat/resume-pwa-theming` → main (résumé fix + `DEPLOY.md` + `scripts/deploy-smoke.mjs`).
3. Vercel: preview-only tokens for deploy agents (blast-radius guardrail).

## Watch-outs
- arcs-v9 prod = ONE deployment across ~70 arcs.care domains. Never `vercel --prod` from a dirty/feature tree.
  `vercel --prod` needs `--archive=tgz` (48k files). Verify render in a browser, not curl (bot-challenge 403s).
- Job-search tooling lives on this website-design branch — relocate to main/a job-search branch.

**Blocking:** NONE.
