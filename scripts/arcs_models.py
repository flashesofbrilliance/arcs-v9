"""The ONLY place Python code gets a Claude model id. Source: runtime/specs/models.json.

    from arcs_models import model   # (scripts/ or operators/ on sys.path)
    model("deep")
"""
import json, os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runtime", "specs", "models.json")


def roles() -> dict:
    with open(_PATH) as f:
        return json.load(f)["roles"]


def model(role: str) -> str:
    return roles()[role]["model"]
