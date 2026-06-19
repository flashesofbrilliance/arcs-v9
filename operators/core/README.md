---
name: core-operators-foundation-layer
description: Foundational operator components — atomic decision primitives and infrastructure
version: 1.0.0
category: operators/foundation
---

# ARCS Core Operators — Foundation Layer (v1.0.0)

The foundation layer contains the **atomic decision primitives** and **infrastructure patterns** that all higher-level operators depend on. This is Layer 1 in the three-tier ARCS operator architecture.

## Architecture

```
Layer 1: Foundation (core/)          ← YOU ARE HERE
  ├── atoms.py                       ← Primitive data structures
  ├── virtue_atoms.py                ← Virtue-encoded atoms
  ├── operators.py                   ← Base operator patterns
  ├── virtue_operators.py            ← Virtue-encoded operators
  ├── governance.py                  ← Cross-layer governance rules
  └── vector_engine.py               ← Vector/tensor operations
        │
        ↓
Layer 2: Decision Operators (../)    ← LAB, BAR, SAGE, CURATOR, etc.
        │
        ↓
Layer 3: Application (compass route) ← Calls Layer 2; optionally Layer 1
```

## Component Descriptions

### Core Data Structures

**`atoms.py`** (5.1KB)
- Primitive data types used across all operator layers
- Role: Define immutable, validated atomic values
- Used by: All operators (Layer 2+)
- Import: `from core.atoms import ...`

**`virtue_atoms.py`** (5.2KB)
- Virtue-encoded variants of atoms (adds constraint/ethical metadata)
- Role: Add declarative constraints to primitive values
- Used by: Constitutional operators, governance checks
- Import: `from core.virtue_atoms import ...`

### Operator Patterns

**`operators.py`** (13KB)
- Base operator class definitions and execution patterns
- Role: Define operator interface (input → process → output)
- Key patterns: `BaseOperator`, execution model, error handling
- Used by: All decision operators (Layer 2)
- Import: `from core.operators import BaseOperator`

**`virtue_operators.py`** (4.3KB)
- Operator variants with built-in virtue checks
- Role: Enforce ethical/constitutional guardrails at execution time
- Used by: Restricted operators (COURT, SAGE, CURATOR)
- Import: `from core.virtue_operators import VirtueOperator`

### Cross-Layer Governance

**`governance.py`** (3.4KB)
- Shared governance rules and policy enforcement
- Role: Centralized authority for layer-to-layer communication
- Key rules: Operator priority, resource allocation, escalation
- Used by: All layers (Layer 2 consults before execution)
- Import: `from core.governance import EnforcePolicy`

### Computation Layer

**`vector_engine.py`** (5.2KB)
- Vector/tensor operations for numerical reasoning
- Role: Linear algebra and manifold operations
- Used by: LTE, Kairos, coherence operators
- Import: `from core.vector_engine import VectorSpace`

## Integration Points

### From Layer 2 (Decision Operators)
```python
from core.atoms import Coordinate, Phase
from core.operators import BaseOperator
from core.governance import EnforcePolicy

class MyDecisionOperator(BaseOperator):
    def execute(self, input_atom: Coordinate) -> Phase:
        EnforcePolicy("MY_DECISION_DOMAIN")  # Check governance
        # ... process ...
        return Phase(...)
```

### From Layer 3 (Application)
When the compass route needs direct foundation access (rare):
```python
from operators.core.vector_engine import VectorSpace
from operators.core.governance import EnforcePolicy

# Use foundation layer directly (bypass Layer 2)
# Only for low-level numerical operations or emergency governance checks
```

## Cross-Repo Validation

The following ADRs expect these files to exist and validate correctly:

| ADR | Expectation | Status |
|-----|-------------|--------|
| ADR-023 | Operators library exists with atomic primitives | ✅ |
| ADR-020 | `core/` layer is complementary, not redundant | ✅ |
| ADR-019 | `governance.py` enforces constitutional rules | ✅ |
| ADR-018 | Vector engine supports manifold operations | ✅ |

## Design Principles

1. **Immutability** — atoms and data structures do not mutate after creation
2. **Validation** — all inputs checked at layer boundaries
3. **Governance First** — policy enforcement before execution
4. **Composability** — foundation layer is orthogonal; operators combine freely
5. **Auditability** — all decisions traceable to an atom origin

## Next Steps

- Use Layer 2 operators (LAB, BAR, SAGE) for high-level decision logic
- Consult `operators/README.md` for the full operator taxonomy
- See `arcs_core.py` in `scripts/` for end-to-end execution examples
