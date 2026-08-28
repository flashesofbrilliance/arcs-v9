"""
arcs_missing_node_sweep.py
ARCS v9 — Hyperstitional Gap Detector

Finds nodes declared by the corpus but absent from the catalog.
These are {ref: id, missing: true} gaps — fictions the corpus has already
committed to (real edges from real nodes point to them) but hasn't built yet.

Hyperstition: fictions that make themselves real. These missing nodes are
prime hyperstitional material because the corpus has ALREADY done the design
work (the edges are there); materializing the body is just completing what
the corpus already decided on.

Output: a prioritized manifest sorted by hyperstitional potency (incoming
edge count from canon/echo-heavy nodes), with traces of where each missing
node might already exist in the repo.
"""

from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ─────────────────────────────────────────────
# CONFIG — directories to sweep for traces
# ─────────────────────────────────────────────

REPO_ROOT = Path("/Users/zharris/arcs-v9")
CATALOG_PATH = Path(
    "/Users/zharris/arcs-v9/.claude/worktrees/"
    "system-arcs-field-os-515d3e/_ARTIFACTS/catalog.json"
)

SWEEP_DIRS = [
    REPO_ROOT / "_MEMORY",
    REPO_ROOT / "_DECISIONS",
    REPO_ROOT / "_SPECS",
    REPO_ROOT / "_PATTERNS",
    REPO_ROOT / "_CANON",
    REPO_ROOT / "_SEEDS",
    REPO_ROOT / "_ARCHIVE",
    REPO_ROOT / "archive",
    REPO_ROOT / "docs",
    REPO_ROOT / "scripts",
    REPO_ROOT / ".claude" / "worktrees",
    REPO_ROOT / "public",
    REPO_ROOT / "_STATE",
    Path("/Users/zharris/Downloads"),
    REPO_ROOT / "archive" / "specs" / "deprecated-versions",
]

SKIP_DIRS = {
    REPO_ROOT / "node_modules",
    REPO_ROOT / ".git",
    REPO_ROOT / ".claude" / "worktrees" / "system-arcs-field-os-515d3e",
}


# ─────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class MissingNode:
    """A node declared by the corpus but absent from the catalog."""
    node_id: str
    incoming_edges: int = 0
    declaring_nodes: List[str] = field(default_factory=list)
    declaring_sections: Set[str] = field(default_factory=set)
    declaring_kinds: Set[str] = field(default_factory=set)
    traces: List[Trace] = field(default_factory=list)
    suggested_location: str = ""
    hyperstition_score: float = 0.0


@dataclass
class Trace:
    """A trace of where a missing node might already exist."""
    kind: str          # file_name | content_ref | source_hint | worktree | download
    path: str = ""
    detail: str = ""
    confidence: float = 0.0


# ─────────────────────────────────────────────

