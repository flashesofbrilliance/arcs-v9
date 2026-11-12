#!/usr/bin/env python3
"""Recoil call service: the stage runner (stdlib only). Backlog row recoil-service-cli (R4).

Spec: _PROPOSALS/2026-11-11-recoil-call-service-arc-weld.md, sections 5 and 6.

  python3 scripts/recoil_service.py run --call <granola-id|calendar-event-id|ssot-path>
                                       [--until J1..J8|Render] [--only STAGE] [--dry-run]
                                       [--budget-usd N]
  python3 scripts/recoil_service.py stages        # the registry and what is built
  python3 scripts/recoil_service.py --self-test

What it does, per stage, in order J1 J2 J3 J4 J5 J6 J7 J8 Render:
  1. Hash the stage's inputs (the SSOT minus the stage's own keys, plus the stage version).
     If the hash and the output both match the last run, the stage is UNCHANGED and nothing is written.
  2. Run the stage. A stage returns a patch; the runner refuses any key the stage does not own.
  3. Gate it (section 6.1, plus the v2 schema check from scripts/recoil_ssot_v2.py).
  4. On FAIL: one repair hook, then gate again. At most 3 molts per stage per run, then stop and
     print the failing gate verbatim (exit 2).
  5. Write the stage's print (ADR-068) to runtime/recoil/runs/<stem>/prints/<stage>.json.

Hard stops (section 6.3) are a deny list checked before every action hook. A stage never touches
the world directly: it asks ctx.act(kind, ...). These kinds always refuse: merge, publish, deploy,
send, canon_change, adr_change, receipt_insert. paid_call refuses past --budget-usd (default 0).
Writes are allowed only under runtime/recoil/generated/ and runtime/recoil/runs/; a write into
_CANON/, _DECISIONS/, an ADR file or the governing docs refuses as a canon or ADR change.

A v1 SSOT is adapted in memory (recoil_ssot_v2.to_v2). The original file is never rewritten:
the v2 working copy lives at runtime/recoil/runs/<stem>/ssot.v2.json. A v2 SSOT is updated in place.
Every run ends with a receipt DRAFT in the run folder. It is never inserted (receipt_insert is denied).

Stage plug-in interface (R7, R8, R9 fill these in; see STAGES below):

    def run(ctx: Ctx, doc: dict) -> dict              # patch: {own_key: value}; only keys in Stage.owns
    def gate(ctx: Ctx, doc: dict) -> Gate             # Gate(ok: bool, lines: list[str]) on the patched doc
    def repair(ctx: Ctx, doc: dict, failed: Gate) -> dict   # optional; patch, same ownership rule

    register(Stage(name="J1", owns=("call",), run=..., gate=..., repair=..., version="1",
                   built=True, print_name="decompose"))

    reads=lambda doc: {...}   # optional: the part of the SSOT the stage reads, for the input hash
    raise NotRun(reason)      # the stage chose not to run its judgment step (dry run, no key, budget);
                              # the runner prints NOT RUN, writes the print, leaves the SSOT alone, moves on

J1 to J3 live in scripts/recoil_decompose.py (R7). J2 and J3 call the model role deep only through
ctx.act("paid_call"), so the default --budget-usd 0 keeps them NOT RUN.

ctx gives: ctx.root, ctx.stem, ctx.run_dir, ctx.dry_run, ctx.source (the --call value parsed),
ctx.act(kind, detail, fn=None, cost_usd=0.0, path=None) and ctx.write(path, text).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Callable

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import recoil_ssot_v2 as v2  # noqa: E402  (R2, PR 2151; not edited here)

GENERATED = os.path.join("runtime", "recoil", "generated")
RUNS = os.path.join("runtime", "recoil", "runs")
ORDER = ["J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "Render"]
MAX_MOLTS = 3

# --------------------------------------------------------------------------- hard stops (section 6.3)

DENY = {
    "merge": "merge is a one-way door: Zach merges (scripts/safe_merge.sh), never the runner",
    "publish": "publish is a one-way door: /recoil-ship runs only on Zach's go",
    "deploy": "deploy is a one-way door: never autopiloted",
    "send": "send to a counterpart is a one-way door: drafts only, Zach sends",
    "canon_change": "a canon change needs a write-lock declaration and Zach's go",
    "adr_change": "an ADR change needs a write-lock declaration and Zach's go",
    "receipt_insert": "inserting a decision_receipt row is Zach's approval; the runner writes a draft only",
}
ALLOWED_KINDS = {"write", "paid_call", "subprocess"}
WRITE_ROOTS = (GENERATED + os.sep, RUNS + os.sep)
CANON_PATHS = re.compile(r"^(_CANON/|_DECISIONS/|AGENTS\.md$|WORLD\.md$|CLAUDE\.md$)|(^|/)ADR-\d+")


class HardStop(Exception):
    """A deny-listed action. The runner stops the stage and prints this message verbatim."""


@dataclass
class Gate:
    ok: bool
    lines: list[str] = field(default_factory=list)


@dataclass
class Stage:
    name: str
    owns: tuple
    run: Callable
    gate: Callable
    repair: Callable | None = None
    version: str = "0"
    built: bool = True
    print_name: str = ""
    builder: str = ""  # backlog row that will fill a NOT BUILT stub
    reads: Callable | None = None  # the part of the SSOT the stage reads; default: everything it does not own


STAGES: dict[str, Stage] = {}


def register(stage: Stage) -> Stage:
    STAGES[stage.name] = stage
    return stage


class Ctx:
    def __init__(self, root: str, stem: str, dry_run: bool, source: dict, budget_usd: float = 0.0):
        self.root, self.stem, self.dry_run, self.source = root, stem, dry_run, source
        self.run_dir = os.path.join(RUNS, stem)
        self.budget_usd, self.spent_usd = budget_usd, 0.0
        self.log: list[str] = []

    def act(self, kind: str, detail: str = "", fn: Callable | None = None,
            cost_usd: float = 0.0, path: str | None = None):
        """The only door to the world. Deny list first, then the write allowlist, then the budget."""
        if kind in DENY:
            raise HardStop(f"HARD STOP [{kind}] {detail}: {DENY[kind]}")
        if kind not in ALLOWED_KINDS:
            raise HardStop(f"HARD STOP [{kind}] {detail}: unknown action kind; only {sorted(ALLOWED_KINDS)} run")
        if kind == "write":
            rel = os.path.relpath(os.path.join(self.root, path), self.root) if path else ""
            if CANON_PATHS.search(rel):
                raise HardStop(f"HARD STOP [canon_change] write {rel}: {DENY['canon_change']}")
            if rel.startswith("..") or not rel.startswith(WRITE_ROOTS):
                raise HardStop(f"HARD STOP [write] {rel}: writes go only under {' or '.join(WRITE_ROOTS)}")
        if kind == "paid_call":
            if self.spent_usd + cost_usd > self.budget_usd:
                raise HardStop(f"HARD STOP [paid_call] {detail}: ${cost_usd:.2f} would pass the run budget "
                               f"${self.budget_usd:.2f} (spent ${self.spent_usd:.2f}); raise --budget-usd on Zach's go")
            self.spent_usd += cost_usd
        if self.dry_run and kind != "subprocess":
            self.log.append(f"dry-run: would {kind} {detail or path}")
            return None
        self.log.append(f"{kind} {detail or path}")
        return fn() if fn else None

    def write(self, path: str, text: str) -> bool:
        """Write only if the bytes differ (idempotence). Returns True if it wrote."""
        full = os.path.join(self.root, path)
        if os.path.exists(full) and open(full, encoding="utf-8").read() == text:
            return False

        def _do():
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(text)
        self.act("write", path, fn=_do, path=path)
        return not self.dry_run


# --------------------------------------------------------------------------- helpers

def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def dump(doc: dict) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def input_hash(stage: Stage, doc: dict) -> str:
    rest = stage.reads(doc) if stage.reads else {k: v for k, v in doc.items() if k not in stage.owns}
    return sha(stage.name + "|" + stage.version + "|" + canon(rest))


def output_hash(stage: Stage, doc: dict) -> str:
    return sha(canon({k: doc.get(k) for k in stage.owns}))


def schema_gate(doc: dict) -> Gate:
    rep = v2.validate(doc)
    errs = rep.errors
    return Gate(not errs, [f"schema: {e}" for e in errs] or ["schema: valid (arcs.recoil.ssot.v2)"])


# --------------------------------------------------------------------------- stages

def _not_built(name: str, builder: str):
    def run(ctx, doc):
        return {}

    def gate(ctx, doc):
        return Gate(True, [f"{name} NOT BUILT (row {builder})"])
    return run, gate


for _name, _owns, _print, _row in [
    ("J4", ("cells",), "hypercube", "R8"),
    ("J5", ("atlas",), "atlas", "R9"),
    ("J6", (), "hud-load", "HUD v2 loader row"),
    ("J7", (), "hud-scrub", "HUD v2 loader row"),
    ("J8", (), "hud-kairos", "HUD v2 loader row"),
]:
    _r, _g = _not_built(_name, _row)
    register(Stage(_name, _owns, _r, _g, built=False, print_name=_print, builder=_row))

import recoil_decompose as decompose  # noqa: E402  (R7: J1 decompose, J2 verbs, J3 deconstruct)
decompose.install(sys.modules[__name__])
NotRun = decompose.NotRun


EM_DASH = chr(0x2014)
RENDER_DEFERRED = ["component_source_gate", "token_source_gate", "impeccable detect",
                   "brand-line-producer (reviewer)"]


def render_run(ctx: Ctx, doc: dict) -> dict:
    """Render through the existing v1 renderer (scripts/recoil) via the R2 export. Owns no SSOT key."""
    v1doc = v2.to_v1(doc)
    out_rel = os.path.join(ctx.run_dir, "render", f"{ctx.stem}.internal.html")
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, f"{ctx.stem}.json")
        with open(src, "w", encoding="utf-8") as fh:
            json.dump(v1doc, fh)
        cmd = [os.path.join(ctx.root, "scripts", "recoil"), "--data", src, "--audience", "internal",
               "--format", "html"]
        res = ctx.act("subprocess", "scripts/recoil --audience internal --format html",
                      fn=lambda: subprocess.run(cmd, cwd=ctx.root, capture_output=True, text=True, timeout=120))
    ctx.render = {"cmd": "scripts/recoil --audience internal --format html", "path": out_rel,
                  "rc": res.returncode, "stderr": res.stderr[-2000:], "html": res.stdout}
    if res.returncode == 0:
        ctx.write(out_rel, res.stdout)
    return {}


def render_gate(ctx: Ctx, doc: dict) -> Gate:
    r = getattr(ctx, "render", None)
    if not r:
        return Gate(False, ["render: renderer did not run"])
    if r["rc"] != 0:
        return Gate(False, [f"render: scripts/recoil exit {r['rc']}", r["stderr"].strip()])
    if len(r["html"]) < 200:
        return Gate(False, [f"render: output is {len(r['html'])} bytes"])
    lines = [f"render: scripts/recoil wrote {len(r['html'])} bytes"]
    ok = True
    visible = re.sub(r"(?s)<style.*?</style>|<script.*?</script>|<!--.*?-->", "", r["html"])
    dashes = visible.count(EM_DASH)
    if dashes:
        ok = False
        lines.append(f"render: {dashes} em-dash(es) in visible text")
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, f"{ctx.stem}.html")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(r["html"])
        pg = subprocess.run([sys.executable, os.path.join(ctx.root, "scripts", "page_gate.py"), "--static", f],
                            cwd=ctx.root, capture_output=True, text=True, timeout=300)
    lines.append(f"page_gate --static (includes artifact_wrap_lint): exit {pg.returncode}")
    if pg.returncode != 0:
        ok = False
        lines += [ln for ln in (pg.stdout + pg.stderr).strip().splitlines()[-40:]]
    lines.append("not run by the runner (R5 component set / reviewer): " + ", ".join(RENDER_DEFERRED))
    return Gate(ok, lines)


register(Stage("Render", (), render_run, render_gate, version="1", print_name="render",
               builder="R5 for the component set"))
__import__("recoil_stage_j5").install(sys.modules[__name__])  # R9: J5 atlas (scripts/recoil_stage_j5.py)


# --------------------------------------------------------------------------- call resolution

GRANOLA = re.compile(r"^(not_[A-Za-z0-9]+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")


def resolve_call(root: str, call: str) -> tuple[dict, str | None]:
    """Return (source, ssot_rel_path or None)."""
    p = call if os.path.isabs(call) else os.path.join(root, call)
    if call.endswith(".json") or os.path.isfile(p):
        if not os.path.isfile(p):
            raise SystemExit(f"recoil_service: no such SSOT: {call}")
        return {"kind": "ssot", "path": os.path.relpath(p, root)}, os.path.relpath(p, root)
    kind = "granola_id" if GRANOLA.match(call) else "calendar_event_id"
    gdir = os.path.join(root, GENERATED)
    for f in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(gdir, f), encoding="utf-8"))
        except (ValueError, OSError):
            continue
        src = ((d.get("call") or {}).get("source") or {}) if isinstance(d, dict) else {}
        if src.get(kind) == call:
            return {"kind": kind, "id": call}, os.path.join(GENERATED, f)
    return {"kind": kind, "id": call}, None


# --------------------------------------------------------------------------- the runner

def load_state(ctx: Ctx) -> dict:
    p = os.path.join(ctx.root, ctx.run_dir, "state.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def run_stage(ctx: Ctx, stage: Stage, doc: dict, state: dict, out: list[str]) -> tuple[str, dict]:
    """Returns (status, doc). status: PASS UNCHANGED NOT_BUILT NOT_RUN FAIL STOP."""
    if not stage.built:
        out.append(f"{stage.name} {stage.print_name}: NOT BUILT (filled by {stage.builder})")
        return "NOT_BUILT", doc
    ih = input_hash(stage, doc)
    prev = state.get(stage.name) or {}
    if (prev.get("status") == "PASS" and prev.get("input") == ih and prev.get("output") == output_hash(stage, doc)
            and os.path.exists(os.path.join(ctx.root, prev.get("print", "")))):
        out.append(f"{stage.name} {stage.print_name}: UNCHANGED (inputs {ih})")
        return "UNCHANGED", doc

    def apply(patch: dict, label: str) -> dict:
        foreign = [k for k in patch if k not in stage.owns]
        if foreign:
            raise HardStop(f"HARD STOP [ownership] {stage.name} {label} wrote {foreign}; it owns {list(stage.owns)}")
        nd = copy.deepcopy(doc)
        nd.update(copy.deepcopy(patch))
        return nd

    def gate_all(d: dict) -> Gate:
        g = stage.gate(ctx, d)
        s = schema_gate(d)
        return Gate(g.ok and s.ok, list(g.lines) + s.lines)

    molts, log0 = 0, len(ctx.log)
    print_rel = os.path.join(ctx.run_dir, "prints", f"{stage.name}.json")
    try:
        work = apply(stage.run(ctx, doc) or {}, "run")
        g = gate_all(work)
        while not g.ok and molts < MAX_MOLTS:
            molts += 1
            if stage.repair:
                work = apply(stage.repair(ctx, work, g) or {}, f"repair {molts}")
            else:
                work = apply(stage.run(ctx, work) or {}, f"rerun {molts}")
            g = gate_all(work)
    except HardStop as e:
        out.append(f"{stage.name} {stage.print_name}: STOP")
        out.append(str(e))
        return "STOP", doc
    except NotRun as e:
        # the judgment step did not run: say so, write the print, change nothing in the SSOT
        ctx.write(print_rel, dump({"stage": stage.name, "print": stage.print_name, "status": "NOT_RUN",
                                   "reason": str(e), "input_hash": ih, "detail": e.lines}))
        out.append(f"{stage.name} {stage.print_name}: NOT RUN ({e})")
        return "NOT_RUN", doc
    status = "PASS" if g.ok else "FAIL"
    pr = {"stage": stage.name, "print": stage.print_name, "status": status, "molts": molts,
          "input_hash": ih, "output_hash": output_hash(stage, work), "gate": g.lines, "actions": ctx.log[log0:]}
    ctx.write(print_rel, dump(pr))
    if status == "PASS":
        state[stage.name] = {"input": ih, "output": pr["output_hash"], "status": "PASS", "print": print_rel}
        out.append(f"{stage.name} {stage.print_name}: PASS after {molts} molt(s)")
        return "PASS", work
    out.append(f"{stage.name} {stage.print_name}: FAIL after {MAX_MOLTS} molts; failing gate verbatim:")
    out += ["  " + ln for ln in g.lines]
    return "FAIL", doc


def select(until: str | None, only: str | None) -> list[str]:
    if only:
        if only not in STAGES:
            raise SystemExit(f"recoil_service: unknown stage {only}; stages are {ORDER}")
        return [only]
    end = ORDER.index(until) + 1 if until else len(ORDER)
    return ORDER[:end]


def run(call: str, until: str | None = None, only: str | None = None, dry_run: bool = False,
        budget_usd: float = 0.0, root: str = ROOT) -> tuple[int, list[str]]:
    out: list[str] = []
    source, ssot_rel = resolve_call(root, call)
    raw = None
    if ssot_rel is None:
        raw = scaffold(root, source)
        if raw is None:
            out.append(f"call {source['kind']} {source['id']}: no SSOT carries this id and no transcript is cached.")
            out.append("J1 decompose: needs the transcript. Fetch it with Granola get_meeting_transcript "
                       f"(include_timestamps) into {decompose.TRANSCRIPTS}/ with the id in its first lines, then rerun. "
                       "Stopping: nothing downstream has input.")
            return 3, out
        ssot_rel = os.path.join(GENERATED, raw["meta"]["report_id"] + ".json")
        out.append(f"call {source['kind']} {source['id']}: new SSOT {ssot_rel} from {raw['call']['source']['transcript']}")
    stem = os.path.splitext(os.path.basename(ssot_rel))[0]
    ctx = Ctx(root, stem, dry_run, source, budget_usd)
    if raw is None:
        raw = json.load(open(os.path.join(root, ssot_rel), encoding="utf-8"))
    kind = v2.detect(raw)
    try:
        doc = v2.to_v2(raw, stem=stem)
    except ValueError as e:
        out.append(f"adapt: {e}")
        return 1, out
    in_place = kind == "v2"
    work_rel = ssot_rel if in_place else os.path.join(ctx.run_dir, "ssot.v2.json")
    if not in_place:
        prev = os.path.join(root, work_rel)
        if os.path.exists(prev):  # resume from the working copy
            doc = json.load(open(prev, encoding="utf-8"))
    g = schema_gate(doc)
    out.append(f"input {ssot_rel} ({kind}) -> {'in place' if in_place else work_rel}; " + "; ".join(g.lines))
    if not g.ok:
        return 1, out
    state = load_state(ctx)
    before = canon(state)
    rc = 0
    for name in select(until, only):
        status, doc = run_stage(ctx, STAGES[name], doc, state, out)
        if status in ("FAIL", "STOP"):
            rc = 2
            break
    try:
        ctx.write(work_rel, dump(doc))
        if canon(state) != before:
            ctx.write(os.path.join(ctx.run_dir, "state.json"), dump(state))
        draft = receipt_draft(ctx, ssot_rel, out, rc, state)
        ctx.write(os.path.join(ctx.run_dir, "receipt.draft.json"), dump(draft))
    except HardStop as e:
        out.append(str(e))
        rc = 2
    out.append(("dry run: nothing written. " if dry_run else "") +
               f"receipt draft: {os.path.join(ctx.run_dir, 'receipt.draft.json')} (never inserted)")
    return rc, out


MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                                     "Nov", "Dec"], 1)}


def scaffold(root: str, source: dict) -> dict | None:
    """A minimal v2 SSOT for a Granola id whose transcript is cached. The date comes from the transcript header."""
    if source.get("kind") != "granola_id":
        return None
    tpath = decompose.find_transcript(root, source["id"])
    if not tpath:
        return None
    head = open(os.path.join(root, tpath), encoding="utf-8").read(2000)
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", head) or re.search(r"\b([A-Z][a-z]{2})[a-z]* (\d{1,2}),? (\d{4})\b", head)
    if not m:
        return None
    date = m.group(1) if m.lastindex == 1 else f"{m.group(3)}-{MONTHS.get(m.group(1), 0):02d}-{int(m.group(2)):02d}"
    if date[5:7] == "00":
        return None
    stem = f"{date}-granola-{source['id'][:8]}"
    return {"schema": v2.SCHEMA_ID, "meta": {"report_id": stem, "date": date},
            "call": {"source": {"granola_id": source["id"], "transcript": tpath}, "atoms": []}}


def receipt_draft(ctx: Ctx, ssot_rel: str, out: list[str], rc: int, state: dict) -> dict:
    """A draft only. Its event_at is deliberately absent: Zach fills it when he approves the insert."""
    return {
        "_DRAFT": "not inserted; receipt_insert is a hard stop. Zach approves and inserts.",
        "question": f"Recoil service run on {ssot_rel}",
        "horizon": "today", "stakes": "low", "mode": "QUICKMOVE",
        # from the state ledger, not the run log, so a rerun with no new input drafts the same bytes
        "what_confirmed": [f"{n} PASS on inputs {st['input']}" for n, st in sorted(state.items())],
        "what_unconfirmed": [ln for ln in out if ("NOT BUILT" in ln or "NOT RUN" in ln or "FAIL" in ln or "STOP" in ln)
                             and "UNCHANGED" not in ln]
                            + ["render gates not run by the runner: " + ", ".join(RENDER_DEFERRED)],
        "operator": "recoil_service.py", "job_id": "job:backlog:recoil-service-cli",
        "tool_id": "tool:script:recoil_service.py", "source_repo": "flashesofbrilliance/arcs-v9",
        "refs": [ssot_rel], "exit": rc,
    }


# --------------------------------------------------------------------------- self-test

def self_test() -> int:
    fails: list[str] = []

    def check(cond: bool, label: str):
        print(("ok   " if cond else "FAIL ") + label)
        if not cond:
            fails.append(label)

    def snap(root: str) -> dict:
        d = {}
        for dp, _, fs in os.walk(root):
            for f in fs:
                fp = os.path.join(dp, f)
                d[fp] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        return d

    saved = dict(STAGES)
    try:
        with tempfile.TemporaryDirectory() as td:
            ctx = Ctx(td, "t", False, {}, budget_usd=1.0)
            # 1. every hard stop refuses
            for kind in DENY:
                try:
                    ctx.act(kind, "self-test")
                    check(False, f"hard stop {kind} refuses")
                except HardStop as e:
                    check(kind in str(e) and DENY[kind] in str(e), f"hard stop {kind} refuses: {e}")
            for path, label in [("_CANON/x.md", "canon write"), ("_DECISIONS/ADR-099-x.md", "ADR write"),
                                ("WORLD.md", "governing doc write"), ("src/app/page.tsx", "write outside run roots"),
                                ("../escape.json", "write escaping the repo")]:
                try:
                    ctx.act("write", path, path=path)
                    check(False, f"{label} refuses")
                except HardStop as e:
                    check(True, f"{label} refuses: {e}")
            try:
                ctx.act("rm_rf", "x")
                check(False, "unknown action kind refuses")
            except HardStop:
                check(True, "unknown action kind refuses")
            ctx.act("paid_call", "within budget", cost_usd=0.6)
            check(ctx.spent_usd == 0.6, "paid call within the budget runs")
            try:
                ctx.act("paid_call", "over budget", cost_usd=0.5)
                check(False, "paid call past the budget refuses")
            except HardStop as e:
                check("budget" in str(e), f"paid call past the budget refuses: {e}")

            # a v2 SSOT in a temp repo layout
            os.makedirs(os.path.join(td, GENERATED))
            good = v2._good_v2()
            rel = os.path.join(GENERATED, "2026-11-11-selftest.json")
            with open(os.path.join(td, rel), "w") as fh:
                fh.write(dump(good))

            # 2. molt cap: a gate that never passes gets exactly 3 repairs, then the verbatim gate
            calls = {"repair": 0}

            def rep(c, d, g):
                calls["repair"] += 1
                return {}
            for n in ORDER:
                STAGES[n] = Stage(n, (), lambda c, d: {}, lambda c, d: Gate(True, ["noop"]), built=False,
                                  print_name="stub", builder="self-test")
            STAGES["J4"] = Stage("J4", ("cells",), lambda c, d: {}, lambda c, d: Gate(False, ["J4 gate: cell X invented"]),
                                 repair=rep, print_name="hypercube")
            rc, out = run(rel, root=td)
            check(rc == 2 and calls["repair"] == MAX_MOLTS, f"molt cap: {calls['repair']} repairs then stop (rc {rc})")
            check(any("J4 gate: cell X invented" in ln for ln in out), "molt cap prints the failing gate verbatim")
            check(not any(ln.startswith("J5") for ln in out), "runner stops at the failing stage")

            # 3. repair that fixes it passes on molt 1
            fixed = {"n": 0}

            def gate_once(c, d):
                return Gate(fixed["n"] > 0, ["J4 gate: ok" if fixed["n"] else "J4 gate: empty"])

            def rep_fix(c, d, g):
                fixed["n"] += 1
                return {"cells": []}
            STAGES["J4"] = Stage("J4", ("cells",), lambda c, d: {}, gate_once, repair=rep_fix, print_name="hypercube")
            rc, out = run(rel, only="J4", root=td)
            check(rc == 0 and any("PASS after 1 molt" in ln for ln in out), "a repair that fixes it passes after 1 molt")

            # 4. ownership: a stage writing a key it does not own refuses
            STAGES["J2"] = Stage("J2", ("verbs",), lambda c, d: {"claims": []}, lambda c, d: Gate(True), print_name="verbs")
            rc, out = run(rel, only="J2", root=td)
            check(rc == 2 and any("ownership" in ln for ln in out), "a stage writing a foreign key refuses")

            # 5. a stage asking for a deny-listed action stops the run
            STAGES["J3"] = Stage("J3", ("claims",), lambda c, d: c.act("send", "email the counterpart") or {},
                                 lambda c, d: Gate(True), print_name="deconstruct")
            rc, out = run(rel, only="J3", root=td)
            check(rc == 2 and any("HARD STOP [send]" in ln for ln in out), "a stage that tries to send is stopped")

            # 6. idempotence: second run with no new input changes nothing
            STAGES["J2"] = Stage("J2", ("verbs",), lambda c, d: {"verbs": d.get("verbs", {})},
                                 lambda c, d: Gate(True, ["J2 ok"]), version="1", print_name="verbs")
            run(rel, only="J2", root=td)
            s1 = snap(td)
            rc, out = run(rel, only="J2", root=td)
            check(rc == 0 and snap(td) == s1, "rerun with no new input changes nothing")
            check(any("UNCHANGED" in ln for ln in out), "rerun reports UNCHANGED")
            with open(os.path.join(td, rel)) as fh:
                d = json.load(fh)
            d["meta"]["date"] = "2026-11-12"
            with open(os.path.join(td, rel), "w") as fh:
                fh.write(dump(d))
            rc, out = run(rel, only="J2", root=td)
            check(any("J2 verbs: PASS" in ln for ln in out), "new input reruns the stage")

            # 7. unknown call id with no cached transcript: clear stop at J1
            rc, out = run("not_ABCDEF123", root=td)
            check(rc == 3 and any("needs the transcript" in ln for ln in out),
                  "a Granola id with no SSOT and no transcript stops at J1 with the fetch step")
    finally:
        STAGES.clear()
        STAGES.update(saved)

    # 7b. the real J1 to J3 stages (scripts/recoil_decompose.py)
    decompose.self_test(sys.modules[__name__], check, snap)

    # 8. dry run on the Gasmi fixture through the real registry: validates via the v2 adapter, writes nothing
    gasmi = os.path.join(GENERATED, "2026-10-29-gasmi.json")
    watch = [os.path.join(ROOT, gasmi), os.path.join(ROOT, RUNS)]
    before = {p: (snap(p) if os.path.isdir(p) else hashlib.sha256(open(p, "rb").read()).hexdigest())
              for p in watch if os.path.exists(p)}
    rc, out = run(gasmi, dry_run=True)
    for ln in out:
        print("     | " + ln)
    after = {p: (snap(p) if os.path.isdir(p) else hashlib.sha256(open(p, "rb").read()).hexdigest())
             for p in watch if os.path.exists(p)}
    check(any("six-tab.v1" in ln and "valid" in ln for ln in out[:1]), "Gasmi v1 SSOT validates through the v2 adapter")
    check(before == after, "dry run writes nothing")
    check(any(ln.startswith(("J1 decompose: PASS", "J1 decompose: UNCHANGED")) for ln in out),
          "J1 decomposes Gasmi (UNCHANGED when a local run already did)")
    check(all(any(ln.startswith(f"{n} ") and "NOT RUN (dry run" in ln for ln in out) for n in ("J2", "J3")),
          "J2 and J3 report NOT RUN on a dry run (no model call)")
    check(all(any(ln.startswith(f"{n} ") and "NOT BUILT" in ln for ln in out) for n in ORDER[3:8] if not STAGES[n].built),
          "J4 to J8 report NOT BUILT")
    check(any(ln.startswith("Render") for ln in out), "Render runs the existing renderer")

    print(f"\nself-test: {'PASS' if not fails else 'FAIL'} ({len(fails)} failing)")
    return 1 if fails else 0


# --------------------------------------------------------------------------- CLI

def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="recoil_service.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run the journey on one call")
    r.add_argument("--call", required=True, help="Granola meeting id, calendar event id, or SSOT path")
    g = r.add_mutually_exclusive_group()
    g.add_argument("--until", choices=ORDER)
    g.add_argument("--only", choices=ORDER)
    r.add_argument("--dry-run", action="store_true", help="run and gate, write nothing")
    r.add_argument("--budget-usd", type=float, default=0.0, help="paid-call budget for this run (default 0)")
    sub.add_parser("stages", help="list the stage registry")
    a = ap.parse_args(argv)
    if a.cmd == "stages":
        for n in ORDER:
            s = STAGES[n]
            print(f"{n:7} {s.print_name:12} owns={list(s.owns)!s:12} "
                  f"{'built' if s.built else 'NOT BUILT -> ' + s.builder}")
        return 0
    rc, out = run(a.call, a.until, a.only, a.dry_run, a.budget_usd)
    print("\n".join(out))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
