# slop-gate

The ARCS slop-free / factuality gate suite, consolidated into one package.

Four checks decide whether a customer-facing surface (a resume, a candidate or marketing page, an
outbound artifact, a public post) reads as human-written and every number on it traces to evidence.
The suite exists because a designed resume for the Success Academy AI PM role read as AI slop to the
hiring manager and the recruiter would not send it (banked 2026-09-25). "Slop-free" is now a gate,
not a hope.

Applies to anything a counterpart sees. NOT internal docs (AGENTS / memory / ADRs legitimately
discuss these very words).

## The four layers

Slop has a mechanical half and a judgment half, and fabrication is a separate failure again from
style. Conflating them either lets slop through or false-fails approved rhetoric. So there are four
layers, each with its own verdict and blast radius:

| # | Layer | What it catches | Verdict | Determinism | Script |
|---|-------|-----------------|---------|-------------|--------|
| 1 | **style** | High-precision cliches (delve, spearheaded, results-driven, and kin) plus em-dashes | HARD FAIL, blocks commit | grep, deterministic | `slop_lint.py` |
| 2 | **human-baseline** | Sentence-length variety (burstiness) + specificity density (lines naming a real tool / system / number) | Advisory (report; `--strict-metrics` to fail) | measurement, deterministic | `slop_lint.py --metrics` |
| 3 | **judgment** | The tells a grep cannot call: forced binary contrast, rule-of-three triads, colon reveals, robotic cadence | Advisory (SHIP / REVISE) | LLM, non-deterministic | `slop_eval.py` |
| 4 | **factual** | Every dollar / percent / latency / count must cite a sibling `evidence.jsonl` entry (documented or self-reported) | FAIL on any uncovered metric | regex over a ledger, deterministic | `provenance_lint.py` |

Layers 1, 2, 4 are a plain grep or a measurement: they cost nothing and never guess. Layer 3 asks a
model to grade the judgment calls, so it is advisory and off the commit path.

A fifth, out-of-scope layer completes the picture but lives elsewhere: **design slop** (glassmorphism,
cyan-on-dark, radial halos, glyph tiles) is caught by the impeccable `detect` hook, not here.

## Thresholds (banked in the rubric)

- **Tier-A cliches: 0** (hard fail) · **em-dashes: 0** (standing rule)
- **Burstiness (stdev of unit word-counts): >= 6**, mode-independent
- **Specificity density**, per mode: resume / operate / default **>= 60%**, persuade / read **>= 50%**
  (positioning prose legitimately carries more connective text than a dense resume)
- **Judgment rubric: total <= 3, no single row = 2**
- **Metrics cited: 100%** on an enrolled surface

