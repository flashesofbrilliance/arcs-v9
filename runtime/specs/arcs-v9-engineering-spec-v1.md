# ARCS v9 Engineering Spec

## Purpose

This document defines a production-grade implementation spec for the ARCS v9 decision system: Question Compass, optional Prep enrichment, Decision Receipt persistence, Brief and Guide retrieval, and Receipt History. It is designed to be pasted into a coding agent with minimal token overhead and maximum implementation clarity.[file:2][file:3][file:21]

## Product Goal

ARCS v9 should expose a single, simple front door where a user states what they are trying to decide, selects horizon and stakes, and receives one clear next move plus a durable Decision Receipt that can be revisited later.[file:2][file:3]

The visible experience should default to SIMPLE clarity mode, with RICH and DEEP acting as presentation layers over the same underlying reasoning pipeline rather than separate decision engines.[file:2][file:3]

## Canonical User Flow

The intended flow is:

1. Question Compass
2. Optional Prep enrichment
3. Decision Receipt creation
4. Brief view
5. Guide view
6. Receipt History

This matches the conceptual architecture already described in the ARCS materials, where Question Compass is the front door, Prep enriches a decision, Brief and Guide are receipt-based views, and receipts serve as durable artifacts for retrieval and longitudinal learning.[file:2][file:3][file:21]

## Product Surfaces

| Surface | Route | Purpose | Notes |
|---|---|---|---|
| Question Compass | `/question-compass` | Primary decision intake | One question field, horizon, stakes, submit.[file:2][file:3] |
| Prep | `/prep` | Optional enrichment | Adds constraints, options, fears, non-negotiables to an existing decision.[file:3] |
| Brief | `/brief/[receiptId]` | Canonical receipt artifact | Compact, human-readable decision summary.[file:3][file:21] |
| Guide | `/guide/[receiptId]` | Deeper operational detail | Risk, assumptions, scenarios, blocked actions.[file:2][file:3] |
| Receipt History | `/receipts` | Archive and retrieval | Reverse-chronological list of prior receipts; currently the missing bridge.[file:3] |

## Design Principles

### Clarity before Curvature

The system should run high-dimensional checks internally while surfacing the minimum useful complexity externally. SIMPLE should be the default; RICH and DEEP are opt-in or stakes-triggered presentation layers.[file:2][file:3]

### Stable Recommendation

The top-line True North recommendation must remain consistent across SIMPLE, RICH, and DEEP. Deeper modes may add rationale, uncertainty, tradeoffs, or dissent, but must not silently reverse the recommendation.[file:2][file:3]

### Durable Artifacts over Ephemeral State

The source of truth is the persisted Decision Receipt, not session-only chat or frontend storage. Frontend session state can improve UX, but production retrieval must flow through the receipt API.[file:3][file:21]

## Functional Requirements

### Question Compass

- Accepts: `question`, `horizon`, `stakes`, optional `clarity_mode`, optional `jtbd`, optional `prep_context`.
- Returns: `receipt_id`, `true_north`, `why_bullets`, `decision_mode`, `clarity_mode`, `drift_state`, and links to Brief and Guide.[file:2][file:3]

### Prep

- Attaches context to an existing receipt or pre-receipt session.
- Must not create a separate decision artifact.
- Should support constraints, fears, considered options, non-negotiables, people affected, and freeform notes.[file:3]

### Brief

- Must render the canonical human-readable decision artifact.
- Should include question, True North, why bullets, horizon, stakes, mode, timestamp, and follow-up metadata.[file:3][file:21]

### Guide

- Must expose deeper operational structure.
- Should include assumptions, tradeoffs, risks, allowed actions, blocked actions, and scenario notes.[file:2][file:3]

### Receipt History

- Must list prior receipts in reverse chronological order.
- Each row or card must link to Brief and Guide.
- Should include question, timestamp, horizon, stakes, and mode.[file:3]

## Non-Functional Requirements

- Python 3.12.
- FastAPI for HTTP layer.
- Pydantic v2 for schema validation.
- SQLAlchemy 2.0 async ORM.
- Alembic for migrations.
- Postgres in production, SQLite allowed for local development.
- Deterministic output contracts even if internal reasoning is heuristic or model-assisted.
- Full unit and integration test coverage for API contracts and decision stability.[file:21][file:2][file:3]

