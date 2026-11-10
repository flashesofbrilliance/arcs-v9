# tabbed-brief: a counterpart brief generated from data

A tabbed page for one counterpart: an overview, then one tab per option (roles, offers, scopes), each with a plan on the
counterpart's own schema. First instance: `public/gravity-brief.html` (gravity.arcs.care), from `_ARTIFACTS/tabbed-brief/gravity.json`.

```
python3 scripts/tabbed_brief_build.py DATA.json -o public/PAGE.html      # the served page (analytics if the data asks)
python3 scripts/tabbed_brief_build.py DATA.json --artifact OUT.html      # the private Artifact body
python3 scripts/tabbed_brief_build.py --check                             # pre-commit: registered pages match their data
python3 scripts/tabbed_brief_build.py --self-test                         # the validator rejects each bad shape
```

**Pages mode** (`"pages": true` in the data): the overview stays at the output path and each role becomes its own page
beside it (`<name>-<id>.html`, served at `/<id>` through the host map in `src/proxy.ts`; in the Artifact build, `<id>.html`).
The kit 42 nav switches to links (`shnavInit(nav, {links: true})`, `aria-current="page"`), roles never fold, and `--check`
compares every page. Gravity uses it.

Never hand-edit a generated page. Change the data (copy), the template layer here (shell.css, shell.js), or a kit part.

## Teardown: atoms to pages

| Layer | Part | Source | Notes |
|---|---|---|---|
| Atoms | colour, type, radius, motion tokens | `recoil-report/_tokens.css` + kit 39 light remap | Inlined verbatim. No literal colour anywhere else. |
| Molecules | chip (Private) | kit 28 | |
| | tile | kit 29 | Numbers in ink; the note is template text, not mono. |
| | callout (Gap, Condition) | kit 31 | |
| | wordmark | kit 38 | |
| | rank pill | kit 42 (`.shnav-pill`) | One pill for rank, in the tabs and the role headings. |
| | header controls (theme switch, reading options) | kit 51 | The global header with kit 38 wordmark (rule 13b). |
| | button | template (`.tb-btn`) | Candidate for the kit once a second template uses it. |
| Organisms | shell nav (tabs, dropdown menu) | kit 42 | Tabs from 1024px; menu below, half width from 600px. |
| | plan matrix (duties by horizon, know strip) | kit 52 | Horizons are data. |
| | hero (headline, lede, next step, actions) | template | Clean above the fold: one action row. |
| | fold section (heading with button, tagline, body) | template | ARIA accordion pattern. |
| | role tab (head, units with hairline spacers, callouts) | template | Becomes a fold below 1024px. |
| | fact table, card grid, list | template | Tables stack with labels below 600px. |
| Template | frame, meta strip, sticky nav, panes | `shell.css`, `shell.js` | Two breakpoints: 600, 1024. |
| Page | Gravity Labs | `_ARTIFACTS/tabbed-brief/gravity.json` | All copy lives here. |

Type ramp: label 0.6875rem (labels only) · 0.875rem small · 1rem body · 1.125rem unit heading · 1.45rem section · serif display.
Spacing: 28px between blocks and units, 12px inside a unit, hairline spacer between units.

## Interaction rules

- **Tabs (1024px and up):** one pane at a time. Arrow keys move between tabs; Home and End jump to the ends. Picking a tab while
  scrolled down brings the content start back under the sticky nav.
- **Menu (below 1024px):** every pane shows. The bar names the current section; the dropdown opens under it, full width on a phone
  and half the frame from 600px. Opening moves focus into the menu; Escape closes it and returns focus to the button. Picking an
  item opens that role and scrolls it 12px below the nav, then focuses its heading.
- **Fold sections and role sections:** a button inside the heading toggles the body (`aria-expanded`, `aria-controls`). Role
  sections fold only below 1024px. Expand all covers every fold, plus the role sections while they fold.
- **Jumps:** one helper measures the sticky nav and stops 12px below it; motion is instant when the reader prefers reduced motion.
- **Addresses:** each jump writes a plain `#name` (the tab id, or a section id) so any view can be linked; the overview clears it.
  A hash on load opens that view. Startup never clears a hash before it is read.
