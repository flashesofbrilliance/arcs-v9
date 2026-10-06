#!/usr/bin/env python3
"""
arcs_verb_eval_judge.py - optional LLM judge for the rubric (the "judge" lane).

Off unless you pass --judge. Needs the Anthropic SDK (pip install 'arcs-verb-eval[judge]')
and credentials from the environment (ANTHROPIC_API_KEY, or an `ant auth login` profile).
The key is never read from a file in this repo and never written anywhere.

What it can and cannot do:
  - It scores rubric rows 0, 1 or 2 and gives one sentence of reason.
  - It NEVER changes a gate, the fate, or go/stop. Those come from the rules lane only.
    judge() works on a copy of the report and self-test proves fate is unchanged.
  - Every call is recorded in the trace: the exact prompt, the model, tokens, and the
    score, so the page and CI can show what hit an LLM and what did not.

One request per rubric row. The artifact and the machine-check evidence sit in the system
prompt with cache_control, so rows 2..n of the same step read them from the prompt cache.
"""
from __future__ import annotations

import copy
import json

DEFAULT_MODEL = "claude-opus-5-5"
SCHEMA = {
    "type": "object",
    "properties": {"score": {"type": "integer", "enum": [0, 1, 2]}, "reason": {"type": "string"}},
    "required": ["score", "reason"],
    "additionalProperties": False,
}


def system_prompt(rep: dict, artifact_text: str) -> str:
    ev = "\n".join(f"- {g['id']}: {'pass' if g['ok'] else 'fail'} ({g['evidence']})" for g in rep["gates"])
    return (f"You score one rubric row at a time for {rep['tool']}, one step of a five-step check "
            "that runs before anything is said to someone.\n"
            "Score 0 (no), 1 (partly) or 2 (yes). Judge only the artifact below. Machine checks already "
            "decided go or stop; your score informs a person and changes nothing else.\n"
            "Be strict: a 2 means a skeptical reader would agree without argument.\n\n"
            f"Machine-check results:\n{ev}\n\n<artifact>\n{artifact_text}\n</artifact>")


def user_prompt(row: dict) -> str:
    q = f"Rubric question: {row['label']}"
    if row.get("evidence"):
        q += f"\nHint from the machine checks: {row['evidence']}"
    return q


def make_client():
    try:
        import anthropic
    except ImportError as e:
        raise SystemExit("--judge needs the Anthropic SDK: pip install 'arcs-verb-eval[judge]' (or pip install anthropic)") from e
    return anthropic.Anthropic()


def _errors():
    try:
        import anthropic
        return anthropic
    except ImportError:
        return None


