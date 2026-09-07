"""Shared file-path module loader for the audit-script unit tests.

The audit scripts live under scripts/ and are NOT a Python package, so we import
them directly by file path via importlib. Each script is stdlib-only and imports
cleanly at module load (no side effects until main()), so this is safe.
"""
from __future__ import annotations

import importlib.util
import os
import sys

# All four audit scripts now live in this worktree's scripts/ dir (believability_ledger.py
# landed on main via PR #294). Resolve locally; keep a sibling-worktree fallback only for
# pre-merge checkouts that don't yet carry the ledger.
_THIS = os.path.dirname(os.path.abspath(__file__))
_WORKTREE = os.path.abspath(os.path.join(_THIS, "..", ".."))  # kind-lamport-dd294a
_SCRIPTS = os.path.join(_WORKTREE, "scripts")
_WORKTREES_ROOT = os.path.abspath(os.path.join(_WORKTREE, ".."))
_BELIEVABILITY = os.path.join(_SCRIPTS, "believability_ledger.py")
_BELIEVABILITY_FALLBACK = os.path.join(
    _WORKTREES_ROOT, "determined-herschel-e59b29", "scripts", "believability_ledger.py"
)


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot build spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_believability():
    path = _BELIEVABILITY if os.path.exists(_BELIEVABILITY) else _BELIEVABILITY_FALLBACK
    return load("believability_ledger", path)


def load_reel_in_scan():
    return load("reel_in_scan", os.path.join(_SCRIPTS, "reel_in_scan.py"))


def load_corrections_link():
    return load("corrections_link", os.path.join(_SCRIPTS, "corrections_link.py"))


def load_receipt_outcome_resolver():
    return load("receipt_outcome_resolver", os.path.join(_SCRIPTS, "receipt_outcome_resolver.py"))
