"""
arcs_echo_embedding.py — ARCS v9
Embedding-backed signature / orthogonality pair for the Orthogonal Echo Detector.

> Companion to arcs_inchworm_echo.py (RC-OPS-001). It does NOT modify the detector; it
> supplies the two injectables the detector already exposes:
>
>     detector = build_embedding_detector()          # OrthogonalEchoDetector(signature_fn=..., orthogonality_fn=...)
>
> The default detector's signature is keyword matching (word overlap against PATTERN_LIBRARY) and its
> default orthogonality is a function of the domain NAMES. Both fire on word-scrambled controls
> (2026-09-27 feed: 0 real matches, FP proxy 0.8) because bags of words survive scrambling.
> This module replaces both with functions of the TEXT:
>
>   signature_fn(domain, text)  -> EmbeddedMotionSignature
>       Segments the text (lines, then sentences), embeds every segment and every PATTERN_LIBRARY
>       keyword phrase with the same local sentence-transformers model that operators/arcs_api.py
>       serves at POST /api/embed (get_embed_model; ARCS_EMBED_MODEL, default all-MiniLM-L6-v2),
>       and keeps a keyword as evidence when some segment is within cosine >= KEYWORD_TAU of it.
>       The keyword list is what the detector's unchanged _score_pattern reads. The signature also
>       carries the domain's mean segment vector (`vector`) and a per-pattern activation
>       (max segment<->pattern-gloss cosine), for callers that want the continuous view.
>
>   orthogonality_fn(domain_a, domain_b) -> float
>       The detector calls this with the two domain NAMES (its interface). Here the names are only
>       the lookup handle: the value is 1 - cosine(vector_a, vector_b) over the domain TEXT vectors
>       recorded by signature_fn in the same run, clipped to [0, 1]. Two texts that say the same
>       thing are not orthogonal even if their names differ; two scrambled controls that were dealt
>       from one word pool converge, which is exactly why the control should lose score.
>       A name whose text was never seen falls back to the detector's own name-based default and
>       says so on stderr, once. This is the honest limit of the interface: orthogonality is
>       content-based only for domains that passed through signature_fn first (the detector always
>       does this: it builds every signature before scoring any pair).
>
> Thresholds are pre-registered here, not tuned on the ridgeline stones (memory:
> pre-register-rule-before-counting). KEYWORD_TAU 0.45 came from the module's own smoke domains:
> chosen so the three canonical smoke domains fire and their word-scrambled control does not.
> If a later run moves it, that run's receipt must say so.
>
> Dependencies: sentence-transformers is the `embeddings` extra already declared in
> operators/pyproject.toml (no new dependency). The model is loaded lazily and read from the local
> HF cache; nothing here makes a network call once the model is cached. Without the extra, the
> factory raises ImportError with the install line — it never silently degrades to keywords.

Usage:
    operators/.venv/bin/python operators/arcs_echo_embedding.py --self-test
"""

from __future__ import annotations

import math
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Callable, Optional

from arcs_inchworm_echo import (
    PATTERN_LIBRARY,
    MotionSignature,
    OrthogonalEchoDetector,
    _default_orthogonality,
)

KEYWORD_TAU: float = 0.45       # keyword phrase counts as evidence when some segment is this close
MIN_SEGMENT_TOKENS: int = 4     # shorter segments are headings / bullets glyphs, not motion
MAX_SEGMENTS_PER_DOMAIN: int = 400

# One-sentence gloss per pattern: what the motion looks like, content-free. Used for the
# continuous per-pattern activation that rides along on the signature (not for scoring).
PATTERN_GLOSS: dict = {
    "autocatalytic_loop":        "a self-reinforcing loop where the output feeds back as input and growth compounds",
    "punctuated_equilibrium":    "a long stable plateau followed by a sudden rapid shift to a new state",
    "ratchet_irreversibility":   "a one-way change that locks in and cannot be undone or rolled back",
    "predator_prey_oscillation": "boom and bust cycles that overshoot, collapse, and rise again with a lag",
    "diffusion_gradient":        "something spreads from where it is concentrated to where it is sparse until it equalizes",
    "threshold_cascade":         "a small push past a tipping point sets off a chain reaction or cascade",
    "bottleneck_throughput":     "one constraint or single point of failure limits the flow of the whole system",
    "adaptive_immune_memory":    "the first encounter is costly, later ones are cheap because the system remembers and adapts",
}

EMBED_MODEL_NAME = os.environ.get("ARCS_EMBED_MODEL", "all-MiniLM-L6-v2")
_model = None
_model_source = None