- **Actions:** `tab` opens that tab (or scrolls to that role on narrow screens); `section` opens and scrolls to a fold.
- **Header:** kit 38 wordmark left, kit 51 right. Theme is light by default; theme, font, text size and spacing are saved as one
  object under `storage_key` on the reader's device only. Escape or Close returns focus to Aa.
- **Print:** every pane and fold opens.

## Data rules

The schema is `brief.schema.json`. Text allows two inline marks only, `[text](https://url)` and `**bold**`; no raw HTML. The
builder also refuses a plan row without one cell per horizon, a table row that does not match its header, a duplicate tab id, an
action to a missing tab or section, and any em-dash.

## Tuning by hand (internal only)

`python3 scripts/tabbed_brief_build.py DATA.json --tune /some/scratch/name.html` writes an internal copy (it refuses `public/`).
Serve that folder and open a page with `?tune&edit`:

- **Tokens.** `--lh` (line height), `--sp-4` (section rhythm), `--gap` (card gap), `--ls` (letter-spacing) and `--fs-body` move live.
- **Breakpoints.** One slider per px width the page's media queries use. The 1024px one is the stack breakpoint (`stack_below` in
  the data, default 1024): the tabs fold into the menu and the cards stack below it. The slider moves the CSS rules and the nav's
  JS together. Container queries (kit 54 signal ledger at 38rem and 58rem, kit 55 sound bite) get their own sliders, marked
  "(container)"; they move live, but their widths live in the kit file, so a moved one is reported "set in source by hand".
- **Wrapping.** `text-wrap` for headings and for body text.
- **Text.** Every data string is editable in place (Enter is blocked: one string, one line; bold and links survive).

Hand the exports back with `python3 scripts/tabbed_brief_build.py DATA.json --apply EXPORT [...]`. It takes any mix of Copy JSON
(the data patch), Copy CSS (the line, saved as a .css file), Copy edits, or Export versions (the latest breadcrumb, or `--version N`).
Text and `stack_below` go to the data file, edited in place so a one-field change is a one-line diff; tokens and wrapping go to
a tuned block at the end of `shell.css` (`/* arcs-tuned:start */`), merged on each apply. It validates, then rebuilds the
registered page; if any part is refused, nothing is written. The tuner never reaches a counterpart page:
`page_gate.py --counterpart` fails any page carrying it.

The same two flags work on every page builder; the mechanics live once in `scripts/page_tune.py`. Where each part lands:

| Builder | Page | Text goes to | Tokens and wrapping go to |
|---|---|---|---|
| `tabbed_brief_build.py DATA` | Gravity brief | DATA (by JSON pointer, `?edit`) | `shell.css` tuned block |
| `proposal_build.py --louisville` | Louisville proposal | `source.html` | `source.html` tuned block |
| `myally_hub_sync.py` | MyAlly hub | the hub HTML (synced Step 1 block masked), else `engagement.json` | the hub's tuned block |
| `engagement_render.py --dir D` | internal proposal.html | `D/engagement.json` | refused (CSS is in the script) |
| `counterpart_onepager_build.py DATA` | Brooks one-pager | DATA (fields are HTML, so new text is escaped) | DATA `tokens` |
| `precall_brief_build.py DATA` | pre-call brief | DATA | `page.tpl` tuned block (every brief) |
| `blog_render.py POST.md` | NFTT post | POST.md | refused (no tuner tokens on the page) |
| `research_render.py [OUT] DIGESTS` | Almanac | the digest that holds the text | refused (no tuner tokens) |
| `milestone_render.py DATA` | milestone map | DATA | refused (no tuner tokens) |

Text from double-click goes to the first source that holds it, and must be there exactly once; text the builder computes (a
cite-substituted value, a derived row) is not in any source, so the pair is refused and named. Builders with no data source
(hand-written pages served straight from public/) take `scripts/token_tuner_inline.py --apply-text` against their own file.
