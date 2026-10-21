# Recoil template drift found while closing the Upside call (2026-10-20)

Status: OPEN, for Zach's ruling. Found in the /recoil-close run on the Upside hiring-manager call.

1. **44 of 65 SSOTs in `runtime/recoil/generated/` use the legacy schema** (`cover`, `receiptLifecycle`,
   `callWalk`, ...). `scripts/recoil` (recoil_brief.py) only renders the `meta` + `page.tabs` schema and
   crashes with `KeyError: 'meta'` on a legacy file. Copying the newest file by mtime handed me a legacy
   one (precall-todd-hotes-2026-07-20.json). Fix: point the skills at a canonical template
   (2026-10-16-concourse.json or 2026-10-20-upside-lindsey-mertz.json), migrate or archive the legacy files, or
   make the renderer fail with a clear "legacy schema" message.
2. **/recoil-close skill doc names no template or schema.** It says "fill the tabs" but never says which
   file shape. Add the path of a reference SSOT and the six tab ids (pre, exante, forge, recoil, wargame, defense).
3. **The prep brief was an artifact, not an SSOT.** Upside Interview Prep (claude.ai/artifact/HxWR22pGUYWR9Dd59QETeD)
   was hand-built HTML with no `runtime/recoil/generated/` file, so the ex-ante had to be copied over by
   hand at close. /recoil-prep should always write the SSOT first and render the artifact from it.
4. **The prep page assumed pronouns ("he") and a title ("Senior Director") for Lindsey Mertz.** On the call
   Lindsey's title was "Director of Revenue Operations". The prep template should use the name and they/them
   until confirmed, and mark titles as unverified when they come from a profile scrape.
5. **The renderer's built-in HTML has one em-dash** (in the template, not in the content); the house rule is 0.
6. **`_ARTIFACTS/forge-*/ex-ante.json` is a job-fit score, not an ex-ante receipt** (no forks or hypothesis).
   The name invites confusion with the recoil ex-ante; consider renaming it to `fit-score.json`.