## Architecture

### Recommended Shape

Implement as a modular FastAPI monolith with explicit service boundaries. This keeps development simple now while preserving an easy path to later extraction if a specific component needs to become its own service.[file:3]

### Internal Pipeline

The orchestration pipeline should be:

1. Normalize input
2. Classify context
3. Select decision mode
4. Compute macro tags
5. Apply guardrails
6. Synthesize True North
7. Persist receipt
8. Render clarity-mode-specific payload

This pipeline directly matches the internal sequence already described in the ARCS notes: classify context, select mode, route internal channels, run reasoners, apply guardrails, synthesize True North, and log a Decision Receipt.[file:3][file:2]

## Repository Structure

```text
app/
  api/
    routes/
      compass.py
      receipts.py
      brief.py
      guide.py
      prep.py
      health.py
  core/
    config.py
    logging.py
    errors.py
  domain/
    enums.py
    models.py
    value_objects.py
  services/
    compass_service.py
    context_classifier.py
    mode_selector.py
    macro_engine.py
    drift_sentinel.py
    court_guardrails.py
    synthesis_engine.py
    receipt_service.py
    brief_service.py
    guide_service.py
  repositories/
    receipt_repository.py
    session_repository.py
  db/
    base.py
    tables.py
    migrations/
  tests/
    unit/
    integration/
main.py
```

## Domain Enums

```python
from enum import Enum

class Horizon(str, Enum):
    TODAY = "today"
    THIS_WEEK = "this_week"
    THIS_QUARTER = "this_quarter"
    ONE_TO_THREE_YEARS = "one_to_three_years"

class Stakes(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AUTO = "auto"

class ClarityMode(str, Enum):
    SIMPLE = "simple"
    RICH = "rich"
    DEEP = "deep"

class DecisionMode(str, Enum):
    QUICKMOVE = "quickmove"
    PLAN = "plan"
    COURT = "court"

class DriftState(str, Enum):
    ONTRACK = "ontrack"
    USEFUL_TANGENT = "useful_tangent"
    DERAILMENT = "derailment"

class ReceiptStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW_DUE = "review_due"
    CLOSED = "closed"

class MacroTag(str, Enum):
    FATED = "fated"
    HCI_PCI = "hci_pci"
    KKL = "kkl"
    BAR = "bar"
    LAB = "lab"
    TAD = "tad"
    CUR = "cur"
    ALC = "alc"
```

These enums reflect the visible clarity modes, decision modes, drift state, and macro vocabulary already defined in the Field OS and v9 notes.[file:2][file:3]

## Pydantic Models

### Request Models

```python
from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

class PrepContext(BaseModel):
    constraints: List[str] = []
    fears: List[str] = []
    considered_options: List[str] = []
    non_negotiables: List[str] = []
    people_affected: List[str] = []
    notes: Optional[str] = None

class DecisionRequest(BaseModel):
    user_id: str
    question: str = Field(min_length=5, max_length=2000)
    horizon: Horizon
    stakes: Stakes
    clarity_mode: ClarityMode = ClarityMode.SIMPLE
    jtbd: Optional[str] = None
    prep_context: Optional[PrepContext] = None
    session_id: Optional[str] = None

class PrepUpdateRequest(BaseModel):
    receipt_id: str
    prep_context: PrepContext
```

### Core Response Models

```python
class CompassResponse(BaseModel):
    receipt_id: str
    true_north: str
    why_bullets: list[str]
    decision_mode: DecisionMode
    clarity_mode: ClarityMode
    drift_state: DriftState
    links: dict[str, str]

class ReceiptListItem(BaseModel):
    receipt_id: str
    question: str
    created_at: datetime
    horizon: Horizon
    stakes: Stakes
    decision_mode: DecisionMode
    clarity_mode: ClarityMode
    status: ReceiptStatus
    true_north: str
```

### Canonical Receipt Model

```python
class DecisionReceipt(BaseModel):
    receipt_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    question: str
    normalized_question: str
    horizon: Horizon
    stakes: Stakes
    clarity_mode: ClarityMode
    decision_mode: DecisionMode
    drift_state: DriftState
    status: ReceiptStatus
    true_north: str
    why_bullets: list[str]
    summary: str | None = None
    prep_context: PrepContext | None = None
    assumptions: list[str] = []
    tradeoffs: list[str] = []
    risks: list[str] = []
    blocked_actions: list[str] = []
    allowed_actions: list[str] = []
    macro_tags: list[MacroTag] = []
    review_on: date | None = None
    metadata: Dict[str, Any] = {}
```

