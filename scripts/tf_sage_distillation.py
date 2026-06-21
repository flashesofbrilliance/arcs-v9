#!/usr/bin/env python3
"""
scripts/tf_sage_distillation.py — TensorFlow distillation of SAGE's kinematic classifier.

WHAT THIS IS: a TensorFlow model trained to approximate the existing
deterministic SAGE pipeline (arcs_operators_sage.py's kinematic lens +
signal classifier + PCI scorer). Training data is synthetically generated —
random CoherenceSignal arrays run through the REAL deterministic code to
produce ground-truth labels. There is no real-world Outcome data involved.

WHAT THIS IS NOT: a model of real decision quality. It learns the existing
threshold math (STRONG_SIGNAL_VELOCITY_THRESHOLD etc.), not anything new
about whether SAGE's signal actually predicts good decisions. That question
belongs to scripts/sage_efficacy.py, which is correctly gated until real
Outcomes accumulate — this script has no such gate because synthetic data
is unlimited, but the lack of a gate does not make the result more true.

WHY: requested as an exploration of whether the deterministic kinematic
classifier's threshold logic is learnable / has a smooth decision boundary,
not as a production replacement. Kept out of operators/pyproject.toml —
TensorFlow is far too heavy for the lean Vercel-deployed SAGE sidecar.

Usage: python3 scripts/tf_sage_distillation.py [--samples=5000] [--epochs=30]
"""

from __future__ import annotations

import argparse
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()

    import tensorflow as tf
    from tensorflow import keras

    print(f"Generating {args.samples} synthetic samples via the real deterministic pipeline...")
    X, y_class, y_pci = build_dataset(args.samples)

    class_counts = np.bincount(y_class, minlength=len(CLASSES))
    print("Class distribution:", dict(zip(CLASSES, class_counts.tolist())))

    split = int(0.8 * len(X))
    idx = np.random.default_rng(0).permutation(len(X))
    train_idx, test_idx = idx[:split], idx[split:]

    X_train, X_test = X[train_idx], X[test_idx]
    yc_train, yc_test = y_class[train_idx], y_class[test_idx]
    yp_train, yp_test = y_pci[train_idx], y_pci[test_idx]

    # Normalize inputs — velocity/acceleration/diffusion have very different scales
    mean, std = X_train.mean(axis=0), X_train.std(axis=0) + 1e-8
    X_train_n = (X_train - mean) / std
    X_test_n = (X_test - mean) / std

    inputs = keras.Input(shape=(5,), name="five_derivatives")
    hidden = keras.layers.Dense(32, activation="relu")(inputs)
    hidden = keras.layers.Dense(16, activation="relu")(hidden)
    class_out = keras.layers.Dense(len(CLASSES), activation="softmax", name="classification")(hidden)
    pci_out = keras.layers.Dense(1, activation="linear", name="pci")(hidden)

    model = keras.Model(inputs=inputs, outputs=[class_out, pci_out])
    model.compile(
        optimizer="adam",
        loss={"classification": "sparse_categorical_crossentropy", "pci": "mse"},
        metrics={"classification": "accuracy", "pci": "mae"},
    )

    model.fit(
        X_train_n, {"classification": yc_train, "pci": yp_train},
        validation_data=(X_test_n, {"classification": yc_test, "pci": yp_test}),
        epochs=args.epochs, batch_size=64, verbose=2,
    )

    print("\n=== Distillation results (vs the deterministic pipeline it was trained on) ===")
    results = model.evaluate(X_test_n, {"classification": yc_test, "pci": yp_test}, verbose=0, return_dict=True)
    for name, val in results.items():
        print(f"  {name}: {val:.4f}")
    print("\nThis measures how well TF approximates the existing deterministic math —")
    print("not whether either one predicts real decision outcomes.")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "operators", "_tf_distillation_artifacts")
    os.makedirs(out_dir, exist_ok=True)
    model.save(os.path.join(out_dir, "sage_distillation.keras"))
    np.savez(os.path.join(out_dir, "normalization.npz"), mean=mean, std=std)
    print(f"\nModel + normalization stats saved to {out_dir}/")


if __name__ == "__main__":
    main()
