# Strudel for Phosphor: research brief (2026-10-23)

> **Status: second-hand research, not verified by us.** Written by a research subagent from web pages and npm registry metadata (read-only; nothing installed or downloaded). Several Codeberg pages came back scrambled by an anti-scraper notice, so claims that depend on them are marked UNVERIFIED. Treat everything below as data to check, not as decided fact. Not legal advice: the licence choice is Zach's. Requested by Zach on 2026-10-23 after he shared https://strudel.cc/learn/getting-started/ and https://codeberg.org/uzu/strudel/ . Follow-on task: evaluate Strudel for Phosphor (adopt vs build), under runtime/specs/phosphor-adopt-vs-build.md.
>
> **Clean-room note:** if a clean-room parser is chosen, whoever writes it should work from this brief and the public documentation only and should not read Strudel source code. Keep a dated log of what was read.

# Strudel decision brief (2026-10-23). Not legal advice; licence choice is Zach's call.
Method: WebFetch of strudel.cc and codeberg pages, npm registry via `npm view`, jsdelivr/unpkg listings (headers/JSON only). Nothing installed or downloaded. Codeberg served scrambled pages to some fetches (anti-scraper notice); those claims are UNVERIFIED. No page contained instructions aimed at me.

## 1. What Strudel is
- Browser JS port of Tidal Cycles; code on Codeberg uzu/strudel (https://codeberg.org/uzu/strudel). Pattern engine returns "haps" (events with whole/part timespans) via queryArc(begin,end); queries split at cycle boundaries (https://strudel.cc/technical-manual/internals/).
- Pieces: @strudel/core (pattern engine), @strudel/mini (mini-notation parser, PEG grammar krill.pegjs), @strudel/transpiler (turns "x" strings into mini parse calls), @strudel/webaudio + superdough (audio output), @strudel/codemirror/@strudel/repl (editor UI). npm descriptions: https://www.npmjs.com/package/@strudel/core etc. (via `npm view`).
- Time: cycles are the unit; a bare sequence fits in one cycle; cps (cycles per second) sets tempo. Scheduler/lookahead/AudioWorklet details: UNVERIFIED (the internals page did not cover them). Evidence only that @strudel/web builds with vite-plugin-bundle-audioworklet and ships a clockworker asset of 1,251 bytes (https://data.jsdelivr.com/v1/packages/npm/@strudel/web@1.3.0?structure=flat, package.json at https://unpkg.com/@strudel/web@1.3.0/package.json), so a Worker clock and an AudioWorklet are very likely.
- Default samples: drum sounds from tidal-drum-machines, instruments from VCSL; only sample maps load at start, audio files load on first play, so first trigger can be silent (https://strudel.cc/learn/samples/). That page does not say the host; fetched from network (not bundled): CONFIRMED by the PWA page's cache list. Avoid by `samples({name:'file.wav'},'base-url')`, strudel.json maps, or the REPL's "Import Sounds Folder".
- Synths/effects: superdough provides oscillators, filters, envelopes, reverb/delay etc. (UNVERIFIED in detail).

## 2. Packages (npm view, 2026-10-23; all licence AGPL-3.0-or-later)
| package | ver | unpackedSize B | contents |
|---|---|---|---|
| @strudel/core | 1.2.6 | 573,707 | pattern engine; deps fraction.js, @kabelsalat/web |
| @strudel/mini | 1.2.6 | 252,164 | mini-notation; dep core |
| @strudel/transpiler | 1.2.6 | 67,409 | user-code transpiler |
| @strudel/webaudio | 1.3.0 | 71,689 | Web Audio glue; deps core, superdough 1.3.0, draw, supradough |
| superdough | 1.3.0 | 393,083 | sound engine (separate unscoped name; @strudel/superdough 404); deps @kabelsalat/lib, nanostores |
| @strudel/codemirror | 1.3.0 | 823,875 | editor |
| @strudel/web | 1.3.0 | 1,548,880 | opinionated bundle: core+mini+tonal+transpiler+webaudio |
| @strudel/repl | 1.3.0 | 5,174,918 | web component `<strudel-editor>` |
| @strudel/embed | 1.1.2 | 37,370 | iframe wrapper `<strudel-repl>` |
| tonal 121,420; draw 89,885; soundfonts 277,738; midi 80,312; osc 49,126; xen 2,472,009; csound 113,484; tidal 5,823,254 | | | extras |
Minimum for mini+schedule+sound: web (or core+mini+transpiler+webaudio+superdough). @strudel/web dist listing: the package's CommonJS build 655,936 B, the package's ES-module build 850,423 B, index.min.js exists but its size was not in my listing (UNVERIFIED). Source: https://data.jsdelivr.com/v1/packages/npm/@strudel/web@1.3.0?structure=flat. Even a tree-shaken subset likely exceeds the 72,520 B of headroom (400,000-327,480) by several times (estimate, UNVERIFIED).

## 3. Licence (not a lawyer)
- Code: AGPL-3.0-or-later on every package checked (npm registry). README: "must abide by the terms of the GNU Affero Public Licence v3"; code "can only be shared within free/open source projects under the same license" (https://codeberg.org/uzu/strudel).
- Project start page: "Source code must be distributed along with web publication"; says clones based on reading Strudel's source count as derivative works (https://strudel.cc/technical-manual/project-start/). This is a maintainer-stated position, relevant to a clean-room.
- Default sample banks: licensed separately, see dough-samples repo (README link); per-bank terms UNVERIFIED (codeberg fetch failed).
- Maintainer statements on embedding, commercial use, relicensing: none found (web search found nothing). UNVERIFIED.
- Consequence of bundling: AGPL s.13 network clause means a publicly served modified page would need to offer its Corresponding Source to users, i.e. all of Phosphor under AGPL-compatible terms; the arcs-v9 repo is private. Consequence of clean-room: no Strudel code or text, so no AGPL on Phosphor; but the maintainers' "reading source = derivative" view means the parser must be written from the public docs only, by someone who has not read krill.pegjs, with a dated record. Names/syntax are ideas, but this is a legal judgement for Zach and counsel. ONE-WAY DOOR: once AGPL code ships publicly, the source duty attaches to that release.

## 4. Offline and embedding
- Strudel REPL is a PWA; first visit caches the app (<1MB), samples cache only after played online, and only from raw.githubusercontent.com, freesound, shabda (https://strudel.cc/learn/pwa/). Fully offline for a bundled single file: possible in principle with local samples/no sample maps; not demonstrated (UNVERIFIED).
- Embedding: iframe share URL; @strudel/embed (iframe to strudel.cc, needs network); @strudel/repl `<strudel-editor>` (no iframe, 5.2 MB); @strudel/web `initStrudel()` with own buttons (project-start page above). Needs a bundler such as Vite for npm use.

## 5. Mini-notation reference (from https://strudel.cc/learn/mini-notation/ and a prose summary of krill.pegjs, which I did not copy)
Quoting: "..." or backticks parse as mini; '...' does not.
- Sequence: space-separated steps share one cycle equally. `c e g b` = 4 events of 1/4.
- `[ ]` group: occupies one parent slot, nests arbitrarily.
- `*n` speed up (decimals ok, factor may be a pattern); `/n` slow down. `[a b]*2` plays twice per cycle; `[a b]/2` spans 2 cycles.
- `< >` alternate: one step per cycle, equals `[...]/N`. `<a b c>*8` = 8 per cycle.
- `~` or `-`: rest (silent slot).
- `_`: extends the previous step's weight by 1 (a lone `_` is only valid as extension). `a _ b` = a takes 2/3.
- `@n`: weight n (default 1); bare `@` adds 1. `a@3 b` = 3:1.
- `!n`: replicate n copies without speeding up; bare `!` adds one copy; `a! b` = a a b. Sets weight to count.
- `?` drop with p=0.5; `?0.1` drop 10%. Each `?` gets its own auto-incremented seed (so reproducible per position); how the random is derived from cycle time: UNVERIFIED.
- `(k,n)` / `(k,n,r)` euclid: k hits spread over n slots; r = offset/rotation. `bd(3,8)` = x..x..x. (standard Bjorklund; exact rotation direction UNVERIFIED, test against site). Args may be patterns.
- `,` stack (chord/polyphony); `|` random choice per cycle (seeded); `.` feet grouping; `a:3` tail/sample index; `..` ranges (not on the docs page, only in grammar summary).
Subset for a kids' step sequencer: sequence, [], *, <>, ~, _, !, ?, euclid. Define: parse to a weighted tree; for cycle c, flatten to 16 steps by LCM subdivision.

## 6. Prior art and limits
- No single-file offline Strudel player found; search did not surface one (UNVERIFIED).
- Latency, iOS Safari audio quirks: not covered by sources I could read; general knowledge only (AudioContext must start from a user gesture; AudioWorklet needs secure context). UNVERIFIED for Strudel.
- Size: @strudel/web unpacked 1.5 MB vs 72.5 KB headroom.

## 7. Options
| | A adopt packages | B clean-room small parser | C do not adopt |
|---|---|---|---|
| Licence | AGPL-3.0-or-later on whole page; source must be offered; private repo conflicts. ONE-WAY | None from Strudel if truly clean-room (record process) | None |
| Size | +~0.5-1.5 MB, breaks 400,000 cap | est. 3-8 KB (estimate) | 0 |
| Offline | Needs sample/network handling, unproven | Full (uses own audio) | Full |
| Effort | Medium to bundle, high to shrink | ~1-2 days incl. tests | 0 |
| Risk | Licence capture; cap break; sample 404s offline | Drift from Strudel semantics; derivative-work claim if source was read | Loses pattern-text feature |

Recommendation: B, subset only, with a provenance note; C if the counsel question stays open.

## Five questions for Zach
1. Is Phosphor allowed to become AGPL (and its source offered), or is that excluded? 
2. Is "uses Strudel mini-notation syntax" a feature kids need, or is a step grid with text export enough?
3. Who writes the parser, and can they avoid reading krill.pegjs, with a dated clean-room log?
4. Which operators are in scope (my proposal: [] * <> ~ _ ! ? euclid), and is `,` `|` `.` out?
5. Should we call it "Strudel-compatible" in UI/docs, given trademark and the maintainers' derivative-work stance?
