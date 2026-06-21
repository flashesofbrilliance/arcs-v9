#!/usr/bin/env python3
"""
scripts/sage_distillation_data.py — shared synthetic dataset for the SAGE
distillation experiments (TensorFlow and PyTorch versions). Keeping this in
one place means both framework scripts train on identical data, so any
accuracy difference between them reflects the framework/architecture, not a
data generation drift between two copy-pasted generators.

See scripts/tf_sage_distillation.py for what this is and isn't.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "operators"))

from arcs_operators_sage import SAGEOperator  # noqa: E402
from arcs_primitives import AxiomCheck, CoherenceSignal, FATEDReasoning  # noqa: E402

CLASSES = ["strong_signal", "noise", "mixed", "decelerating"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}

# Fixed at maximal completeness/alignment so PCI variation in the training
# signal comes from the kinematic features alone, not from reasoning quality.
_NEUTRAL_FATED = FATEDReasoning(
    facts="x" * 60, assumptions="x" * 60, tradeoffs="x" * 60,
    emotions="x" * 60, direction="x" * 60,
)
_NEUTRAL_AXIOMS = AxiomCheck(
    clarity_before_curvature="YES", agency_over_automation="YES",
    minimum_steps_to_coherence="YES", kairos_over_neuroticism="YES",
)


def generate_synthetic_signal(rng: np.random.Generator) -> np.ndarray:
    """One random signal, stratified by intended regime so all four classes
    (strong_signal/noise/mixed/decelerating) appear with reasonable balance
    in the training set. The actual label still comes from the real
    deterministic classifier afterward — this only biases which corner of
    the input space gets sampled; it doesn't fabricate the ground truth."""
    length = rng.integers(15, 60)
    regime = rng.choice(["clean_trend", "noisy", "mixed", "decelerating"])

    if regime == "clean_trend":
        # A pure linear ramp does NOT reliably classify as strong_signal: its
        # second derivative (acceleration) is near-zero noise with a sign
        # that's essentially random relative to velocity, which trips the
        # phase_cancellation threshold almost every time. strong_signal needs
        # *consistent curvature* (accelerating, single-signed), not just a
        # consistent slope — hence the quadratic term below.
        sign = rng.choice([-1, 1])
        velocity_coef = sign * rng.uniform(1.0, 2.0)
        accel_coef = sign * rng.uniform(0.5, 1.5)
        t = np.linspace(0, 1, length)
        base = velocity_coef * length * t + accel_coef * length * t**2
        noise_level = rng.uniform(0.0, 0.1)
    elif regime == "noisy":
        # High diffusion, no clear directional signal
        base = np.zeros(length)
        noise_level = rng.uniform(2.0, 5.0)
    elif regime == "decelerating":
        # Strong initial trend that reverses partway through
        trend = rng.choice([-1, 1]) * rng.uniform(1.0, 2.0)
        base = np.linspace(0, trend * length, length)
        midpoint = length // 2
        base[midpoint:] = base[midpoint] - 0.6 * (base[midpoint:] - base[midpoint])
        noise_level = rng.uniform(0.0, 0.5)
    else:  # mixed — moderate trend, moderate noise, some phase cancellation
        trend = rng.choice([-1, 1]) * rng.uniform(0.3, 0.8)
        base = np.linspace(0, trend * length, length)
        base += np.sin(np.linspace(0, rng.uniform(2, 6), length)) * rng.uniform(0.5, 1.5)
        noise_level = rng.uniform(0.5, 1.5)

    return base + rng.normal(0, noise_level, size=length)


def build_dataset(n_samples: int, seed: int = 42):
    rng = np.random.default_rng(seed)
    sage = SAGEOperator()
    X, y_class, y_pci = [], [], []

    for i in range(n_samples):
        raw = generate_synthetic_signal(rng)
        signal = CoherenceSignal(signal=raw, domain="research", label=f"synthetic_{i}")
        _, five_derivatives, classification = sage._run_kinematic_lens(signal)
        pci = sage._compute_pci(five_derivatives, _NEUTRAL_FATED, _NEUTRAL_AXIOMS, classification)

        X.append([
            five_derivatives["velocity"],
            five_derivatives["acceleration"],
            five_derivatives["diffusion"],
            five_derivatives["phase_cancellation"],
            five_derivatives["deceleration"],
        ])
        y_class.append(CLASS_TO_IDX[classification])
        y_pci.append(pci)

    return np.array(X, dtype=np.float32), np.array(y_class, dtype=np.int32), np.array(y_pci, dtype=np.float32)


def train_test_split(X, y_class, y_pci, train_frac: float = 0.8, seed: int = 0):
    idx = np.random.default_rng(seed).permutation(len(X))
    split = int(train_frac * len(X))
    train_idx, test_idx = idx[:split], idx[split:]
    return (
        X[train_idx], X[test_idx],
        y_class[train_idx], y_class[test_idx],
        y_pci[train_idx], y_pci[test_idx],
    )
