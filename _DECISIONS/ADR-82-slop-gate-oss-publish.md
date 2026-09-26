# ADR-82 · slop-gate OSS publish (npm first, Homebrew deferred)

> **Status:** PROPOSED · reversible prep committed; the publish itself is WRITE-LOCKED pending the user's go
> **Date:** 2026-09-26
> **Commit:** (set at merge)
> **Y:** YELLOW / MODERATE / SHIFTING (name reservation + license reliance are one-way; everything built so far is reversible)
> **Relates to:** `tools/slop-gate/` (the bundle), `scripts/slop_lint.py` · `slop_eval.py` · `provenance_lint.py` (the SSOT linters), `_PATTERNS/slop-free-rubric.md`, `public/resume-tailor.html` (the surface that showcases it), the sibling OSS tools `germinate` + `rosetta-shell` in `flashesofbrilliance/homebrew-tap`.

## D — The Decision

**Sharp question:** The four-layer slop-free / factuality gate (style / human-baseline / judgment / factual) has been consolidated into a distributable bundle at `tools/slop-gate/`. Shipping it as a public good means reserving a package name and attaching a license, both of which are hard to walk back. Under what name, license, and channel does it publish, and what stays gated?

**Decision (LOCKED by the user):**
1. **npm name/scope: `@arcs-care/slop-gate`.** Unscoped `slop-gate` is already taken on npm (verified 200); the `@arcs` scope cannot be assumed. `@arcs-care` is free (verified 404) but the scope requires the user to create the free `@arcs-care` npm org first.
2. **License: MIT**, Copyright (c) 2026 Zach Harris (ARCS). The tool is MIT even though the parent `arcs-v9` repo is all-rights-reserved. This is a deliberate carve-out for this bundle only.
3. **Channel order: npm first, Homebrew deferred.** Homebrew rides the EXISTING tap `flashesofbrilliance/homebrew-tap` (installs via `brew tap flashesofbrilliance/tap`), mirroring the sibling formulae `germinate.rb` and `rosetta-shell.rb`. Do NOT invent a `homebrew-arcs` tap.
4. **Governance: this ADR + a WRITE-LOCK on the publish** (per ROM primitive #7: irreversibility is declared, not assumed).
5. **Implementation: shell to python3, do not port to JS** (recommendation carried from the bundle README: the linters are proven, self-tested, stdlib-only; a port doubles the surface for no user gain).

## W — WRITE-LOCK declaration (ROM primitive #7)

`npm publish --access public` is a **one-way door** and is therefore WRITE-LOCKED. Two irreversible effects:
- **Name reservation.** Publishing `@arcs-care/slop-gate` claims that name on the public registry. Unpublish is time-limited and rate-limited by npm policy; the name and its version history do not cleanly return.
- **License reliance.** Once published MIT, downstream consumers may rely on those terms for that version; the grant on a shipped version cannot be retracted.

Therefore `npm publish` requires the user's **explicit, per-action go**. No agent (this harness or any other) may run it. The `private: true` field in `package.json` is the mechanical backstop: `npm publish` refuses while it is set, and removing it is itself a user step. The Homebrew tap push is likewise deferred and user-gated (and additionally blocked by placeholder `url`/`sha256`).

## What is CONFIRMED (verifiable now)
- `@arcs-care/slop-gate` is the chosen name; unscoped `slop-gate` is taken, `@arcs-care` package path is free (per the coordinator's npm checks).
- `tools/slop-gate/` builds and runs green: `slop-gate self-test` passes both deterministic gates (fail-on-bad + pass-on-good); `build.sh` vendors `lib/` and the vendored-resolution path runs; bash + node runners both work.
- The MIT text, `package.json` (`"license": "MIT"`, `private: true`), and `Formula/slop-gate.rb` (`license "MIT"`, tap = homebrew-tap, url/sha256 = TODO) are in place.
- The tap `flashesofbrilliance/homebrew-tap` exists and carries the two sibling formulae whose conventions the formula matches.

## What is PENDING (not yet done, user-gated)
- The `@arcs-care` npm org does not exist yet (user creates it).
- No `slop-gate` release tarball is cut, so the Homebrew `url`/`sha256` are placeholders.
- `private: true` is still set (publish blocked by design).
- `npm publish` has NOT run; nothing is on any public registry.

## The publish sequence (the user runs this, in order)
```
# 1. create the free @arcs-care npm org (npm web UI or `npm org create arcs-care`)
cd tools/slop-gate
# 2. remove "private": true from package.json
# 3. bash build.sh                 # vendor lib/
# 4. npm publish --access public   # WRITE-LOCK: explicit go required (this ADR)
# Homebrew: LATER — cut a release tarball (with vendored lib/), fill url+sha256, push to homebrew-tap
```

## Y — Gate

YELLOW / MODERATE / SHIFTING. The prep is fully reversible and committed; the conviction gap is the org-creation + publish, which is the user's one-way call. Nothing here fires without that explicit go.
