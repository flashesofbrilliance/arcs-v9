"""
arcs_operator_contract.py
ARCS v9 — Formal Operator Contract (Phase 6 rewrite)

Dual-pattern:
  - abc.ABC  (nominal / inheritance surface)
  - typing.Protocol + @runtime_checkable  (structural / duck-typing surface)

Every operator must implement:
  name      (str property)
  version   (str property)
  process(signal: dict) -> dict
  validate(signal: dict) -> bool
  describe() -> str

Prior Phase 4 contract (ARCSOperatorContract / analyze()) is preserved below
as a legacy compatibility alias so existing operators do not break.
"""

from __future__ import annotations

import abc
import functools
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class ContractViolation(Exception):
    """Raised when an operator fails contract compliance checks."""


# ---------------------------------------------------------------------------
# Protocol  (structural — duck-typing / @runtime_checkable)
# ---------------------------------------------------------------------------

@runtime_checkable
class OperatorProtocol(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def process(self, signal: dict) -> dict: ...

    def validate(self, signal: dict) -> bool: ...

    def describe(self) -> str: ...


# ---------------------------------------------------------------------------
# Abstract base class  (nominal — inheritance)
# ---------------------------------------------------------------------------

class ARCSOperator(abc.ABC):
    """Base class for all ARCS v9 operators (Phase 6+)."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique operator name (e.g. 'SAGE', 'LAB')."""

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Semantic version string (e.g. '1.0.0')."""

    @abc.abstractmethod
    def process(self, signal: dict) -> dict:
        """Run the operator on a signal dict; return enriched dict."""

    @abc.abstractmethod
    def validate(self, signal: dict) -> bool:
        """Return True if the signal satisfies operator pre-conditions."""

    @abc.abstractmethod
    def describe(self) -> str:
        """Return a human-readable one-line description of this operator."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} version={self.version!r}>"


# ---------------------------------------------------------------------------
# Contract validation
# ---------------------------------------------------------------------------

_REQUIRED_PROPERTIES = ("name", "version")
_REQUIRED_METHODS    = ("process", "validate", "describe")


def validate_operator(op: object) -> None:
    """
    Verify that *op* satisfies the full OperatorProtocol.
    Raises ContractViolation with a specific message on the first failure found.
    """
    for prop in _REQUIRED_PROPERTIES:
        if not hasattr(op, prop):
            raise ContractViolation(
                f"Operator {op!r} is missing required property '{prop}'."
            )
        value = getattr(op, prop, None)
        if value is None:
            raise ContractViolation(
                f"Operator {op!r} property '{prop}' returned None."
            )
        if not isinstance(value, str):
            raise ContractViolation(
                f"Operator {op!r} property '{prop}' must be str, got {type(value).__name__}."
            )
        if not value.strip():
            raise ContractViolation(
                f"Operator {op!r} property '{prop}' must not be empty."
            )

    for method in _REQUIRED_METHODS:
        if not callable(getattr(op, method, None)):
            raise ContractViolation(
                f"Operator {op!r} is missing required callable '{method}'."
            )

    if not isinstance(op, OperatorProtocol):
        raise ContractViolation(
            f"Operator {op!r} does not satisfy OperatorProtocol structural check."
        )


# ---------------------------------------------------------------------------
# Decorator — enforces contract at instantiation time
# ---------------------------------------------------------------------------

def operator_contract(cls):
    """
    Class decorator that runs validate_operator() immediately after __init__.
    Any contract violation raises ContractViolation before the instance escapes.
    """
    original_init = cls.__init__

    @functools.wraps(original_init)
    def checked_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        validate_operator(self)

    cls.__init__ = checked_init
    return cls


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

REGISTERED_OPERATORS: dict[str, ARCSOperator] = {}


def register_operator(op: ARCSOperator) -> None:
    """
    Validate and register an operator instance by name.
    Raises ContractViolation if the contract is not satisfied.
    Re-registration of the same name overwrites the previous entry.
    """
    validate_operator(op)
    REGISTERED_OPERATORS[op.name] = op


# ---------------------------------------------------------------------------
# Legacy compatibility alias (Phase 4 ARCSOperatorContract)
# Existing operators that subclass ARCSOperatorContract continue to work;
# they are NOT automatically registered in REGISTERED_OPERATORS.
# ---------------------------------------------------------------------------

try:
    from arcs_primitives import CoherenceSignal, CoherenceReceipt  # type: ignore[import]
    _primitives_available = True
except ImportError:
    _primitives_available = False

CONTRACT_VERSION = "v9.0-phase6"

if _primitives_available:
    from typing import Tuple

    class ARCSOperatorContract(abc.ABC):  # noqa: F811  (intentional re-def as alias)
        """Phase 4 legacy contract — kept for backward compatibility."""

        @property
        @abc.abstractmethod
        def operator_id(self) -> str: ...

        @abc.abstractmethod
        def analyze(self, signal: "CoherenceSignal", **kwargs) -> "Tuple[CoherenceSignal, CoherenceReceipt]": ...

        def assert_axioms(self) -> dict[str, str]:
            return {
                "clarity_before_curvature":   "YES",
                "agency_over_automation":      "YES",
                "minimum_steps_to_coherence":  "YES",
                "kairos_over_neuroticism":     "YES",
            }

        def __repr__(self) -> str:
            return f"<ARCSOperator: {self.operator_id}>"


# ---------------------------------------------------------------------------
# __main__ — summary of registered operators
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # --- Demo: two minimal compliant operators --------------------------------

    @operator_contract
    class _StubSAGE(ARCSOperator):
        @property
        def name(self) -> str:
            return "SAGE"

        @property
        def version(self) -> str:
            return "1.0.0"

        def process(self, signal: dict) -> dict:
            return {**signal, "sage_processed": True}

        def validate(self, signal: dict) -> bool:
            return isinstance(signal, dict)

        def describe(self) -> str:
            return "SAGE — discernment and signal/noise separation operator."

    @operator_contract
    class _StubLAB(ARCSOperator):
        @property
        def name(self) -> str:
            return "LAB"

        @property
        def version(self) -> str:
            return "1.0.0"

        def process(self, signal: dict) -> dict:
            return {**signal, "lab_processed": True}

        def validate(self, signal: dict) -> bool:
            return isinstance(signal, dict)

        def describe(self) -> str:
            return "LAB — Loki/Advisors/Bayesian adversarial reasoning operator."

    @operator_contract
    class _StubBAR(ARCSOperator):
        @property
        def name(self) -> str:
            return "BAR"

        @property
        def version(self) -> str:
            return "1.0.0"

        def process(self, signal: dict) -> dict:
            return {**signal, "bar_processed": True}

        def validate(self, signal: dict) -> bool:
            return isinstance(signal, dict)

        def describe(self) -> str:
            return "BAR — Baseline/Asymmetric/Ruin risk geometry operator."

    register_operator(_StubSAGE())
    register_operator(_StubLAB())
    register_operator(_StubBAR())

    # --- Demonstrate ContractViolation on a broken operator -------------------
    print("=" * 60)
    print("ContractViolation guard test:")
    try:
        class _BrokenOp(ARCSOperator):
            @property
            def name(self) -> str: return "BROKEN"
            @property
            def version(self) -> str: return ""   # empty — should fail
            def process(self, signal: dict) -> dict: return signal
            def validate(self, signal: dict) -> bool: return True
            def describe(self) -> str: return "broken"

        validate_operator(_BrokenOp())
        print("  UNEXPECTED PASS — guard failed to catch empty version")
    except ContractViolation as exc:
        print(f"  Caught ContractViolation: {exc}")

    # --- Print registry summary -----------------------------------------------
    print("=" * 60)
    print("ARCS v9 — Registered Operators")
    print("=" * 60)
    for op_name, op in REGISTERED_OPERATORS.items():
        proto_ok = isinstance(op, OperatorProtocol)
        print(f"  [{op_name}] v{op.version}")
        print(f"    {op.describe()}")
        print(f"    OperatorProtocol: {'PASS' if proto_ok else 'FAIL'}")
    print("=" * 60)
    print(f"  Total registered: {len(REGISTERED_OPERATORS)}")
    print("=" * 60)