This structure expresses the Decision Receipt as a durable decision artifact with rationale, time context, risk framing, and future review hooks, which is consistent with the broader ARCS receipt concept.[file:21][file:2]

## SQLAlchemy Schema

```python
from sqlalchemy import String, DateTime, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class ReceiptTable(Base):
    __tablename__ = "receipts"

    receipt_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_question: Mapped[str] = mapped_column(Text, nullable=False)
    horizon: Mapped[Horizon] = mapped_column(SAEnum(Horizon), nullable=False)
    stakes: Mapped[Stakes] = mapped_column(SAEnum(Stakes), nullable=False)
    clarity_mode: Mapped[ClarityMode] = mapped_column(SAEnum(ClarityMode), nullable=False)
    decision_mode: Mapped[DecisionMode] = mapped_column(SAEnum(DecisionMode), nullable=False)
    drift_state: Mapped[DriftState] = mapped_column(SAEnum(DriftState), nullable=False)
    status: Mapped[ReceiptStatus] = mapped_column(SAEnum(ReceiptStatus), nullable=False)
    true_north: Mapped[str] = mapped_column(Text, nullable=False)
    why_bullets: Mapped[dict] = mapped_column(JSON, nullable=False)
    prep_context: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    assumptions: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    tradeoffs: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    risks: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    blocked_actions: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    allowed_actions: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    macro_tags: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    review_on: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
```

## Services

### `context_classifier`

Responsibilities:
- Normalize question text.
- Infer decision type.
- Infer irreversibility score.
- Infer altitude or complexity class.
- Attach contextual hints for macro evaluation.[file:3][file:2]

### `mode_selector`

Responsibilities:
- Map low-stakes, reversible, short-horizon decisions to `QUICKMOVE`.
- Map medium complexity to `PLAN`.
- Escalate high-stakes, high-irreversibility, or identity-conflict decisions to `COURT`.[file:3][file:2]

### `macro_engine`

Responsibilities:
- Produce machine-readable macro outputs for FATED, HCI/PCI, KKL, BAR, LAB, TAD, and optional CUR/ALC.
- Keep macro computation internal by default.
- Only expose compact summaries unless clarity mode or UX explicitly requests more detail.[file:3][file:2]

### `court_guardrails`

Responsibilities:
- Enforce user-authored non-negotiables.
- Block ruin-risk recommendations.
- Downgrade or reshape recommendations that violate autonomy, energy, or relationship coherence.[file:2][file:3]

### `drift_sentinel`

Responsibilities:
- Compare incoming question or thread state against JTBD.
- Set drift state to `ONTRACK`, `USEFUL_TANGENT`, or `DERAILMENT`.
- Generate a land-the-plane prompt when threshold is crossed.[file:2][file:3]

### `synthesis_engine`

Responsibilities:
- Generate one stable True North.
- Generate one to three why bullets.
- Expand output structure for RICH and DEEP without changing the top-line recommendation.[file:2][file:3]

### `receipt_service`

Responsibilities:
- Create receipts.
- Update receipts with prep context and status changes.
- Retrieve raw receipt by ID.
- List receipts for history.
- Support future audit and regret-analysis extensions.[file:21][file:3]

### `brief_service`

Responsibilities:
- Render a compact artifact payload optimized for the Brief page.

### `guide_service`

Responsibilities:
- Render a deeper payload optimized for the Guide page.

## API Contract

### `POST /api/compass`

Primary decision endpoint.

#### Request

```json
{
  "user_id": "user-123",
  "question": "Should I accept this offer or keep building ARCS full-time?",
  "horizon": "one_to_three_years",
  "stakes": "high",
  "clarity_mode": "simple",
  "jtbd": "Decide next 90-day operating posture",
  "prep_context": {
    "constraints": ["Need cashflow within 60 days"],
    "fears": ["Losing momentum on ARCS"],
    "considered_options": ["Take offer", "Go all in", "Hybrid"],
    "non_negotiables": ["Protect autonomy"],
    "people_affected": ["Partner"],
    "notes": "I am biased toward total commitment plays."
  }
}
```

