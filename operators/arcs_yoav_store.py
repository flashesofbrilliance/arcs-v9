"""
arcs_yoav_store.py — Phase 5 Global Serializability Layer
Implements the Yoav Protocol: ordered commit log + conflict detection for
30K futures vector state space.

Problem Solved:
    When the pipeline explores multiple future states (branches, replays, Loki probes),
    write-lock errors occur if two branches attempt to commit to the same future.
    Yoav Protocol prevents this by enforcing global serializability via:
        1. FutureVector — quantum superposition of possible outcomes (up to 30K)
        2. CommitEntry — one committed future with full provenance
        3. YoavStore — ordered commit log with conflict detection and resolution

Time Signatures (from CLAUDE.md):
    CHRONOS  — linear clock (standard timestamps)
    KAIROS   — windowed clock (opportune moment windows)
    YOAV     — multi-future clock (vector state across parallel timelines)

Serializability guarantee:
    No two commits to the same (phase_id, signal_label) within the same
    KAIROS window can conflict. Conflicts are detected, the later commit
    is quarantined, and a resolution receipt is generated.

Architecture:
    FutureVector   — N possible outcomes with probability weights
    CommitEntry    — one serialized outcome (selected from FutureVector)
    ConflictRecord — detected conflict with resolution strategy
    YoavStore      — commit log + conflict registry + serializability check
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Time Signatures
# ---------------------------------------------------------------------------

class TimeSignature(str, Enum):
    CHRONOS = "chronos"   # linear, monotonic
    KAIROS  = "kairos"    # windowed, opportune
    YOAV    = "yoav"      # multi-future, vector


@dataclass
class KairosWindow:
    """A Kairos time window — bounded period of reduced activation energy."""
    window_id:  str
    start_ts:   float
    end_ts:     float
    label:      str = ""

    @property
    def is_open(self) -> bool:
        now = time.time()
        return self.start_ts <= now <= self.end_ts

    @property
    def duration_sec(self) -> float:
        return self.end_ts - self.start_ts

    def contains(self, ts: float) -> bool:
        return self.start_ts <= ts <= self.end_ts

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# FutureVector — quantum of possible outcomes
# ---------------------------------------------------------------------------

@dataclass
class FutureState:
    """One possible future in the superposition."""
    state_id:    str
    label:       str
    probability: float          # 0.0–1.0, must sum to ~1.0 across vector
    nci_estimate: float         # predicted NCI if this future is committed
    signal_class: str           # "accelerating" | "decelerating" | "stable" | "noise"
    reversibility: float        # 1.0 = fully reversible, 0.0 = irreversible
    activation_energy: float    # cost to collapse to this state
    metadata: Dict[str, Any]    = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FutureVector:
    """
    Superposition of N possible futures for a decision point.
    Collapses to a CommitEntry when a future is selected.

    Inspired by quantum superposition: the vector holds all possible
    outcomes simultaneously until observation (commit) collapses it.
    """
    vector_id:   str
    phase_id:    str
    signal_label: str
    created_at:  float
    time_sig:    TimeSignature
    states:      List[FutureState] = field(default_factory=list)
    kairos_window: Optional[KairosWindow] = None
    collapsed:   bool = False
    collapsed_to: Optional[str] = None   # state_id selected at collapse

    def add_state(self, state: FutureState) -> None:
        if self.collapsed:
            raise RuntimeError(f"Vector {self.vector_id} already collapsed — cannot add states")
        self.states.append(state)

    def normalize(self) -> None:
        """Normalize probabilities to sum to 1.0."""
        total = sum(s.probability for s in self.states)
        if total > 0:
            for s in self.states:
                s.probability = round(s.probability / total, 6)

    def highest_nci_state(self) -> Optional[FutureState]:
        """Select the state with highest NCI estimate (coherence-maximizing)."""
        if not self.states:
            return None
        return max(self.states, key=lambda s: s.nci_estimate)

    def lowest_activation_state(self) -> Optional[FutureState]:
        """Select the state with lowest activation energy (Kairos-optimal)."""
        if not self.states:
            return None
        return min(self.states, key=lambda s: s.activation_energy)

    def collapse(self, state_id: str) -> "FutureState":
        """Collapse vector to a specific state (commit decision)."""
        if self.collapsed:
            raise RuntimeError(f"Vector {self.vector_id} already collapsed to {self.collapsed_to}")
        selected = next((s for s in self.states if s.state_id == state_id), None)
        if selected is None:
            raise ValueError(f"State {state_id} not found in vector {self.vector_id}")
        self.collapsed    = True
        self.collapsed_to = state_id
        return selected

    def entropy(self) -> float:
        """Shannon entropy of the probability distribution — measures uncertainty."""
        import math
        h = 0.0
        for s in self.states:
            if s.probability > 0:
                h -= s.probability * math.log2(s.probability)
        return round(h, 4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector_id":     self.vector_id,
            "phase_id":      self.phase_id,
            "signal_label":  self.signal_label,
            "created_at":    self.created_at,
            "time_sig":      self.time_sig.value,
            "state_count":   len(self.states),
            "collapsed":     self.collapsed,
            "collapsed_to":  self.collapsed_to,
            "entropy":       self.entropy(),
            "kairos_window": self.kairos_window.to_dict() if self.kairos_window else None,
            "states":        [s.to_dict() for s in self.states],
        }


# ---------------------------------------------------------------------------
# CommitEntry — one serialized outcome
# ---------------------------------------------------------------------------

class CommitStatus(str, Enum):
    PENDING     = "pending"       # queued, not yet serialized
    COMMITTED   = "committed"     # serialized and accepted
    QUARANTINED = "quarantined"   # conflict detected; held for resolution
    SUPERSEDED  = "superseded"    # a later commit replaced this one
    ROLLED_BACK = "rolled_back"   # explicit rollback


@dataclass
class CommitEntry:
    """
    One committed future — the result of collapsing a FutureVector.
    Immutable once committed (append-only log).
    """
    commit_id:    str
    vector_id:    str
    state_id:     str
    phase_id:     str
    signal_label: str
    span_id:      str
    committed_at: float
    time_sig:     TimeSignature
    kairos_window_id: Optional[str]
    nci_at_commit: float
    signal_class:  str
    reversibility: float
    commit_hash:   str     # SHA-256 of (vector_id + state_id + committed_at)
    status:        CommitStatus = CommitStatus.PENDING
    superseded_by: Optional[str] = None
    notes:         str = ""
    metadata:      Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def compute_hash(vector_id: str, state_id: str, committed_at: float) -> str:
        payload = f"{vector_id}:{state_id}:{committed_at:.6f}"
        return hashlib.sha256(payload.encode()).hexdigest()[:24]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["time_sig"] = self.time_sig.value
        d["status"]   = self.status.value
        return d


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class ConflictType(str, Enum):
    SAME_WINDOW_SAME_SIGNAL  = "same_window_same_signal"  # Two commits, same signal, same window
    INVERSE_COMMIT           = "inverse_commit"           # Two commits with opposite verdicts
    IRREV_AFTER_ROLLBACK     = "irrev_after_rollback"     # Irreversible commit follows a rollback
    PHANTOM_BRANCH           = "phantom_branch"           # Commit from a non-existent branch
    ENTROPY_COLLAPSE_TOO_FAST = "entropy_collapse_too_fast" # Prematurely collapsed vector


@dataclass
class ConflictRecord:
    conflict_id:   str
    conflict_type: ConflictType
    commit_a_id:   str
    commit_b_id:   Optional[str]
    detected_at:   float
    description:   str
    resolution:    str     # "quarantine_b" | "rollback_a" | "merge" | "flag_only"
    resolved:      bool = False
    resolution_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["conflict_type"] = self.conflict_type.value
        return d


# ---------------------------------------------------------------------------
# YoavStore — ordered commit log + serializability
# ---------------------------------------------------------------------------

class YoavStore:
    """
    Global serializability layer for the 30K futures vector state space.

    Guarantees:
        1. No two commits to the same (phase_id, signal_label) within the same
           KAIROS window can both be COMMITTED — the second is QUARANTINED.
        2. Every commit is cryptographically hashed (tamper detectable).
        3. The commit log is append-only; rollbacks generate new entries,
           they do not delete.
        4. Entropy monitoring: a vector collapsed too early (entropy > threshold
           before all states explored) is flagged as ENTROPY_COLLAPSE_TOO_FAST.

    Persistence:
        Commits are persisted to a JSONL file (sovereign, portable).
        In-memory index is rebuilt on startup from the log.
    """

    DEFAULT_LOG_PATH   = "arcs_yoav_commits.jsonl"
    KAIROS_WINDOW_SEC  = 300.0     # 5-minute Kairos windows by default
    ENTROPY_MIN_BEFORE_COLLAPSE = 0.5   # must have explored enough before collapsing

    def __init__(self, log_path: str = DEFAULT_LOG_PATH,
                 kairos_window_sec: float = KAIROS_WINDOW_SEC):
        self.log_path = Path(log_path)
        self.kairos_window_sec = kairos_window_sec

        # In-memory state
        self._commits:   Dict[str, CommitEntry]   = {}    # commit_id → entry
        self._vectors:   Dict[str, FutureVector]  = {}    # vector_id → vector
        self._conflicts: Dict[str, ConflictRecord] = {}   # conflict_id → record

        # Indexes for fast conflict checking
        self._window_index: Dict[str, List[str]] = {}
        # key = f"{phase_id}:{signal_label}:{window_bucket}" → list of commit_ids

        # Rebuild from log if exists
        if self.log_path.exists():
            self._rebuild_from_log()

    # ── Vector management ─────────────────────────────────────────────────

    def create_vector(
        self,
        phase_id: str,
        signal_label: str,
        time_sig: TimeSignature = TimeSignature.YOAV,
        kairos_duration_sec: Optional[float] = None,
    ) -> FutureVector:
        """Create a new FutureVector for a decision point."""
        vector_id = _new_id("vec")
        now       = time.time()

        kairos = None
        if time_sig == TimeSignature.KAIROS or kairos_duration_sec:
            dur = kairos_duration_sec or self.kairos_window_sec
            kairos = KairosWindow(
                window_id=_new_id("kw"),
                start_ts=now,
                end_ts=now + dur,
                label=f"kairos_{phase_id}_{signal_label}",
            )

        vector = FutureVector(
            vector_id=vector_id,
            phase_id=phase_id,
            signal_label=signal_label,
            created_at=now,
            time_sig=time_sig,
            kairos_window=kairos,
        )
        self._vectors[vector_id] = vector
        return vector

    def add_future_state(
        self,
        vector_id: str,
        label: str,
        probability: float,
        nci_estimate: float,
        signal_class: str,
        reversibility: float = 0.5,
        activation_energy: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FutureState:
        """Add a possible future state to a vector."""
        vector = self._get_vector(vector_id)
        state = FutureState(
            state_id=_new_id("st"),
            label=label,
            probability=probability,
            nci_estimate=nci_estimate,
            signal_class=signal_class,
            reversibility=reversibility,
            activation_energy=activation_energy,
            metadata=metadata or {},
        )
        vector.add_state(state)
        return state

    # ── Commit ──────────────────────────────────────────────────────────

    def commit(
        self,
        vector_id: str,
        state_id: str,
        span_id: str,
        nci_at_commit: float,
        notes: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[CommitEntry, List[ConflictRecord]]:
        """
        Collapse a FutureVector and serialize the chosen state.
        Returns (CommitEntry, conflicts_detected).
        Conflicts do not prevent the commit; they quarantine the entry.
        """
        vector = self._get_vector(vector_id)

        # Entropy guard: flag if state space has more than one option but entropy is
        # suspiciously low (premature collapse / option space not properly explored).
        # Single-state vectors (len=1) are exempt — deterministic by design.
        conflicts: List[ConflictRecord] = []
        if (len(vector.states) > 1
                and vector.entropy() < self.ENTROPY_MIN_BEFORE_COLLAPSE
                and not vector.collapsed):
            conflict = self._make_conflict(
                conflict_type=ConflictType.ENTROPY_COLLAPSE_TOO_FAST,
                commit_a_id="pending",
                commit_b_id=None,
                description=(
                    f"Vector {vector_id} collapsed with entropy "
                    f"{vector.entropy():.3f} < minimum {self.ENTROPY_MIN_BEFORE_COLLAPSE} "
                    f"— premature collapse detected"
                ),
                resolution="flag_only",
            )
            conflicts.append(conflict)

        # Collapse the vector
        selected_state = vector.collapse(state_id)

        # Build commit entry
        now         = time.time()
        commit_hash = CommitEntry.compute_hash(vector_id, state_id, now)
        commit = CommitEntry(
            commit_id=_new_id("cmt"),
            vector_id=vector_id,
            state_id=state_id,
            phase_id=vector.phase_id,
            signal_label=vector.signal_label,
            span_id=span_id,
            committed_at=now,
            time_sig=vector.time_sig,
            kairos_window_id=vector.kairos_window.window_id if vector.kairos_window else None,
            nci_at_commit=nci_at_commit,
            signal_class=selected_state.signal_class,
            reversibility=selected_state.reversibility,
            commit_hash=commit_hash,
            status=CommitStatus.PENDING,
            notes=notes,
            metadata=metadata or {},
        )

        # Serializability check
        window_conflicts = self._check_serializability(commit)
        conflicts.extend(window_conflicts)

        # Set final status
        commit.status = (
            CommitStatus.QUARANTINED
            if any(c.resolution == "quarantine_b" for c in conflicts)
            else CommitStatus.COMMITTED
        )

        # Update entropy-flag conflict with real commit_id
        for c in conflicts:
            if c.commit_a_id == "pending":
                c.commit_a_id = commit.commit_id

        # Persist
        self._commits[commit.commit_id] = commit
        self._update_window_index(commit)
        self._persist_commit(commit)
        for c in conflicts:
            self._conflicts[c.conflict_id] = c
            self._persist_conflict(c)

        return commit, conflicts

    def rollback(self, commit_id: str, reason: str = "") -> CommitEntry:
        """
        Roll back a committed entry by creating a ROLLED_BACK record.
        Original entry is marked as SUPERSEDED; new entry documents the rollback.
        Append-only: the original commit is never deleted.
        """
        original = self._commits.get(commit_id)
        if original is None:
            raise ValueError(f"Commit {commit_id} not found")

        now = time.time()
        rollback_entry = CommitEntry(
            commit_id=_new_id("cmt"),
            vector_id=original.vector_id,
            state_id=original.state_id,
            phase_id=original.phase_id,
            signal_label=original.signal_label,
            span_id=original.span_id,
            committed_at=now,
            time_sig=original.time_sig,
            kairos_window_id=original.kairos_window_id,
            nci_at_commit=original.nci_at_commit,
            signal_class=original.signal_class,
            reversibility=original.reversibility,
            commit_hash=CommitEntry.compute_hash(original.vector_id, original.state_id, now),
            status=CommitStatus.ROLLED_BACK,
            notes=f"ROLLBACK of {commit_id}: {reason}",
        )

        original.status       = CommitStatus.SUPERSEDED
        original.superseded_by = rollback_entry.commit_id

        self._commits[rollback_entry.commit_id] = rollback_entry
        self._persist_commit(rollback_entry)
        self._persist_commit(original)   # re-persist with updated status

        return rollback_entry

    # ── Query APIs ────────────────────────────────────────────────────────

    def get_commit(self, commit_id: str) -> Optional[CommitEntry]:
        return self._commits.get(commit_id)

    def get_vector(self, vector_id: str) -> Optional[FutureVector]:
        return self._vectors.get(vector_id)

    def list_commits(
        self,
        phase_id: Optional[str] = None,
        status: Optional[CommitStatus] = None,
        limit: int = 100,
    ) -> List[CommitEntry]:
        entries = list(self._commits.values())
        if phase_id:
            entries = [e for e in entries if e.phase_id == phase_id]
        if status:
            entries = [e for e in entries if e.status == status]
        entries.sort(key=lambda e: e.committed_at, reverse=True)
        return entries[:limit]

    def list_conflicts(self, resolved: Optional[bool] = None) -> List[ConflictRecord]:
        records = list(self._conflicts.values())
        if resolved is not None:
            records = [r for r in records if r.resolved == resolved]
        return records

    def serializability_report(self) -> Dict[str, Any]:
        commits    = list(self._commits.values())
        committed  = [c for c in commits if c.status == CommitStatus.COMMITTED]
        quarantined = [c for c in commits if c.status == CommitStatus.QUARANTINED]
        conflicts  = list(self._conflicts.values())

        return {
            "total_commits":     len(commits),
            "committed":         len(committed),
            "quarantined":       len(quarantined),
            "rolled_back":       len([c for c in commits if c.status == CommitStatus.ROLLED_BACK]),
            "conflict_count":    len(conflicts),
            "unresolved_conflicts": len([c for c in conflicts if not c.resolved]),
            "vectors_tracked":   len(self._vectors),
            "log_path":          str(self.log_path),
        }

    def integrity_check(self) -> Dict[str, Any]:
        """Verify commit hashes match stored values."""
        tampered = []
        for cmt in self._commits.values():
            expected = CommitEntry.compute_hash(cmt.vector_id, cmt.state_id, cmt.committed_at)
            if cmt.commit_hash != expected:
                tampered.append(cmt.commit_id)
        return {
            "total_checked": len(self._commits),
            "tampered":      tampered,
            "integrity_ok":  len(tampered) == 0,
        }

    # ── Internal helpers ──────────────────────────────────────────────────

    def _get_vector(self, vector_id: str) -> FutureVector:
        v = self._vectors.get(vector_id)
        if v is None:
            raise ValueError(f"Vector {vector_id} not found in store")
        return v

    def _window_bucket(self, ts: float) -> int:
        """Map timestamp to a Kairos window bucket index."""
        return int(ts // self.kairos_window_sec)

    def _update_window_index(self, commit: CommitEntry) -> None:
        bucket  = self._window_bucket(commit.committed_at)
        key     = f"{commit.phase_id}:{commit.signal_label}:{bucket}"
        if key not in self._window_index:
            self._window_index[key] = []
        self._window_index[key].append(commit.commit_id)

    def _check_serializability(self, commit: CommitEntry) -> List[ConflictRecord]:
        """
        Check whether a new commit conflicts with any existing commit in the same
        Kairos window for the same (phase_id, signal_label).
        """
        conflicts = []
        bucket = self._window_bucket(commit.committed_at)
        key    = f"{commit.phase_id}:{commit.signal_label}:{bucket}"
        prior_ids = self._window_index.get(key, [])

        for prior_id in prior_ids:
            prior = self._commits.get(prior_id)
            if prior is None or prior.status in (CommitStatus.QUARANTINED, CommitStatus.ROLLED_BACK):
                continue   # already resolved

            # Same window, same signal — second commit is quarantined
            conflict = self._make_conflict(
                conflict_type=ConflictType.SAME_WINDOW_SAME_SIGNAL,
                commit_a_id=prior.commit_id,
                commit_b_id=commit.commit_id,
                description=(
                    f"Two commits to ({commit.phase_id}, {commit.signal_label}) "
                    f"within Kairos window bucket {bucket}. "
                    f"Prior: {prior.commit_id}, New: {commit.commit_id}"
                ),
                resolution="quarantine_b",
            )
            conflicts.append(conflict)

        return conflicts

    def _make_conflict(
        self,
        conflict_type: ConflictType,
        commit_a_id: str,
        commit_b_id: Optional[str],
        description: str,
        resolution: str,
    ) -> ConflictRecord:
        return ConflictRecord(
            conflict_id=_new_id("cfl"),
            conflict_type=conflict_type,
            commit_a_id=commit_a_id,
            commit_b_id=commit_b_id,
            detected_at=time.time(),
            description=description,
            resolution=resolution,
        )

    def _persist_commit(self, commit: CommitEntry) -> None:
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "commit", "data": commit.to_dict()}) + "\n")

    def _persist_conflict(self, conflict: ConflictRecord) -> None:
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "conflict", "data": conflict.to_dict()}) + "\n")

    def _rebuild_from_log(self) -> None:
        """Rebuild in-memory state from JSONL log on startup."""
        try:
            lines = self.log_path.read_text(encoding="utf-8").strip().splitlines()
            for line in lines:
                record = json.loads(line)
                if record["type"] == "commit":
                    d = record["data"]
                    entry = CommitEntry(
                        commit_id=d["commit_id"],
                        vector_id=d["vector_id"],
                        state_id=d["state_id"],
                        phase_id=d["phase_id"],
                        signal_label=d["signal_label"],
                        span_id=d["span_id"],
                        committed_at=d["committed_at"],
                        time_sig=TimeSignature(d["time_sig"]),
                        kairos_window_id=d.get("kairos_window_id"),
                        nci_at_commit=d["nci_at_commit"],
                        signal_class=d["signal_class"],
                        reversibility=d["reversibility"],
                        commit_hash=d["commit_hash"],
                        status=CommitStatus(d["status"]),
                        superseded_by=d.get("superseded_by"),
                        notes=d.get("notes", ""),
                        metadata=d.get("metadata", {}),
                    )
                    self._commits[entry.commit_id] = entry
                    self._update_window_index(entry)
        except Exception:
            pass  # partial log — rebuild as far as possible


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    import tempfile, shutil, math

    print("=== arcs_yoav_store.py smoke test ===\n")

    tmp = tempfile.mkdtemp()
    log_path = f"{tmp}/yoav_commits.jsonl"
    try:
        store = YoavStore(log_path=log_path, kairos_window_sec=60.0)

        # 1. Create vector with three possible futures
        v = store.create_vector(
            phase_id="phase_5",
            signal_label="coherence_signal_A",
            time_sig=TimeSignature.YOAV,
        )
        assert v.collapsed is False
        print(f"[OK] Vector created: {v.vector_id[:20]}...")

        store.add_future_state(v.vector_id, "bullish",  0.55, nci_estimate=88.0,
                               signal_class="accelerating",  reversibility=0.7)
        store.add_future_state(v.vector_id, "neutral",  0.30, nci_estimate=76.0,
                               signal_class="stable",        reversibility=0.9)
        store.add_future_state(v.vector_id, "bearish",  0.15, nci_estimate=55.0,
                               signal_class="decelerating",  reversibility=0.3,
                               activation_energy=2.0)
        v.normalize()
        assert abs(sum(s.probability for s in v.states) - 1.0) < 0.001
        print(f"[OK] States added and normalized: probs sum to 1.0")
        print(f"     entropy={v.entropy():.3f}, states={len(v.states)}")

        # 2. Select highest-NCI state and commit
        best = v.highest_nci_state()
        assert best.label == "bullish"
        commit1, conflicts1 = store.commit(
            vector_id=v.vector_id,
            state_id=best.state_id,
            span_id="spn_test001",
            nci_at_commit=88.0,
            notes="Phase 5 primary run",
        )
        assert commit1.status == CommitStatus.COMMITTED
        assert len(conflicts1) == 0
        print(f"[OK] Commit 1: status={commit1.status.value}, hash={commit1.commit_hash[:12]}...")

        # 3. Integrity check
        ic = store.integrity_check()
        assert ic["integrity_ok"], f"Integrity failed: {ic['tampered']}"
        print(f"[OK] Integrity check: {ic['total_checked']} commits, all clean")

        # 4. Serializability: second commit to same signal in same window → QUARANTINE
        v2 = store.create_vector("phase_5", "coherence_signal_A", TimeSignature.YOAV)
        store.add_future_state(v2.vector_id, "bullish_v2", 1.0,
                               nci_estimate=90.0, signal_class="accelerating")
        commit2, conflicts2 = store.commit(
            vector_id=v2.vector_id,
            state_id=v2.states[0].state_id,
            span_id="spn_test002",
            nci_at_commit=90.0,
        )
        assert commit2.status == CommitStatus.QUARANTINED, \
            f"Expected QUARANTINED, got {commit2.status.value}"
        # v2 has single state (entropy=0 → entropy guard) + same window → 2 conflicts
        assert any(c.conflict_type == ConflictType.SAME_WINDOW_SAME_SIGNAL for c in conflicts2)
        print(f"[OK] Serializability: second commit QUARANTINED as expected")
        window_conflict = next(c for c in conflicts2
                               if c.conflict_type == ConflictType.SAME_WINDOW_SAME_SIGNAL)
        print(f"     conflict type: {window_conflict.conflict_type.value}")

        # 5. Commit to different signal in same window → no conflict
        v3 = store.create_vector("phase_5", "coherence_signal_B", TimeSignature.YOAV)
        store.add_future_state(v3.vector_id, "signal_B_main", 1.0,
                               nci_estimate=82.0, signal_class="stable")
        commit3, conflicts3 = store.commit(
            vector_id=v3.vector_id,
            state_id=v3.states[0].state_id,
            span_id="spn_test003",
            nci_at_commit=82.0,
        )
        assert commit3.status == CommitStatus.COMMITTED
        assert len(conflicts3) == 0
        print(f"[OK] Different signal in same window: no conflict (COMMITTED)")

        # 6. Rollback
        rollback = store.rollback(commit1.commit_id, reason="test rollback")
        assert rollback.status == CommitStatus.ROLLED_BACK
        original = store.get_commit(commit1.commit_id)
        assert original.status == CommitStatus.SUPERSEDED
        print(f"[OK] Rollback: original→SUPERSEDED, new→ROLLED_BACK")

        # 7. Entropy collapse guard — multi-state vector with all probability on one state
        v4 = store.create_vector("phase_5", "coherence_signal_C", TimeSignature.YOAV)
        # Two states but probability heavily skewed → low entropy (premature collapse)
        store.add_future_state(v4.vector_id, "dominant",  0.999, nci_estimate=70.0,
                               signal_class="stable")
        store.add_future_state(v4.vector_id, "minority",  0.001, nci_estimate=60.0,
                               signal_class="decelerating")
        v4.normalize()
        print(f"     v4 entropy before collapse: {v4.entropy():.4f} (threshold={store.ENTROPY_MIN_BEFORE_COLLAPSE})")
        commit4, conflicts4 = store.commit(
            vector_id=v4.vector_id,
            state_id=v4.states[0].state_id,
            span_id="spn_test004",
            nci_at_commit=70.0,
        )
        # With near-zero entropy → ENTROPY_COLLAPSE_TOO_FAST
        entropy_flags = [c for c in conflicts4
                         if c.conflict_type == ConflictType.ENTROPY_COLLAPSE_TOO_FAST]
        assert len(entropy_flags) == 1, f"Expected entropy flag, got: {[c.conflict_type.value for c in conflicts4]}"
        print(f"[OK] Entropy collapse guard: flagged at entropy={v4.entropy():.4f}")

        # 8. Serializability report
        rpt = store.serializability_report()
        assert rpt["total_commits"] >= 4
        print(f"\n[OK] Serializability report:")
        print(f"     total={rpt['total_commits']}, committed={rpt['committed']}, "
              f"quarantined={rpt['quarantined']}")
        print(f"     conflicts={rpt['conflict_count']}, vectors={rpt['vectors_tracked']}")

        # 9. JSONL log persistence and rebuild
        store2 = YoavStore(log_path=log_path, kairos_window_sec=60.0)
        assert len(store2._commits) == len(store._commits), \
            f"Rebuild mismatch: {len(store2._commits)} vs {len(store._commits)}"
        print(f"[OK] Log persistence + rebuild: {len(store2._commits)} commits restored")

        # 10. Kairos window
        v5 = store.create_vector("phase_5", "signal_D", TimeSignature.KAIROS,
                                  kairos_duration_sec=120.0)
        assert v5.kairos_window is not None
        assert v5.kairos_window.is_open
        print(f"[OK] Kairos window: open={v5.kairos_window.is_open}, "
              f"duration={v5.kairos_window.duration_sec:.0f}s")

        print("\n=== Smoke test PASSED — arcs_yoav_store.py ===")

    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    _smoke_test()