def get_embed_model():
    """Prefer the exact loader arcs_api.py serves at /api/embed; fall back to the same model
    name when arcs_api's own imports (fastapi et al.) are not installed in this interpreter."""
    global _model, _model_source
    if _model is not None:
        return _model
    try:
        from arcs_api import get_embed_model as _api_loader   # same model, same env var
        _model = _api_loader()
        _model_source = "arcs_api.get_embed_model"
        return _model
    except ImportError:
        pass
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:   # pragma: no cover
        raise ImportError(
            "sentence-transformers not installed in this interpreter. It is the declared "
            "`embeddings` extra: operators/.venv/bin/pip install -e 'operators[embeddings]' "
            "(or pip install 'sentence-transformers>=3.0')."
        ) from e
    _model = SentenceTransformer(EMBED_MODEL_NAME)
    _model_source = f"sentence_transformers.SentenceTransformer({EMBED_MODEL_NAME!r})"
    return _model


def model_source() -> Optional[str]:
    return _model_source


# ── text -> segments ──────────────────────────────────────────────────────────

_SENT_SPLIT = re.compile(r"(?<=[.!?;])\s+")
_MD_NOISE = re.compile(r"^[\s#>*\-\d.)`|]+")


def segment(text: str) -> list:
    out = []
    for line in text.splitlines():
        line = _MD_NOISE.sub("", line).strip()
        if not line:
            continue
        for s in _SENT_SPLIT.split(line):
            s = s.strip()
            if len(re.findall(r"[A-Za-z]+", s)) >= MIN_SEGMENT_TOKENS:
                out.append(s)
    return out[:MAX_SEGMENTS_PER_DOMAIN]


# ── vectors ───────────────────────────────────────────────────────────────────

def _cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _mean(vectors) -> list:
    if not vectors:
        return []
    n = len(vectors)
    return [sum(v[i] for v in vectors) / n for i in range(len(vectors[0]))]


@dataclass
class EmbeddedMotionSignature(MotionSignature):
    """MotionSignature (domain, keywords, raw_text) + the continuous view."""
    vector:             list = field(default_factory=list)   # mean segment embedding
    pattern_activation: dict = field(default_factory=dict)   # pattern -> max segment<->gloss cosine
    keyword_evidence:   dict = field(default_factory=dict)   # keyword -> (best cosine, best segment)
    n_segments:         int = 0


class EmbeddingEcho:
    """Holds the shared state (keyword/gloss vectors, per-run domain vectors) behind the two
    injectables. One instance per detector."""

    def __init__(self, keyword_tau: float = KEYWORD_TAU, fallback: Callable = _default_orthogonality):
        self.keyword_tau = keyword_tau
        self._fallback = fallback
        self._vectors: dict = {}          # domain name -> mean vector, refreshed per signature call
        self._kw_vecs: Optional[dict] = None
        self._gloss_vecs: Optional[dict] = None
        self._warned = set()
        self.calls = {"signature": 0, "orthogonality": 0, "orthogonality_fallback": 0}

    # -- lazy library vectors --
    def _library(self):
        if self._kw_vecs is None:
            model = get_embed_model()
            kws = sorted({k for kws in PATTERN_LIBRARY.values() for k in kws})
            kv = model.encode(kws, normalize_embeddings=True)
            self._kw_vecs = {k: [float(x) for x in v] for k, v in zip(kws, kv)}
            names = list(PATTERN_GLOSS)
            gv = model.encode([PATTERN_GLOSS[n] for n in names], normalize_embeddings=True)
            self._gloss_vecs = {n: [float(x) for x in v] for n, v in zip(names, gv)}
        return self._kw_vecs, self._gloss_vecs

    # -- injectable 1 --
    def signature(self, domain: str, text: str) -> EmbeddedMotionSignature:
        self.calls["signature"] += 1
        kw_vecs, gloss_vecs = self._library()
        segs = segment(text)
        if not segs:
            self._vectors[domain] = []
            return EmbeddedMotionSignature(domain=domain, keywords=[], raw_text=text)
        model = get_embed_model()
        sv = [[float(x) for x in v] for v in model.encode(segs, normalize_embeddings=True)]
        mean = _mean(sv)
        self._vectors[domain] = mean
        evidence: dict = {}
        for kw, kvec in kw_vecs.items():
            best_i = max(range(len(sv)), key=lambda i: _cosine(sv[i], kvec))
            best = _cosine(sv[best_i], kvec)
            if best >= self.keyword_tau:
                evidence[kw] = (round(best, 4), segs[best_i])
        activation = {p: round(max(_cosine(s, gvec) for s in sv), 4) for p, gvec in gloss_vecs.items()}
        # keyword order: strongest first, so evidence lists read as ranked
        keywords = sorted(evidence, key=lambda k: -evidence[k][0])
        return EmbeddedMotionSignature(
            domain=domain, keywords=keywords, raw_text=text,
            vector=mean, pattern_activation=activation, keyword_evidence=evidence, n_segments=len(segs),
        )

    # -- injectable 2 --
    def orthogonality(self, domain_a: str, domain_b: str) -> float:
        self.calls["orthogonality"] += 1
        va, vb = self._vectors.get(domain_a), self._vectors.get(domain_b)
        if not va or not vb:
            self.calls["orthogonality_fallback"] += 1
            key = (domain_a, domain_b)
            if key not in self._warned:
                self._warned.add(key)
                print(f"arcs_echo_embedding: no text vector for {domain_a!r}/{domain_b!r}; "
                      f"falling back to name-based orthogonality", file=sys.stderr)
            return self._fallback(domain_a, domain_b)
        return round(min(1.0, max(0.0, 1.0 - _cosine(va, vb))), 4)

    def reset(self):
        self._vectors.clear()