def judge(rep: dict, artifact_text: str, client=None, model: str = DEFAULT_MODEL, effort: str = "medium") -> dict:
    """Return a copy of rep with rubric scores filled and judge-lane trace events marked sent."""
    out = copy.deepcopy(rep)
    client = client or make_client()
    sdk = _errors()
    import inspect
    try:
        typed = "fallbacks" in inspect.signature(client.beta.messages.create).parameters
    except (TypeError, ValueError):
        typed = False
    fb = {"fallbacks": "default"} if typed else {"extra_body": {"fallbacks": "default"}}  # older SDKs lack the typed param
    system = [{"type": "text", "text": system_prompt(out, artifact_text), "cache_control": {"type": "ephemeral"}}]
    calls = []
    for row in out["rubric"]:
        if row["score"] is not None:
            continue  # a person already scored it; the judge never overwrites a human
        call = {"row": row["row"], "model": model, "sent": True}
        try:
            resp = client.beta.messages.create(
                model=model,
                max_tokens=2000,
                betas=["server-side-fallback-2026-07-01"],
                **fb,
                system=system,
                output_config={"effort": effort, "format": {"type": "json_schema", "schema": SCHEMA}},
                messages=[{"role": "user", "content": user_prompt(row)}],
            )
            call["served_by"] = getattr(resp, "model", model)
            u = getattr(resp, "usage", None)
            if u is not None:
                call["usage"] = {k: getattr(u, k, None) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
            if resp.stop_reason == "refusal":
                call["outcome"] = "refused"
            elif resp.stop_reason == "max_tokens":
                call["outcome"] = "cut off"
            else:
                data = json.loads(next(b.text for b in resp.content if b.type == "text"))
                row["score"], row["judge"], row["reason"], row["by"] = int(data["score"]), call["served_by"], data["reason"], "model"
                call["outcome"], call["score"] = "scored", row["score"]
        except Exception as e:  # classify, never let a judge failure touch the fate
            if sdk is not None and isinstance(e, sdk.AuthenticationError):
                raise SystemExit("--judge: the API key was rejected. Set ANTHROPIC_API_KEY in your shell, not in this repo.") from e
            if sdk is not None and isinstance(e, sdk.RateLimitError):
                call["outcome"] = "rate limited"
            elif sdk is not None and isinstance(e, sdk.APIConnectionError):
                call["outcome"] = "no connection"
            elif sdk is not None and isinstance(e, sdk.APIStatusError):
                call["outcome"] = f"api error {e.status_code}"
            elif ("authentication" in str(e).lower() or "credentials" in str(e).lower()) and not (sdk is not None and isinstance(e, sdk.APIStatusError)):
                raise SystemExit("--judge: no Anthropic credentials found. Run: export ANTHROPIC_API_KEY=... in your own shell (never paste it into chat or commit it).") from e
            else:
                call["outcome"] = f"error: {type(e).__name__}: {str(e)[:120]}"
        calls.append(call)
    out["judge_calls"] = calls
    import arcs_verb_eval as _core
    out["floor_advisory"] = _core.rubric_floor(out["verb"], out["rubric"], by="any")  # never gates
    # rewrite the judge lane of the trace with what actually happened
    by_row = {c["row"]: c for c in calls}
    for ev in out["trace"]:
        if ev["lane"] == "judge" and ev["id"] in by_row:
            c = by_row[ev["id"]]
            ev.update(sent=True, model=c["model"], outcome=c["outcome"], usage=c.get("usage"),
                      score=next(r["score"] for r in out["rubric"] if r["row"] == ev["id"]),
                      prompt={"system": system[0]["text"], "user": user_prompt(next(r for r in out["rubric"] if r["row"] == ev["id"]))})
        if ev["lane"] == "summary":
            ev["llm_calls"] = sum(c["outcome"] in ("scored", "refused", "cut off") for c in calls)
            ev["llm_errors"] = sum(c["outcome"] not in ("scored", "refused", "cut off") for c in calls)
            ev["judge_pending"] = sum(r["score"] is None for r in out["rubric"])
    return out


class FakeClient:
    """Offline stand-in for self-test: returns a fixed score without any network call."""

    def __init__(self, score=2, refuse_rows=()):
        self.score, self.refuse_rows, self.calls = score, set(refuse_rows), []
        self.beta = self
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        q = kw["messages"][0]["content"]
        refused = any(r in q for r in self.refuse_rows)

        class B:  # text block
            type = "text"
            text = json.dumps({"score": self.score, "reason": "fixed test score"})

        class R:
            model = kw["model"]
            stop_reason = "refusal" if refused else "end_turn"
            content = [] if refused else [B()]
            usage = None
        return R()


def self_test() -> int:
    import arcs_verb_eval as core
    ok = []
    text = core.GOOD["synthesis"]
    up = None
    for v in core.VERBS[:3]:
        up = core.evaluate(v, core.GOOD[v], upstream=up, slop=False)
    base = core.evaluate("synthesis", text, upstream=up, slop=False)
    bad = core.evaluate("synthesis", text.replace('data-id="c3" data-render="grain"', 'data-id="c3"'), upstream=up, slop=False)
    fc = FakeClient(score=2, refuse_rows=["Compression"])
    j = judge(base, text, client=fc)
    ok.append(("one call per unscored rubric row", len(fc.calls) == len(base["rubric"])))
    ok.append(("fate unchanged by the judge (go stays go)", j["fate"] == base["fate"] and j["gates"] == base["gates"]))
    jb = judge(bad, text, client=FakeClient(score=2))
    ok.append(("fate unchanged by the judge (stop stays stop, even with perfect scores)", jb["fate"] == bad["fate"] == "hold"))
    ok.append(("refusal leaves the row unscored and says so", any(c["outcome"] == "refused" for c in j["judge_calls"])
               and any(r["score"] is None for r in j["rubric"])))
    ok.append(("trace marks judge calls as sent and counts them", j["trace"][-1]["llm_calls"] == len(fc.calls)
               and all(e.get("sent") for e in j["trace"] if e["lane"] == "judge")))
    ok.append(("original report untouched", all(r["score"] is None for r in base["rubric"])))
    kw = fc.calls[0]
    ok.append(("request: structured output + fallbacks + cached system", kw["output_config"]["format"]["type"] == "json_schema"
               and (kw.get("fallbacks") or kw.get("extra_body", {}).get("fallbacks")) == "default" and kw["system"][0]["cache_control"]["type"] == "ephemeral"))
    human = copy.deepcopy(base)
    human["rubric"][0]["score"] = 1
    fc2 = FakeClient()
    jh = judge(human, text, client=fc2)
    ok.append(("never overwrites a human score", jh["rubric"][0]["score"] == 1 and len(fc2.calls) == len(base["rubric"]) - 1))
    for name, cond in ok:
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}")
    failed = sum(not c for _, c in ok)
    print(f"\n{len(ok) - failed} passed, {failed} failed")
    return 1 if failed else 0