#### Response

```json
{
  "receipt_id": "dr_20260421_8f3a2c",
  "true_north": "Run a hybrid phase for 90 days instead of making an all-in commitment today.",
  "why_bullets": [
    "It protects cashflow without abandoning the core bet.",
    "It avoids a high-irreversibility move under uncertainty.",
    "It creates evidence you can review in one quarter."
  ],
  "decision_mode": "court",
  "clarity_mode": "simple",
  "drift_state": "ontrack",
  "links": {
    "brief": "/api/brief/dr_20260421_8f3a2c",
    "guide": "/api/guide/dr_20260421_8f3a2c"
  }
}
```

This single-endpoint orchestration pattern matches the design already described in the ARCS notes.[file:3][file:2]

### `POST /api/prep`

Attach or update Prep context for an existing receipt.

#### Request

```json
{
  "receipt_id": "dr_20260421_8f3a2c",
  "prep_context": {
    "constraints": ["Need cashflow within 60 days"],
    "fears": ["Regretting a half-measure"],
    "considered_options": ["Hybrid", "All-in", "Accept offer"],
    "non_negotiables": ["No full-time lock-in longer than 12 months"]
  }
}
```

#### Response

```json
{
  "receipt_id": "dr_20260421_8f3a2c",
  "updated": true,
  "recompute_recommended": true
}
```

### `GET /api/brief/{receipt_id}`

Returns the compact artifact for the Brief page.

#### Response shape

```json
{
  "receipt_id": "dr_20260421_8f3a2c",
  "question": "Should I accept this offer or keep building ARCS full-time?",
  "true_north": "Run a hybrid phase for 90 days instead of making an all-in commitment today.",
  "why_bullets": [
    "It protects cashflow without abandoning the core bet.",
    "It avoids a high-irreversibility move under uncertainty.",
    "It creates evidence you can review in one quarter."
  ],
  "horizon": "one_to_three_years",
  "stakes": "high",
  "decision_mode": "court",
  "created_at": "2026-04-21T11:20:00Z",
  "review_on": "2026-07-21"
}
```

### `GET /api/guide/{receipt_id}`

Returns deeper structured detail for the Guide page.

#### Response shape

```json
{
  "receipt_id": "dr_20260421_8f3a2c",
  "assumptions": ["ARCS can still progress in a hybrid mode"],
  "tradeoffs": ["Less speed on ARCS in exchange for lower financial pressure"],
  "risks": ["Hybrid mode may drift without time-boxing"],
  "allowed_actions": ["Take a fixed-duration role", "Time-box ARCS build"],
  "blocked_actions": ["Unbounded full-time lock-in"],
  "macro_tags": ["bar", "kkl", "lab", "tad"],
  "notes": "Deeper rationale payload"
}
```

### `GET /api/receipts`

Returns reverse-chronological receipt history.

#### Response shape

```json
[
  {
    "receipt_id": "dr_20260421_8f3a2c",
    "question": "Should I accept this offer or keep building ARCS full-time?",
    "created_at": "2026-04-21T11:20:00Z",
    "horizon": "one_to_three_years",
    "stakes": "high",
    "decision_mode": "court",
    "clarity_mode": "simple",
    "status": "open",
    "true_north": "Run a hybrid phase for 90 days instead of making an all-in commitment today."
  }
]
```

This endpoint is the backend half of the missing Receipt History bridge identified in the current product architecture.[file:3]

### `GET /api/receipts/{receipt_id}`

Returns the full canonical receipt object for admin, export, and debugging use.

### `GET /api/health`

Returns a simple liveness response.

## Decision Logic Rules

### Mode Selection

- `QUICKMOVE`: low stakes, high reversibility, short horizon.[file:3][file:2]
- `PLAN`: medium stakes or moderate complexity.[file:3][file:2]
- `COURT`: high stakes, high irreversibility, identity-level conflict, or ruin-risk.[file:3][file:2]

### Clarity Modes

- `SIMPLE`: True North plus up to three why bullets.[file:2]
- `RICH`: same answer plus short context or a small table.[file:2][file:3]
- `DEEP`: same answer plus exposed reasoning layers, dissent, and guardrails.[file:2][file:3]

### Stability Rule

The True North recommendation must remain constant across clarity modes for the same receipt unless the receipt itself is materially updated by new prep or changed inputs.[file:2][file:3]