def build_embedding_detector(min_similarity: float = 0.20, keyword_tau: float = KEYWORD_TAU) -> OrthogonalEchoDetector:
    """The detector with both injectables bound to one EmbeddingEcho. The instance is reachable as
    detector._echo for callers that want call counts or the continuous activations."""
    echo = EmbeddingEcho(keyword_tau=keyword_tau)
    det = OrthogonalEchoDetector(
        signature_fn=echo.signature,
        orthogonality_fn=echo.orthogonality,
        min_similarity=min_similarity,
    )
    det._echo = echo  # type: ignore[attr-defined]
    return det


# ── self-test: pass-on-good, fail-on-bad, injectables actually invoked ─────────

SMOKE_DOMAINS = {
    "organisational behaviour": (
        "teams gradually stop attending rituals when tooling fails repeatedly; "
        "trust erodes across a long stable period then collapses suddenly; "
        "rebuilding requires a triggering success event and recovery of trust"
    ),
    "evolutionary biology": (
        "species remain in stable stasis across long periods then rapidly speciate "
        "after environmental shock or sudden habitat disruption"
    ),
    "infrastructure engineering": (
        "systems degrade slowly until a threshold is crossed then cascade-fail; "
        "recovery requires isolating the bottleneck constraint and relieving it first"
    ),
}


def _scramble(texts: dict, seed: int = 1) -> dict:
    import random
    rng = random.Random(seed)
    words = [w for t in texts.values() for w in t.split()]
    rng.shuffle(words)
    out, i = {}, 0
    for d, t in texts.items():
        n = len(t.split()); out[d] = " ".join(words[i:i + n]); i += n
    return out


def self_test() -> int:
    try:
        get_embed_model()
    except ImportError as e:
        print(f"SKIP  {e}")
        return 3
    fails = 0

    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'PASS' if cond else 'FAIL'}  {label}  {detail}")
        fails += 0 if cond else 1

    det = build_embedding_detector()
    echo = det._echo
    good = det.run(SMOKE_DOMAINS)
    check("pass-on-good: smoke domains produce >= 1 echo", len(good.matches) >= 1,
          f"matches={len(good.matches)} top={good.top_pattern}")
    check("signature_fn invoked once per domain", echo.calls["signature"] == len(SMOKE_DOMAINS), echo.calls)
    check("orthogonality_fn invoked, never fell back to names",
          echo.calls["orthogonality"] > 0 and echo.calls["orthogonality_fallback"] == 0, echo.calls)
    names = list(SMOKE_DOMAINS)
    o_ab = echo.orthogonality(names[0], names[1])
    check("orthogonality is a function of text: 0 < orth(a,b) < 1 (name-default would be exactly 1.0)",
          0.0 < o_ab < 1.0, f"orth={o_ab}")
    # same NAMES, one text swapped -> orthogonality must change (proves the value tracks content)
    swapped = dict(SMOKE_DOMAINS); swapped[names[1]] = SMOKE_DOMAINS[names[0]]
    det.run(swapped)
    o_same = echo.orthogonality(names[0], names[1])
    check("same names, identical texts -> orthogonality ~ 0", o_same < 0.05, f"orth={o_same}")
    bad = det.run(_scramble(SMOKE_DOMAINS))
    check("fail-on-bad: word-scrambled control yields fewer echoes than the real text",
          len(bad.matches) < len(good.matches), f"scrambled={len(bad.matches)} real={len(good.matches)}")
    print(f"  model: {model_source()}  keyword_tau={KEYWORD_TAU}")
    print(f"self-test: {'OK' if fails == 0 else f'{fails} FAIL'}")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    det = build_embedding_detector()
    print(det.run(SMOKE_DOMAINS).to_brief())
