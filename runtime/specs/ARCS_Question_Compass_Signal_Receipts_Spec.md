# ARCS Question Compass, Signal, and Receipts

## S-tier Design Spec / PRD / Implementation Plan

Prepared as a Claude Code-ready engineering handoff for the ARCS local-hosted brief, based on the existing Question Compass critique, the simplification direction for v9, and the role of Signal and Decision Receipts as core product primitives.[cite:3][cite:23][cite:4][cite:21]

## Executive summary

ARCS should treat Question Compass as the canonical front door: a low-friction decision intake that converts messy user context into one clear next move with minimal cognitive overhead.[cite:3][cite:23]

The current implementation underdelivers because it behaves like a form without a complete decision loop: it lacks a durable inline answer surface, clear state transitions, mobile-native submission, and a first-class receipt layer that preserves continuity across time.[cite:3]

The revised product model should separate three layers: **Compass** as intake, **Signal** as the structured answer surface, and **Receipts** as the durable learning, accountability, and calibration substrate.[cite:3][cite:4][cite:21]

The correct implementation strategy is not a one-shot UI rewrite alone. It is a phased product build with a stable response contract, an orchestration layer behind the Compass façade, and first-class receipt generation for every meaningful decision interaction.[cite:3][cite:21]

## Product intent

### Product thesis

ARCS is most differentiated when it hides its internal complexity and presents a simple, trustworthy front door that helps a user decide what to do next.[cite:3][cite:23]

The revised Question Compass should embody the “clarity before curvature” principle: default to one obvious move, reveal deeper structure only on demand or when the stakes justify escalation, and never burden the user with internal system lore unless it helps them act.[cite:23][cite:3]

### Primary JTBD

Help a user turn a messy decision into one trustworthy next move in under two minutes.[cite:3]

### User outcomes

- Immediate clarity: the user gets a concrete recommendation rather than a navigation dead end.[cite:3]
- Justified confidence: the system explains why the recommendation exists without overwhelming the user.[cite:3]
- Continuity over time: the system creates a Decision Receipt that can be revisited, compared, and used to calibrate future choices against actual outcomes.[cite:4][cite:21]

## Problem statement

### Current failures

The current Compass experience fails at the core promise level because the user can provide context but does not receive a visible, structured answer on the same surface.[cite:3]

The current form also treats the input fields as disconnected controls rather than one decision object, which weakens the user’s sense that the system is actually synthesizing a coherent recommendation.[cite:3]

Submission is not adequately exposed across devices, because keyboard shortcut-only behavior breaks the primary action path on mobile and creates ambiguity even on desktop.[cite:3]

The UI further lacks explicit loading, result, receipt, history, and refinement states, making the system feel like an incomplete shell rather than a trustworthy decision instrument.[cite:3]

### Root causes

- No inline answer surface.[cite:3]
- No durable response contract.[cite:3]
- No explicit system state model for input, loading, result, refine, and save.[cite:3]
- No first-class receipt architecture, despite receipts being central to ARCS’s accountability and learning model.[cite:4][cite:21]
- Too much implicit architecture and not enough user-facing continuity.[cite:3][cite:23]

## Product architecture

### Frontstage model

The product should expose three primary surfaces:

| Surface | User-facing purpose | System role |
|---|---|---|
| Compass | Ask the question and set lightweight qualifiers.[cite:3] | Creates a normalized decision object for orchestration.[cite:3] |
| Signal | View the answer, rationale, weighted factors, and suggested next moves.[cite:3] | Renders a stable response contract independent of internal routing complexity.[cite:3] |
| Receipts | Revisit prior decisions, compare outcomes, and sharpen future calibration.[cite:4][cite:21] | Stores the durable decision artifact and later outcome updates.[cite:4][cite:21] |

### Backstage model

Behind the front door, the system should route requests through an orchestration layer that infers complexity, selects mode, applies guardrails, synthesizes the recommendation, and logs a receipt.[cite:3][cite:23]

This reflects the v9 direction in which the user sees a minimal prompt surface while ARCS invisibly handles altitude, risk, identity, domain, and guardrail logic under the hood.[cite:3]

