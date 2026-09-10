"""Quantum Study Coach — daily prescription engine across all study apps.

Turns cross-app history (see dashboard.py for schemas) into a concrete,
rules-based plan for today.  Deterministic given the data; no network, no API.

Usage:
    python coach.py                # today's plan (default)
    python coach.py --diagnostic   # 20-question placement quiz
    python coach.py --badges      # IBM Quantum Learning badge checklist
    python coach.py --review      # unified SRS review queue

Data dir defaults to dashboard.DATA_DIR (~/.local/share/quantum-study/)
and can be overridden with the QUANTUM_STUDY_DATA_DIR environment variable.

Flagged-for-review items: every "<prefix>_flagged.json" in the data dir
(plus flashcard-drill's legacy flagged_cards.json) is discovered at run
time.  Entries may be bare string ids or dicts per the suite's flagging
contract — {"id", "label", "category", "app", "timestamp"}, only "id"
required.  The app comes from the entry's "app" field, else from the file
prefix (quiz_ -> quantum-quiz, math_ -> math-quiz, ...); undated entries
take the file's mtime.  Items dedupe by (app, id); --review shows the
REVIEW_CAP oldest and says how many more were dropped.

Coach state is stored in <data dir>/coach_state.json:

    {
      "activity_dates": ["YYYY-MM-DD", ...],   # days with real study activity
      "current_streak": int,
      "best_streak": int,
      "badges": {"<badge name>": "not_started"|"in_progress"|"earned"},
      "diagnostic": {"timestamp": float,
                     "rungs": {"<rung>": {"total": n, "correct": n}},
                     "recommended_rung": "<rung>"},
      "last_plan_date": "YYYY-MM-DD"
    }
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# Reuse dashboard's schema knowledge + half-life weighting.  Import the module
# (not individual names) so its helpers stay in one place.
import dashboard

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR")
                or dashboard.DATA_DIR).expanduser()
STATE_PATH = DATA_DIR / "coach_state.json"

_NOW = time.time()
_TODAY = datetime.now().strftime("%Y-%m-%d")

STALE_DAYS = 7            # untouched for more than this many whole days = "stale"
FOCUS_MAX_AVG = 8.0       # a category / exam section / kata section already
                          # averaging this (of 10, i.e. 80%) or better is solid
                          # and is not prescribed as focus work in the plan
REVIEW_WINDOW_DAYS = 30   # low-score attempts newer than this are reviewable
REVIEW_LOW_SCORE = 5.0    # attempts scoring below this go to the review queue
REVIEW_CAP = 20
EXAM_PASS_CORRECT = 47    # C1000-179 style pass line
EXAM_PASS_TOTAL = 68

# History files the coach reads (relative to DATA_DIR).  App keys are the
# runnable app names printed in plans.
_HISTORY_FILES = {
    "qec-trainer":     "qec_history.json",
    "vqa-trainer":     "vqa_history.json",
    "flashcard-drill": "flashcard_history.json",
    "circuit-trainer": "trainer_history.json",
    "math-quiz":       "math_history.json",
    "quantum-quiz":    "quiz_history.json",
    "paper-drill":     "paper_history.json",
    "qiskit-dojo":     "dojo_history.json",
    "exam-sim":        "exam_history.json",
    "problem-trainer": "problems_history.json",
}

# Flagged-for-review files are discovered at run time: every
# "<prefix>_flagged.json" in DATA_DIR, where <prefix> is the app's history
# filename prefix (qec_ -> qec-trainer, quiz_ -> quantum-quiz, ...).
# flashcard-drill predates the convention and writes flagged_cards.json.
_FLAGGED_GLOB = "*_flagged.json"
_LEGACY_FLAGGED_FILES = {"flagged_cards.json": "flashcard-drill"}
_PREFIX_TO_APP = {fname[:-len("_history.json")]: app
                  for app, fname in _HISTORY_FILES.items()}

# Curriculum rungs, in docs-ladder order, with their docs dir + practice app.
RUNGS = [
    ("math",       "docs/01_mathematical_foundations",   "math-quiz"),
    ("qm",         "docs/02_quantum_mechanics",          "quantum-quiz"),
    ("circuits",   "docs/03_quantum_gates_and_circuits", "circuit-trainer"),
    ("algorithms", "docs/04_quantum_algorithms",         "quantum-quiz"),
    ("qec",        "docs/05_quantum_error_correction",   "qec-trainer"),
    ("vqa",        "docs/06_variational_quantum_algorithms", "vqa-trainer"),
    ("hardware",   "docs/07_quantum_hardware",           "flashcard-drill"),
    ("qiskit-api", "docs/08_advanced_topics",            "qiskit-dojo"),
]
RUNG_ORDER = [r[0] for r in RUNGS]

BADGES = [
    "Basics of Quantum Information",
    "Fundamentals of Quantum Algorithms",
    "General Formulation of Quantum Information",
    "Foundations of Quantum Error Correction",
    "Variational Algorithm Design",
    "Quantum Computing in Practice",
    "C1000-179 Certification (Qiskit Associate Developer)",
]
BADGE_STATUSES = ["not_started", "in_progress", "earned"]
_BADGE_LABEL = {"not_started": "not started", "in_progress": "IN PROGRESS",
                "earned": "EARNED"}


# ---------------------------------------------------------------------------
# 20-question diagnostic (2-3 per rung; answer index is 0-based)
# ---------------------------------------------------------------------------

DIAGNOSTIC_QUESTIONS = [
    # -- math (3) --
    {"rung": "math", "q": "The inner product <0|1> equals:",
     "choices": ["0", "1", "1/sqrt(2)", "-1"], "answer": 0},
    {"rung": "math", "q": "The eigenvalues of the Pauli Z matrix are:",
     "choices": ["0 and 1", "+1 and -1", "+i and -i", "+1 only"], "answer": 1},
    {"rung": "math", "q": "A matrix U is unitary when:",
     "choices": ["U = U^T", "U^dagger U = I", "det(U) = 0", "U^2 = I"],
     "answer": 1},
    # -- qm (3) --
    {"rung": "qm", "q": "For a valid qubit state a|0> + b|1>, which must hold?",
     "choices": ["a + b = 1", "|a| + |b| = 1", "|a|^2 + |b|^2 = 1",
                 "a^2 + b^2 = 1 (no absolute values)"], "answer": 2},
    {"rung": "qm", "q": "Measuring |+> = (|0>+|1>)/sqrt(2) in the computational "
                        "basis yields outcome 0 with probability:",
     "choices": ["0", "1/4", "1/2", "1"], "answer": 2},
    {"rung": "qm", "q": "Which two-qubit state is maximally entangled?",
     "choices": ["|00>", "(|00>+|11>)/sqrt(2)", "(|0>+|1>)|0>/sqrt(2)",
                 "|01>"], "answer": 1},
    # -- circuits (3) --
    {"rung": "circuits", "q": "Applying a Hadamard gate to |0> gives:",
     "choices": ["|1>", "(|0>+|1>)/sqrt(2)", "(|0>-|1>)/sqrt(2)", "|0>"],
     "answer": 1},
    {"rung": "circuits", "q": "CNOT applied to |10> (control=1, target=0) gives:",
     "choices": ["|10>", "|00>", "|11>", "|01>"], "answer": 2},
    {"rung": "circuits", "q": "The Pauli X gate acts as:",
     "choices": ["a phase flip", "a bit flip (|0> <-> |1>)",
                 "a measurement", "the identity"], "answer": 1},
    # -- algorithms (3) --
    {"rung": "algorithms", "q": "Grover search over N unstructured items needs "
                                "how many oracle queries?",
     "choices": ["O(N)", "O(log N)", "O(sqrt(N))", "O(1)"], "answer": 2},
    {"rung": "algorithms", "q": "Shor's algorithm provides an exponential "
                                "speedup for:",
     "choices": ["sorting", "integer factoring", "matrix multiplication",
                 "graph coloring"], "answer": 1},
    {"rung": "algorithms", "q": "Deutsch-Jozsa decides, with a single oracle "
                                "query, whether f is:",
     "choices": ["injective or not", "constant or balanced",
                 "periodic or not", "linear or not"], "answer": 1},
    # -- qec (2) --
    {"rung": "qec", "q": "The 3-qubit repetition (bit-flip) code can correct:",
     "choices": ["any single-qubit error", "one bit-flip (X) error",
                 "one phase-flip (Z) error", "two bit-flip errors"],
     "answer": 1},
    {"rung": "qec", "q": "The surface code's error threshold is roughly:",
     "choices": ["~1e-6", "~0.01 (1%)", "~0.5 (50%)", "~0.25 (25%)"],
     "answer": 1},
    # -- vqa (2) --
    {"rung": "vqa", "q": "VQE is designed to estimate:",
     "choices": ["a Hamiltonian's ground-state energy",
                 "the period of a function", "a database index",
                 "an error syndrome"], "answer": 0},
    {"rung": "vqa", "q": "A 'barren plateau' in variational training means:",
     "choices": ["the ansatz is too shallow",
                 "gradients vanish exponentially with system size",
                 "the optimizer found the global minimum",
                 "measurement noise is zero"], "answer": 1},
    # -- hardware (2) --
    {"rung": "hardware", "q": "A qubit's T1 time characterizes:",
     "choices": ["dephasing", "energy relaxation (|1> decaying to |0>)",
                 "gate speed", "readout fidelity"], "answer": 1},
    {"rung": "hardware", "q": "A transmon qubit is best described as:",
     "choices": ["a trapped ion", "a superconducting anharmonic oscillator",
                 "a photonic cavity", "a nitrogen-vacancy center"],
     "answer": 1},
    # -- qiskit-api (2) --
    {"rung": "qiskit-api", "q": "In Qiskit, adding a Hadamard on qubit 0 of "
                                "circuit qc is written:",
     "choices": ["qc.hadamard(0)", "qc.h(0)", "qc.H[0]", "qc.gate('h', 0)"],
     "answer": 1},
    {"rung": "qiskit-api", "q": "Which Qiskit primitive computes expectation "
                                "values of observables?",
     "choices": ["Sampler", "Estimator", "Transpiler", "Provider"],
     "answer": 1},
]


# ---------------------------------------------------------------------------
# Loading (tolerant of missing / empty / corrupt files)
# ---------------------------------------------------------------------------

def _path(filename: str) -> Path:
    return DATA_DIR / filename


def _read_json(path: Path):
    """Parsed JSON from *path*, or None if missing, unreadable or corrupt."""
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _load_list(filename: str) -> list:
    """Like dashboard._load but rooted at the coach's (overridable) DATA_DIR."""
    data = _read_json(_path(filename))
    return data if isinstance(data, list) else []


