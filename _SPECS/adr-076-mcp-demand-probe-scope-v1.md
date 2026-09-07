# ADR-076 MCP-Led Growth — Demand Probe Scope v1

> **Status:** DRAFT scope for Zach review. Validates ADR-076 (`_DECISIONS/ADR-076-mcp-led-growth-attribution-wedge.md`).
> **Rule:** this probe exists to FALSIFY, cheaply. Do not build a hosted MCP server. Ship the smallest
> thing that produces an honest pull/no-pull signal.

## The job we are testing

Not "can we build an ARCS MCP" (yes, trivially). The bet is: **do people want to query ARCS from
inside their agent (Claude/Cursor/etc.), and does the attribution wedge — cited answers, not the model
guessing — pull them?** The probe must be able to come back **negative** and mean it.

## The crux: measurement, not the tool

An MCP tool that runs locally (stdio, on the user's machine) is the cheapest to ship AND the hardest to
measure — a local process is invisible to us unless it phones home, and phoning home is a privacy cost
we should not pay casually. Every design decision below is driven by *how we detect pull honestly*, not
by the tool's features.

## Two stages, cheapest first (cheap-tripwire-before-expensive-jtbd)

### Stage 0 — Painted door (~1 hr). Ship this first; it may end the experiment.
- On `good.arcs.care` (public-goods index) and `good.arcs.care/blog/nftt`, add a **"Connect an agent →"**
  card: one line of copy ("Query these field notes from your AI tools — every answer cites its source"),
  expanding to a short waitlist / "what would you ask ARCS?" capture (email + free-text intent).
- **Signal:** Vercel Web Analytics on the card (view→expand→submit funnel) + the captured intents.
- **Decision:** if, over the window, the card gets effectively zero engagement, the thesis is weakened
  for ~1 hour of work. Stop here; ADR-076 stays DRAFT. If it gets knocks, proceed to Stage 1.
- Cost: one card + one capture endpoint (or a first-party form). No MCP code.

### Stage 1 — Working read-only probe (~0.5–1 day). Only if Stage 0 gets knocks.
- **Distribution:** a local **stdio MCP server** shipped through the rails ARCS already owns (the
  `arcs-skills` marketplace + `npx`/brew), NOT a hosted endpoint. Users add it with one line
  (`claude mcp add arcs-field-notes ...`). Zero hosting cost; runs on the user's machine.
- **Corpus (already-public only):** the NFTT field-notes posts. Exported once to a small static JSON at
  `good.arcs.care/field-notes.json` (id, slug, title, standfirst, body-text, url, date). No auth, no
  private data, repo stays private.
- **Tools (read-only, verb+entity-namespaced — 2 to start):**
  - `search_field_notes(query)` → ranked matches, each with title + url + a cited snippet.
  - `get_field_note(slug)` → full text + canonical url.
  - Every response **carries the source url** — the attribution wedge in miniature. This is the whole point.
- **Measurement (the load-bearing design choice):** the tool fetches the corpus from
  `good.arcs.care/field-notes.json` on each cold start / query rather than bundling it. We then count
  requests to that path (Vercel logs / a lightweight edge counter), filtered to the MCP user-agent. That
  request count = active-usage signal, with **no PII and no bespoke telemetry** — the user's own agent
  fetching public JSON is the beacon. (Fallback if fetch-per-query is too chatty: a single anonymous
  `HEAD /field-notes.json?mcp=1` ping per session.)

## Decision gate (Zach sets the two numbers)

- **Window:** e.g. 4 weeks after the Stage-0 card is live (Stage-1 clock starts when Stage 1 ships).
- **Threshold (OPEN — needs your call):** e.g. "≥ N distinct install/active-query sessions" and/or
  "≥ M waitlist intents." Below → thesis weakened, ADR-076 stays DRAFT or is retired with the receipt.
  At/above → graduate: now the hosted-server / API-tier build is justified.
- Either outcome is a win: a clean negative saves the hosted-server spend the ADR explicitly guards against.

## Cost / leverage

- Stage 0: ~1 hr (a card + capture). Stage 1: ~0.5–1 day (a ~150-line stdio MCP + a JSON export + a
  request counter + a marketplace entry). No hosting, no new deps beyond the MCP SDK.
- Reuses existing rails: `arcs-skills` marketplace, good.arcs.care, Vercel analytics, the sitemap corpus.

## Risks / honest caveats

1. **Thin corpus.** Field notes alone may be too narrow to be interesting. If Stage 0 intents ask for
   decision/receipt querying, widen the Stage-1 corpus to whatever public receipts exist (still no
   private data) before judging the thesis.
2. **Local MCP is low-visibility.** The fetch-from-endpoint measurement is the mitigation; if it proves
   too noisy or too quiet, the honest read is "inconclusive," not "negative."
3. **Distribution ≠ demand.** Marketplace presence is not pull; the beacon/intent counts are. Do not read
   an install as usage.

## Open questions for Zach

1. The two gate numbers (window + threshold).
2. Corpus scope for Stage 1: field-notes only, or include any public decision receipts?
3. Is a first-party waitlist/capture acceptable for Stage 0, or keep it to click-analytics only (no capture)?