## Product principles

- **Simple by default.** One question, a few lightweight qualifiers, one next move.[cite:3]
- **Depth on demand.** Court, simulations, alternative paths, and expert layers only appear when explicitly requested or when risk thresholds force escalation.[cite:3][cite:23]
- **Trust through transparency.** The user should always see why the system is pointing in a given direction, at least at a concise level.[cite:3]
- **Receipts over rhetoric.** Every meaningful recommendation should generate a durable record to enable accountability and calibration against future outcomes.[cite:4][cite:21]
- **Agency preservation.** The system should guide, not coerce; if guardrails trigger, the user should see why and retain a deliberate override path where appropriate.[cite:3]

## Scope

### In scope for MVP

- Single-page Question Compass intake.[cite:3]
- Inline Signal result surface with loading state and editable refine loop.[cite:3]
- Lightweight qualifiers and mobile-safe submission.[cite:3]
- Stable `CompassResponse` schema.[cite:3]
- Automatic receipt generation for each successful submission.[cite:21][cite:4]
- Basic receipt list/detail views.[cite:21]
- Mode selection between Quick Move, Plan, and Court at the orchestration layer.[cite:3]

### Out of scope for MVP

- Full multi-channel TV Guide exposure in the UI, because the canon recommends hiding most routing complexity from first-line UX.[cite:3][cite:31]
- Expert/God-mode surfaces such as the full channel architecture, FATED hypercube, or dense constitutional abstractions on the front door.[cite:3]
- Multi-user collaboration and advanced analytics dashboards unless required later by explicit roadmap work.[cite:3]

## User experience blueprint

### Primary flow

1. User lands on Question Compass and sees a single focused prompt asking what they are deciding.[cite:3]
2. User enters free text and optionally sets qualifiers such as feel, reversibility, horizon, or stakes.[cite:3]
3. User submits through a visible primary CTA or keyboard shortcut.[cite:3]
4. UI enters a clear thinking state with disabled controls, live feedback, and a result skeleton.[cite:3]
5. Signal renders inline with a recommendation, rationale, and signal summary.[cite:3]
6. A Decision Receipt is created automatically and linked to the result surface.[cite:21][cite:4]
7. User can refine the question, open a deeper path, or start a new decision.[cite:3]

### Output contract for the user

Every answer should preserve a stable, human-readable structure:

- **Your move**: one sentence recommendation.[cite:3]
- **Why**: concise explanation with 2–3 sentences or bullets.[cite:3]
- **Signal**: a short note showing what inputs or inferred factors mattered most.[cite:3]
- **Mode**: Quick Move, Plan, or Court, translated into plain language.[cite:3]
- **Receipt**: a durable identifier and save point for future review.[cite:21]

## Proposed components

### New component inventory

| Component | Responsibility | Notes |
|---|---|---|
| `DecisionComposer` | Wraps the input prompt and all qualifiers into one normalized decision object.[cite:3] | Replaces the current disconnected-form feeling.[cite:3] |
| `CompassTextarea` | Large auto-growing input with rotating example placeholders.[cite:3] | Stops rotation on focus and resumes only when blurred and empty.[cite:3] |
| `QualifierChips` | Handles single-select and optional multi-select chips with proper affordance, focus, and keyboard behavior.[cite:3] | Needed for feel, reversibility, horizon, and stakes.[cite:3] |
| `CompassSubmitBar` | Owns submit, loading copy, clear behavior, and mobile-safe CTA.[cite:3] | Primary action must always be visible.[cite:3] |
| `ThinkingState` | Skeleton and progress micro-copy during orchestration.[cite:3] | Avoids silent wait pathology.[cite:3] |
| `SignalCard` | Inline result rendering surface for the recommendation and rationale.[cite:3] | Core answer container.[cite:3] |
| `ModeBadge` | Displays the inferred mode in humane language.[cite:3] | Keeps internal routing mostly invisible.[cite:3] |
| `SignalFactors` | Displays the top weighted inputs and caution/opportunity framing.[cite:3] | Improves trust and transparency.[cite:3] |
| `DecisionReceiptCard` | Displays receipt ID, timestamp, status, and quick actions.[cite:21][cite:4] | Makes receipts visible and useful.[cite:21] |
| `DeepenTray` | Hosts “Go deeper”, “Show alternatives”, or “Run Court view”.[cite:3] | Keeps depth behind explicit user intent.[cite:3] |
| `ReceiptTimeline` | Shows related or prior decisions and outcome loops.[cite:4][cite:21] | Supports future calibration and anthology behavior.[cite:4] |
| `DriftSentinelNotice` | Detects repeated unproductive refinement and proposes a landing action.[cite:23] | Aligns with Field OS drift rules.[cite:23] |

