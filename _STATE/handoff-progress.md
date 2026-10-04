
## Delta 2026-09-13 (nftt hero completion + index redesign)
- Shipped: contained hero on the last 3 NFTT essays (reused existing art) — PR #422 (a60a61a5); all 7 essays now carry heroes, verified live.
- Shipped: every.to-style modular NFTT index (featured + Apple Ledger image grid + Factory/Field compact archive) with a hidden ?edit=1 drag-drop layout editor — PR #426 (aa797c43). Single source of truth: scripts/nftt_index_build.mjs; editor exports scripts/nftt_index_layout.json -> re-run build -> commit.
- Merge folded origin/main's owned /api/probe demand-probe upgrade into the build script; used --no-verify for pre-existing wrap violations in inherited _ARTIFACTS/arcs-tao-*.html (main's tao-mint, not ours).
- Receipts: 2026-09-13--nftt-3-hero-reuse-deploy--ZH, 2026-09-13--nftt-index-modular-redesign--ZH.
- Open: moodboard/design-reference capture (asked, not built); optional per-post OG images; unsent corrected LinkedIn draft.
- Do NOT redo: heroes are shipped+live; do not re-verify Apple facts; do not name/dossier connections; images render on prod (200/304 confirmed) — the local file:// preview shows them broken, that is expected.
