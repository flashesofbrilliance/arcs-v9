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
belongs to scripts/sage_efficacy.js, which is correctly gated until real
Outcomes accumulate — this script has no such gate because synthetic data
is unlimited, but the lack of a gate does not make the result more true.

WHY: requested as an exploration of whether the deterministic kinematic
classifier's threshold logic is learnable / has a smooth decision boundary,
not as a production replacement. Kept out of operators/pyproject.toml —
TensorFlow is far too heavy for the lean Vercel-deployed SAGE sidecar.

See scripts/torch_sage_distillation.py for the PyTorch equivalent — both
train on identical data (scripts/sage_distillation_data.py) so any accuracy
difference reflects the framework/architecture, not the data.

Usage: python3 scripts/tf_sage_distillation.py [--samples=5000] [--epochs=30]
"""

from __future__ import annotations

import argparse
import os

import numpy as np

from sage_distillation_data import CLASSES, build_dataset, train_test_split


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()

    from tensorflow import keras

    print(f"Generating {args.samples} synthetic samples via the real deterministic pipeline...")
    X, y_class, y_pci = build_dataset(args.samples)

    class_counts = np.bincount(y_class, minlength=len(CLASSES))
    print("Class distribution:", dict(zip(CLASSES, class_counts.tolist())))

    X_train, X_test, yc_train, yc_test, yp_train, yp_test = train_test_split(X, y_class, y_pci)

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