### Suggested component tree

```text
QuestionCompassPage
├── AppShell
│   ├── ARCSNav
│   └── MainColumn
├── CompassHeader
├── DecisionComposer
│   ├── CompassTextarea
│   ├── QualifierSection(feel)
│   │   └── QualifierChips
│   ├── QualifierSection(reversibility)
│   │   └── QualifierChips
│   ├── QualifierSection(horizon)
│   │   └── QualifierChips
│   ├── QualifierSection(stakes)
│   │   └── QualifierChips
│   └── CompassSubmitBar
├── ThinkingState
├── SignalPanel
│   ├── ModeBadge
│   ├── SignalCard
│   ├── SignalFactors
│   ├── DeepenTray
│   └── DecisionReceiptCard
├── ReceiptTimeline
└── DriftSentinelNotice
```

## Information architecture

### Recommended primary navigation

The strongest navigation model is not three opaque, equal-weight pages. The system should foreground the linear decision workflow and subordinate the deeper tools.[cite:3]

Recommended IA:

- **Compass** — ask the question.[cite:3]
- **Signal** — current answer state and active decision view.[cite:3]
- **Receipts** — saved decisions, histories, and outcome loops.[cite:21][cite:4]
- **Zoetrope** — optional deep simulation/exploration layer, secondary in hierarchy.[cite:3]

This reduces nav ambiguity while preserving the internal product vocabulary.[cite:3]

## Functional requirements

### FR-1 Intake

The system must provide a primary text input for the decision question and support optional qualifiers via interactive chips.[cite:3]

The primary input must support placeholder rotation when empty and unfocused, and must stop rotating while focused or non-empty.[cite:3]

### FR-2 Submission

The system must provide a visible submit CTA on all viewports and support keyboard submission through Cmd/Ctrl + Enter.[cite:3]

The CTA must be disabled when required input is absent and visibly enabled once the user has entered content.[cite:3]

### FR-3 Loading state

Upon submission, the system must enter a clear thinking state with disabled inputs, animated loading feedback, and a result skeleton.[cite:3]

### FR-4 Signal rendering

The system must render the recommendation inline on the same page, without forcing a route change to receive the primary answer.[cite:3]

### FR-5 Receipt creation

Every successful submission must create a Decision Receipt containing the input question, qualifiers, inferred mode, result, timestamp, and receipt identifier.[cite:21][cite:4]

### FR-6 Refinement loop

After a result renders, the user must be able to edit and resubmit the same decision without losing prior context.[cite:3]

### FR-7 Deepen path

The system must provide an explicit path to request deeper reasoning, alternatives, or Court-style escalation without cluttering the default answer surface.[cite:3]

### FR-8 Accessibility

The system must support keyboard navigation, visible focus states, ARIA attributes for chip pressed states, and mobile-safe touch targets.[cite:3]

## Non-functional requirements

- Responsive at 375px, 768px, and 1280px minimum.[cite:3]
- Perceived performance must include immediate visual acknowledgment after submit.[cite:3]
- The response contract must remain backward-compatible across UI iterations.[cite:3]
- The orchestration layer must tolerate heuristic mode selection at first and later upgrades to richer reasoning without breaking the front-end contract.[cite:3]
- Receipt storage must support later attachment of outcomes for calibration loops.[cite:21][cite:4]

## Data model

### Core entities

#### DecisionDraft

