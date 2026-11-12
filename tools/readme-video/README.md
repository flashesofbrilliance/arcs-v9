# README to video: the walkthrough build

Rescued 2026-10-31 from an uncommitted Claude scratchpad (see `ASSETS.md`). The skill that drives it is
`.claude/skills/readme-to-video/SKILL.md`; the rules are `_PATTERNS/2026-10-30-readme-to-video-resonance-rules.md`.

| File | Role |
|---|---|
| `build.cjs` | 8 HTML cards rendered with Playwright, each held for its take plus 0.8 s (`-t`, rule R8), concatenated to `out/walkthrough.mp4` |
| `voice/SCRIPT.md` | the narration, one section per card (rule R0: must equal each card's `v`) |
| `keep.json` | declared omissions with reasons (rules R1, R5) |
| `variants/` | the later cuts from the same session: blueprint kit (`kit.cjs`, `bp-build.cjs`), fluid timing (`fluid-*.cjs`), music bed (`mix.sh`), shorts, making-of, bench. Kept as found; they still carry absolute paths to Zach's Mac and are not wired to the checker |

Run (takes in `voice/NN.mp3`, or it falls back to the macOS `say` voice):

```bash
PLAYWRIGHT_PATH=/Users/zharris/arcs-v9/node_modules/playwright node tools/readme-video/build.cjs
python3 scripts/readme_video_check.py --vid tools/readme-video --readme <README.md> --keep tools/readme-video/keep.json
```

No API key or voice id is read by any file here: the takes were generated outside the build. A voice id, when the voice step
is scripted, goes in a config line (`ELEVENLABS_VOICE_ID`), and the key only in the environment (`ELEVENLABS_API_KEY`).