The full rubric, with the per-row 0-2 scoring and the reference numbers, is `lib/slop-free-rubric.md`
(the single source is the repo's `_PATTERNS/slop-free-rubric.md`).

## Run it

```
# style lint (exit 1 on any tier-A cliche or em-dash)
slop-gate lint path/to/page.html [...]
slop-gate lint --pair staged.html head.html      # ratcheted (pre-commit form): only NEW slop blocks

# human-baseline scorecard
slop-gate metrics --mode persuade path/to/page.html
slop-gate metrics --strict --mode resume resume.txt   # exit 1 under baseline

# judgment tier (needs ANTHROPIC_API_KEY; no key -> prints a notice, exits 0)
slop-gate eval path/to/page.html
slop-gate eval --strict path/to/page.html             # exit 1 on REVISE

# factual tier (enrolled = a sibling <stem>.evidence.jsonl or evidence.jsonl exists)
slop-gate provenance path/to/page.html

# style + metrics + provenance on one file, in one call
slop-gate all path/to/page.html

# prove every deterministic gate fails-on-bad AND passes-on-good
slop-gate self-test
```

In the repo the runner finds the linters in `../../scripts`; when packaged it finds the vendored
copies in `./lib`. Same behavior either way.

## Fixtures

`fixtures/` carries a worked fail-on-bad / pass-on-good pair so you can see each layer fire:

```
slop-gate lint        fixtures/bad.txt    # FAIL: tier-A cliches + em-dash
slop-gate lint        fixtures/good.txt   # PASS
slop-gate metrics     fixtures/bad.txt    # UNDER baseline
slop-gate metrics     fixtures/good.txt   # MEETS baseline
slop-gate provenance  fixtures/bad.txt    # FAIL: 40+ / 75% have no evidence entry
slop-gate provenance  fixtures/good.txt   # PASS: 480ms / 110ms both cite the sibling ledger
```

## Deps

- **python3 (>= 3.8), standard library only.** No pip install, no network (layer 3 calls the
  Anthropic API over stdlib urllib only when a key is present).
- **bash** for the `slop-gate` runner, or **node (>= 16)** for the npm `bin/slop-gate.js` wrapper.

## Pre-commit (already wired in arcs-v9)

`scripts/git-hooks/pre-commit` runs layer 1 (ratcheted, scoped to `public/**` + `_ARTIFACTS/**`
html) and layer 4 (opt-in, on any changed html), alongside `artifact_wrap_lint.py` and
`token_source_gate.py`. This package does not change that wiring; it repackages the same scripts for
use outside the repo.

## Distribution (scaffold - NOT published)

Everything below is built but deliberately unshipped. Three decisions are the user's:

1. **Package name + npm scope.** `package.json` names it `@arcs/slop-gate` as a candidate, flagged
   `nameCandidatePendingApproval`. Verify the name is free (`npm view <name>`) before claiming it; do
   not squat an existing name. `private: true` blocks `npm publish` until removed on purpose.
2. **License.** The repo is All-rights-reserved; the suite's license is undecided. `LICENSE`,
   `package.json` (`UNLICENSED`), and the Homebrew formula (`:cannot_represent`) all hold placeholders.
   Recommended: MIT, matching the sibling resume-tailor-skill and the public-good framing.
3. **python3 shell vs JS port.** See the next section.

### Build the self-contained tarball

```
cd tools/slop-gate
bash build.sh          # vendors scripts/*.py + the rubric into ./lib (gitignored)
npm pack               # produces the tarball (does NOT publish)
```

### Why python3, not a JS port (recommendation)

**Recommendation: keep shelling to python3; do not port to JS.** The three linters are proven,
self-tested, stdlib-only Python already on the repo's commit path. A JS port would duplicate the
cliche catalogs, the burstiness / specificity math, and the ledger regex logic, doubling the
maintenance and test surface for zero user benefit (the audience has python3). The cost is one honest
runtime prerequisite: npm users need python3 on PATH, documented in `package.json.engineNote` and
above. If a pure-node install with no python3 ever becomes a hard requirement, port layers 1, 2, 4
(the deterministic ones) and leave layer 3 as-is; but that is a later call, not this scaffold's.

### npm (do NOT run until the decisions above are made)

```
cd tools/slop-gate
# 1. set final name + scope, choose a license, then in package.json remove "private": true
# 2. bash build.sh          # vendor lib/
# 3. npm publish --access public
```

### Homebrew (do NOT run until a release tarball exists)

Formula: `Formula/slop-gate.rb`. Intended tap repo: **`flashesofbrilliance/homebrew-arcs`**
(recommendation; the tap repo name is the user's call). A repo named `homebrew-arcs` installs via
`brew tap flashesofbrilliance/arcs && brew install slop-gate`. The formula's `url` + `sha256` are
placeholders until a release is cut.

```
# after cutting a release tarball and filling url + sha256 + license in the formula:
git clone https://github.com/flashesofbrilliance/homebrew-arcs
cp Formula/slop-gate.rb homebrew-arcs/Formula/
# commit + push the tap repo (the user's call)
```

## Layout

```
tools/slop-gate/
├── slop-gate              # bash entrypoint (dispatches to python3; resolves lib/ or ../../scripts)
├── bin/slop-gate.js       # npm bin wrapper (node -> python3; same resolution)
├── package.json           # npm scaffold (private: true; name + license flagged for approval)
├── Formula/slop-gate.rb   # Homebrew scaffold (url/sha256/license = placeholders)
├── build.sh               # vendors the linters + rubric into lib/ at pack time
├── fixtures/              # fail-on-bad + pass-on-good samples (+ per-file evidence ledgers)
├── lib/                   # (gitignored) vendored linters + rubric, produced by build.sh
├── LICENSE                # placeholder: license undecided
└── README.md              # this file
```

## Sources

Rubric + provenance model banked 2026-09-25/26 (this engagement). Design tells: impeccable.style/slop.
Writing tells: hardikpandya/stop-slop, petergyang/no-ai-slop, Strunk & White, Orwell "Politics and the
English Language". Full rubric: `lib/slop-free-rubric.md`.