```ts
interface DecisionDraft {
  id: string;
  question: string;
  feel?: 'clear' | 'murky' | 'stuck' | 'torn';
  reversibility?: 'easy' | 'effort' | 'not_really';
  horizon?: 'today' | 'this_week' | 'this_quarter' | 'one_to_three_years';
  stakes?: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
}
```

#### CompassResponse

```ts
interface CompassResponse {
  decisionId: string;
  receiptId: string;
  mode: 'QUICK_MOVE' | 'PLAN' | 'COURT';
  trueNorth: string;
  rationale: string;
  signalSummary: string;
  weightedFactors: WeightedFactor[];
  guardrailStatus: GuardrailStatus;
  suggestedNextActions: SuggestedAction[];
  deepenOptions: DeepenOption[];
  relatedReceipts: string[];
  generatedAt: string;
}
```

#### DecisionReceipt

```ts
interface DecisionReceipt {
  receiptId: string;
  decisionId: string;
  question: string;
  qualifiers: {
    feel?: string;
    reversibility?: string;
    horizon?: string;
    stakes?: string;
  };
  inferredMode: 'QUICK_MOVE' | 'PLAN' | 'COURT';
  recommendation: string;
  rationale: string;
  signalSummary: string;
  guardrailStatus: GuardrailStatus;
  timestamp: string;
  status: 'OPEN' | 'ACTED' | 'REVIEWED' | 'SUPERSEDED';
  outcome?: ReceiptOutcome;
}
```

## API contracts

### Public endpoint

#### `POST /api/question-compass`

Creates or updates a decision and returns the current Signal response.[cite:3]

**Request**

```json
{
  "question": "Should we ship the MVP this week or wait one more sprint?",
  "feel": "murky",
  "reversibility": "easy",
  "horizon": "this_week",
  "stakes": "medium",
  "sessionId": "sess_123",
  "decisionId": null,
  "clarityMode": "SIMPLE"
}
```

**Response**

```json
{
  "decisionId": "dec_123",
  "receiptId": "rcpt_123",
  "mode": "QUICK_MOVE",
  "trueNorth": "Ship the MVP this week and learn from live signal.",
  "rationale": "The decision is somewhat murky, but the downside is reversible and the cost of waiting is rising. Real-world feedback is more valuable than another round of internal polish.",
  "signalSummary": "Murky feeling + reversible decision + short horizon favored action over delay.",
  "weightedFactors": [
    { "label": "Reversibility", "weight": "high", "direction": "act_now" },
    { "label": "Horizon", "weight": "medium", "direction": "act_now" }
  ],
  "guardrailStatus": {
    "level": "clear",
    "message": "No blocking guardrails triggered."
  },
  "suggestedNextActions": [
    { "type": "task", "label": "Define the post-ship feedback loop" },
    { "type": "task", "label": "Name the one metric that decides if the release worked" }
  ],
  "deepenOptions": [
    { "type": "court", "label": "Run Court view" },
    { "type": "alternatives", "label": "Show 3-path simulation" }
  ],
  "relatedReceipts": [],
  "generatedAt": "2026-04-21T11:45:00Z"
}
```

### Supporting endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/receipts/:receiptId` | GET | Fetch full receipt detail. |
| `/api/receipts` | GET | List receipts for the current user/session. |
| `/api/receipts/:receiptId/outcome` | POST | Attach outcome data later for calibration and review.[cite:21][cite:4] |
| `/api/question-compass/deepen` | POST | Request Court, alternatives, or simulation depth for a current decision.[cite:3] |

## Orchestration design

### Internal services

The orchestration layer should be decomposed into explicit services so Claude Code does not entangle rendering logic with reasoning logic.[cite:3]

