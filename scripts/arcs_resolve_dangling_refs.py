"""
arcs_resolve_dangling_refs.py
Resolve the 68 dangling_declared references from catalog.json
against the local git repo to find their actual files/commits.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/zharris/arcs-v9")
CATALOG = REPO / ".claude/worktrees/system-arcs-field-os-515d3e/_ARTIFACTS/catalog.json"


def main():
    with open(CATALOG) as f:
        cat = json.load(f)

    node_ids = {n["id"] for n in cat["nodes"]}
    edges = cat["edges"]

    # Find dangling refs: edge targets not in node_ids
    dangling = {}
    for e in edges:
        target = e["to"]
        if target not in node_ids:
            dangling.setdefault(target, []).append(e)

    print(f"Total edges: {len(edges)}")
    print(f"Nodes in catalog: {len(node_ids)}")
    print(f"Dangling targets: {len(dangling)}")
    print()

    # For each dangling target, try to find it in the repo
    resolved = []
    unresolved = []

    for target_id, edge_list in sorted(dangling.items(), key=lambda x: -len(x[1])):
        sources = [e["from"] for e in edge_list]
        rels = [e.get("rel", "") for e in edge_list]

        # Try to find the target in the repo
        # Strategy 1: grep for the target id in file contents
        # Strategy 2: check if there's a file with that name
        # Strategy 3: check git history for the target

        found_files = []
        found_in_git = False
        git_commit = None

        # Check if any file in the repo contains this id as a wiki-link or reference
        try:
            result = subprocess.run(
                ["rg", "-l", target_id, str(REPO),
                 "--ignore-file=node_modules/.gitignore"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                found_files = [f.strip() for f in result.stdout.strip().split("\n")[:5]]
        except Exception:
            pass

        # Check if this looks like a memory file (id.md)
        md_file = REPO / f"_MEMORY/{target_id}.md"
        if md_file.exists():
            found_files.append(str(md_file))
            found_in_git = True

        # Check decision files
        adr_file = REPO / f"_DECISIONS/ADR-{target_id}.md"
        # ADR numbers are numeric, so this won't match text ids

        if found_files:
            resolved.append({
                "target": target_id,
                "source_count": len(edge_list),
                "sources": sources[:3],
                "relations": list(set(rels)),
                "found_in_repo": found_files,
            })
        else:
            unresolved.append({
                "target": target_id,
                "source_count": len(edge_list),
                "sources": sources[:3],
                "relations": list(set(rels)),
            })

    print("=== RESOLVED DANGLING REFS (found in local repo) ===")
    print(f"Count: {len(resolved)}")
    for r in resolved[:20]:
        print(f"\n  {r['target']}  (declared by {r['source_count']} nodes)")
        print(f"    sources: {r['sources']}")
        print(f"    relations: {r['relations']}")
        print(f"    found in: {r['found_in_repo'][:2]}")

    if len(resolved) > 20:
        print(f"\n  ... and {len(resolved)-20} more resolved")

    print(f"\n=== UNRESOLVED DANGLING REFS (not found in local repo) ===")
    print(f"Count: {len(unresolved)}")
    for u in unresolved[:15]:
        print(f"\n  {u['target']}  (declared by {u['source_count']} nodes)")
        print(f"    sources: {u['sources']}")
        print(f"    relations: {u['relations']}")

    if len(unresolved) > 15:
        print(f"\n  ... and {len(unresolved)-15} more unresolved")

    # Save full results
    output = {
        "catalog_source": str(CATALOG),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "total_dangling": len(dangling),
        "resolved": resolved,
        "unresolved": unresolved,
    }
    out_path = REPO / "_STATE" / "dangling-ref-resolution.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFull resolution saved to: {out_path}")


if __name__ == "__main__":
    main()
