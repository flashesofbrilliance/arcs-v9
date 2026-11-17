# Babel Fish Loki test: pre-registration

- **Registered:** 2026-11-16, before any run against real Claude. This commit is the timestamp.
- **Why:** canon §4.4 (hyperstition pipeline). An idea reaches APEX only after it survives a Loki
  challenge. The transceiver carries the whole "lossless" claim, so this test attacks the transceiver.
- **Instrument:** the Loki section of `babel-fish-artifact.html` (https://claude.ai/artifact/QQFyyZa3xeUhfuhyMtjKz9).

## Method

10 fixed concepts, built into the page: a conditional, a causal chain, a mixed result, irony,
a counterintuitive claim, an attribution, a definition, a multi-part policy, a qualified finding and
an enumerated negative. Each concept gets one persona, cycling through the codex's six. For each:

1. Decompose into claims. Render once for the persona: this is the clean control.
2. Plant four corruptions in copies of the clean rendering:
   - **drop:** the last claim's sentence is deleted mechanically.
   - **add:** a fabricated number is appended mechanically.
   - **negate:** claim 1 is reversed, an edit made by Claude.
   - **soften:** claim 2 is hedged, an edit made by Claude.
3. Each copy goes through the same blind receive and compare steps as a normal run.

A corruption counts as caught when:
- for drop, negate and soften, the target claim is marked anything other than kept;
- for add, the compare step lists at least one added claim.

A corruption is excluded, listed but not counted, when the edit left the text unchanged or the
claim's sentence could not be located.

## Pass bar (fixed before any result)

| Group | Bar |
|---|---|
| Dropped or negated claims caught | at least 90% |
| Added numbers or softened claims caught | at least 80% |

Both must hold over all 10 concepts. A partial run (stopped or errored) does not count. The control
false-alarm rate (claims in the clean rendering not marked kept) is reported alongside, with no bar.

## After a run

File the copied JSON in a decision receipt (`job:backlog:babel-fish-transceiver`) whether it passes
or fails. Each miss is a named failure mode. Changing the bar after a result means a new
pre-registration, not an edit to this file.