| Service | Responsibility |
|---|---|
| `ContextClassifier` | Parses the question and qualifiers into a structured context object.[cite:3] |
| `ModeSelector` | Chooses `QUICK_MOVE`, `PLAN`, or `COURT` based on stakes, horizon, reversibility, and inferred complexity.[cite:3] |
| `ChannelRouter` | Maps the selected mode to the correct internal reasoning stack without exposing the full TV Guide to the user.[cite:3][cite:31] |
| `GuardrailEngine` | Applies Constitutional/Court-like checks when required, especially for high-stakes or low-reversibility cases.[cite:3] |
| `TrueNorthSynthesizer` | Produces the concise top-line recommendation.[cite:3] |
| `SignalFormatter` | Translates model output into the stable `CompassResponse` contract.[cite:3] |
| `ReceiptLogger` | Creates and updates Decision Receipts for each successful result.[cite:21][cite:4] |
| `ReceiptLinker` | Finds prior related receipts for continuity and calibration.[cite:4][cite:21] |

### Mode selection heuristics

Initial orchestration can be heuristic and should still be formalized.[cite:3]

Suggested v1 logic:

- `QUICK_MOVE`: short horizon + low/medium stakes + reversible decision.[cite:3]
- `PLAN`: medium horizon and/or medium stakes with meaningful execution tradeoffs.[cite:3]
- `COURT`: high stakes, identity-sensitive, low reversibility, or explicit user request for deep review.[cite:3]

## State machine

### Front-end state machine

```text
IDLE
  -> TYPING
  -> QUALIFYING
  -> READY
READY
  -> SUBMITTING
SUBMITTING
  -> LOADING
LOADING
  -> RESULT_SUCCESS
  -> RESULT_ERROR
RESULT_SUCCESS
  -> EDITING
  -> DEEPENING
  -> RESETTING
EDITING
  -> READY
DEEPENING
  -> DEEPENED_RESULT
RESETTING
  -> IDLE
RESULT_ERROR
  -> READY
```

### Behavioral notes

- `IDLE`: placeholder rotation active only when unfocused and empty.[cite:3]
- `READY`: submit CTA enabled.[cite:3]
- `LOADING`: inputs disabled, skeleton visible, loading copy rotating.[cite:3]
- `RESULT_SUCCESS`: Signal and receipt shown inline.[cite:3][cite:21] 
- `DEEPENING`: preserves the same decision object while requesting a richer response.[cite:3]
- `RESETTING`: clears active draft and returns user to an empty input state.[cite:3]

## Receipt design

### Why receipts matter

Across ARCS materials, Decision Receipts are not ornamental. They are the mechanism for ex-ante accountability, later calibration, and the replacement of optimism bias with historical learning.[cite:21][cite:4]

This means the product should not bury receipts as backend logs. It should progressively expose them as the memory substrate that makes Compass better over time.[cite:4][cite:21]

### MVP receipt surface

Each result should show a lightweight receipt strip with:

- Receipt ID.[cite:21]
- Timestamp.[cite:21]
- Inferred mode.[cite:3]
- Guardrail status.[cite:3]
- Status (`OPEN`, `ACTED`, `REVIEWED`, `SUPERSEDED`).[cite:21]
- Actions: `Open receipt`, `Mark outcome later`, `Compare with prior`.[cite:21][cite:4]

### Future receipt evolution

- Outcome capture after the fact.[cite:21]
- Estimated vs. actual reflection loops, aligning with ARCS’s emphasis on historical receipts over present feeling.[cite:4]
- Receipt clustering by domain or repeated pattern.[cite:21]
- Drift detection using repeated superseded or abandoned receipts.[cite:23][cite:4]

## Visual and interaction system

### Design direction

The existing Nexus-style dark palette is directionally correct for ARCS and supports a high-signal, low-distraction environment.[cite:3]

The design should feel like an instrument panel rather than a decorative SaaS landing page: quiet surfaces, strong typography hierarchy, one dominant action, and obvious state change when the system thinks or returns a result.[cite:3][cite:4]

### Interaction requirements

- Chips must visibly press/select and expose `aria-pressed`.[cite:3]
- Result rendering must be inline and animated, not route-gated.[cite:3]
- Loading must feel intentional and alive.[cite:3]
- Editing after answer must be frictionless.[cite:3]
- Mobile must preserve the primary CTA in full-width form.[cite:3]

## Dependency graph

### Build order