## Drift Sentinel Rules

- Every focused session may optionally include a JTBD anchor.
- Drift state is evaluated relative to that JTBD.
- If drift threshold is crossed, return a land-the-plane suggestion in a machine-readable field or UI hint.
- Drift output must remain concise in SIMPLE mode.[file:2][file:3]

Suggested optional field:

```json
{
  "drift_hint": {
    "state": "useful_tangent",
    "message": "You've drifted from the original JTBD. Land the plane or keep exploring?",
    "recommended_next_prompt": "Summarize what we have into one v9 artifact and list the top 3 next actions."
  }
}
```

## Frontend Integration Notes

The current frontend lives in a separate Next.js worktree and already contains Question Compass, Prep, and dynamic Brief routes. The implementation should preserve that structure while replacing session-only assumptions with receipt-backed retrieval as the production source of truth.[file:3]

### Required Frontend Pages

- `/question-compass`
- `/prep`
- `/brief/[receiptId]`
- `/guide/[receiptId]`
- `/receipts`[file:3]

### Navigation Rules

- After successful `POST /api/compass`, route to `/brief/[receiptId]`.
- Prep updates should preserve the same `receiptId`.
- Receipt History should fetch `GET /api/receipts`.
- Brief page should expose links to Guide and History.[file:3]

## Implementation Skeleton

### `main.py`

```python
from fastapi import FastAPI
from app.api.routes import compass, receipts, brief, guide, prep, health

app = FastAPI(title="ARCS API", version="0.9.0")

app.include_router(health.router, prefix="/api")
app.include_router(compass.router, prefix="/api")
app.include_router(prep.router, prefix="/api")
app.include_router(receipts.router, prefix="/api")
app.include_router(brief.router, prefix="/api")
app.include_router(guide.router, prefix="/api")
```

### `api/routes/compass.py`

```python
from fastapi import APIRouter, Depends
from app.domain.models import DecisionRequest, CompassResponse
from app.services.compass_service import CompassService, get_compass_service

router = APIRouter(tags=["compass"])

@router.post("/compass", response_model=CompassResponse)
async def run_compass(
    payload: DecisionRequest,
    service: CompassService = Depends(get_compass_service),
) -> CompassResponse:
    return await service.run(payload)
```

### `services/compass_service.py`

```python
class CompassService:
    def __init__(
        self,
        classifier,
        mode_selector,
        macro_engine,
        court_guardrails,
        synthesis_engine,
        receipt_service,
        drift_sentinel,
    ):
        self.classifier = classifier
        self.mode_selector = mode_selector
        self.macro_engine = macro_engine
        self.court_guardrails = court_guardrails
        self.synthesis_engine = synthesis_engine
        self.receipt_service = receipt_service
        self.drift_sentinel = drift_sentinel

    async def run(self, req):
        context = await self.classifier.classify(req)
        decision_mode = self.mode_selector.select(context)
        macros = self.macro_engine.evaluate(context, req)
        drift = self.drift_sentinel.evaluate(req.jtbd, req.question)
        guarded = self.court_guardrails.apply(context, macros, req)
        answer = self.synthesis_engine.synthesize(
            req=req,
            context=context,
            decision_mode=decision_mode,
            macros=macros,
            guarded=guarded,
            drift=drift,
        )
        receipt = await self.receipt_service.create(
            req=req,
            context=context,
            decision_mode=decision_mode,
            macros=macros,
            drift=drift,
            answer=answer,
        )
        return CompassResponse(
            receipt_id=receipt.receipt_id,
            true_north=receipt.true_north,
            why_bullets=receipt.why_bullets,
            decision_mode=receipt.decision_mode,
            clarity_mode=receipt.clarity_mode,
            drift_state=receipt.drift_state,
            links={
                "brief": f"/api/brief/{receipt.receipt_id}",
                "guide": f"/api/guide/{receipt.receipt_id}",
            },
        )
```

## Acceptance Criteria

### API

- `POST /api/compass` validates input and returns a stable response shape.
- Every successful compass call creates a persisted receipt.
- `POST /api/prep` updates an existing receipt rather than creating a new one.
- `GET /api/brief/{id}` returns a compact artifact payload.
- `GET /api/guide/{id}` returns deeper detail.
- `GET /api/receipts` returns reverse-chronological history.
- `GET /api/receipts/{id}` returns full canonical receipt.
- `GET /api/health` returns status 200.