class GapSweep:
    """Sweep the repo for traces of missing catalog nodes."""

    def __init__(self, catalog_path: Path, repo_root: Path):
        self.catalog_path = catalog_path
        self.repo_root = repo_root
        self.catalog: Optional[Dict[str, Any]] = None
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, str]] = []
        self.declared_ids: Set[str] = set()
        self.referenced_ids: Counter[str] = Counter()
        self.missing_ids: Set[str] = set()
        self.missing_nodes: Dict[str, MissingNode] = {}

    # ── catalog parsing ──────────────────────

    def load_catalog(self) -> None:
        """Load the catalog and extract nodes + edges."""
        with open(self.catalog_path, "r") as f:
            self.catalog = json.load(f)

        for node in self.catalog.get("nodes", []):
            self.nodes[node["id"]] = node
            self.declared_ids.add(node["id"])

        self.edges = self.catalog.get("edges", [])
        # Count how many times each ID is referenced (as a target of an edge)
        for edge in self.edges:
            target = edge.get("to", "")
            if target:
                self.referenced_ids[target] += 1

        # Missing = referenced but not declared
        self.missing_ids = {
            rid for rid, count in self.referenced_ids.items()
            if rid not in self.declared_ids and not rid.startswith("@ref")
        }

        print(f"Catalog: {len(self.declared_ids)} declared nodes, "
              f"{len(self.edges)} edges, "
              f"{len(self.missing_ids)} missing (declared-but-absent) nodes")

    def build_missing_nodes(self) -> None:
        """Build MissingNode objects for each gap."""
        for edge in self.edges:
            target = edge.get("to", "")
            if target not in self.missing_ids:
                continue
            source_id = edge.get("from", "")
            source_node = self.nodes.get(source_id, {})

            if target not in self.missing_nodes:
                self.missing_nodes[target] = MissingNode(node_id=target)

            mn = self.missing_nodes[target]
            mn.incoming_edges += 1
            mn.declaring_nodes.append(source_id)
            if source_node.get("section"):
                mn.declaring_sections.add(source_node["section"])
            if source_node.get("kind"):
                mn.declaring_kinds.add(source_node["kind"])

        # Compute hyperstition score: potency = incoming edge count weighted
        # by the echo weight of the declaring nodes (canon nodes casting votes
        # count more than uncited nodes)
        for mn in self.missing_nodes.values():
            total_potency = 0.0
            for declarer_id in mn.declaring_nodes:
                declarer = self.nodes.get(declarer_id, {})
                echo = declarer.get("echo_weight", 0) if "echo_weight" in declarer else 0
                # If the node came from catalog.json, echo_weight is on the node;
                # if from a different catalog, it may be on field_state
                field_state = declarer.get("field_state")
                if not echo and field_state:
                    echo = field_state.get("echo_weight", 0)
                total_potency += max(1, echo)
            mn.hyperstition_score = total_potency

    # ── trace discovery ──────────────────────

    def discover_traces(self) -> None:
        """For each missing node, find traces in the repo."""
        for mn in self.missing_nodes.values():
            self._sweep_for_traces(mn)

    def _sweep_for_traces(self, mn: MissingNode) -> None:
        """Search the repo for traces of a missing node ID."""
        node_id = mn.node_id

        # 1. File name traces: does any file in the repo contain the node ID
        #    in its name (partial draft, stub, exported ticket)?
        self._file_name_trace(mn, node_id)

        # 2. Content traces: grep repo files (subset) for the node ID as a
        #    wiki-link [[node_id]] or @ref or plain mention
        self._content_trace(mn, node_id)

        # 3. Source hint traces: if declaring nodes have source paths, the
        #    missing node likely belongs near them
        self._source_hint_trace(mn)

        # 4. Worktree traces: check .claude/worktrees for the node ID
        self._worktree_trace(mn, node_id)

        # 5. Download traces: check ~/Downloads for exported tickets or bundles
        self._download_trace(mn, node_id)

    def _file_name_trace(self, mn: MissingNode, node_id: str) -> None:
        """Find files whose name contains the node ID."""
        # Normalize: node IDs use hyphens; file names may too
        # Also check for .md versions (node_id.md is the canonical body)
        candidates = [
            node_id,
            node_id + ".md",
            node_id + ".json",
            node_id + ".html",
            "ticket-" + node_id + ".html",
        ]
        for candidate in candidates:
            for sweep_dir in SWEEP_DIRS:
                if not sweep_dir.exists() or sweep_dir in SKIP_DIRS:
                    continue
                try:
                    for path in sweep_dir.rglob(candidate):
                        if path.is_file():
                            rel = str(path.relative_to(Path.home()))
                            if SWEEP_DIRS and any(
                                str(path).startswith(str(d)) for d in SWEEP_DIRS
                            ):
                                mn.traces.append(Trace(
                                    kind="file_name",
                                    path=str(path),
                                    detail=f"File name matches '{candidate}'",
                                    confidence=0.9 if candidate == node_id + ".md" else 0.6,
                                ))
                                break
                except (PermissionError, OSError):
                    continue

    def _content_trace(self, mn: MissingNode, node_id: str) -> None:
        """Grep for the node ID in repo text files."""
        # Limit to likely directories to avoid full-repo grep cost
        grep_roots = [
            REPO_ROOT / "_MEMORY",
            REPO_ROOT / "_DECISIONS",
            REPO_ROOT / "_SPECS",
            REPO_ROOT / "_PATTERNS",
            REPO_ROOT / "_CANON",
            REPO_ROOT / "_SEEDS",
            REPO_ROOT / "_ARCHIVE",
            REPO_ROOT / "archive",
            REPO_ROOT / "docs",
            REPO_ROOT / "scripts",
            Path("/Users/zharris/Downloads"),
        ]
        for root in grep_roots:
            if not root.exists():
                continue
            try:
                # Use rg (ripgrep) if available, else fall back to grep
                result = subprocess.run(
                    ["rg", "-l", "--max-count", "1", node_id, str(root)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0 and result.stdout.strip():
                    for matched_file in result.stdout.strip().split("\n"):
                        rel = str(Path(matched_file).relative_to(REPO_ROOT)) \
                            if matched_file.startswith(str(REPO_ROOT)) \
                            else matched_file
                        mn.traces.append(Trace(
                            kind="content_ref",
                            path=matched_file,
                            detail=f"Node ID '{node_id}' found in content",
                            confidence=0.7,
                        ))
                        break  # one trace per kind is enough
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                # rg not available or timed out; skip
                continue

    def _source_hint_trace(self, mn: MissingNode) -> None:
        """Infer suggested location from declaring nodes' source paths."""
        if not mn.declaring_nodes:
            return

        # Collect source paths from declaring nodes
        source_dirs: Counter[str] = Counter()
        for declarer_id in mn.declaring_nodes:
            declarer = self.nodes.get(declarer_id, {})
            source = declarer.get("source", "")
            if source and source.startswith("~"):
                # Expand ~ and extract directory
                expanded = os.path.expanduser(source)
                d = os.path.dirname(expanded)
                source_dirs[d] += 1

        if source_dirs:
            top_dir, count = source_dirs.most_common(1)[0]
            mn.suggested_location = top_dir
            mn.traces.append(Trace(
                kind="source_hint",
                detail=f"Most declaring nodes ({count}) source from '{top_dir}' — "
                       f"missing node likely belongs there",
                confidence=0.5,
            ))

    def _worktree_trace(self, mn: MissingNode, node_id: str) -> None:
        """Check .claude/worktrees for traces of the node."""
        wt_dir = REPO_ROOT / ".claude" / "worktrees"
        if not wt_dir.exists():
            return
        try:
            for worktree in wt_dir.iterdir():
                if not worktree.is_dir():
                    continue
                # Check for _ARTIFACTS/catalog.json in the worktree
                wt_catalog = worktree / "_ARTIFACTS" / "catalog.json"
                if wt_catalog.exists():
                    try:
                        with open(wt_catalog, "r") as f:
                            wt_data = json.load(f)
                        for wt_node in wt_data.get("nodes", []):
                            if wt_node.get("id") == node_id:
                                mn.traces.append(Trace(
                                    kind="worktree",
                                    path=str(wt_catalog),
                                    detail=f"Node '{node_id}' found in worktree catalog: "
                                           f"{worktree.name}",
                                    confidence=0.8,
                                ))
                    except (json.JSONDecodeError, OSError):
                        continue
                # Check for the node body file
                for ext in [".md", ".json", ".html"]:
                    body_path = worktree / (node_id + ext)
                    if body_path.exists():
                        mn.traces.append(Trace(
                            kind="worktree",
                            path=str(body_path),
                            detail=f"Node body file found in worktree: {worktree.name}",
                            confidence=0.9,
                        ))
        except (PermissionError, OSError):
            pass

    def _download_trace(self, mn: MissingNode, node_id: str) -> None:
        """Check ~/Downloads for exported tickets or bundles."""
        dl_dir = Path("/Users/zharris/Downloads")
        if not dl_dir.exists():
            return
        try:
            for f in dl_dir.iterdir():
                if not f.is_file():
                    continue
                if node_id in f.name:
                    mn.traces.append(Trace(
                        kind="download",
                        path=str(f),
                        detail=f"File in ~/Downloads matches node ID: {f.name}",
                        confidence=0.4,
                    ))
        except (PermissionError, OSError):
            pass

    # ── report ───────────────────────────────

    def report(self, top_n: int = 30) -> None:
        """Print the prioritized missing-nodes manifest."""
        if not self.missing_nodes:
            print("No missing nodes found.")
            return

        # Sort by hyperstition score (descending)
        sorted_missing = sorted(
            self.missing_nodes.values(),
            key=lambda m: m.hyperstition_score,
            reverse=True,
        )

        print(f"\n{'='*80}")
        print(f"HYPERSTITIONAL GAP MANIFEST — {len(sorted_missing)} missing nodes")
        print(f"{'='*80}")
        print(f"Sorted by hyperstition score (incoming edge potency from echo-heavy nodes)")
        print(f"Top {top_n} shown")
        print()

        for i, mn in enumerate(sorted_missing[:top_n], 1):
            print(f"{i:3d}. {mn.node_id}")
            print(f"    hyperstition_score: {mn.hyperstition_score:.1f}  "
                  f"incoming_edges: {mn.incoming_edges}  "
                  f"declaring_nodes: {len(mn.declaring_nodes)}")
            if mn.declaring_sections:
                print(f"    sections: {', '.join(sorted(mn.declaring_sections))}")
            if mn.declaring_kinds:
                print(f"    kinds: {', '.join(sorted(mn.declaring_kinds))}")
            if mn.suggested_location:
                print(f"    suggested_location: {mn.suggested_location}")
            if mn.traces:
                print(f"    traces ({len(mn.traces)}):")
                for t in mn.traces:
                    conf_str = f"[{t.confidence:.0%}]"
                    if t.path:
                        print(f"      {conf_str} {t.kind}: {t.path} — {t.detail}")
                    else:
                        print(f"      {conf_str} {t.kind}: {t.detail}")
            print()

        if len(sorted_missing) > top_n:
            print(f"... and {len(sorted_missing) - top_n} more")

        # Save full manifest to JSON
        manifest = {
            "generated": "auto",
            "catalog_source": str(self.catalog_path),
            "missing_count": len(sorted_missing),
            "missing_nodes": [
                {
                    "node_id": mn.node_id,
                    "hyperstition_score": mn.hyperstition_score,
                    "incoming_edges": mn.incoming_edges,
                    "declaring_nodes": mn.declaring_nodes,
                    "declaring_sections": sorted(mn.declaring_sections),
                    "declaring_kinds": sorted(mn.declaring_kinds),
                    "suggested_location": mn.suggested_location,
                    "traces": [
                        {
                            "kind": t.kind,
                            "path": t.path,
                            "detail": t.detail,
                            "confidence": t.confidence,
                        }
                        for t in mn.traces
                    ],
                }
                for mn in sorted_missing
            ],
        }
        out_path = self.repo_root / "_STATE" / "hyperstition-gap-manifest.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\nFull manifest saved to: {out_path}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("ARCS Missing-Node Hyperstition Sweep")
    print(f"Catalog: {CATALOG_PATH}")
    print(f"Repo root: {REPO_ROOT}")
    print()

    sweeper = GapSweep(CATALOG_PATH, REPO_ROOT)
    sweeper.load_catalog()
    sweeper.build_missing_nodes()
    sweeper.discover_traces()
    sweeper.report(top_n=30)


if __name__ == "__main__":
    main()