# Expected JSON types of the known coach_state.json keys; a stored value of
# the wrong type (a hand-edited file) is replaced by the default instead of
# crashing the plan.  Unknown keys are carried through untouched.
_STATE_TYPES = {
    "activity_dates": list,
    "current_streak": (int, float),
    "best_streak": (int, float),
    "badges": dict,
    "diagnostic": (dict, type(None)),
    "last_plan_date": (str, type(None)),
}


def load_state() -> dict:
    default = {
        "activity_dates": [],
        "current_streak": 0,
        "best_streak": 0,
        "badges": {},
        "diagnostic": None,
        "last_plan_date": None,
    }
    try:
        raw = json.loads(STATE_PATH.read_text())
    except Exception:
        return default
    if not isinstance(raw, dict):
        return default
    for key, value in raw.items():
        expected = _STATE_TYPES.get(key)
        if expected is None:
            default[key] = value
        elif isinstance(value, expected) and not isinstance(value, bool):
            if expected == (int, float):
                try:
                    value = int(value)          # rejects NaN / Infinity
                except (OverflowError, ValueError):
                    continue
            default[key] = value
    return default


def save_state(state: dict) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2))
    except Exception:
        pass  # never crash the plan over an unwritable state file


# ---------------------------------------------------------------------------
# Per-(app, category) mastery with recency decay
# ---------------------------------------------------------------------------

def _clean_sessions(sessions: list) -> list[dict]:
    return [s for s in sessions if isinstance(s, dict)]