### Product Behavior

- SIMPLE is default clarity mode.[file:2]
- True North remains stable across SIMPLE, RICH, and DEEP for the same receipt.[file:2][file:3]
- Prep enriches an existing decision rather than forking product state.[file:3]
- Receipt History is reachable from Brief and from the main nav.[file:3]

### Persistence

- Receipts survive server restarts.
- Timestamps are timezone-aware UTC.
- Receipts can be listed by user and retrieved by `receipt_id`.
- Schema supports later addition of review outcomes and regret-analysis fields.[file:21]

### Testing

- Unit tests cover classifier, mode selector, guardrails, synthesis stability, and receipt service.
- Integration tests cover all HTTP endpoints.
- Golden tests verify identical True North across clarity modes for fixed fixtures.[file:2][file:3]

## Test Plan

### Unit Tests

- `test_mode_selector_quickmove()`
- `test_mode_selector_court_on_high_irreversibility()`
- `test_guardrails_block_ruin_risk()`
- `test_synthesis_true_north_stable_across_modes()`
- `test_receipt_service_persists_receipt()`

### Integration Tests

- `test_post_compass_creates_receipt()`
- `test_post_prep_updates_existing_receipt()`
- `test_get_brief_returns_expected_payload()`
- `test_get_guide_returns_expected_payload()`
- `test_get_receipts_returns_reverse_chronological_order()`

### Golden Fixtures

Create 15 to 20 canonical decision examples across:
- low-stakes tactical
- medium-stakes planning
- high-stakes identity or career
- high irreversibility / ruin risk
- prep-enriched vs non-prepped

This is important because the existing ARCS rules explicitly require stable output shape and stable top-line recommendation across clarity modes.[file:2][file:3]

## Migration Plan

### Phase 1

- Build core models and enums.
- Implement `POST /api/compass` with deterministic stub internals.
- Persist receipts.
- Implement `GET /api/receipts` and `GET /api/brief/{id}`.

### Phase 2

- Implement `POST /api/prep`.
- Implement `GET /api/guide/{id}`.
- Add receipt status transitions.

### Phase 3

- Add richer macro internals.
- Add drift hints.
- Add review outcomes and audit support.

This sequence minimizes implementation risk while delivering the missing product connective tissue early, especially Receipt History and durable receipt retrieval.[file:3]

## Coding-Agent Prompt

```text
Build a production-grade FastAPI backend for ARCS v9 using Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Alembic, and Postgres.

Goal:
Implement the ARCS Question Compass flow with persisted Decision Receipts and retrieval endpoints.

Product constraints:
- One front door: Question Compass.
- Inputs: question, horizon, stakes, optional clarity_mode, optional jtbd, optional prep_context.
- Outputs: stable True North, up to 3 why bullets, decision_mode, clarity_mode, receipt_id.
- Clarity modes SIMPLE/RICH/DEEP are presentation filters only. The top-line recommendation must remain stable across all modes.
- Internal decision modes: QUICKMOVE / PLAN / COURT.
- Persist all decisions as Decision Receipts.
- Support Brief view, Guide view, and Receipt History.
- Prep enriches an existing receipt; it does not create a separate decision artifact.

Build these endpoints:
- POST /api/compass
- POST /api/prep
- GET /api/brief/{receipt_id}
- GET /api/guide/{receipt_id}
- GET /api/receipts
- GET /api/receipts/{receipt_id}
- GET /api/health

Implementation requirements:
- Use explicit domain models and enums.
- Use service layer + repository layer.
- Add migrations.
- Add unit and integration tests.
- Keep reasoning internals modular: context_classifier, mode_selector, macro_engine, court_guardrails, synthesis_engine, drift_sentinel, receipt_service.
- If reasoning is heuristic at first, keep API contracts stable and deterministic.
- Include example seed data and a README with run commands.
- Optimize for maintainability, not cleverness.
```

## True North

Build the backend around persisted Decision Receipts as the core artifact, then wire Brief, Guide, and Receipt History around that durable object model. That is the shortest path from current ARCS concept and partial UI wiring to a production-grade system with stable contracts and room for deeper intelligence later.[file:3][file:2][file:21]
