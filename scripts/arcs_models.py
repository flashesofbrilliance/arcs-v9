"""Python's read of the ONE model registry: the MODELS block in src/lib/claude-models.ts.

There is no second source: this parses `role: "claude-..."` lines inside
`export const MODELS = { ... } as const`, so a role change in the TS file is picked up here.

    from arcs_models import model   # (scripts/ or operators/ on sys.path)
    model("deep")
"""
import os, re

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "lib", "claude-models.ts")
_BLOCK = re.compile(r"export const MODELS = \{(.*?)\} as const", re.S)
_ROLE = re.compile(r'^\s*(\w+):\s*"(claude-[\w.-]+)"', re.M)


def parse(text: str) -> dict:
    m = _BLOCK.search(text)
    if not m:
        raise RuntimeError("arcs_models: no `export const MODELS = { ... } as const` block in claude-models.ts")
    return dict(_ROLE.findall(m.group(1)))


def roles() -> dict:
    with open(_PATH, encoding="utf-8") as f:
        return parse(f.read())


def model(role: str) -> str:
    return roles()[role]