def _parse_iso(value: str) -> Optional[datetime]:
    """Aware datetime from an ISO-8601 string (naive input is taken as UTC,
    which is what the apps write), or None when it does not parse."""
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _session_timestamp(session: dict) -> Optional[float]:
    """Epoch seconds from a session's own "timestamp" field, or None.

    Accepts an epoch float, a numeric string, or the ISO-8601 *string* that
    circuit-trainer / math-quiz / quantum-quiz write (dashboard's float()
    rejects the latter).  Ignores the "date" field -- see _session_epoch.
    """
    ts = session.get("timestamp")
    if ts is not None and not isinstance(ts, bool):
        try:
            return float(ts)            # epoch float, or a numeric string
        except (TypeError, ValueError):
            pass
    if isinstance(ts, str):
        dt = _parse_iso(ts)
        if dt is not None:
            try:
                return dt.timestamp()
            except (OverflowError, OSError, ValueError):
                pass
    return None


def _session_epoch(session: dict) -> Optional[float]:
    """Best-effort Unix timestamp for a session (None if unknown).

    Like dashboard._session_timestamp, but also understands ISO-8601 string
    timestamps (via _session_timestamp) and anchors a date-only session at
    *local* midnight rather than UTC midnight so its calendar day survives
    the round trip through datetime.fromtimestamp() in every timezone.
    """
    ts = _session_timestamp(session)
    if ts is not None:
        return ts
    day = session.get("date")
    if isinstance(day, str) and _valid_date(day):
        try:
            return datetime.strptime(day, "%Y-%m-%d").timestamp()
        except (OverflowError, OSError, ValueError):
            pass
    return None