```text
Design tokens / shell / nav
  -> DecisionComposer
    -> CompassTextarea
    -> QualifierChips
    -> CompassSubmitBar
  -> ThinkingState
  -> SignalCard
    -> ModeBadge
    -> SignalFactors
    -> DeepenTray
    -> DecisionReceiptCard
  -> CompassResponse contract
    -> Orchestrator stub
      -> ContextClassifier
      -> ModeSelector
      -> GuardrailEngine
      -> TrueNorthSynthesizer
      -> SignalFormatter
      -> ReceiptLogger
  -> ReceiptTimeline
  -> Deepen endpoint
  -> DriftSentinelNotice
```

### Delivery dependencies by milestone

| Milestone | Depends on |
|---|---|
| M1 UI shell and intake | Tokens, nav, layout, DecisionComposer. |
| M2 Inline result loop | M1 plus SignalCard and loading states. |
| M3 Structured backend contract | M2 plus CompassResponse schema and orchestrator stub. |
| M4 Receipt layer | M3 plus ReceiptLogger and receipt views. |
| M5 Depth and guardrails | M4 plus deepen endpoint and guardrail orchestration. |
| M6 Drift and calibration | M5 plus receipt outcome capture and timeline logic.[cite:23][cite:4] |

## Phased implementation plan

### Phase 1 — Front-door rebuild

**Goal:** Fix the obvious product breakages and deliver a complete local interaction loop.[cite:3]

**Deliverables**

- New single-page Compass UI.[cite:3]
- Visible primary submit action.[cite:3]
- Proper chip affordances and selected states.[cite:3]
- Placeholder rotation behavior.[cite:3]
- Loading state with skeleton and rotating micro-copy.[cite:3]
- Inline Signal result card.[cite:3]

**Acceptance criteria**

- A user can submit on desktop and mobile without needing keyboard-only behavior.[cite:3]
- The page always renders a visible answer after submit.[cite:3]
- Loading is visually explicit within 100ms of submit.[cite:3]
- The result can be refined without page reload.[cite:3]

### Phase 2 — Response contract and orchestrator stub

**Goal:** Formalize the answer shape so UI and reasoning can evolve independently.[cite:3]

**Deliverables**

- Typed `CompassResponse` contract.[cite:3]
- Heuristic `ModeSelector`.[cite:3]
- Mock or local `CompassOrchestrator` returning structured payloads.[cite:3]
- Initial guardrail status field.[cite:3]

**Acceptance criteria**

- UI consumes typed response data, not ad hoc strings.[cite:3]
- Mode badge renders correctly for at least three scenarios.[cite:3]
- The system can swap mock logic for real orchestration without changing component contracts.[cite:3]

### Phase 3 — Receipts MVP

**Goal:** Make receipts a first-class product object.[cite:21][cite:4]

**Deliverables**

- Automatic receipt creation on successful result.[cite:21]
- `DecisionReceiptCard` in the result surface.[cite:21]
- Receipts list view.[cite:21]
- Receipt detail page or drawer.[cite:21]

**Acceptance criteria**

- Every successful answer produces a receipt ID.[cite:21]
- A prior receipt can be reopened and understood without the original chat/session context.[cite:21][cite:4]
- Receipt metadata includes question, qualifiers, mode, recommendation, timestamp, and status.[cite:21]

### Phase 4 — Deepen paths and Court escalation

**Goal:** Preserve simplicity while allowing high-stakes analysis to unfold when needed.[cite:3]

**Deliverables**

- “Go deeper” action tray.[cite:3]
- Court path for high-stakes decisions.[cite:3]
- Alternatives / simulation view.[cite:3]
- Clear explanation when a guardrail escalates or blocks a path.[cite:3]

**Acceptance criteria**

- Deepening reuses the current decision object rather than starting over.[cite:3]
- High-stakes, low-reversibility cases can trigger Court mode automatically.[cite:3]
- A blocked recommendation explains why in plain language.[cite:3]

### Phase 5 — Drift and calibration loop

**Goal:** Move from one-shot answers to operating-system behavior over time.[cite:23][cite:4]

**Deliverables**

