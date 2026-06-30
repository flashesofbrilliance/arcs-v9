#!/usr/bin/env python3
"""
scripts/torch_sage_distillation.py — PyTorch distillation of SAGE's kinematic classifier.

Same exercise as scripts/tf_sage_distillation.py, same shared dataset
(scripts/sage_distillation_data.py), same architecture shape (5 -> 32 -> 16
-> {4-way classification, 1 regression}) — different framework, so any
accuracy/speed difference reflects PyTorch vs Keras, not a data difference.

See scripts/tf_sage_distillation.py's docstring for the full "what this is
and isn't" disclaimer — it applies here unchanged. Kept out of
operators/pyproject.toml for the same reason: PyTorch is far too heavy for
the lean Vercel-deployed SAGE sidecar, and this never runs there.

Usage: python3 scripts/torch_sage_distillation.py [--samples=5000] [--epochs=30]
"""

from __future__ import annotations

import argparse
import os

import numpy as np

from sage_distillation_data import CLASSES, build_dataset, train_test_split


class SageDistillationNet:
    def __init__(self, torch, nn):
        self.torch = torch
        self.nn = nn
        self.model = nn.Sequential(
            nn.Linear(5, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
        )
        self.class_head = nn.Linear(16, len(CLASSES))
        self.pci_head = nn.Linear(16, 1)

    def parameters(self):
        return list(self.model.parameters()) + list(self.class_head.parameters()) + list(self.pci_head.parameters())

    def forward(self, x):
        hidden = self.model(x)
        return self.class_head(hidden), self.pci_head(hidden).squeeze(-1)

    def eval(self):
        self.model.eval()
        self.class_head.eval()
        self.pci_head.eval()

    def train(self):
        self.model.train()
        self.class_head.train()
        self.pci_head.train()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()

    import torch
    import torch.nn as nn

    print(f"Generating {args.samples} synthetic samples via the real deterministic pipeline...")
    X, y_class, y_pci = build_dataset(args.samples)

    class_counts = np.bincount(y_class, minlength=len(CLASSES))
    print("Class distribution:", dict(zip(CLASSES, class_counts.tolist())))

    X_train, X_test, yc_train, yc_test, yp_train, yp_test = train_test_split(X, y_class, y_pci)

    # Normalize inputs — velocity/acceleration/diffusion have very different scales
    mean, std = X_train.mean(axis=0), X_train.std(axis=0) + 1e-8
    X_train_n = (X_train - mean) / std
    X_test_n = (X_test - mean) / std

    X_train_t = torch.from_numpy(X_train_n)
    X_test_t = torch.from_numpy(X_test_n)
    yc_train_t = torch.from_numpy(yc_train).long()
    yc_test_t = torch.from_numpy(yc_test).long()
    yp_train_t = torch.from_numpy(yp_train)
    yp_test_t = torch.from_numpy(yp_test)

    net = SageDistillationNet(torch, nn)
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-3)
    class_loss_fn = nn.CrossEntropyLoss()
    pci_loss_fn = nn.MSELoss()

    n_train = len(X_train_t)
    batch_size = 64

    for epoch in range(args.epochs):
        net.train()
        perm = torch.randperm(n_train)
        epoch_class_loss, epoch_pci_loss = 0.0, 0.0
        for i in range(0, n_train, batch_size):
            idx = perm[i:i + batch_size]
            xb, ycb, ypb = X_train_t[idx], yc_train_t[idx], yp_train_t[idx]

            optimizer.zero_grad()
            class_logits, pci_pred = net.forward(xb)
            class_loss = class_loss_fn(class_logits, ycb)
            pci_loss = pci_loss_fn(pci_pred, ypb)
            loss = class_loss + pci_loss
            loss.backward()
            optimizer.step()

            epoch_class_loss += class_loss.item() * len(idx)
            epoch_pci_loss += pci_loss.item() * len(idx)

        net.eval()
        with torch.no_grad():
            val_class_logits, val_pci_pred = net.forward(X_test_t)
            val_class_loss = class_loss_fn(val_class_logits, yc_test_t).item()
            val_pci_loss = pci_loss_fn(val_pci_pred, yp_test_t).item()
            val_acc = (val_class_logits.argmax(dim=1) == yc_test_t).float().mean().item()

        print(
            f"Epoch {epoch+1}/{args.epochs} - "
            f"train_class_loss: {epoch_class_loss/n_train:.4f} - train_pci_loss: {epoch_pci_loss/n_train:.4f} - "
            f"val_acc: {val_acc:.4f} - val_pci_loss: {val_pci_loss:.4f}"
        )

    net.eval()
    with torch.no_grad():
        val_class_logits, val_pci_pred = net.forward(X_test_t)
        val_acc = (val_class_logits.argmax(dim=1) == yc_test_t).float().mean().item()
        val_pci_mae = (val_pci_pred - yp_test_t).abs().mean().item()

    print("\n=== Distillation results (vs the deterministic pipeline it was trained on) ===")
    print(f"  classification_accuracy: {val_acc:.4f}")
    print(f"  pci_mae: {val_pci_mae:.4f}")
    print("\nThis measures how well PyTorch approximates the existing deterministic math —")
    print("not whether either one predicts real decision outcomes.")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "operators", "_torch_distillation_artifacts")
    os.makedirs(out_dir, exist_ok=True)
    torch.save({
        "model_state": net.model.state_dict(),
        "class_head_state": net.class_head.state_dict(),
        "pci_head_state": net.pci_head.state_dict(),
        "mean": mean, "std": std,
    }, os.path.join(out_dir, "sage_distillation.pt"))
    print(f"\nModel + normalization stats saved to {out_dir}/")


if __name__ == "__main__":
    main()
