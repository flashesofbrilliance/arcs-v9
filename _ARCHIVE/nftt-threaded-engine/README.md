# Retired: the threaded NFTT story engine (archived 2026-09-07)

`story_render.py` + `nftt-story.schema.json` + the `.story.md` sources + the `-full.html`
renders were the **data-driven threaded** NFTT format (mono, thread-braid, arc-ladder).

The live NFTT series moved to a **hand-authored literary theme** (the take-home-trap
"With Life" standard: Newsreader serif, 520px measure, `.panel`, blockquotes) in commit
`22781915` (2026-09-02). By 2026-09-07 all six served posts were literary and every
threaded `-full.html` was orphaned (routed by nothing) — the skill/engine had drifted
for five days while describing a format the site no longer served.

Decision (Zach, 2026-09-07): retire the threaded engine, repoint `nftt-story-factory`
to the literary standard (template + checklist, no engine). Kept here, not deleted,
per KINTSUGI / "history relocated, never deleted". Recoverable via git.
