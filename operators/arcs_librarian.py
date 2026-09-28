#!/usr/bin/env python3
"""
arcs_librarian.py — Operator 21 (Librarian): recommend(q, budget).

Retrieval by EXPECTED VALUE under a fixed context budget, never by recency or
match score alone. Policy: _SEEDS/index.jsonl#seed-service-librarian-retrieval-policy.
Tier table (data, not prose): runtime/specs/read-friction-tiers.json.
Source trust (read FIRST, before the claim's own backing): runtime/specs/source-trust.json.

For each candidate c (ADR, memory, seed, tao proverb, LEGEND/LORE row, ledger row,
receipt, lattice node, prior Librarian pick) and a query q:

    value(c, q) = p_load_bearing(c, q) * cost_if_absent(q)
    cost(c)     = read_friction(c) + displacement(c)
    retrieve c iff value > cost; rank by value - cost; stop when the marginal
    item's value - cost < 0 OR the budget is spent.

Honesty rules (mechanical, tested by --self-test):
  * backing(c) = M0 refs (git shas that resolve in this repo, witness/transcript
    files that exist). No M0 backing -> the item is M1 and is returned ONLY under
    what_unconfirmed. It never enters what_confirmed.
  * a source tiered ZERO-WEIGHT in source-trust.json contributes NO backing, even
    when its text carries a resolvable sha: the source's word counts for nothing.
  * every result carries reserve_ratio (backed:unbacked) and curation_debt (the
    pathology sinks consulted raw).
  * p_load_bearing is a mechanical PRE-SCORE (query overlap + lineage in-degree,
    demoted by the ouroboros clause). It is surfaced, never acted on (NOTOMATION).
  * OUROBOROS: the Librarian's own prior picks are candidates; a pick later
    falsified (F-row in _STATE/falsification-ledger.jsonl) demotes its class.

stdlib-only. Python >= 3.9.

CLI:
  python3 operators/arcs_librarian.py "query text" [--budget 16000] [--stakes medium] [--out path.json]
  python3 operators/arcs_librarian.py --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

LIBRARIAN_VERSION = "0.1.0"
HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent
TIERS_REL = Path("runtime/specs/read-friction-tiers.json")
TRUST_REL = Path("runtime/specs/source-trust.json")
PICKS_REL = Path("_STATE/librarian")

DISPLACEMENT_WEIGHT = 1.0
DEMOTION_PER_FALSIFIED_PICK = 0.15
DEMOTION_FLOOR = 0.4
DEFEATED_FACTOR = 0.5
MAX_TEXT_CHARS = 6000
DEFAULT_SOURCE = "claude-fable"   # repo content is authored by this harness's sessions unless a row says otherwise

SHA_RE = re.compile(r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")
WITNESS_RE = re.compile(r"_STATE/witness/\d{4}-\d{2}-\d{2}\.jsonl")
RECEIPT_ID_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}--[\w.\-]+--[A-Z]{2}\b")
PR_RE = re.compile(r"(?:PR\s*)?#(\d{2,5})\b")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
WORD_RE = re.compile(r"[a-z0-9][a-z0-9_\-]{2,}")
STOP = set("""the and for that with this from into over under are was were been being have has had not but
its their they them then than when where which while who whom whose what why how all any each every
one two per via use used using can could should would will shall may might must also only just very
more most less least such same other another some many much few any into onto upon about above below
between within without across after before during since until again further here there once out off
own too own new old""".split())


# ─────────────────────────────────────────────────────────────────────────────
# Candidate
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Candidate:
    id: str
    cls: str
    text: str
    path: str = ""
    date: Optional[str] = None
    source: str = DEFAULT_SOURCE
    refs: List[str] = field(default_factory=list)
    superseded_by: Optional[str] = None
    aliases: List[str] = field(default_factory=list)

    @property
    def bytes(self) -> int:
        return len(self.text.encode("utf-8", errors="replace"))

    @staticmethod
    def from_store_receipt(r: Dict[str, Any]) -> "Candidate":
        rid = str(r.get("receipt_id") or f"receipt_{int(r.get('timestamp', 0))}")
        text = " ".join(str(r.get(k, "")) for k in ("phase_id", "status", "pipeline_verdict", "next_action"))
        text += f" nci={r.get('pipeline_nci')}"
        ts = r.get("timestamp") or r.get("stored_at")
        d = datetime.utcfromtimestamp(float(ts)).strftime("%Y-%m-%d") if ts else None
        return Candidate(id=rid, cls="store-receipt", text=text, path="operators/arcs_receipts_store.json", date=d)


def _first_date(*vals: Any) -> Optional[str]:
    for v in vals:
        if not v:
            continue
        m = DATE_RE.search(str(v))
        if m:
            return m.group(1)
    return None


def _clip(s: str) -> str:
    return s if len(s) <= MAX_TEXT_CHARS else s[:MAX_TEXT_CHARS]


def _jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            out.append(row)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Corpus loaders (each returns a list of Candidate; all failures degrade to [])
# ─────────────────────────────────────────────────────────────────────────────

def load_adrs(root: Path) -> List[Candidate]:
    out = []
    for p in sorted((root / "_DECISIONS").glob("ADR-*.md")):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.search(r"\*\*Date:\*\*\s*([^\n]+)", txt)
        sup = re.search(r"\*\*Status:\*\*\s*SUPERSEDED[^\n]*?(ADR-\d{3})", txt, re.I)
        out.append(Candidate(id=re.match(r"(ADR-\d{3})", p.name).group(1) if re.match(r"(ADR-\d{3})", p.name) else p.stem,
                             cls="adr", text=_clip(txt), path=str(p.relative_to(root)),
                             date=_first_date(m.group(1) if m else None),
                             superseded_by=sup.group(1) if sup else None))
    return out


def load_memory(memory_dir: Optional[Path]) -> List[Candidate]:
    if not memory_dir or not memory_dir.exists():
        return []
    out = []
    for p in sorted(memory_dir.glob("*.md")):
        if p.name == "MEMORY.md":
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.search(r"^\s*modified:\s*(\S+)", txt, re.M)
        out.append(Candidate(id=p.stem, cls="memory", text=_clip(txt), path=f"memory/{p.name}",
                             date=_first_date(m.group(1) if m else None)))
    return out


def load_seeds(root: Path) -> List[Candidate]:
    out = []
    planted: Dict[str, str] = {}
    for row in _jsonl(root / "_SEEDS" / "ledger.jsonl"):
        sid = row.get("seed_id") or row.get("seed")
        if sid and row.get("ts"):
            planted.setdefault(str(sid), str(row["ts"]))
        out.append(Candidate(id=f"seed-ledger:{row.get('seed_id') or row.get('seed')}:{row.get('event')}:{row.get('ts')}",
                             cls="seed-ledger",
                             text=" ".join(str(row.get(k, "")) for k in ("seed_id", "event", "receipt", "gaps")),
                             path="_SEEDS/ledger.jsonl", date=_first_date(row.get("ts"))))
    for row in _jsonl(root / "_SEEDS" / "index.jsonl"):
        sid = str(row.get("id", ""))
        text = " ".join(str(row.get(k, "")) for k in ("id", "alias", "local", "local_note", "conforms_to", "content", "confluence"))
        out.append(Candidate(id=sid, cls="seed", text=_clip(text), path="_SEEDS/index.jsonl",
                             date=_first_date(planted.get(sid), row.get("provenance")),
                             aliases=[str(row.get("alias"))] if row.get("alias") else []))
    return out


def load_tao(root: Path) -> List[Candidate]:
    out = []
    for row in _jsonl(root / "_CANON" / "tao-proverbs.jsonl"):
        out.append(Candidate(id=str(row.get("id")), cls="tao",
                             text=" ".join([str(row.get("text", "")), " ".join(map(str, row.get("lineage", []) or [])), " ".join(map(str, row.get("themes", []) or []))]),
                             path="_CANON/tao-proverbs.jsonl", date=_first_date(row.get("date"))))
    return out


def load_legend(root: Path) -> List[Candidate]:
    out = []
    for row in _jsonl(root / "runtime" / "specs" / "legend.jsonl"):
        out.append(Candidate(id=f"legend:{row.get('term')}", cls="legend",
                             text=" ".join(str(row.get(k, "")) for k in ("term", "expansion", "operational_definition", "aliases", "source")),
                             path="runtime/specs/legend.jsonl", date=_first_date(row.get("first_seen")),
                             aliases=[str(a) for a in (row.get("aliases") or [])]))
    return out


def load_lore(root: Path) -> List[Candidate]:
    out = []
    for row in _jsonl(root / "runtime" / "specs" / "lore.jsonl"):
        out.append(Candidate(id=str(row.get("id")), cls="lore",
                             text=" ".join(str(row.get(k, "")) for k in ("story", "observation", "mechanism_claimed", "binding_verdict", "teaches", "refs")),
                             path="runtime/specs/lore.jsonl", date=_first_date(row.get("date")),
                             superseded_by=row.get("superseded_by"),
                             refs=[str(r) for r in (row.get("refs") or [])]))
    return out


def load_registry(root: Path) -> List[Candidate]:
    p = root / "operators" / "OPERATOR-REGISTRY.json"
    if not p.exists():
        return []
    try:
        reg = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    out = []
    for r in reg.get("operators", []):
        b = r.get("binding") or {}
        text = " ".join(str(x) for x in (r.get("symbol"), r.get("name"), r.get("role"), r.get("function"), r.get("status"),
                                          b.get("module"), b.get("symbol"), b.get("entrypoint"), b.get("note"), r.get("nearest")) if x)
        out.append(Candidate(id=f"op:{r.get('op')}", cls="registry", text=text, path="operators/OPERATOR-REGISTRY.json",
                             date=_first_date(reg.get("source_of_truth")), aliases=[str(r.get("name")), str(r.get("symbol"))]))
    return out


def load_lattice(root: Path) -> List[Candidate]:
    p = root / "runtime" / "specs" / "knowledge-lattice-v1.json"
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    out = []
    for n in d.get("nodes", []) or []:
        text = " ".join(str(x) for x in (n.get("label"), n.get("what"), n.get("status"), " ".join(n.get("shore", []) or [])) if x)
        out.append(Candidate(id=f"lattice:{n.get('id')}", cls="lattice", text=text, path=str(p.relative_to(root)),
                             date=_first_date(d.get("last_drift_check"), d.get("last_reviewed"))))
    return out


def load_ledgers(root: Path) -> List[Candidate]:
    out = []
    for row in _jsonl(root / "_STATE" / "falsification-ledger.jsonl"):
        out.append(Candidate(id=str(row.get("id")), cls="falsification",
                             text=" ".join(str(row.get(k, "")) for k in ("claim", "test", "verdict", "delta", "fix", "refs")),
                             path="_STATE/falsification-ledger.jsonl", date=_first_date(row.get("ts")),
                             refs=[str(r) for r in (row.get("refs") or [])]))
    for row in _jsonl(root / "_STATE" / "assumptions.jsonl"):
        out.append(Candidate(id=str(row.get("id")), cls="assumption",
                             text=" ".join(str(row.get(k, "")) for k in ("assumption", "test_that_would_decide", "status", "decided_ref", "notes")),
                             path="_STATE/assumptions.jsonl", date=_first_date(row.get("decided_on"), row.get("held_since")),
                             source=str(row.get("held_by") or DEFAULT_SOURCE), superseded_by=row.get("supersedes") and None))
    for row in _jsonl(root / "_QUEUE" / "induced-backlog.jsonl"):
        out.append(Candidate(id=f"backlog:{row.get('id')}", cls="backlog",
                             text=" ".join(str(row.get(k, "")) for k in ("id", "jtbd", "route", "gates", "trigger", "status", "fates")),
                             path="_QUEUE/induced-backlog.jsonl", date=_first_date((row.get("route") or {}).get("verified") if isinstance(row.get("route"), dict) else None)))
    wdir = root / "_STATE" / "witness"
    if wdir.exists():
        for p in sorted(wdir.glob("*.jsonl")):
            for row in _jsonl(p):
                out.append(Candidate(id=f"witness:{row.get('ts')}", cls="witness",
                                     text=" ".join(str(row.get(k, "")) for k in ("quote", "context", "gut", "y", "promoted")),
                                     path=str(p.relative_to(root)), date=_first_date(row.get("ts"), p.stem)))
    for row in _jsonl(root / "operators" / "ledger" / "operator-receipts.jsonl"):
        env = row.get("envelope") or {}
        out.append(Candidate(id=f"opreceipt:{row.get('receipt_id')}", cls="operator-receipt",
                             text=" ".join(str(x) for x in (row.get("tool"), row.get("op"), env.get("name"), env.get("status"), env.get("blocked_reason"), env.get("nearest")) if x),
                             path="operators/ledger/operator-receipts.jsonl", date=_first_date(row.get("event_at"))))
    return out


def load_prior_picks(root: Path) -> Tuple[List[Candidate], List[Dict[str, Any]]]:
    """The ouroboros pool: every item this Librarian recommended before, with when."""
    picks: List[Dict[str, Any]] = []
    pdir = root / PICKS_REL
    if pdir.exists():
        for p in sorted(pdir.glob("*.json")):
            try:
                res = json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(res, dict) or res.get("generator", "").split("@")[0] != "operators/arcs_librarian.py":
                continue
            for it in res.get("items", []):
                picks.append({"id": it.get("id"), "cls": it.get("class"), "ts": _first_date(res.get("ts")), "q": res.get("q"), "from": str(p.relative_to(root))})
    for row in _jsonl(root / "operators" / "ledger" / "operator-receipts.jsonl"):
        if row.get("op") != 21:
            continue
        res = ((row.get("envelope") or {}).get("result") or {})
        if not isinstance(res, dict):
            continue
        for it in res.get("items", []) or []:
            picks.append({"id": it.get("id"), "cls": it.get("class"), "ts": _first_date(row.get("event_at")), "q": res.get("q"), "from": "operators/ledger/operator-receipts.jsonl"})
    cands = [Candidate(id=f"pick:{pk['id']}@{pk['ts']}", cls="librarian-pick",
                       text=f"prior Librarian recommendation of {pk['id']} ({pk['cls']}) for q: {pk.get('q')}",
                       path=pk["from"], date=pk["ts"]) for pk in picks if pk.get("id")]
    return cands, picks


# ─────────────────────────────────────────────────────────────────────────────
# Librarian
# ─────────────────────────────────────────────────────────────────────────────

def _tokens(s: str) -> List[str]:
    return [w for w in WORD_RE.findall(s.lower()) if w not in STOP]


def _guess_memory_dir(root: Path) -> Optional[Path]:
    env = os.environ.get("ARCS_MEMORY_DIR")
    if env:
        p = Path(env).expanduser()
        return p if p.exists() else None
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=str(root), capture_output=True, text=True, timeout=10).stdout.strip()
        main_root = Path(common).resolve().parent if common else root
    except (OSError, subprocess.SubprocessError):
        main_root = root
    p = Path.home() / ".claude" / "projects" / str(main_root).replace("/", "-") / "memory"
    return p if p.exists() else None


class Librarian:
    def __init__(self, root: Optional[Path] = None, git_root: Optional[Path] = None,
                 memory_dir: Optional[Path] = None, extra_candidates: Optional[List[Candidate]] = None,
                 load_corpus: bool = True, tiers_path: Optional[Path] = None, trust_path: Optional[Path] = None):
        self.root = Path(root or DEFAULT_ROOT)
        self.git_root = Path(git_root or self.root)
        self.tiers = json.loads((tiers_path or (DEFAULT_ROOT / TIERS_REL)).read_text(encoding="utf-8"))
        tp = trust_path or (self.root / TRUST_REL)
        if not tp.exists():
            tp = DEFAULT_ROOT / TRUST_REL
        self.trust = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else {"sources": {}}
        self.memory_dir = memory_dir if memory_dir is not None else (_guess_memory_dir(self.root) if load_corpus else None)
        self.not_consulted: List[str] = ["externals (Granola / Sugar / Supabase): expensive-read, expensive-write; retrieve only via a wrapping tool that pays the read once, never raw"]
        self.candidates: List[Candidate] = []
        self.prior_picks: List[Dict[str, Any]] = []
        if load_corpus:
            self.candidates += load_adrs(self.root) + load_seeds(self.root) + load_tao(self.root) + load_legend(self.root) \
                + load_lore(self.root) + load_registry(self.root) + load_lattice(self.root) + load_ledgers(self.root)
            mem = load_memory(self.memory_dir)
            if not mem:
                self.not_consulted.append("memory bodies: no memory dir found (set ARCS_MEMORY_DIR)")
            self.candidates += mem
            picks, self.prior_picks = load_prior_picks(self.root)
            self.candidates += picks
        self.candidates += list(extra_candidates or [])
        self._falsified_rows = [c for c in self.candidates if c.cls == "falsification" and "FALSIFIED" in c.text]

    # ── backing ──────────────────────────────────────────────────────────────

    def _verify_shas(self, shas: Iterable[str]) -> Dict[str, bool]:
        shas = sorted(set(shas))
        if not shas:
            return {}
        try:
            proc = subprocess.run(["git", "cat-file", "--batch-check"], cwd=str(self.git_root), input="\n".join(shas) + "\n",
                                  capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            return {s: False for s in shas}
        ok: Dict[str, bool] = {}
        for line in proc.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1] in ("commit", "tree", "blob", "tag"):
                for s in shas:
                    if parts[0].startswith(s):
                        ok[s] = True
        return {s: ok.get(s, False) for s in shas}

    def _source_tier(self, key: str) -> Tuple[str, str]:
        src = (self.trust.get("sources") or {}).get(key)
        if not src:
            return "STANDARD", "spot-check load-bearing claims; unbacked claims stay what_unconfirmed"
        return str(src.get("tier", "STANDARD")), str(src.get("verification_demand", ""))

    def _backing(self, c: Candidate, sha_ok: Dict[str, bool]) -> Tuple[Optional[List[str]], List[str], Optional[str]]:
        """Returns (m0_refs | None, m1_refs, note). Source tier is read FIRST."""
        blob = c.text + " " + " ".join(c.refs)
        m1 = sorted(set(RECEIPT_ID_RE.findall(blob)) | {f"PR#{n}" for n in PR_RE.findall(blob)})
        tier, _ = self._source_tier(c.source)
        if tier == "ZERO-WEIGHT":
            return None, m1, f"source {c.source} is ZERO-WEIGHT: its refs contribute no backing; verify via an independent primary record"
        m0 = [s for s in sorted(set(SHA_RE.findall(blob))) if sha_ok.get(s)]
        m0 += [w for w in sorted(set(WITNESS_RE.findall(blob))) if (self.root / w).exists()]
        return (m0 or None), m1, None

    # ── scoring ──────────────────────────────────────────────────────────────

    def _demotions(self) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
        falsified: List[Dict[str, Any]] = []
        for pk in self.prior_picks:
            pid = str(pk.get("id"))
            for f in self._falsified_rows:
                if pid and pid in f.text and (not pk.get("ts") or not f.date or f.date >= pk["ts"]):
                    falsified.append({"pick": pid, "class": pk.get("cls"), "picked": pk.get("ts"), "falsified_by": f.id})
        per_class: Dict[str, int] = {}
        for f in falsified:
            per_class[str(f["class"])] = per_class.get(str(f["class"]), 0) + 1
        return {k: max(DEMOTION_FLOOR, 1.0 - DEMOTION_PER_FALSIFIED_PICK * n) for k, n in per_class.items()}, falsified

    def recommend(self, q: str, budget: int = 16000, stakes: str = "medium", n_max: int = 12,
                  classes: Optional[List[str]] = None) -> Dict[str, Any]:
        t0 = time.time()
        today = date.today()
        qt = _tokens(q)
        qset = set(qt)
        cands = [c for c in self.candidates if not classes or c.cls in classes]
        # lineage: how many OTHER candidates mention this id (an item nothing stands on is rarely load-bearing)
        texts_l = [c.text.lower() for c in cands]
        # idf over the pool: a rare query term ("librarian") outweighs a common one ("value")
        n_docs = max(1, len(texts_l))
        idf = {w: math.log((n_docs + 1) / (1 + sum(1 for tl in texts_l if w in tl))) + 0.1 for w in qset}
        idf_total = sum(idf.values()) or 1.0
        indeg: Dict[str, int] = {}
        for c in cands:
            keys = [c.id.lower()] + [a.lower() for a in c.aliases if a and len(a) >= 4]
            keys = [k for k in keys if len(k) >= 4]
            n = 0
            for j, tl in enumerate(texts_l):
                if cands[j] is c:
                    continue
                if any(k in tl for k in keys):
                    n += 1
            indeg[c.id] = n
        sha_ok = self._verify_shas(s for c in cands for s in SHA_RE.findall(c.text + " " + " ".join(c.refs)))
        demotion, falsified_picks = self._demotions()
        cia_map = self.tiers.get("cost_if_absent_by_stakes", {})
        cia = float(cia_map.get(stakes, cia_map.get("medium", 2.0)))
        tps = float(self.tiers.get("tokens_per_step", 4000))
        stale_surcharge = float(self.tiers.get("stale_surcharge_steps", 1.0))

        scored: List[Dict[str, Any]] = []
        for c in cands:
            cl = self.tiers["classes"].get(c.cls, self.tiers["classes"]["external"])
            tier = self.tiers["tiers"][cl["tier"]]
            tl = c.text.lower()
            hits = sorted((w for w in qset if w in tl), key=lambda w: -idf[w])
            overlap = sum(idf[w] for w in hits) / idf_total if qset else 0.0
            if q.strip().lower() in tl or c.id.lower() in q.lower():
                overlap = min(1.0, overlap + 0.25)
            lineage = min(1.0, math.log1p(indeg[c.id]) / math.log1p(10))
            # relevance is necessary; lineage only amplifies it (an item nothing stands on is rarely load-bearing,
            # but an item everything stands on is still not load-bearing for THIS q unless q touches it)
            p = overlap * (0.7 + 0.3 * lineage)
            p *= demotion.get(c.cls, 1.0)
            defeated_by = [f.id for f in self._falsified_rows if f is not c and c.id.lower() in f.text.lower() and len(c.id) >= 4]
            if defeated_by or c.superseded_by:
                p *= DEFEATED_FACTOR
            p = round(min(1.0, max(0.0, p)), 4)
            tokens = c.bytes / 4.0
            stale = None
            age = None
            if c.date:
                try:
                    age = (today - date.fromisoformat(c.date[:10])).days
                    stale = age > int(cl["horizon_days"])
                except ValueError:
                    pass
            rf = float(tier["steps"]) + tokens / tps + (stale_surcharge if stale else 0.0)
            m0, m1, note = self._backing(c, sha_ok)
            s_tier, demand = self._source_tier(c.source)
            scored.append({
                "id": c.id, "class": c.cls, "quadrant": cl["quadrant"], "path": c.path, "bytes": c.bytes,
                "p_load_bearing": p,
                "cost_if_absent": cia,
                "value": round(p * cia, 4),
                "read_friction": {"tier": cl["tier"], "verification_steps": tier["steps"], "tokens_est": int(tokens),
                                  "stale_surcharge": stale_surcharge if stale else 0.0, "score": round(rf, 4)},
                "_rf": rf,
                "backing": m0, "m1_refs": m1, "backing_note": note,
                "source": {"key": c.source, "tier": s_tier, "verification_demand": demand},
                "freshness": {"verified": c.date, "age_days": age, "horizon_days": cl["horizon_days"], "stale": stale,
                              "defeaters": ["FALSIFIED F-row citing this id", "superseded_by set", "shift row in a fold ridgeline"],
                              "defeated_by": defeated_by, "superseded_by": c.superseded_by},
                "why_load_bearing": f"query terms hit (idf-ranked): {hits[:8]} ({len(hits)}/{len(qset)}, idf share {overlap:.2f}); cited by {indeg[c.id]} other item(s)"
                                    + (f"; class demoted x{demotion[c.cls]:.2f} (ouroboros)" if c.cls in demotion else "")
                                    + ("; DEFEATED" if defeated_by or c.superseded_by else ""),
            })

        # rank by value - cost with displacement priced against the REMAINING budget as items are taken
        remaining = int(budget)
        used = 0
        taken: List[Dict[str, Any]] = []
        skipped_displacement: List[str] = []
        stopped = "candidate pool exhausted"
        pool = sorted(scored, key=lambda s: s["value"] - s["_rf"], reverse=True)
        for s in pool:
            if len(taken) >= n_max:
                stopped = f"n_max={n_max} reached"
                break
            if remaining <= 0:
                stopped = "budget spent"
                break
            if s["bytes"] > remaining:
                skipped_displacement.append(s["id"])
                continue
            disp = s["bytes"] / remaining
            cost = s["_rf"] + DISPLACEMENT_WEIGHT * disp
            net = s["value"] - cost
            if net < 0:
                stopped = "marginal item value - cost < 0"
                break
            s["displacement"] = round(disp, 4)
            s["cost"] = round(cost, 4)
            s["net"] = round(net, 4)
            s["confirmed"] = bool(s["backing"])
            remaining -= s["bytes"]
            used += s["bytes"]
            taken.append(s)
        for s in scored:
            s.pop("_rf", None)

        backed = [s["id"] for s in taken if s["confirmed"]]
        unbacked = [s["id"] for s in taken if not s["confirmed"]]
        sinks: Dict[str, Dict[str, Any]] = {}
        for s in scored:
            if s["quadrant"] == "PATHOLOGY":
                sink = "memory/ (all bodies)" if s["class"] == "memory" else s["path"]
                d = sinks.setdefault(s["class"], {"sink": sink, "class": s["class"], "scanned": 0, "returned": 0})
                d["scanned"] += 1
        rom_or_ram_returned = any(s["quadrant"] in ("ROM", "RAM") for s in taken)
        for s in taken:
            if s["class"] in sinks:
                sinks[s["class"]]["returned"] += 1
        for d in sinks.values():
            d["only_source"] = d["returned"] > 0 and not rom_or_ram_returned
        counts: Dict[str, int] = {}
        for c in cands:
            counts[c.cls] = counts.get(c.cls, 0) + 1
        return {
            "generator": f"operators/arcs_librarian.py@{LIBRARIAN_VERSION}",
            "operator": 21, "name": "Librarian", "entrypoint": "recommend",
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "q": q, "stakes": stakes,
            "budget": {"given_bytes": int(budget), "used_bytes": used, "remaining_bytes": remaining},
            "formula": "value = p_load_bearing * cost_if_absent(stakes); cost = read_friction(tier.steps + tokens/tokens_per_step + stale_surcharge) "
                       f"+ {DISPLACEMENT_WEIGHT} * bytes/remaining_budget; take iff value - cost >= 0, ranked by value - cost",
            "notomation": "p_load_bearing is a mechanical pre-score (idf-weighted query overlap, amplified by lineage in-degree, ouroboros-demoted). The rank is surfaced for a human to adjudicate; nothing here is acted on.",
            "items": taken,
            "what_confirmed": backed,
            "what_unconfirmed": unbacked,
            "reserve_ratio": {"backed": len(backed), "unbacked": len(unbacked), "ratio": f"{len(backed)}:{len(unbacked)}",
                              "backed_share": round(len(backed) / len(taken), 3) if taken else None},
            "curation_debt": sorted(sinks.values(), key=lambda d: -d["scanned"]),
            "ouroboros": {"prior_picks_considered": len(self.prior_picks), "prior_picks_falsified": falsified_picks,
                          "class_demotions": demotion},
            "skipped_for_displacement": skipped_displacement,
            "stopped_because": stopped,
            "not_consulted": self.not_consulted,
            "corpus": {"candidates": len(cands), "by_class": dict(sorted(counts.items()))},
            "elapsed_s": round(time.time() - t0, 3),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Self-test: the honesty rules must be mechanically true
# ─────────────────────────────────────────────────────────────────────────────

def self_test() -> int:
    import tempfile
    fails = 0

    def check(label: str, cond: bool, detail: Any = "") -> None:
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {str(detail)[:120]}")
        fails += 0 if cond else 1

    print("self-test: arcs_librarian")
    real_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(DEFAULT_ROOT), capture_output=True, text=True).stdout.strip()
    check("repo HEAD sha available for M0 tests", len(real_sha) == 40, real_sha)
    tmp = Path(tempfile.mkdtemp())
    (tmp / "_STATE").mkdir()
    (tmp / "runtime" / "specs").mkdir(parents=True)
    # a ZERO-WEIGHT source and an ELEVATED one, in a private trust file
    trust = {"sources": {"hermes": {"tier": "ZERO-WEIGHT", "verification_demand": "independent primary record"},
                         "claude-fable": {"tier": "ELEVATED", "verification_demand": "grep or sha"}}}
    (tmp / TRUST_REL).write_text(json.dumps(trust))
    # an F-row that falsifies a prior pick of class 'memory'
    (tmp / "_STATE" / "falsification-ledger.jsonl").write_text(json.dumps({
        "id": "F900", "ts": "2026-09-27", "claim": "mem-old-pick said X", "verdict": "FALSIFIED",
        "delta": "the pick mem-old-pick was wrong", "refs": ["mem-old-pick"]}) + "\n")
    (tmp / PICKS_REL).mkdir(parents=True)
    (tmp / PICKS_REL / "prior.json").write_text(json.dumps({
        "generator": "operators/arcs_librarian.py@0.0.0", "ts": "2026-09-20T00:00:00", "q": "old q",
        "items": [{"id": "mem-old-pick", "class": "memory"}]}))
    q = "librarian retrieval policy value backing"
    cands = [
        Candidate(id="A-backed", cls="adr", text=f"librarian retrieval policy by value with backing; merged at {real_sha[:12]}", source="claude-fable"),
        Candidate(id="B-unbacked", cls="adr", text="librarian retrieval policy by value with backing; merged at deadbeef1234 (no such object)", source="claude-fable"),
        Candidate(id="C-zero-weight", cls="adr", text=f"librarian retrieval policy by value with backing; merged at {real_sha[:12]}", source="hermes"),
        Candidate(id="D-memory-demoted", cls="memory", text="librarian retrieval policy by value with backing (memory body)", source="claude-fable"),
        Candidate(id="E-irrelevant", cls="tao", text="the river does not argue with the stone", source="claude-fable"),
    ]
    lib = Librarian(root=tmp, git_root=DEFAULT_ROOT, memory_dir=None, extra_candidates=cands, load_corpus=False, trust_path=tmp / TRUST_REL)
    lib.candidates += load_ledgers(tmp)            # picks up F900 as a falsification candidate
    picks, lib.prior_picks = load_prior_picks(tmp)
    lib.candidates += picks
    lib._falsified_rows = [c for c in lib.candidates if c.cls == "falsification" and "FALSIFIED" in c.text]
    res = lib.recommend(q, budget=20000, stakes="high", n_max=10)
    ids = {s["id"]: s for s in res["items"]}

    check("A (real sha, ELEVATED source) is backed and in what_confirmed", "A-backed" in res["what_confirmed"], ids.get("A-backed", {}).get("backing"))
    check("B (unresolvable sha) never enters what_confirmed", "B-unbacked" in res["what_unconfirmed"] and "B-unbacked" not in res["what_confirmed"], ids.get("B-unbacked", {}).get("backing"))
    check("C (ZERO-WEIGHT source, real sha) contributes NO backing", ids.get("C-zero-weight", {}).get("backing") is None and "C-zero-weight" in res["what_unconfirmed"], ids.get("C-zero-weight", {}).get("backing_note"))
    check("fail-on-bad: the same sha that backs A is stripped from C by the source tier alone",
          ids.get("A-backed", {}).get("backing") and ids.get("C-zero-weight", {}).get("backing") is None)
    check("reserve_ratio present and counts what_confirmed:what_unconfirmed", res["reserve_ratio"]["ratio"] == f"{len(res['what_confirmed'])}:{len(res['what_unconfirmed'])}", res["reserve_ratio"])
    check("curation_debt present (list) and names the raw sinks", isinstance(res["curation_debt"], list) and any(d["class"] == "falsification" for d in res["curation_debt"]), [d["class"] for d in res["curation_debt"]])
    check("ouroboros: prior memory pick falsified by F900 -> class 'memory' demoted", res["ouroboros"]["class_demotions"].get("memory", 1.0) < 1.0, res["ouroboros"])
    check("D (memory) p_load_bearing < A (same overlap) because of the demotion", ids.get("D-memory-demoted", {}).get("p_load_bearing", 1) < ids.get("A-backed", {}).get("p_load_bearing", 0),
          (ids.get("D-memory-demoted", {}).get("p_load_bearing"), ids.get("A-backed", {}).get("p_load_bearing")))
    check("E (irrelevant) not retrieved: marginal value - cost < 0 stops the take", "E-irrelevant" not in ids, res["stopped_because"])
    check("p_load_bearing surfaced on every item; no action field anywhere", all("p_load_bearing" in s and "action" not in s for s in res["items"]))
    check("formula + notomation clause present", "formula" in res and "surfaced" in res["notomation"])
    tiny = lib.recommend(q, budget=40, stakes="high")
    check("budget respected: nothing over 40 bytes is taken; skips recorded", tiny["budget"]["used_bytes"] <= 40 and (tiny["skipped_for_displacement"] or not tiny["items"]), (tiny["budget"], len(tiny["skipped_for_displacement"])))
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Operator 21 Librarian: recommend(q, budget)")
    ap.add_argument("q", nargs="?", help="query")
    ap.add_argument("--budget", type=int, default=16000, help="context budget in bytes")
    ap.add_argument("--stakes", default="medium", choices=["low", "medium", "high", "critical"])
    ap.add_argument("--n-max", type=int, default=12)
    ap.add_argument("--classes", nargs="*", default=None)
    ap.add_argument("--out", default=None, help="write the result JSON here (e.g. _STATE/librarian/<date>-<slug>.json)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())
    if not a.q:
        ap.error("q is required (or --self-test)")
    res = Librarian().recommend(a.q, budget=a.budget, stakes=a.stakes, n_max=a.n_max, classes=a.classes)
    text = json.dumps(res, indent=2, ensure_ascii=False) + "\n"
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out}  items={len(res['items'])} reserve={res['reserve_ratio']['ratio']} stopped={res['stopped_because']}")
    else:
        print(text)


if __name__ == "__main__":
    main()