def _session_day(session: dict) -> Optional[str]:
    """Local YYYY-MM-DD a session was recorded on (None if unknown).

    A session's own "date" string is authoritative -- it is the local
    calendar day the app stamped when the user studied.  Otherwise the
    timestamp is converted to the local date.
    """
    day = session.get("date")
    if isinstance(day, str) and _valid_date(day.strip()):
        parsed = datetime.strptime(day.strip(), "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    ts = _session_epoch(session)
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return None


def build_category_stats(histories: dict[str, list]) -> dict[tuple[str, str], dict]:
    """Return {(app, category): {"w_sum", "ws", "last_ts", "last_day", "n"}}.

    Scores are on a 0-10 scale, weighted by dashboard's 14-day half-life.
    "last_day" is the YYYY-MM-DD of the latest session when that session
    carried only a "date" (no usable timestamp, so last_ts is its local
    midnight); None when the latest session had a real timestamp.
    """
    stats: dict[tuple[str, str], dict] = {}

    def add(app: str, cat: str, weight: float, score: float,
            ts: Optional[float], day: Optional[str]) -> None:
        cat = str(cat).strip()
        if not cat:
            return
        entry = stats.setdefault((app, cat),
                                 {"w_sum": 0.0, "ws": 0.0, "last_ts": 0.0,
                                  "last_day": None, "n": 0})
        entry["w_sum"] += weight * score
        entry["ws"] += weight
        entry["n"] += 1
        if ts and ts > entry["last_ts"]:
            entry["last_ts"] = ts
            entry["last_day"] = day

    _ease = {"got_it": 10.0, "unsure": 5.0, "missed": 0.0}

    for app, sessions in histories.items():
        for s in _clean_sessions(sessions):
            w = dashboard._session_weight(s)
            ts = _session_epoch(s)
            # Date-only session: ts is local midnight of its "date"; keep the
            # day so stale_categories() can count whole calendar days.
            day = (_session_day(s)
                   if ts is not None and _session_timestamp(s) is None
                   else None)
            if app in ("qec-trainer", "vqa-trainer", "circuit-trainer"):
                for a in s.get("attempts", []):
                    if isinstance(a, dict):
                        add(app, a.get("category", ""), w,
                            _num(a.get("score", 0)), ts, day)
            elif app == "flashcard-drill":
                for r in s.get("results", []):
                    if isinstance(r, dict):
                        add(app, r.get("category", ""), w,
                            _ease.get(r.get("rating", ""), 5.0), ts, day)
            elif app in ("math-quiz", "quantum-quiz"):
                for r in s.get("records", []):
                    if isinstance(r, dict):
                        cat = r.get("topic") or r.get("subject") or ""
                        add(app, cat, w, _num(r.get("score", 0)), ts, day)
            elif app == "qiskit-dojo":
                for a in s.get("attempts", []):
                    if isinstance(a, dict):
                        add(app, a.get("section", ""), w,
                            10.0 if a.get("passed") else 0.0, ts, day)
            elif app == "exam-sim":
                sections = s.get("sections", {})
                if isinstance(sections, dict):
                    for name, sec in sections.items():
                        if isinstance(sec, dict):
                            tot = _num(sec.get("total", 0))
                            cor = _num(sec.get("correct", 0))
                            if tot > 0:
                                add(app, name, w * tot, cor / tot * 10.0, ts, day)
            elif app == "problem-trainer":
                for a in s.get("attempts", []):
                    if isinstance(a, dict):
                        cat = a.get("kind") or a.get("problem_id") or ""
                        add(app, cat, w, _num(a.get("score", 0)), ts, day)
            # paper-drill has no categories

    return stats


def _num(x, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def weakest_categories(stats: dict[tuple[str, str], dict],
                       top_n: int = 3) -> list[tuple[str, str, float]]:
    """Top-N weakest (app, category, weighted_avg), deterministic order."""
    rows = [(app, cat, e["w_sum"] / e["ws"])
            for (app, cat), e in stats.items() if e["ws"] > 1e-9]
    rows.sort(key=lambda r: (r[2], r[0], r[1]))
    return rows[:top_n]


def stale_categories(stats: dict[tuple[str, str], dict]
                     ) -> list[tuple[str, str, int]]:
    """Categories touched before, but untouched for MORE than STALE_DAYS
    whole days -- so every "(Nd)" listed has N > STALE_DAYS, matching the
    "Stale (> 7 days untouched)" heading.

    Days are whole days since the last session's timestamp; a session that
    carried only a "date" (anchored at local midnight, time of day unknown)
    is measured in local calendar days instead, so one dated exactly
    STALE_DAYS days ago is not yet stale.
    """
    today = datetime.fromtimestamp(_NOW).date()
    out = []
    for (app, cat), e in stats.items():
        last_ts = e.get("last_ts", 0.0)
        if not last_ts or last_ts <= 0:
            continue
        last_day = e.get("last_day")
        if isinstance(last_day, str) and _valid_date(last_day):
            days = (today - datetime.strptime(last_day, "%Y-%m-%d").date()).days
        else:
            days = int((_NOW - last_ts) / 86400.0)
        if days > STALE_DAYS:
            out.append((app, cat, days))
    out.sort(key=lambda r: (-r[2], r[0], r[1]))   # most stale first
    return out


# ---------------------------------------------------------------------------
# Exam readiness
# ---------------------------------------------------------------------------

def exam_readiness(exam_sessions: list) -> Optional[dict]:
    """Latest full-exam score vs the pass line, plus weakest sections."""
    fulls = [s for s in _clean_sessions(exam_sessions)
             if s.get("mode") == "full" and _num(s.get("total", 0)) > 0]
    if not fulls:
        return None
    latest = max(fulls, key=lambda s: _num(s.get("timestamp", 0)))
    total = _num(latest.get("total", 0))
    correct = _num(latest.get("correct", 0))
    pct = correct / total * 100.0 if total else 0.0
    pass_pct = EXAM_PASS_CORRECT / EXAM_PASS_TOTAL * 100.0

    sections = []
    secs = latest.get("sections", {})
    if isinstance(secs, dict):
        for name, sec in secs.items():
            if isinstance(sec, dict) and _num(sec.get("total", 0)) > 0:
                sections.append(
                    (name, _num(sec.get("correct", 0))
                     / _num(sec.get("total", 1)) * 100.0))
    sections.sort(key=lambda r: (r[1], r[0]))

    return {
        "correct": int(correct),
        "total": int(total),
        "pct": pct,
        "passing": correct / total >= EXAM_PASS_CORRECT / EXAM_PASS_TOTAL,
        "pass_pct": pass_pct,
        "weakest_sections": sections[:3],
        "timestamp": _num(latest.get("timestamp", 0)),
    }


def dojo_weakest_section(dojo_sessions: list) -> Optional[tuple[str, float]]:
    """(section, pass_rate_pct) with the lowest pass rate."""
    buckets: dict[str, list[bool]] = {}
    for s in _clean_sessions(dojo_sessions):
        for a in s.get("attempts", []):
            if isinstance(a, dict):
                sec = str(a.get("section", "")).strip()
                if sec:
                    buckets.setdefault(sec, []).append(bool(a.get("passed")))
    if not buckets:
        return None
    rates = [(sec, sum(v) / len(v) * 100.0) for sec, v in buckets.items()]
    rates.sort(key=lambda r: (r[1], r[0]))
    return rates[0]


# ---------------------------------------------------------------------------
# Flagged-for-review items — every app's *_flagged.json (see module docstring)
# ---------------------------------------------------------------------------

_FLAG_ID_KEYS = ("id", "card_id", "problem_id", "question_id", "kata_id")
_LABEL_MAX = 72   # longest label / category rendered before truncation


def _file_mtime(path: Path) -> float:
    try:
        return float(path.stat().st_mtime)
    except OSError:
        return 0.0


def _epoch(value) -> float:
    """Coerce a contract timestamp to epoch seconds (0.0 when unusable).

    Accepts an epoch number (seconds or milliseconds, numeric strings too)
    or an ISO-8601 string.
    """
    ts = _num(value)
    if ts <= 0 and isinstance(value, str):
        dt = _parse_iso(value)
        if dt is not None:
            try:
                ts = dt.timestamp()
            except (OverflowError, OSError, ValueError):
                ts = 0.0
    if ts <= 0:
        return 0.0
    if ts > 1e11:            # millisecond epoch — normalise to seconds
        ts /= 1000.0
    return ts


def _short(text) -> str:
    """One-line, whitespace-collapsed, length-capped rendering of *text*."""
    text = " ".join(str(text).split())
    return text if len(text) <= _LABEL_MAX else text[:_LABEL_MAX - 1] + "…"


def _app_for_flag_file(path: Path) -> str:
    """Owning app for a flagged file, inferred from its name."""
    if path.name in _LEGACY_FLAGGED_FILES:
        return _LEGACY_FLAGGED_FILES[path.name]
    suffix = "_flagged.json"
    prefix = (path.name[:-len(suffix)] if path.name.endswith(suffix)
              else path.stem)
    return _PREFIX_TO_APP.get(prefix, prefix or "unknown")


def discover_flagged_files() -> list[tuple[str, Path]]:
    """(app, path) for each flagged file present in DATA_DIR, by filename."""
    found: dict[Path, str] = {}
    try:
        for p in DATA_DIR.glob(_FLAGGED_GLOB):
            if p.is_file():
                found[p] = _app_for_flag_file(p)
        for name, app in _LEGACY_FLAGGED_FILES.items():
            p = DATA_DIR / name
            if p.is_file():
                found[p] = app
    except OSError:
        pass
    return [(app, p) for p, app in sorted(found.items(),
                                          key=lambda kv: kv[0].name)]


def _flag_entry(item, app: str, fallback_ts: float = 0.0) -> Optional[dict]:
    """Normalize one flagged-file entry into a review item (None = skip).

    Accepts a bare string id, or a dict per the flagging contract —
    {"id", "label", "category", "app", "timestamp"}, only "id" required
    (legacy id keys card_id/problem_id/question_id/kata_id also work).
    A missing or invalid timestamp falls back to *fallback_ts* (file mtime).
    """
    if isinstance(item, str):
        ident = item.strip()
        if not ident:
            return None
        return {"app": app, "id": ident, "label": _short(ident),
                "category": "", "ts": fallback_ts, "score": 0.0,
                "why": "flagged"}
    if not isinstance(item, dict):
        return None
    ident = ""
    for key in _FLAG_ID_KEYS:
        value = item.get(key)
        if value is not None and str(value).strip():
            ident = str(value).strip()
            break
    if not ident:
        return None
    label = item.get("label")
    label = (_short(label) if isinstance(label, str) and label.strip()
             else _short(ident))
    category = item.get("category")
    category = _short(category) if isinstance(category, str) else ""
    entry_app = item.get("app")
    if isinstance(entry_app, str) and entry_app.strip():
        app = entry_app.strip()
    return {"app": app, "id": ident, "label": label, "category": category,
            "ts": _epoch(item.get("timestamp")) or fallback_ts,
            "score": 0.0, "why": "flagged"}


def load_flagged_items(notes: Optional[list[str]] = None) -> list[dict]:
    """Every flagged item across all apps, deduped by (app, id).

    Unreadable files and malformed entries are skipped; when *notes* is a
    list, a one-line note per problem is appended to it.
    """
    items: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for app, path in discover_flagged_files():
        raw = _read_json(path)
        if not isinstance(raw, list):
            if notes is not None:
                notes.append(f"skipped {path.name}: not a readable JSON list")
            continue
        mtime = _file_mtime(path)
        malformed = 0
        for entry in raw:
            item = _flag_entry(entry, app, mtime)
            if item is None:
                malformed += 1
                continue
            key = (item["app"], item["id"])
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
        if malformed and notes is not None:
            notes.append(f"{path.name}: ignored {malformed} malformed "
                         f"entr{'y' if malformed == 1 else 'ies'}")
    return items


def flagged_counts(items: list[dict]) -> dict[str, int]:
    """{app: number of flagged items in *items*}, sorted by app name."""
    counts: dict[str, int] = {}
    for item in items:
        if item.get("why") == "flagged":
            counts[item["app"]] = counts.get(item["app"], 0) + 1
    return dict(sorted(counts.items()))


# ---------------------------------------------------------------------------
# Unified review queue (--review, also counted in the default plan)
# ---------------------------------------------------------------------------

def collect_review_items(histories: dict[str, list],
                         notes: Optional[list[str]] = None) -> list[dict]:
    """Merge flagged items (all apps), exam misses, and recent low scores.

    Sorted oldest+worst first (timestamp asc, score asc) and deduped by
    (app, id, why).  NOT capped — build_review_queue()/render_review()
    apply REVIEW_CAP.  Each item: {app, id, label, category, ts, score, why}.
    """
    items: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    def push(item: Optional[dict]) -> None:
        if not item:
            return
        item.setdefault("id", item["label"])
        item.setdefault("category", "")
        key = (item["app"], item["id"], item["why"])
        if key in seen:
            return
        seen.add(key)
        items.append(item)

    # 1. Flagged items from every app's flagged file
    for item in load_flagged_items(notes):
        push(item)

    # 2. Missed exam questions
    for m in _load_list("exam_missed.json"):
        if isinstance(m, dict):
            ident = m.get("question_id")
            if ident is None:
                continue
            push({"app": "exam-sim", "id": str(ident), "label": str(ident),
                  "category": str(m.get("section", "")).strip(),
                  "ts": _epoch(m.get("timestamp")), "score": 0.0,
                  "why": "missed exam question"})

    # 3. Low-scoring quiz / problem attempts in the last 30 days
    cutoff = _NOW - REVIEW_WINDOW_DAYS * 86400.0
    for app in ("math-quiz", "quantum-quiz"):
        for s in _clean_sessions(histories.get(app, [])):
            ts = _session_epoch(s)
            if not ts or ts < cutoff:
                continue
            for r in s.get("records", []):
                if isinstance(r, dict):
                    score = _num(r.get("score", 10))
                    if score < REVIEW_LOW_SCORE:
                        topic = str(r.get("topic") or r.get("subject") or "?")
                        subject = str(r.get("subject") or "").strip()
                        push({"app": app, "id": topic, "label": topic,
                              "category": subject if subject != topic else "",
                              "ts": ts, "score": score,
                              "why": f"scored {score:g}/10"})
    for s in _clean_sessions(histories.get("problem-trainer", [])):
        ts = _session_epoch(s)
        if not ts or ts < cutoff:
            continue
        for a in s.get("attempts", []):
            if isinstance(a, dict):
                score = _num(a.get("score", 10))
                if score < REVIEW_LOW_SCORE:
                    ident = str(a.get("problem_id") or a.get("kind") or "?")
                    kind = str(a.get("kind") or "").strip()
                    push({"app": "problem-trainer", "id": ident,
                          "label": ident,
                          "category": kind if kind != ident else "",
                          "ts": ts, "score": score,
                          "why": f"scored {score:g}/10"})

    items.sort(key=lambda i: (i["ts"], i["score"], i["app"], i["label"],
                              i["id"]))
    return items


def build_review_queue(histories: dict[str, list],
                       notes: Optional[list[str]] = None) -> list[dict]:
    """The REVIEW_CAP oldest/worst items from collect_review_items()."""
    return collect_review_items(histories, notes)[:REVIEW_CAP]


# ---------------------------------------------------------------------------
# Streak (real activity only — coach running does NOT count)
# ---------------------------------------------------------------------------

def latest_activity_dates(histories: dict[str, list]) -> set[str]:
    """Every YYYY-MM-DD (local) on which any history session was recorded.

    Date-only sessions (circuit-trainer / math-quiz / quantum-quiz) are
    credited to their own "date" string; epoch and ISO-string timestamps are
    converted to the local calendar day.
    """
    days: set[str] = set()
    for sessions in histories.values():
        for s in _clean_sessions(sessions):
            day = _session_day(s)
            if day:
                days.add(day)
    return days


def _compute_streaks(dates: list[str]) -> tuple[int, int]:
    """(current, best) streak from a list of YYYY-MM-DD strings."""
    if not dates:
        return 0, 0
    parsed = sorted({datetime.strptime(d, "%Y-%m-%d").date()
                     for d in dates if _valid_date(d)})
    if not parsed:
        return 0, 0
    best = run = 1
    for prev, cur in zip(parsed, parsed[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        best = max(best, run)
    today = datetime.now().date()
    current = 0
    check = today
    dateset = set(parsed)
    if today not in dateset and (today - timedelta(days=1)) in dateset:
        check = today - timedelta(days=1)   # streak still alive from yesterday
    while check in dateset:
        current += 1
        check -= timedelta(days=1)
    return current, best


def _valid_date(d) -> bool:
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def update_streak_state(state: dict, histories: dict[str, list]) -> None:
    """Record today as active only if history files show activity today."""
    dates = [d for d in state.get("activity_dates", []) if _valid_date(d)]
    dates = sorted(set(dates) | latest_activity_dates(histories))
    state["activity_dates"] = dates[-365:]        # keep a year of history
    cur, best = _compute_streaks(state["activity_dates"])
    state["current_streak"] = cur
    state["best_streak"] = max(best, int(_num(state.get("best_streak", 0))))


# ---------------------------------------------------------------------------
# Diagnostic scoring (pure functions, testable headlessly)
# ---------------------------------------------------------------------------

def score_diagnostic(answers: list[Optional[int]]) -> dict[str, dict]:
    """Score answers (0-based choice indices, None = skipped) per rung."""
    rungs: dict[str, dict] = {r: {"total": 0, "correct": 0}
                              for r in RUNG_ORDER}
    for q, a in zip(DIAGNOSTIC_QUESTIONS, answers):
        r = rungs[q["rung"]]
        r["total"] += 1
        if a is not None and a == q["answer"]:
            r["correct"] += 1
    return rungs


def _rung_counts(rung) -> tuple[float, float]:
    """(total, correct) for one stored rung record; (0, 0) if malformed."""
    if not isinstance(rung, dict):
        return 0.0, 0.0
    return _num(rung.get("total", 0)), _num(rung.get("correct", 0))


def recommended_rung(rungs: dict[str, dict]) -> str:
    """First rung (in ladder order) below 2/3 accuracy; else the weakest."""
    if not isinstance(rungs, dict):
        return RUNG_ORDER[0]
    for name in RUNG_ORDER:
        total, correct = _rung_counts(rungs.get(name))
        if total > 0 and correct / total < 2 / 3:
            return name
    # All rungs solid — recommend the (relatively) weakest one.
    scored = []
    for n, r in rungs.items():
        total, correct = _rung_counts(r)
        if total > 0 and n in RUNG_ORDER:
            scored.append((correct / total, RUNG_ORDER.index(n), n))
    return min(scored)[2] if scored else RUNG_ORDER[0]


def rung_docs_dir(rung: str) -> str:
    for name, docs, _app in RUNGS:
        if name == rung:
            return docs
    return "docs/"


def rung_app(rung: str) -> str:
    for name, _docs, app in RUNGS:
        if name == rung:
            return app
    return "flashcard-drill"


def weak_rungs(rungs: dict[str, dict]) -> list[str]:
    """Rungs below 2/3 accuracy, in ladder order."""
    out = []
    if not isinstance(rungs, dict):
        return out
    for name in RUNG_ORDER:
        total, correct = _rung_counts(rungs.get(name))
        if total > 0 and correct / total < 2 / 3:
            out.append(name)
    return out


# ---------------------------------------------------------------------------
# Plan builder (deterministic, rules-based)
# ---------------------------------------------------------------------------

def build_plan(histories: dict[str, list], state: dict) -> dict:
    """Compute everything the default view prints."""
    stats = build_category_stats(histories)
    weakest = weakest_categories(stats, top_n=3)
    stale = stale_categories(stats)
    exam = exam_readiness(histories.get("exam-sim", []))
    dojo = dojo_weakest_section(histories.get("qiskit-dojo", []))
    review_all = collect_review_items(histories)
    review = review_all[:REVIEW_CAP]
    review_dropped = len(review_all) - len(review)
    flagged_by_app = flagged_counts(review_all)
    flagged_total = sum(flagged_by_app.values())
    missed_count = len({str(m["question_id"])
                        for m in _load_list("exam_missed.json")
                        if isinstance(m, dict)
                        and m.get("question_id") is not None})

    diag = state.get("diagnostic") or None
    diag_rungs = diag.get("rungs") if isinstance(diag, dict) else None
    if not isinstance(diag_rungs, dict):
        diag_rungs = {}
    weak_rung_list = weak_rungs(diag_rungs) if diag_rungs else []

    items: list[str] = []

    # 1. Review queue first — overdue material beats new material.
    if review:
        apps = sorted({i["app"] for i in review})
        detail = [", ".join(apps)]
        if flagged_total:
            detail.append(f"{flagged_total} flagged across "
                          f"{len(flagged_by_app)} app(s)")
        if review_dropped:
            detail.append(f"+{review_dropped} more past the cap of "
                          f"{REVIEW_CAP}")
        items.append(
            f"review queue — {len(review)} item(s) due "
            f"({'; '.join(detail)}): run `python coach.py --review`")

    # 2. Weakest categories, grouped per app -- but only ones that are
    #    actually weak: with a single perfect exam on file the "weakest"
    #    rows average 10.0/10, and prescribing those would be noise.  Solid
    #    categories (>= FOCUS_MAX_AVG) are skipped; the starter defaults
    #    below pad the plan instead.
    by_app: dict[str, list[tuple[str, float]]] = {}
    for app, cat, avg in weakest:
        if avg < FOCUS_MAX_AVG:
            by_app.setdefault(app, []).append((cat, avg))
    for app in sorted(by_app):
        cats = ", ".join(c for c, _ in by_app[app])
        worst = min(a for _, a in by_app[app])
        items.append(f"{app} — 15 min, focus: {cats} "
                     f"(weakest, avg {worst:.1f}/10)")

    def _planned_apps() -> set[str]:
        return {i.split(" — ")[0] for i in items}

    # 3. Exam readiness: sprint on a genuinely weak section (same floor,
    #    in percent); otherwise a retake if the last full exam failed.
    if exam and "exam-sim" not in _planned_apps():
        sprint = exam["weakest_sections"][0] if exam["weakest_sections"] \
            else None
        if sprint and sprint[1] < FOCUS_MAX_AVG * 10.0:
            sec, pct = sprint
            items.append(f"exam-sim — Sprint: {sec} "
                         f"({pct:.0f}% on last full exam)")
        elif not exam["passing"]:
            items.append(f"exam-sim — full exam retake "
                         f"(last: {exam['correct']}/{exam['total']}, "
                         f"need {EXAM_PASS_CORRECT}/{EXAM_PASS_TOTAL})")

    # 4. Dojo lowest pass-rate section (unless already covered above, and
    #    only if it is actually below the floor).
    if dojo and "qiskit-dojo" not in _planned_apps():
        sec, rate = dojo
        if rate < FOCUS_MAX_AVG * 10.0:
            items.append(f"qiskit-dojo — 2 katas in '{sec}' "
                         f"({rate:.0f}% pass rate, lowest)")

    # 5. Diagnostic bias: hit the weakest rung with its practice app.
    if weak_rung_list:
        rung = weak_rung_list[0]
        total, correct = _rung_counts(diag_rungs.get(rung))
        items.append(f"{rung_app(rung)} — 1 session on rung '{rung}' "
                     f"(diagnostic: {correct:g}/{total:g}"
                     f"; read {rung_docs_dir(rung)})")

    # 6. Stale categories (skip apps already planned above).
    for app, cat, days in stale:
        if app not in _planned_apps():
            items.append(f"{app} — 1 short session: {cat} "
                         f"(untouched {days} days)")
            break

    # Cap at 5; pad to 3 with sensible defaults.
    items = items[:5]
    defaults = [
        "flashcard-drill — 10 min mixed deck (keep the streak alive)",
        "quantum-quiz — 5 questions, mixed topics",
        "read one docs section from the ladder (start: docs/01_...)",
    ]
    for d in defaults:
        if len(items) >= 3:
            break
        items.append(d)

    return {
        "items": items,
        "weakest": weakest,
        "stale": stale,
        "exam": exam,
        "dojo": dojo,
        "review_count": len(review),
        "review_total": len(review_all),
        "review_dropped": review_dropped,
        "flagged_total": flagged_total,
        "flagged_by_app": flagged_by_app,
        "missed_count": missed_count,
        "diagnostic": diag,
        "weak_rungs": weak_rung_list,
    }


# ---------------------------------------------------------------------------
# Rendering (rich if available, plain text otherwise)
# ---------------------------------------------------------------------------

def _console():
    """Return a rich Console or None (plain-text fallback).

    soft_wrap=True keeps rich from inserting hard line breaks at the
    detected width (80 columns when stdout is a pipe without COLUMNS), so
    a long plan line stays one line when piped to a file or grep; an
    interactive terminal still wraps it visually.
    """
    try:
        from rich.console import Console
        return Console(soft_wrap=True)
    except ImportError:
        return None


def _heading(console, text: str) -> None:
    if console:
        console.rule(f"[bold cyan]{text}[/bold cyan]")
    else:
        print()
        print("=" * 62)
        print(f"  {text}")
        print("=" * 62)


def _escape_markup(text: str) -> str:
    """Escape rich markup so dynamic text like "[qec]" prints literally."""
    try:
        from rich.markup import escape
    except ImportError:
        return text
    return escape(text)


def _line(console, text: str, style: str = "") -> None:
    if console:
        text = _escape_markup(text)
        console.print(f"[{style}]{text}[/{style}]" if style else text)
    else:
        print(text)


def _fmt_date(ts: float) -> str:
    if not ts:
        return "undated"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return "undated"


def _flagged_summary(flagged_by_app: dict[str, int]) -> str:
    total = sum(flagged_by_app.values())
    per_app = ", ".join(f"{a} {n}" for a, n in flagged_by_app.items())
    return (f"Flagged for review: {total} item(s) across "
            f"{len(flagged_by_app)} app(s) — {per_app}")


def render_plan(plan: dict, state: dict) -> None:
    console = _console()
    _heading(console, f"Quantum Study Coach — plan for {_TODAY}")
    print()

    # Situation report
    if plan["weakest"]:
        _line(console, "Weakest categories (recency-weighted):", "bold")
        for app, cat, avg in plan["weakest"]:
            _line(console, f"  - {cat} [{app}] — {avg:.1f}/10")
    else:
        _line(console, "No scored history yet — starter plan below.", "dim")

    if plan["stale"]:
        names = ", ".join(f"{c} ({d}d)" for _a, c, d in plan["stale"][:5])
        _line(console, f"Stale (> {STALE_DAYS} days untouched): {names}")

    exam = plan["exam"]
    if exam:
        verdict = "PASSING" if exam["passing"] else "below pass line"
        _line(console,
              f"Exam readiness: {exam['correct']}/{exam['total']} "
              f"({exam['pct']:.0f}%) on last full exam — {verdict} "
              f"(pass = {EXAM_PASS_CORRECT}/{EXAM_PASS_TOTAL}, "
              f"{exam['pass_pct']:.0f}%)")
        if exam["weakest_sections"]:
            secs = ", ".join(f"{n} ({p:.0f}%)"
                             for n, p in exam["weakest_sections"])
            _line(console, f"  weakest sections: {secs}")
    if plan["missed_count"]:
        _line(console,
              f"Missed exam questions due for review: {plan['missed_count']}")
    if plan["flagged_total"]:
        _line(console, _flagged_summary(plan["flagged_by_app"]))

    diag = plan["diagnostic"]
    if isinstance(diag, dict) and isinstance(diag.get("recommended_rung"), str) \
            and diag["recommended_rung"]:
        rung = diag["recommended_rung"]
        _line(console,
              f"Docs ladder: start at rung '{rung}' -> {rung_docs_dir(rung)}"
              + (f" (weak rungs: {', '.join(plan['weak_rungs'])})"
                 if plan["weak_rungs"] else ""))
    else:
        _line(console,
              "No diagnostic on file — run `python coach.py --diagnostic` "
              "to calibrate the docs ladder.", "dim")

    # The plan itself
    print()
    _line(console, "TODAY'S PLAN", "bold green")
    for i, item in enumerate(plan["items"], 1):
        _line(console, f"  {i}. {item}")

    # Streak + badges summary
    print()
    cur = state.get("current_streak", 0)
    best = state.get("best_streak", 0)
    flame = " *" if cur >= 7 else ""
    _line(console, f"Streak: {cur} day(s) (best: {best}){flame}",
          "bold yellow")

    badges = state.get("badges", {})
    earned = sum(1 for b in BADGES if badges.get(b) == "earned")
    in_prog = sum(1 for b in BADGES if badges.get(b) == "in_progress")
    _line(console,
          f"Badges: {earned}/{len(BADGES)} earned, {in_prog} in progress "
          f"(`python coach.py --badges`)")
    print()


def render_review(items: list[dict],
                  notes: Optional[list[str]] = None) -> None:
    """Print the review queue.

    *items* is the full, sorted list from collect_review_items(); the first
    REVIEW_CAP are shown as "<app> — <label or id> [<category>] — <why>"
    and the number dropped by the cap is reported.
    """
    console = _console()
    _heading(console, "Review Today — unified SRS queue")
    print()
    for note in notes or []:
        _line(console, f"note: {note}", "dim")
    if notes:
        print()

    queue = items[:REVIEW_CAP]
    dropped = len(items) - len(queue)
    if not queue:
        _line(console, "Nothing due for review. Nice.", "green")
        print()
        return

    shown = (f"{len(queue)} of {len(items)} item(s)" if dropped
             else f"{len(queue)} item(s)")
    _line(console, f"{shown}, oldest & worst first (capped at {REVIEW_CAP}):",
          "bold")
    for i, item in enumerate(queue, 1):
        cat = f" [{item['category']}]" if item.get("category") else ""
        _line(console,
              f"  {i:2}. {item['app']} — {item['label']}{cat} — "
              f"{item['why']} ({_fmt_date(item['ts'])})")
    if dropped:
        _line(console,
              f"  ... {dropped} more item(s) dropped by the cap of "
              f"{REVIEW_CAP} — clear the ones above first.", "dim")
    print()
    flagged_by_app = flagged_counts(items)
    if flagged_by_app:
        _line(console, _flagged_summary(flagged_by_app))
    apps = sorted({i["app"] for i in queue})
    _line(console, f"Open these apps to clear the queue: {', '.join(apps)}")
    print()


# ---------------------------------------------------------------------------
# Interactive modes
# ---------------------------------------------------------------------------

def run_diagnostic(state: dict) -> None:
    console = _console()
    _heading(console, "Placement Diagnostic — 20 questions")
    print()
    _line(console, "Answer a/b/c/d (or 1-4). Press Enter to skip.", "dim")
    print()

    answers: list[Optional[int]] = []
    for i, q in enumerate(DIAGNOSTIC_QUESTIONS, 1):
        _line(console, f"Q{i}/20 [{q['rung']}]  {q['q']}", "bold")
        for j, choice in enumerate(q["choices"]):
            _line(console, f"    {'abcd'[j]}) {choice}")
        ans = _read_choice(len(q["choices"]))
        answers.append(ans)
        print()

    rungs = score_diagnostic(answers)
    rec = recommended_rung(rungs)
    state["diagnostic"] = {
        "timestamp": _NOW,
        "rungs": rungs,
        "recommended_rung": rec,
    }
    save_state(state)

    total = sum(r["total"] for r in rungs.values())
    correct = sum(r["correct"] for r in rungs.values())
    _line(console, f"Score: {correct}/{total}", "bold green")
    print()
    for name in RUNG_ORDER:
        r = rungs[name]
        mark = "weak" if (r["total"] and r["correct"] / r["total"] < 2 / 3) \
            else "ok"
        _line(console,
              f"  {name:<12} {r['correct']}/{r['total']}  [{mark}]")
    print()
    _line(console,
          f"Recommended docs-ladder starting rung: '{rec}' "
          f"-> {rung_docs_dir(rec)}", "bold")
    _line(console, "Future plans will bias toward your weak rungs.", "dim")
    print()


def _read_choice(n_choices: int) -> Optional[int]:
    """Read one MC answer from stdin; None means skipped/EOF."""
    letters = "abcd"[:n_choices]
    while True:
        try:
            raw = input("  > ").strip().lower()
        except EOFError:
            return None
        if raw == "":
            return None
        if raw in letters:
            return letters.index(raw)
        if raw.isdigit() and 1 <= int(raw) <= n_choices:
            return int(raw) - 1
        print(f"    (enter one of: {', '.join(letters)} / 1-{n_choices}, "
              f"or Enter to skip)")


def cycle_badge(state: dict, badge: str) -> str:
    """Advance a badge's status (not_started -> in_progress -> earned -> ...)."""
    badges = state.setdefault("badges", {})
    cur = badges.get(badge, "not_started")
    if cur not in BADGE_STATUSES:
        cur = "not_started"
    nxt = BADGE_STATUSES[(BADGE_STATUSES.index(cur) + 1) % len(BADGE_STATUSES)]
    badges[badge] = nxt
    return nxt


def run_badges(state: dict) -> None:
    console = _console()
    _heading(console, "IBM Quantum Learning — badge tracker")
    print()
    _line(console,
          "Enter a number to cycle its status "
          "(not started -> in progress -> earned). q to quit.", "dim")
    while True:
        print()
        badges = state.get("badges", {})
        for i, name in enumerate(BADGES, 1):
            status = badges.get(name, "not_started")
            if status not in BADGE_STATUSES:
                status = "not_started"
            _line(console, f"  {i}. [{_BADGE_LABEL[status]:<11}] {name}")
        print()
        try:
            raw = input("badge # (q to quit) > ").strip().lower()
        except EOFError:
            break
        if raw in ("q", "quit", "exit", ""):
            break
        if raw.isdigit() and 1 <= int(raw) <= len(BADGES):
            name = BADGES[int(raw) - 1]
            new = cycle_badge(state, name)
            save_state(state)
            _line(console, f"  -> {name}: {_BADGE_LABEL[new]}")
        else:
            _line(console, "  (enter 1-7 or q)")
    save_state(state)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def load_histories() -> dict[str, list]:
    return {app: _load_list(fname) for app, fname in _HISTORY_FILES.items()}


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Quantum Study Coach — daily plan from cross-app history")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--diagnostic", action="store_true",
                      help="20-question placement quiz")
    mode.add_argument("--badges", action="store_true",
                      help="IBM Quantum Learning badge checklist")
    mode.add_argument("--review", action="store_true",
                      help="unified SRS review queue")
    args = parser.parse_args(argv)

    state = load_state()

    if args.diagnostic:
        run_diagnostic(state)
        return
    if args.badges:
        run_badges(state)
        return

    histories = load_histories()

    if args.review:
        notes: list[str] = []
        render_review(collect_review_items(histories, notes), notes)
        return

    # Default: today's plan.
    update_streak_state(state, histories)
    plan = build_plan(histories, state)
    state["last_plan_date"] = _TODAY
    save_state(state)
    render_plan(plan, state)


if __name__ == "__main__":
    main()
