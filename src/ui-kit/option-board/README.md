# option-board: three rendered options per block

A design review where each block of a page is shown as two to four rendered options (A, B, C) built from kit
tokens and the page's real copy. The reviewer clicks one per block, moves the dials, and sends or copies one line:

> Header C, Stats B, Week One C, Folds A, Evidence rows B. Glass strength 1x.

An unpicked block stays as it is now. Each block names its atomic layer (atom, molecule, organism, template, page)
so a pick maps onto a construction rule. Memory: `visual-work-three-rendered-options-per-block`.

## Use

```bash
python3 scripts/option_board.py _ARTIFACTS/option-board/gravity-glass.json -o _ARTIFACTS/option-board/gravity-glass.html
python3 scripts/option_board.py SPEC.json --fragment -o /tmp/board.html   # body only, paste into show_widget
python3 scripts/option_board.py --self-test
```

- **Inline widget** (`--fragment`): the board runs in the chat; "Send my picks" calls `sendPrompt`, so the line
  comes back as the reviewer's next message.
- **Page or Artifact** (default): "Send my picks" hides itself when there is no `sendPrompt`; "Copy my picks"
  copies the line and posts `{type: "option-board-picks", board, text}` to a parent frame.

## Spec

See the docstring of `scripts/option_board.py`. In a variant's `css`, `:scope` is that option's stage, so rules
never leak into the other options. A dial with id `glass` sets `--k-glass` on `<html>`; scale effects with
`calc(<alpha> * var(--k-glass))`.

## Files

| File | Role |
|---|---|
| `page.tpl` | Page shell with `{{...}}` holes |
| `board.css` | Review frame, plus the glass depth layer copied from the ARCS OS Design System artifact |
| `board.js` | Pick, dial and send logic |

Tokens are `src/ui-kit/recoil-report/_tokens.css`, inlined verbatim with the sentinel line kept, so
`token_source_gate.py` passes. Run `artifact_wrap_lint.py` and `page_gate.py` on every built board.