- Receipt outcome capture.[cite:21][cite:4]
- Receipt timeline and related receipt linking.[cite:4][cite:21]
- Drift Sentinel prompts when repeated refinement is not producing progress.[cite:23]
- Expected-vs-actual review moments.[cite:4]

**Acceptance criteria**

- Users can mark what happened after acting on a receipt.[cite:21]
- The system can surface related prior decisions.[cite:4]
- Drift detection offers a concrete landing action, not just a warning.[cite:23]

## Acceptance criteria

### Product acceptance

- The Compass must answer the user’s question on the same surface where it is asked.[cite:3]
- The user must understand what to do next within one screen of the result.[cite:3]
- The answer must feel like a recommendation, not a navigation instruction.[cite:3]
- Receipts must exist as reusable artifacts, not hidden telemetry.[cite:21][cite:4]

### UX acceptance

- Mobile submission path works cleanly at 375px.[cite:3]
- Every interactive control has visible affordance and selected state.[cite:3]
- Loading, success, edit, clear, and reset states are all explicit.[cite:3]
- The system retains calm visual hierarchy and avoids decorative clutter.[cite:3]

### Engineering acceptance

- UI components consume typed models rather than freeform result strings.[cite:3]
- State transitions are implemented explicitly and testably.[cite:3]
- Orchestration is isolated from rendering logic.[cite:3]
- Receipt persistence is introduced before deep analytics.[cite:21]

## Risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Over-exposing ARCS lore | Front-door UX becomes cognitively heavy.[cite:3] | Keep expert architecture backstage and expose only mode/result/receipt by default.[cite:3] |
| Replacing one black box with another | Simplicity can drift into opaque paternalism.[cite:3] | Show concise weighted factors and guardrail explanations; preserve deepen/override paths.[cite:3] |
| UI-first implementation without product contract | Leads to brittle rewrites later.[cite:3] | Define `CompassResponse` and receipt models before backend complexity expands.[cite:3] |
| Receipt layer postponed too long | Loses ARCS’s accountability advantage.[cite:21][cite:4] | Make receipt generation part of the MVP, not a later analytics add-on.[cite:21] |
| Mobile neglected again | Recreates the most obvious current failure.[cite:3] | Treat mobile CTA and touch flow as a launch blocker.[cite:3] |

## Engineering recommendations for Claude Code

- Build the UI against typed mock data first, not direct model strings.[cite:3]
- Treat `QuestionCompassPage` as the façade and keep orchestration behind a service boundary.[cite:3]
- Introduce the receipt schema as early as the response schema, because both are foundational contracts.[cite:21]
- Implement explicit finite states for idle, ready, loading, success, error, deepen, and reset.[cite:3]
- Keep the default answer compact and stable; deeper modes should add explanatory layers without destabilizing the top recommendation unnecessarily.[cite:3][cite:23]

## Recommended repository structure

```text
/apps/arcs-web
  /src
    /pages
      QuestionCompassPage.tsx
      SignalPage.tsx
      ReceiptsPage.tsx
    /components
      DecisionComposer.tsx
      CompassTextarea.tsx
      QualifierChips.tsx
      CompassSubmitBar.tsx
      ThinkingState.tsx
      SignalCard.tsx
      ModeBadge.tsx
      SignalFactors.tsx
      DecisionReceiptCard.tsx
      DeepenTray.tsx
      ReceiptTimeline.tsx
      DriftSentinelNotice.tsx
    /lib
      api.ts
      state-machine.ts
      heuristics.ts
    /services
      compass-orchestrator.ts
      context-classifier.ts
      mode-selector.ts
      channel-router.ts
      guardrail-engine.ts
      true-north-synthesizer.ts
      signal-formatter.ts
      receipt-logger.ts
      receipt-linker.ts
    /types
      compass.ts
      receipts.ts
```

## Final directive

The implementation should optimize for semantic velocity and low cognitive mass: one simple intake, one visible next move, one durable receipt, and deeper ARCS machinery only when necessary.[cite:23][cite:3]

If Claude Code has to make tradeoffs, it should favor a complete front-door decision loop with typed response and receipt contracts over decorative polish or premature expansion into expert-mode surfaces.[cite:3][cite:21]
