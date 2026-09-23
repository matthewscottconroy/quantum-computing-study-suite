"""Quantum Study Dashboard — unified mastery view across all study apps.

Run standalone:
    python dashboard.py                 # mastery + retention/forgetting view
    python dashboard.py --retention     # only the retention/forgetting view
    python dashboard.py --no-retention  # only the classic mastery report

Import as a module:
    from dashboard import build_report, build_retention, AppStats

Data dir defaults to ~/.local/share/quantum-study/ and is overridden by the
QUANTUM_STUDY_DATA_DIR environment variable (read once, at import time).

Besides the ten history files this module also reads two cross-app signal
files written by the apps -- mistakes.json (the mistake journal, with a
"why did I get this wrong?" cause per entry) and confidence.json (a 1-4
confidence rating captured BEFORE each answer is revealed).  Their schema
helpers live here (make_mistake_entry / normalise_mistake / load_mistakes /
mistakes_panel, normalise_confidence / load_confidence / calibration_panel)
so that coach.py's --mistakes, --calibration and --item-analysis reports and
this dashboard's panels all read the files the same way.  Nothing here ever
writes: the dashboard is read-only.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Shared suite data directory.  QUANTUM_STUDY_DATA_DIR overrides it -- the
# same override coach.py, launch.py and every app already honour -- so tests
# and experiments never read or write the real history.  Read once at import
# time, like the apps.
DATA_DIR = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR")
                or (Path.home() / ".local" / "share" / "quantum-study"))

# Actual filenames written by each app's persistence layer
_FILES = {
    "QEC Trainer":       DATA_DIR / "qec_history.json",
    "VQA Trainer":       DATA_DIR / "vqa_history.json",
    "Flashcard Drill":   DATA_DIR / "flashcard_history.json",
    "Circuit Trainer":   DATA_DIR / "trainer_history.json",
    "Math Quiz":         DATA_DIR / "math_history.json",
    "Quantum Quiz":      DATA_DIR / "quiz_history.json",
    "Paper Drill":       DATA_DIR / "paper_history.json",
    "Qiskit Dojo":       DATA_DIR / "dojo_history.json",
    "Exam Simulator":    DATA_DIR / "exam_history.json",
    "Problem Trainer":   DATA_DIR / "problems_history.json",
}

_HALF_LIFE_DAYS = 14.0   # score weight halves every 14 days (matches app SRS)
_NOW = time.time()       # snapshot once so all comparisons are consistent


# ---------------------------------------------------------------------------
# Schema notes (verified against each app's persistence.py)
#
# qec_history / vqa_history:
#   [ { total, correct, accuracy, timestamp,
#       attempts: [ {problem_id, category, difficulty, score, verdict,
#                    hints_used, elapsed_secs} ] } ]
#
# flashcard_history:
#   [ { total, got_it, unsure, missed, timestamp,
#       results: [ {card_id, category, rating} ] } ]
#   rating in {"got_it", "unsure", "missed"}
#
# trainer_history (Circuit Trainer):
#   [ { date, total, correct, accuracy,
#       attempts: [ {category, difficulty, score} ] } ]
#   (no session-level timestamp — uses "date" string)
#
# math_history / quiz_history (Math Quiz / Quantum Quiz):
#   [ { date, answered, average_score,
#       records: [ {subject, topic, score} ] } ]
#   (no session-level timestamp — uses "date" string)
#
# paper_history:
#   [ { title, total, average, scores: [float, ...] } ]
#   (no timestamp at all)
#
# dojo_history (Qiskit Dojo):
#   [ { timestamp, total, passed,
#       attempts: [ {kata_id, section, passed: bool, tries} ] } ]
#
# exam_history (Exam Simulator):
#   [ { timestamp, mode: "full"|"sprint", total, correct, duration_secs,
#       sections: { "<name>": {total, correct} } } ]
#
# problems_history (Problem Trainer):
#   [ { timestamp, total, avg_score,
#       attempts: [ {problem_id, kind: "problem"|"derivation", score} ] } ]
# ---------------------------------------------------------------------------


def _session_weight(session: dict) -> float:
    """14-day half-life decay.  Missing/unparseable timestamp → weight 0.1."""
    ts = session.get("timestamp")
    if ts is not None:
        try:
            days = (_NOW - float(ts)) / 86400.0
            return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)
        except (TypeError, ValueError):
            pass
    # Try ISO date string ("date" key used by circuit/math/quiz apps)
    date_str = session.get("date")
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days = (_NOW - d.timestamp()) / 86400.0
            return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)
        except (TypeError, ValueError):
            pass
    return 0.1   # very old / unknown age


def _session_timestamp(session: dict) -> Optional[float]:
    """Best-effort Unix timestamp for a session (None if totally unknown)."""
    ts = session.get("timestamp")
    if ts is not None:
        try:
            return float(ts)
        except (TypeError, ValueError):
            pass
    date_str = session.get("date")
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return d.timestamp()
        except (TypeError, ValueError):
            pass
    return None


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Per-app extraction helpers
# ---------------------------------------------------------------------------

def _extract_qec_vqa(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Return (session_count, total_attempts, weighted_avg, timestamps,
               all_scores, all_weights) for qec or vqa."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            score = a.get("score", 0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_flashcard(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Flashcard uses rating strings; map to 0–10 scores."""
    _ease = {"got_it": 10.0, "unsure": 5.0, "missed": 0.0}
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for r in s.get("results", []):
            score = _ease.get(r.get("rating", ""), 5.0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_circuit(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Circuit trainer: attempts[].score (0–10 scale from app)."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            score = a.get("score", 0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_math_quiz(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Math / Quantum Quiz: records[].score with session-level date."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for r in s.get("records", []):
            score = r.get("score", 0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_paper(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Paper drill: each session is a quiz on one paper; scores list + average."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    # Paper has no timestamp; all sessions treated as weight 0.1
    for s in sessions:
        w = _session_weight(s)   # will return 0.1 (no timestamp/date key)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for score in s.get("scores", []):
            total_attempts += 1
            w_sum += w * float(score)
            ws_sum += w
            all_scores.append(float(score))
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_dojo(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Qiskit Dojo: attempts[].passed bool → 10.0 / 0.0 score."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            score = 10.0 if a.get("passed") else 0.0
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_exam(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Exam Simulator: session-level total/correct → per-question 10/0 scores."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        try:
            total = int(s.get("total", 0))
            correct = int(s.get("correct", 0))
        except (TypeError, ValueError):
            continue
        if total <= 0:
            continue
        correct = max(0, min(correct, total))
        total_attempts += total
        w_sum += w * correct * 10.0
        ws_sum += w * total
        all_scores.extend([10.0] * correct + [0.0] * (total - correct))
        all_weights.extend([w] * total)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_problems(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Problem Trainer: attempts[].score (0–10 scale)."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            try:
                score = float(a.get("score", 0))
            except (TypeError, ValueError):
                score = 0.0
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


# ---------------------------------------------------------------------------
# Topic-level weak-spot analysis (qec, vqa, flashcard)
# ---------------------------------------------------------------------------

def _topic_scores_qec_vqa(sessions: list[dict]) -> dict[str, tuple[float, float]]:
    """Return {category: (weighted_sum, weight_sum)} from qec/vqa data."""
    buckets: dict[str, list[tuple[float, float]]] = {}
    for s in sessions:
        w = _session_weight(s)
        for a in s.get("attempts", []):
            cat = a.get("category", "").strip()
            if cat:
                buckets.setdefault(cat, []).append((w, a.get("score", 0)))
    return {
        cat: (sum(w * sc for w, sc in pairs), sum(w for w, _ in pairs))
        for cat, pairs in buckets.items()
    }


def _topic_scores_flashcard(sessions: list[dict]) -> dict[str, tuple[float, float]]:
    _ease = {"got_it": 10.0, "unsure": 5.0, "missed": 0.0}
    buckets: dict[str, list[tuple[float, float]]] = {}
    for s in sessions:
        w = _session_weight(s)
        for r in s.get("results", []):
            cat = r.get("category", "").strip()
            if cat:
                score = _ease.get(r.get("rating", ""), 5.0)
                buckets.setdefault(cat, []).append((w, score))
    return {
        cat: (sum(w * sc for w, sc in pairs), sum(w for w, _ in pairs))
        for cat, pairs in buckets.items()
    }


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AppStats:
    name: str
    sessions: int
    total_attempts: int
    weighted_avg: float       # 0–10
    timestamps: list[float]   # Unix timestamps of sessions (may be empty)
    file_present: bool


@dataclass
class DashboardReport:
    apps: list[AppStats]
    weakest_topics: list[tuple[str, float]]    # (label, avg_score) sorted asc, top 5
    recent_apps: dict[str, int]                # app_name -> problems in last 7 days
    streak_days: int
    # Tier-5 signals (see mistakes_panel() / calibration_panel()).  Defaulted
    # so that older callers constructing a report by hand keep working.
    mistakes: dict = field(default_factory=dict)
    calibration: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Core build function
# ---------------------------------------------------------------------------

def build_report() -> DashboardReport:
    """Load all history files and compute the dashboard report."""

    raw: dict[str, list[dict]] = {}
    for app_name, path in _FILES.items():
        raw[app_name] = _load(path)

    # ── Per-app stats ─────────────────────────────────────────────────────
    app_stats: list[AppStats] = []

    extractors = {
        "QEC Trainer":     (_extract_qec_vqa,    _FILES["QEC Trainer"]),
        "VQA Trainer":     (_extract_qec_vqa,    _FILES["VQA Trainer"]),
        "Flashcard Drill": (_extract_flashcard,  _FILES["Flashcard Drill"]),
        "Circuit Trainer": (_extract_circuit,    _FILES["Circuit Trainer"]),
        "Math Quiz":       (_extract_math_quiz,  _FILES["Math Quiz"]),
        "Quantum Quiz":    (_extract_math_quiz,  _FILES["Quantum Quiz"]),
        "Paper Drill":     (_extract_paper,      _FILES["Paper Drill"]),
        "Qiskit Dojo":     (_extract_dojo,       _FILES["Qiskit Dojo"]),
        "Exam Simulator":  (_extract_exam,       _FILES["Exam Simulator"]),
        "Problem Trainer": (_extract_problems,   _FILES["Problem Trainer"]),
    }

    for app_name, (fn, path) in extractors.items():
        sessions = raw[app_name]
        file_present = path.exists()
        if not sessions:
            app_stats.append(AppStats(
                name=app_name, sessions=0, total_attempts=0,
                weighted_avg=0.0, timestamps=[], file_present=file_present,
            ))
            continue
        n_sess, n_att, w_avg, tss, _, _ = fn(sessions)
        app_stats.append(AppStats(
            name=app_name,
            sessions=n_sess,
            total_attempts=n_att,
            weighted_avg=w_avg,
            timestamps=tss,
            file_present=file_present,
        ))

    # ── Weakest topics (qec + vqa + flashcard) ────────────────────────────
    merged: dict[str, tuple[float, float]] = {}

    def _merge(buckets: dict[str, tuple[float, float]], prefix: str) -> None:
        for cat, (ws, w) in buckets.items():
            label = f"[{prefix}] {cat}"
            if label in merged:
                old_ws, old_w = merged[label]
                merged[label] = (old_ws + ws, old_w + w)
            else:
                merged[label] = (ws, w)

    _merge(_topic_scores_qec_vqa(raw["QEC Trainer"]),     "QEC")
    _merge(_topic_scores_qec_vqa(raw["VQA Trainer"]),     "VQA")
    _merge(_topic_scores_flashcard(raw["Flashcard Drill"]), "FC")

    topic_avgs = [
        (label, ws / w)
        for label, (ws, w) in merged.items()
        if w > 0
    ]
    topic_avgs.sort(key=lambda x: x[1])
    weakest_topics = topic_avgs[:5]

    # ── Recent activity (last 7 days) ─────────────────────────────────────
    cutoff = _NOW - 7 * 86400.0
    recent_apps: dict[str, int] = {}

    def _recent_count_attempts(sessions: list[dict], key: str) -> int:
        count = 0
        for s in sessions:
            ts = _session_timestamp(s)
            if ts and ts >= cutoff:
                count += len(s.get(key, []))
        return count

    def _recent_count_paper(sessions: list[dict]) -> int:
        count = 0
        for s in sessions:
            ts = _session_timestamp(s)
            # Paper has no timestamp; skip from recent count
            if ts and ts >= cutoff:
                count += len(s.get("scores", []))
        return count

    for app_name, sessions in raw.items():
        if app_name in ("QEC Trainer", "VQA Trainer"):
            n = _recent_count_attempts(sessions, "attempts")
        elif app_name == "Flashcard Drill":
            n = _recent_count_attempts(sessions, "results")
        elif app_name == "Circuit Trainer":
            n = _recent_count_attempts(sessions, "attempts")
        elif app_name in ("Math Quiz", "Quantum Quiz"):
            n = _recent_count_attempts(sessions, "records")
        elif app_name == "Paper Drill":
            n = _recent_count_paper(sessions)
        elif app_name in ("Qiskit Dojo", "Problem Trainer"):
            n = _recent_count_attempts(sessions, "attempts")
        elif app_name == "Exam Simulator":
            n = 0
            for s in sessions:
                ts = _session_timestamp(s)
                if ts and ts >= cutoff:
                    try:
                        n += int(s.get("total", 0))
                    except (TypeError, ValueError):
                        pass
        else:
            n = 0
        if n > 0:
            recent_apps[app_name] = n

    # ── Streak (consecutive days with any activity) ───────────────────────
    all_ts: list[float] = []
    for app_stats_item in app_stats:
        all_ts.extend(app_stats_item.timestamps)

    active_days: set[str] = set()
    for ts in all_ts:
        d = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        active_days.add(d)

    streak_days = 0
    check = datetime.now(tz=timezone.utc).date()
    while True:
        if check.strftime("%Y-%m-%d") in active_days:
            streak_days += 1
            check -= timedelta(days=1)
        else:
            break

    return DashboardReport(
        apps=app_stats,
        weakest_topics=weakest_topics,
        recent_apps=recent_apps,
        streak_days=streak_days,
        mistakes=mistakes_panel(),
        calibration=calibration_panel(),
    )


# ---------------------------------------------------------------------------
# Retention & forgetting  (Tier-4 analytics)
#
# Two views, both computed from the history files above and both designed to
# say "not enough data yet" rather than guess:
#
#   1. Weekly accuracy per category — raw (un-decayed) accuracy bucketed into
#      trailing 7-day windows, printed with the number of observations behind
#      every single figure.
#   2. A forgetting curve — accuracy plotted against the number of days since
#      the *same item* (card / kata / problem / question id) was last seen.
#      An exponential R(t) = exp(-t/tau) is fitted through the origin by
#      observation-weighted least squares on the bucket means, and the fit is
#      only ever reported when at least FORGET_MIN_OBS repeat observations
#      spread over at least FORGET_MIN_BUCKETS interval buckets support it.
#
# Nothing here decays scores by recency: recency weighting is exactly what a
# retention view must not do.
# ---------------------------------------------------------------------------

RETENTION_WEEKS = 6           # trailing 7-day windows shown in the week table
RETENTION_MAX_ROWS = 12       # category rows printed (most observations first)
RETENTION_MIN_ROW_OBS = 3     # a category needs this many observations to show

# Interval buckets for the forgetting curve, in days: [lo, hi)
FORGET_BUCKETS = ((0.0, 1.0), (1.0, 3.0), (3.0, 7.0), (7.0, 14.0),
                  (14.0, 30.0), (30.0, math.inf))
FORGET_MIN_BUCKET_OBS = 5     # observations before a bucket's accuracy is used
FORGET_MIN_OBS = 20           # N: never fit a curve to fewer than this
FORGET_MIN_BUCKETS = 2        # ... spread over at least this many buckets
FORGET_MIN_R2 = 0.50          # ... and never report a fit this bad

_APP_PREFIX = {
    "QEC Trainer": "QEC", "VQA Trainer": "VQA", "Flashcard Drill": "FC",
    "Circuit Trainer": "CT", "Math Quiz": "MQ", "Quantum Quiz": "QQ",
    "Paper Drill": "PAPER", "Qiskit Dojo": "DOJO", "Exam Simulator": "EXAM",
    "Problem Trainer": "PT",
}

# Flashcard ratings as a recall fraction ("unsure" is a half-remembered card).
_RECALL = {"got_it": 1.0, "unsure": 0.5, "missed": 0.0}

_ATTEMPT_APPS = ("QEC Trainer", "VQA Trainer", "Circuit Trainer",
                 "Problem Trainer")


def _finite(value: float) -> bool:
    """True for a real number (json.loads happily produces NaN / Infinity)."""
    return value == value and value not in (float("inf"), float("-inf"))


def _parse_epoch(value) -> Optional[float]:
    """Epoch seconds from an epoch number, numeric string or ISO-8601 string.

    Naive ISO input is read as UTC (what the apps write).  Returns None when
    the value is missing or unparseable.  Unlike ``_session_timestamp`` this
    also accepts the ISO *strings* that circuit-trainer / math-quiz /
    quantum-quiz store in their "timestamp" field.
    """
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        pass
    else:
        # json.loads accepts NaN / Infinity; neither is a point in time.
        return number if _finite(number) else None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    try:
        return dt.timestamp()
    except (OverflowError, OSError, ValueError):
        return None


def _retention_epoch(session: dict) -> Optional[float]:
    """Session time for retention maths (tolerant of every schema variant)."""
    ts = _parse_epoch(session.get("timestamp"))
    if ts is not None:
        return ts
    return _parse_epoch(session.get("date"))


def _fraction(score, scale: float = 10.0) -> float:
    """A 0..scale score as a 0..1 fraction, clamped; unparseable -> 0.0."""
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0.0
    if not _finite(value):
        return 0.0
    return max(0.0, min(1.0, value / scale)) if scale else 0.0


@dataclass
class RetentionEvent:
    """One graded encounter.

    ``total`` is 1 for an item-level encounter and the question count for an
    aggregate one (an exam section), so accuracy is always correct/total.
    ``item`` is None when the schema gives no stable id — such events feed
    the weekly table but can never feed the forgetting curve.
    """
    app: str
    category: str
    label: str
    item: Optional[str]
    ts: float
    correct: float
    total: float


@dataclass
class WeeklyRow:
    label: str
    cells: list[Optional[tuple[float, int]]]   # (accuracy, n) per week, or None
    total_n: int


@dataclass
class CurveBucket:
    label: str
    mean_gap: float
    accuracy: float
    n: int
    in_fit: bool = False


@dataclass
class ForgettingCurve:
    n_obs: int
    buckets: list[CurveBucket]
    usable_buckets: int
    half_life_days: Optional[float]
    predicted_7d: Optional[float]
    baseline: Optional[float]      # fitted R(0): accuracy at zero elapsed days
    r_squared: Optional[float]     # weighted R^2 of the ln-accuracy fit
    note: str

    @property
    def fitted(self) -> bool:
        return self.half_life_days is not None


@dataclass
class RetentionReport:
    weeks: int
    week_labels: list[str]
    week_rows: list[WeeklyRow]
    rows_hidden: int
    curve: ForgettingCurve
    category_curves: list[tuple[str, ForgettingCurve]]
    n_events: int
    n_gap_obs: int
    week0: Optional[tuple[float, int]]   # (accuracy, n) over the last 7 days
    notes: list[str]


def _event(app: str, category, item, ts: float,
           correct: float, total: float) -> RetentionEvent:
    cat = " ".join(str(category or "").split()) or "uncategorised"
    ident = " ".join(str(item).split()) if item not in (None, "") else None
    return RetentionEvent(app=app, category=cat,
                          label=f"[{_APP_PREFIX.get(app, app)}] {cat}",
                          item=ident, ts=ts,
                          correct=float(correct), total=float(total))


def iter_retention_events(raw: dict[str, list]) -> list[RetentionEvent]:
    """Flatten every app's history into timestamped, graded encounters.

    Paper Drill is skipped: its schema has neither a timestamp nor a
    category, so it cannot be placed on a time axis.
    """
    events: list[RetentionEvent] = []
    for app, sessions in raw.items():
        if not isinstance(sessions, list) or app == "Paper Drill":
            continue
        for s in sessions:
            if not isinstance(s, dict):
                continue
            s_ts = _retention_epoch(s)

            def ts_of(record: dict) -> Optional[float]:
                own = _parse_epoch(record.get("timestamp"))
                return own if own is not None else s_ts

            if app in _ATTEMPT_APPS:
                for a in s.get("attempts", []) or []:
                    if not isinstance(a, dict):
                        continue
                    ts = ts_of(a)
                    if ts is None:
                        continue
                    cat = (a.get("kind") if app == "Problem Trainer"
                           else a.get("category"))
                    events.append(_event(app, cat, a.get("problem_id"), ts,
                                         _fraction(a.get("score", 0)), 1.0))
            elif app == "Flashcard Drill":
                for r in s.get("results", []) or []:
                    if not isinstance(r, dict):
                        continue
                    ts = ts_of(r)
                    if ts is None:
                        continue
                    events.append(_event(app, r.get("category"),
                                         r.get("card_id"), ts,
                                         _RECALL.get(r.get("rating"), 0.5),
                                         1.0))
            elif app in ("Math Quiz", "Quantum Quiz"):
                for r in s.get("records", []) or []:
                    if not isinstance(r, dict):
                        continue
                    ts = ts_of(r)
                    if ts is None:
                        continue
                    cat = r.get("topic") or r.get("subject")
                    events.append(_event(app, cat,
                                         r.get("question_id") or cat, ts,
                                         _fraction(r.get("score", 0)), 1.0))
            elif app == "Qiskit Dojo":
                for a in s.get("attempts", []) or []:
                    if not isinstance(a, dict):
                        continue
                    ts = ts_of(a)
                    if ts is None:
                        continue
                    events.append(_event(app, a.get("section"),
                                         a.get("kata_id"), ts,
                                         1.0 if a.get("passed") else 0.0, 1.0))
            elif app == "Exam Simulator":
                if s_ts is None:
                    continue
                secs = s.get("sections")
                emitted = False
                if isinstance(secs, dict):
                    for name, sec in secs.items():
                        if not isinstance(sec, dict):
                            continue
                        try:
                            total = float(sec.get("total", 0))
                            correct = float(sec.get("correct", 0))
                        except (TypeError, ValueError):
                            continue
                        if not (_finite(total) and _finite(correct)):
                            continue
                        if total <= 0:
                            continue
                        correct = max(0.0, min(correct, total))
                        events.append(_event(app, name, None, s_ts,
                                             correct, total))
                        emitted = True
                if not emitted:
                    try:
                        total = float(s.get("total", 0))
                        correct = float(s.get("correct", 0))
                    except (TypeError, ValueError):
                        continue
                    if not (_finite(total) and _finite(correct)):
                        continue
                    if total > 0:
                        events.append(_event(app, "whole exam", None, s_ts,
                                             max(0.0, min(correct, total)),
                                             total))
    events.sort(key=lambda e: (e.ts, e.label, e.item or ""))
    return events


def week_labels(weeks: int = RETENTION_WEEKS) -> list[str]:
    """Trailing 7-day window labels, most recent first ("0-6d", "7-13d", ...)."""
    return [f"{i * 7}-{i * 7 + 6}d" for i in range(weeks)]


def weekly_accuracy(events: list[RetentionEvent],
                    weeks: int = RETENTION_WEEKS,
                    now: Optional[float] = None) -> list[WeeklyRow]:
    """Per-category accuracy in each trailing 7-day window.

    Every cell is (accuracy, observations) or None when nothing was studied
    in that window — the count travels with the figure so a 100% built on two
    cards never reads like mastery.
    """
    now = _NOW if now is None else now
    buckets: dict[str, list[list[float]]] = {}
    for e in events:
        idx = int((now - e.ts) // (7 * 86400.0))
        idx = max(0, idx)
        if idx >= weeks:
            continue
        row = buckets.setdefault(e.label, [[0.0, 0.0] for _ in range(weeks)])
        row[idx][0] += e.correct
        row[idx][1] += e.total
    rows = []
    for label, cells in buckets.items():
        total_n = sum(c[1] for c in cells)
        rows.append(WeeklyRow(
            label=label,
            cells=[(c[0] / c[1], int(round(c[1]))) if c[1] > 0 else None
                   for c in cells],
            total_n=int(round(total_n))))
    rows.sort(key=lambda r: (-r.total_n, r.label))
    return rows


def gap_observations(events: list[RetentionEvent]
                     ) -> list[tuple[float, float, str]]:
    """(days since that item was last seen, accuracy then, category label).

    Only item-level encounters (a stable id, one question) participate, so
    exam sections never enter the forgetting curve.
    """
    by_item: dict[tuple[str, str], list[RetentionEvent]] = {}
    for e in events:
        if e.item is None or e.total != 1.0:
            continue
        by_item.setdefault((e.app, e.item), []).append(e)
    obs: list[tuple[float, float, str]] = []
    for evs in by_item.values():
        evs.sort(key=lambda e: e.ts)
        for prev, cur in zip(evs, evs[1:]):
            gap = (cur.ts - prev.ts) / 86400.0
            if gap < 0:
                continue
            obs.append((gap, max(0.0, min(1.0, cur.correct)), cur.label))
    obs.sort(key=lambda o: (o[0], o[2]))
    return obs


def fit_forgetting_curve(obs: list[tuple[float, float, str]]
                         ) -> ForgettingCurve:
    """Fit R(t) = R0 * exp(-t/tau) to bucketed (gap, accuracy) observations.

    Observation-weighted least squares on ln(accuracy).  With three or more
    usable buckets the baseline R0 is free (clamped to <= 1, since accuracy
    cannot exceed 1); with exactly two the line is forced through R0 = 1 and
    buckets at a zero mean gap cannot contribute.

    Refuses to fit — half_life_days stays None and ``note`` says why —
    unless at least FORGET_MIN_OBS observations spread over
    FORGET_MIN_BUCKETS buckets, each carrying FORGET_MIN_BUCKET_OBS
    observations and a non-zero accuracy, support it.  The bucket table is
    always returned so the raw numbers can be shown even when no curve can.
    """
    n = len(obs)
    rows: list[CurveBucket] = []
    for lo, hi in FORGET_BUCKETS:
        sel = [o for o in obs if lo <= o[0] < hi]
        if not sel:
            continue
        rows.append(CurveBucket(
            label=f"{lo:g}-{hi:g}d" if hi != math.inf else f"{lo:g}d+",
            mean_gap=sum(o[0] for o in sel) / len(sel),
            accuracy=sum(o[1] for o in sel) / len(sel),
            n=len(sel)))
    usable = [r for r in rows if r.n >= FORGET_MIN_BUCKET_OBS
              and r.accuracy > 0.0]

    def refuse(note: str) -> ForgettingCurve:
        return ForgettingCurve(n, rows, len(usable), None, None, None, None,
                               note)

    if n < FORGET_MIN_OBS:
        return refuse(f"not enough data yet — {n} of {FORGET_MIN_OBS} repeat "
                      f"observations needed before a curve is fitted")
    if len(usable) < FORGET_MIN_BUCKETS:
        return refuse(
            f"not enough spread yet — need {FORGET_MIN_BUCKETS} interval "
            f"buckets holding >= {FORGET_MIN_BUCKET_OBS} observations and a "
            f"non-zero accuracy (have {len(usable)})")

    free_intercept = len(usable) >= 3
    fit = usable if free_intercept else [r for r in usable if r.mean_gap > 0.0]
    if len(fit) < FORGET_MIN_BUCKETS:
        return refuse(
            f"not enough spread yet — only {len(fit)} interval bucket(s) with "
            f"a non-zero mean gap")

    if free_intercept:
        sw = sum(r.n for r in fit)
        sx = sum(r.n * r.mean_gap for r in fit)
        sy = sum(r.n * math.log(r.accuracy) for r in fit)
        sxx = sum(r.n * r.mean_gap ** 2 for r in fit)
        sxy = sum(r.n * r.mean_gap * math.log(r.accuracy) for r in fit)
        denom = sw * sxx - sx * sx
        slope = (sw * sxy - sx * sy) / denom if denom else 0.0
        intercept = (sy - slope * sx) / sw if sw else 0.0
        if intercept > 0.0:        # R0 > 1 is impossible -> refit through 1
            free_intercept = False
            fit = [r for r in usable if r.mean_gap > 0.0]
            if len(fit) < FORGET_MIN_BUCKETS:
                return refuse(
                    f"not enough spread yet — only {len(fit)} interval "
                    f"bucket(s) with a non-zero mean gap")
    if not free_intercept:
        sxy = sum(r.n * r.mean_gap * math.log(r.accuracy) for r in fit)
        sxx = sum(r.n * r.mean_gap ** 2 for r in fit)
        slope = sxy / sxx if sxx > 0 else 0.0
        intercept = 0.0

    for r in fit:
        r.in_fit = True

    # Weighted R^2 on ln(accuracy): a curve nobody could draw through these
    # points is worse than no curve at all.
    sw = sum(r.n for r in fit)
    ybar = sum(r.n * math.log(r.accuracy) for r in fit) / sw if sw else 0.0
    ss_res = sum(r.n * (math.log(r.accuracy)
                        - (intercept + slope * r.mean_gap)) ** 2 for r in fit)
    ss_tot = sum(r.n * (math.log(r.accuracy) - ybar) ** 2 for r in fit)
    r2 = (1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else 0.0

    if slope >= -1e-12:
        return ForgettingCurve(
            n, rows, len(usable), None, None, None, r2,
            f"no measurable decay — accuracy is flat or rising with the "
            f"interval across {n} repeat observations")
    if r2 < FORGET_MIN_R2:
        return ForgettingCurve(
            n, rows, len(usable), None, None, None, r2,
            f"too noisy to fit — accuracy vs interval explains only "
            f"{r2 * 100:.0f}% of the variation across {n} repeat "
            f"observations (need {FORGET_MIN_R2 * 100:.0f}%); the bucket "
            f"table above is the honest answer")
    tau = -1.0 / slope
    baseline = min(1.0, math.exp(intercept))
    shape = ("free baseline" if free_intercept else "baseline pinned at 100%")
    return ForgettingCurve(
        n, rows, len(usable), tau * math.log(2.0),
        baseline * math.exp(-7.0 / tau), baseline, r2,
        f"fitted to {n} repeat observations across {len(fit)} interval "
        f"bucket(s), {shape}, R^2 {r2:.2f}")


def build_retention(raw: Optional[dict[str, list]] = None,
                    weeks: int = RETENTION_WEEKS) -> RetentionReport:
    """The retention/forgetting view.  *raw* maps app display name -> sessions
    (loaded from _FILES when omitted)."""
    if raw is None:
        raw = {name: _load(path) for name, path in _FILES.items()}
    events = iter_retention_events(raw)
    all_rows = weekly_accuracy(events, weeks)
    shown = [r for r in all_rows if r.total_n >= RETENTION_MIN_ROW_OBS]
    hidden = len(all_rows) - len(shown[:RETENTION_MAX_ROWS])
    obs = gap_observations(events)

    per_label: dict[str, list[tuple[float, float, str]]] = {}
    for o in obs:
        per_label.setdefault(o[2], []).append(o)
    category_curves = []
    for label, sel in per_label.items():
        if len(sel) >= FORGET_MIN_OBS:
            curve = fit_forgetting_curve(sel)
            if curve.fitted:
                category_curves.append((label, curve))
    category_curves.sort(key=lambda lc: (-lc[1].n_obs, lc[0]))

    notes: list[str] = []
    if raw.get("Paper Drill"):
        notes.append("Paper Drill is excluded: its schema carries no "
                     "timestamp and no categories.")
    if any(e.item is None for e in events):
        notes.append("Exam Simulator sections count towards weekly accuracy "
                     "but not the forgetting curve (no per-question ids).")
    if events and not obs:
        notes.append("No item has been seen twice yet, so there is nothing "
                     "to measure forgetting against.")

    w0_correct = w0_total = 0.0
    for row in all_rows:                      # unfiltered: the honest rollup
        cell = row.cells[0] if row.cells else None
        if cell:
            w0_correct += cell[0] * cell[1]
            w0_total += cell[1]

    return RetentionReport(weeks=weeks, week_labels=week_labels(weeks),
                           week_rows=shown[:RETENTION_MAX_ROWS],
                           rows_hidden=hidden,
                           curve=fit_forgetting_curve(obs),
                           category_curves=category_curves,
                           n_events=len(events), n_gap_obs=len(obs),
                           week0=((w0_correct / w0_total, int(w0_total))
                                  if w0_total else None),
                           notes=notes)


def retention_summary(raw: Optional[dict[str, list]] = None) -> Optional[dict]:
    """One-line-teaser material, or None when there is nothing to say.

    {"half_life_days": float|None,      # pooled fit, None when unsupported
     "n_gap_obs": int,                  # repeat observations behind it
     "week_acc": float|None,            # accuracy over the last 7 days
     "week_n": int,                     # ... and the observations behind that
     "category_label": str|None,        # best-supported per-category fit
     "category_half_life": float|None,
     "category_n": int,
     "note": str}                       # why the pooled fit did or did not run
    """
    report = build_retention(raw)
    if report.n_events == 0:
        return None
    best = report.category_curves[0] if report.category_curves else None
    return {
        "half_life_days": report.curve.half_life_days,
        "n_gap_obs": report.n_gap_obs,
        "week_acc": report.week0[0] if report.week0 else None,
        "week_n": report.week0[1] if report.week0 else 0,
        "category_label": best[0] if best else None,
        "category_half_life": best[1].half_life_days if best else None,
        "category_n": best[1].n_obs if best else 0,
        "note": report.curve.note,
    }


_ROW_LABEL_WIDTH = 24


def _cell_text(cell: Optional[tuple[float, int]]) -> str:
    if not cell:
        return "--"
    acc, n = cell
    return f"{acc * 100:.0f}%/{n}"


def _row_label(label: str) -> str:
    if len(label) <= _ROW_LABEL_WIDTH:
        return label
    return label[:_ROW_LABEL_WIDTH - 1] + "\u2026"


def _render_retention_plain(report: RetentionReport) -> None:
    print("RETENTION & FORGETTING")
    print("-" * 62)
    if report.n_events == 0:
        print("  No timestamped, graded history yet — nothing to retain.")
        print("  Study anything with a timestamp (any app but Paper Drill)")
        print("  and this view fills in.")
        print()
        return

    print(f"  Weekly accuracy by category  (cell = accuracy/observations, "
          f"last {report.weeks} weeks)")
    print("  " + f"{'category':<{_ROW_LABEL_WIDTH}}"
          + "".join(f"{lab:>9}" for lab in report.week_labels)
          + f"{'total':>8}")
    for row in report.week_rows:
        cells = "".join(f"{_cell_text(c):>9}" for c in row.cells)
        print(f"  {_row_label(row.label):<{_ROW_LABEL_WIDTH}}{cells}"
              f"{'n=' + str(row.total_n):>8}")
    if not report.week_rows:
        print(f"  (no category reached {RETENTION_MIN_ROW_OBS} observations "
              f"in the last {report.weeks} weeks)")
    if report.rows_hidden > 0:
        print(f"  ... {report.rows_hidden} thinner category row(s) hidden "
              f"(< {RETENTION_MIN_ROW_OBS} observations or past the "
              f"{RETENTION_MAX_ROWS}-row cap)")
    print()

    curve = report.curve
    print("  Forgetting curve — accuracy vs days since that item was last seen")
    if curve.buckets:
        print(f"    {'gap':<10}{'accuracy':>10}{'n':>6}{'mean gap':>11}"
              f"   in fit")
        for b in curve.buckets:
            print(f"    {b.label:<10}{b.accuracy * 100:9.0f}%{b.n:6d}"
                  f"{b.mean_gap:10.1f}d   "
                  f"{'yes' if b.in_fit else 'no'}")
    else:
        print("    (no repeat observations yet)")
    if curve.fitted:
        print(f"    Estimated retention half-life: "
              f"{curve.half_life_days:.1f} days — {curve.note}")
        print(f"    Fitted accuracy right after a review: "
              f"{curve.baseline * 100:.0f}%; after 7 days: "
              f"{curve.predicted_7d * 100:.0f}%")
    else:
        print(f"    No curve: {curve.note}.")
    print()
    if report.category_curves:
        print("  Per-category half-life (only where the fit is supported):")
        for label, c in report.category_curves:
            print(f"    {label[:34]:<34} {c.half_life_days:6.1f}d  "
                  f"n={c.n_obs}")
        print()
    for note in report.notes:
        print(f"  note: {note}")
    if report.notes:
        print()


def _render_retention_rich(report: RetentionReport) -> None:
    from rich.console import Console
    from rich.table import Table
    from rich import box

    console = Console()
    console.print("[bold]Retention & Forgetting[/bold]")
    if report.n_events == 0:
        console.print("[dim]  No timestamped, graded history yet — study "
                      "anything with a timestamp and this view fills in."
                      "[/dim]")
        console.print()
        return

    wtable = Table(title=f"[bold]Weekly accuracy by category[/bold] "
                         f"(accuracy/observations, last {report.weeks} weeks)",
                   box=box.SIMPLE_HEAD, header_style="bold magenta")
    wtable.add_column("Category", style="cyan", no_wrap=True)
    for lab in report.week_labels:
        wtable.add_column(lab, justify="right")
    wtable.add_column("n", justify="right")
    for row in report.week_rows:
        wtable.add_row(row.label,
                       *[("[dim]—[/dim]" if not c
                          else f"{c[0] * 100:.0f}%/{c[1]}") for c in row.cells],
                       str(row.total_n))
    if report.week_rows:
        console.print(wtable)
    else:
        console.print(f"[dim]  No category reached {RETENTION_MIN_ROW_OBS} "
                      f"observations in the last {report.weeks} weeks.[/dim]")
    if report.rows_hidden > 0:
        console.print(f"[dim]  ... {report.rows_hidden} thinner category "
                      f"row(s) hidden.[/dim]")
    console.print()

    curve = report.curve
    ctable = Table(title="[bold]Forgetting curve[/bold] — accuracy vs days "
                         "since that item was last seen",
                   box=box.SIMPLE_HEAD, header_style="bold magenta")
    ctable.add_column("Gap", style="cyan")
    ctable.add_column("Accuracy", justify="right")
    ctable.add_column("n", justify="right")
    ctable.add_column("Mean gap", justify="right")
    ctable.add_column("In fit", justify="center")
    for b in curve.buckets:
        ctable.add_row(b.label, f"{b.accuracy * 100:.0f}%", str(b.n),
                       f"{b.mean_gap:.1f}d",
                       "yes" if b.in_fit else "[dim]no[/dim]")
    if curve.buckets:
        console.print(ctable)
    else:
        console.print("[dim]  No repeat observations yet.[/dim]")
    if curve.fitted:
        console.print(f"  [bold]Estimated retention half-life:[/bold] "
                      f"{curve.half_life_days:.1f} days [dim]— {curve.note}"
                      f"[/dim]")
        console.print(f"  Fitted accuracy right after a review: "
                      f"{curve.baseline * 100:.0f}%; after 7 days: "
                      f"{curve.predicted_7d * 100:.0f}%")
    else:
        console.print(f"  [yellow]No curve:[/yellow] {curve.note}.")
    console.print()
    if report.category_curves:
        console.print("[bold]Per-category half-life[/bold] "
                      "(only where the fit is supported):")
        for label, c in report.category_curves:
            console.print(f"  {label} — {c.half_life_days:.1f}d "
                          f"[dim](n={c.n_obs})[/dim]")
        console.print()
    for note in report.notes:
        console.print(f"[dim]  note: {note}[/dim]")
    if report.notes:
        console.print()


# ---------------------------------------------------------------------------
# Mistake journal & confidence calibration  (Tier-5 signals)
#
# Two files the apps write as you answer (this module only ever reads them):
#
#   mistakes.json    [ {"id", "app", "category", "question", "your_answer",
#                       "correct_answer", "cause", "note", "timestamp",
#                       "resolved"} ]
#     cause is one of MISTAKE_CAUSES or null -- null means "logged, but the
#     learner has not said WHY yet".  A wrong answer that only becomes a
#     bookmark teaches nothing; the cause is the payload.
#
#   confidence.json  [ {"id", "app", "category", "confidence": 1-4,
#                       "correct": bool, "timestamp"} ]
#     1 = guessing, 2 = unsure, 3 = fairly sure, 4 = certain.  The confidence
#     is recorded BEFORE the answer is revealed, so "confident and wrong" --
#     the unknown unknowns -- becomes measurable.
#
# Both are read defensively: absent, empty, truncated, corrupt, wrong-typed
# and hand-edited files all degrade to "no data" instead of raising.  The
# schema helpers live here, in one place, because coach.py builds its
# --mistakes / --calibration / --item-analysis reports on exactly these
# normalisers.
# ---------------------------------------------------------------------------

MISTAKES_FILE = "mistakes.json"
CONFIDENCE_FILE = "confidence.json"

# Cause vocabulary, in the order the apps show the buttons.
MISTAKE_CAUSES = ("misread", "didnt_know", "knew_but_slipped", "confused",
                  "out_of_time", "other")
UNCATEGORISED = "uncategorised"        # synthetic bucket for cause = null

CAUSE_LABELS = {
    "misread":          "misread the question",
    "didnt_know":       "didn't know it",
    "knew_but_slipped": "knew it but slipped",
    "confused":         "confused two ideas",
    "out_of_time":      "ran out of time",
    "other":            "other",
    UNCATEGORISED:      "not categorised yet",
}

# The whole point of the cause vocabulary: each one implies a DIFFERENT fix.
CAUSE_ADVICE = {
    "misread": "Slow down and re-read. Cover the options, restate the "
               "question in your own words, then look.",
    "didnt_know": "This is missing knowledge, not a slip — go back to the "
                  "chapter and re-read before drilling.",
    "knew_but_slipped": "You need drilling, not reading — short, frequent "
                        "reps until the recall is automatic.",
    "confused": "Two ideas are colliding. Write the pair out side by side "
                "and name the one difference that tells them apart.",
    "out_of_time": "Practise under the clock: budget per question, answer "
                   "the cheap ones first, and flag rather than stall.",
    "other": "Re-read these notes — if a pattern shows up, give it its own "
             "cause next time.",
    UNCATEGORISED: "Categorise them. Until a mistake has a cause it is a "
                   "bookmark, not analysis — the cause row takes one click.",
}

CONFIDENCE_LEVELS = (1, 2, 3, 4)
CONFIDENCE_LABELS = {1: "guessing", 2: "unsure", 3: "fairly sure",
                     4: "certain"}
# What a perfectly calibrated learner scores at each level.
CONFIDENCE_TARGET = {1: 0.25, 2: 0.50, 3: 0.75, 4: 0.95}
CONFIDENT_LEVEL = 3            # >= this counts as "said they were confident"

CONFIDENCE_MIN_OBS = 20        # N: no calibration verdict below this
CONFIDENCE_MIN_LEVEL_OBS = 5   # per-level floor before a level is judged

JOURNAL_TEXT_MAX = 200         # contract cap on question / answer strings
JOURNAL_READ_CAP = 20000       # newest-N entries kept when a file grows huge


def _journal_text(value, limit: int = JOURNAL_TEXT_MAX) -> str:
    """One-line, whitespace-collapsed, length-capped text (never None)."""
    if value is None or isinstance(value, bool):
        return ""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _journal_epoch(value) -> float:
    """Contract timestamp as epoch seconds; 0.0 when missing or unusable."""
    ts = _parse_epoch(value)
    if ts is None or ts <= 0:
        return 0.0
    if ts > 1e11:              # millisecond epoch -- normalise to seconds
        ts /= 1000.0
    return ts


def make_mistake_entry(id: str, app: str, category: str = "",
                       question: str = "", your_answer: str = "",
                       correct_answer: str = "", cause: Optional[str] = None,
                       note: str = "", timestamp: Optional[float] = None,
                       resolved: bool = False) -> dict:
    """A schema-valid mistakes.json entry.

    The canonical constructor for the journal: the apps call it when an
    answer is graded wrong, and the tests round-trip it through
    ``normalise_mistake``.  An unknown *cause* is stored as None rather than
    invented, which is the same thing as "logged but not yet categorised".
    """
    return {
        "id": _journal_text(id, 200),
        "app": _journal_text(app, 64),
        "category": _journal_text(category, 120),
        "question": _journal_text(question),
        "your_answer": _journal_text(your_answer),
        "correct_answer": _journal_text(correct_answer),
        "cause": cause if cause in MISTAKE_CAUSES else None,
        "note": _journal_text(note),
        "timestamp": _journal_epoch(
            timestamp if timestamp is not None else time.time()),
        "resolved": bool(resolved),
    }


def normalise_mistake(raw) -> Optional[dict]:
    """A mistakes.json entry coerced to the schema, or None if unusable.

    Only ``id`` is truly required; a missing app becomes "unknown" so the
    entry still counts instead of being silently dropped.
    """
    if not isinstance(raw, dict):
        return None
    ident = _journal_text(raw.get("id"), 200)
    if not ident:
        return None
    cause = raw.get("cause")
    entry = make_mistake_entry(
        id=ident,
        app=_journal_text(raw.get("app"), 64) or "unknown",
        category=raw.get("category") or "",
        question=raw.get("question") or "",
        your_answer=raw.get("your_answer") or "",
        correct_answer=raw.get("correct_answer") or "",
        cause=cause if isinstance(cause, str) else None,
        note=raw.get("note") or "",
        timestamp=_journal_epoch(raw.get("timestamp")),
        resolved=bool(raw.get("resolved")),
    )
    return entry


def make_confidence_entry(id: str, app: str, confidence: int,
                          correct: bool, category: str = "",
                          timestamp: Optional[float] = None) -> dict:
    """A schema-valid confidence.json observation (pure; writes nothing).

    The apps call this when an answer is graded, pairing the rating the
    learner gave BEFORE the reveal with the verdict.  An out-of-range
    confidence raises rather than being silently clamped -- a 5 or a 0 means
    the caller's UI and this schema disagree.
    """
    level = int(confidence)
    if level not in CONFIDENCE_TARGET:
        raise ValueError(f"confidence must be 1-4, got {confidence!r}")
    return {
        "id": _journal_text(id, 200),
        "app": _journal_text(app, 64),
        "category": _journal_text(category, 120),
        "confidence": level,
        "correct": bool(correct),
        "timestamp": _journal_epoch(
            timestamp if timestamp is not None else time.time()),
    }


def normalise_confidence(raw) -> Optional[dict]:
    """A confidence.json observation coerced to the schema, or None.

    Requires an id and a confidence inside 1..4; ``correct`` is read as a
    plain truthy flag so a 0/1 int from a hand-edited file still works.
    """
    if not isinstance(raw, dict):
        return None
    ident = _journal_text(raw.get("id"), 200)
    if not ident:
        return None
    raw_level = raw.get("confidence")
    # A bool is an int in Python; True is not a confidence of 1.
    if isinstance(raw_level, bool) or not isinstance(raw_level,
                                                     (int, float, str)):
        return None
    try:
        level = int(raw_level)          # int(NaN) / int("high") raise here
    except (TypeError, ValueError, OverflowError):
        return None
    if level not in CONFIDENCE_TARGET:
        return None
    correct = raw.get("correct")
    if correct is None:
        return None
    return {
        "id": ident,
        "app": _journal_text(raw.get("app"), 64) or "unknown",
        "category": _journal_text(raw.get("category"), 120),
        "confidence": level,
        "correct": bool(correct),
        "timestamp": _journal_epoch(raw.get("timestamp")),
    }


def _read_journal(name: str, path: Optional[Path] = None) -> list:
    """Raw JSON list from *path* (default <DATA_DIR>/<name>).

    Returns [] for absent, empty, corrupt or wrong-shaped files.  DATA_DIR is
    read at call time so tests can monkeypatch it; coach.py passes its own
    (separately overridable) path instead.
    """
    target = Path(path) if path is not None else DATA_DIR / name
    try:
        data = json.loads(target.read_text())
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def _cap_newest(entries: list[dict], cap: int = JOURNAL_READ_CAP
                ) -> list[dict]:
    """The newest *cap* entries (by timestamp) when a journal grows huge.

    Neither file is ever rewritten here — this only bounds what one report
    holds in memory.  Reports say so when the cap bites.
    """
    if len(entries) <= cap:
        return entries
    return sorted(entries, key=lambda e: e["timestamp"])[-cap:]


def load_mistakes(path: Optional[Path] = None) -> list[dict]:
    """Every readable mistakes.json entry, oldest first.

    Byte-identical duplicate writes of the same (app, id, timestamp) are
    collapsed; a genuine second miss of the same item keeps its own entry,
    because repetition is exactly the signal the report is looking for.
    """
    out: list[dict] = []
    seen: set[tuple[str, str, float]] = set()
    for raw in _read_journal(MISTAKES_FILE, path):
        entry = normalise_mistake(raw)
        if entry is None:
            continue
        key = (entry["app"], entry["id"], round(entry["timestamp"], 3))
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    out = _cap_newest(out)
    out.sort(key=lambda e: (e["timestamp"], e["app"], e["id"]))
    return out


def load_confidence(path: Optional[Path] = None) -> list[dict]:
    """Every readable confidence.json observation, oldest first."""
    out = [c for c in (normalise_confidence(raw)
                       for raw in _read_journal(CONFIDENCE_FILE, path))
           if c is not None]
    out = _cap_newest(out)
    out.sort(key=lambda c: (c["timestamp"], c["app"], c["id"]))
    return out


def latest_mistakes(entries: list[dict]) -> list[dict]:
    """The newest entry per (app, id) — the current state of each item."""
    newest: dict[tuple[str, str], dict] = {}
    for entry in entries:
        key = (entry["app"], entry["id"])
        current = newest.get(key)
        if current is None or entry["timestamp"] >= current["timestamp"]:
            newest[key] = entry
    return sorted(newest.values(),
                  key=lambda e: (e["timestamp"], e["app"], e["id"]))


def unresolved_mistakes(entries: list[dict]) -> list[dict]:
    """Still-unresolved items, oldest first (one row per app+id)."""
    return [e for e in latest_mistakes(entries) if not e["resolved"]]


def cause_of(entry: dict) -> str:
    """The entry's cause, with null mapped to the UNCATEGORISED bucket."""
    cause = entry.get("cause")
    return cause if cause in MISTAKE_CAUSES else UNCATEGORISED


def mistake_cause_counts(entries: list[dict]) -> dict[str, int]:
    """{cause: count} over *entries*, ranked most frequent first."""
    counts: dict[str, int] = {}
    for entry in entries:
        key = cause_of(entry)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def mistakes_panel(entries: Optional[list[dict]] = None) -> dict:
    """Compact mistakes-by-cause summary (the dashboard panel + coach header)."""
    if entries is None:
        entries = load_mistakes()
    total = len(entries)
    counts = mistake_cause_counts(entries)
    rows = [{"cause": cause,
             "label": CAUSE_LABELS.get(cause, cause),
             "n": n,
             "pct": (n / total * 100.0) if total else 0.0}
            for cause, n in counts.items()]
    categorised = [r for r in rows if r["cause"] != UNCATEGORISED]
    dominant: Optional[str] = (str(categorised[0]["cause"]) if categorised
                               else None)
    latest = latest_mistakes(entries)
    unresolved = [e for e in latest if not e["resolved"]]
    apps: dict[str, int] = {}
    for entry in entries:
        apps[entry["app"]] = apps.get(entry["app"], 0) + 1
    stamps = [e["timestamp"] for e in entries if e["timestamp"] > 0]
    return {
        "n": total,
        "n_items": len(latest),
        "n_unresolved": len(unresolved),
        "n_resolved": len(latest) - len(unresolved),
        "rows": rows,
        "counts": counts,
        "dominant": dominant,
        "advice": CAUSE_ADVICE.get(dominant) if dominant else None,
        "uncategorised": counts.get(UNCATEGORISED, 0),
        "apps": dict(sorted(apps.items(), key=lambda kv: (-kv[1], kv[0]))),
        "first_ts": min(stamps) if stamps else None,
        "last_ts": max(stamps) if stamps else None,
    }


def confidence_levels(obs: list[dict]) -> list[dict]:
    """Per-confidence-level accuracy against the calibrated target."""
    rows = []
    for level in CONFIDENCE_LEVELS:
        at = [o for o in obs if o["confidence"] == level]
        n = len(at)
        correct = sum(1 for o in at if o["correct"])
        accuracy = (correct / n) if n else None
        target = CONFIDENCE_TARGET[level]
        rows.append({
            "level": level,
            "label": CONFIDENCE_LABELS[level],
            "n": n,
            "correct": correct,
            "accuracy": accuracy,
            "target": target,
            "gap": (accuracy - target) if accuracy is not None else None,
            "judged": n >= CONFIDENCE_MIN_LEVEL_OBS,
        })
    return rows


def overconfidence_index(obs: list[dict]) -> Optional[float]:
    """Mean(claimed accuracy) - mean(actual), in percentage points.

    Positive = overconfident (you believe yourself more than the marking
    agrees), negative = underconfident.  None with no observations.
    """
    if not obs:
        return None
    claimed = sum(CONFIDENCE_TARGET[o["confidence"]] for o in obs) / len(obs)
    actual = sum(1 for o in obs if o["correct"]) / len(obs)
    return (claimed - actual) * 100.0


def confidently_wrong(obs: list[dict]) -> list[dict]:
    """Topics answered wrong while claiming confidence >= CONFIDENT_LEVEL.

    Grouped by (app, category) and ranked worst first: most confidently-wrong
    answers, then highest average claimed confidence, then most recent.
    These are the unknown unknowns — the ones that sink an exam score,
    because nothing in the study loop flags them as shaky.
    """
    groups: dict[tuple[str, str], dict] = {}
    for o in obs:
        if o["confidence"] < CONFIDENT_LEVEL or o["correct"]:
            continue
        key = (o["app"], o["category"] or "(no category)")
        row = groups.setdefault(key, {"app": key[0], "category": key[1],
                                      "n": 0, "ids": [], "conf_sum": 0,
                                      "last_ts": 0.0})
        row["n"] += 1
        row["conf_sum"] += o["confidence"]
        row["last_ts"] = max(row["last_ts"], o["timestamp"])
        if o["id"] not in row["ids"]:
            row["ids"].append(o["id"])
    rows = list(groups.values())
    for row in rows:
        row["mean_confidence"] = row["conf_sum"] / row["n"]
        del row["conf_sum"]
    rows.sort(key=lambda r: (-r["n"], -r["mean_confidence"], -r["last_ts"],
                             r["app"], r["category"]))
    return rows


def calibration_panel(obs: Optional[list[dict]] = None) -> dict:
    """Confidence-vs-accuracy summary (the dashboard panel + coach report)."""
    if obs is None:
        obs = load_confidence()
    n = len(obs)
    n_correct = sum(1 for o in obs if o["correct"])
    confident = [o for o in obs if o["confidence"] >= CONFIDENT_LEVEL]
    conf_wrong = [o for o in confident if not o["correct"]]
    index = overconfidence_index(obs)
    enough = n >= CONFIDENCE_MIN_OBS
    if not enough:
        verdict = (f"not enough graded confidence ratings yet — "
                   f"{CONFIDENCE_MIN_OBS} needed, {n} on file")
    elif index is None:
        verdict = "no verdict"
    elif index > 10.0:
        verdict = "overconfident"
    elif index < -10.0:
        verdict = "underconfident"
    else:
        verdict = "well calibrated"
    apps: dict[str, int] = {}
    for o in obs:
        apps[o["app"]] = apps.get(o["app"], 0) + 1
    return {
        "n": n,
        "n_correct": n_correct,
        "accuracy": (n_correct / n) if n else None,
        "levels": confidence_levels(obs),
        "overconfidence": index,
        "n_confident": len(confident),
        "n_confidently_wrong": len(conf_wrong),
        "confident_error_rate": (len(conf_wrong) / len(confident)
                                 if confident else None),
        "confidently_wrong": confidently_wrong(obs),
        "enough": enough,
        "min_obs": CONFIDENCE_MIN_OBS,
        "min_level_obs": CONFIDENCE_MIN_LEVEL_OBS,
        "verdict": verdict,
        "apps": dict(sorted(apps.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


# -- panel rendering (shared by the rich and plain-text mastery reports) -----

SIGNAL_BAR_WIDTH = 16


def signal_bar(fraction: float, width: int = SIGNAL_BAR_WIDTH) -> str:
    filled = max(0, min(width, int(round(fraction * width))))
    return "█" * filled + "░" * (width - filled)


def signal_panel_lines(mistakes: Optional[dict] = None,
                       calibration: Optional[dict] = None) -> list[tuple[str, str]]:
    """(text, style) lines for the two Tier-5 panels.

    Style names double as plain-text semantics: nothing here depends on
    colour, every judgement is also spelled out in words, so the panels read
    the same on a monochrome terminal or through a screen reader.
    """
    # A falsy argument means "nothing supplied": a DashboardReport built by
    # hand carries {} for both panels, and must still render.
    m = mistakes if mistakes else mistakes_panel([] if mistakes == {} else None)
    c = (calibration if calibration
         else calibration_panel([] if calibration == {} else None))
    lines: list[tuple[str, str]] = []

    if not m["n"] and not c["n"]:
        lines.append(("No mistake-journal or confidence data yet — the apps "
                      "write mistakes.json / confidence.json as you answer.",
                      "dim"))
        return lines

    lines.append(("MISTAKES BY CAUSE", "bold"))
    if not m["n"]:
        lines.append(("  no mistakes logged yet", "dim"))
    else:
        lines.append((f"  {m['n']} logged over {m['n_items']} item(s) — "
                      f"{m['n_unresolved']} unresolved, "
                      f"{m['n_resolved']} cleared", ""))
        for row in m["rows"]:
            lines.append((f"  {row['label']:<22} {row['n']:>4}  "
                          f"{signal_bar(row['n'] / m['n'])} "
                          f"{row['pct']:>3.0f}%", ""))
        if m["dominant"]:
            lines.append((f"  dominant cause: {CAUSE_LABELS[m['dominant']]} "
                          f"-> {CAUSE_ADVICE[m['dominant']]}", "yellow"))
        if m["uncategorised"]:
            lines.append((f"  {m['uncategorised']} mistake(s) have no cause "
                          f"yet — categorise them in the app to make this "
                          f"panel mean something", "dim"))
        lines.append(("  full breakdown: python coach.py --mistakes", "dim"))
    lines.append(("", ""))

    lines.append(("CONFIDENCE CALIBRATION", "bold"))
    if not c["n"]:
        lines.append(("  no confidence ratings yet", "dim"))
        return lines
    lines.append((f"  {c['n']} rated answer(s), "
                  f"{c['accuracy'] * 100:.0f}% correct overall", ""))
    for row in c["levels"]:
        if not row["n"]:
            continue
        if row["judged"]:
            gap = row["gap"] * 100.0
            mark = "over" if gap < -5 else ("under" if gap > 5 else "ok")
            acc = f"{row['accuracy'] * 100:>3.0f}%"
        else:
            mark = f"n<{c['min_level_obs']}"
            acc = f"{row['accuracy'] * 100:>3.0f}%"
        lines.append((f"  {row['level']} {row['label']:<12} n={row['n']:<4} "
                      f"{acc} vs {row['target'] * 100:.0f}% target  [{mark}]",
                      ""))
    if c["enough"] and c["overconfidence"] is not None:
        lines.append((f"  overconfidence index "
                      f"{c['overconfidence']:+.0f} pts — {c['verdict']}",
                      "yellow"))
    else:
        # Below the floor no index is quoted: a number from 6 answers would
        # read as a measurement when it is noise.
        lines.append((f"  no overconfidence index yet — {c['verdict']}",
                      "dim"))
    if c["confidently_wrong"]:
        top = ", ".join(f"{r['category']} [{r['app']}] x{r['n']}"
                        for r in c["confidently_wrong"][:3])
        lines.append((f"  confidently WRONG ({c['n_confidently_wrong']} "
                      f"answer(s)): {top}", "red"))
    else:
        lines.append(("  no confidently-wrong answers on file — good", ""))
    lines.append(("  full breakdown: python coach.py --calibration", "dim"))
    return lines


# ---------------------------------------------------------------------------
# Rendering helpers (shared by rich and plain-text renderers)
# ---------------------------------------------------------------------------

def _bar(score: float, max_score: float = 10.0, width: int = 10) -> tuple[str, int]:
    """Return (bar_string, pct) for a score on a 0..max_score scale."""
    pct = int(round(score / max_score * 100)) if max_score else 0
    pct = max(0, min(100, pct))
    filled = round(pct / 100 * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return bar, pct


# ---------------------------------------------------------------------------
# Rich renderer
# ---------------------------------------------------------------------------

def _render_rich(report: DashboardReport) -> None:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from rich.panel import Panel
    from rich.text import Text

    console = Console()
    console.print()
    console.rule("[bold cyan]Quantum Study Dashboard[/bold cyan]")
    console.print()

    # ── Section 1: Overall mastery ─────────────────────────────────────────
    table = Table(
        title="[bold]Overall Mastery[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        expand=False,
    )
    table.add_column("App", style="cyan", no_wrap=True)
    table.add_column("Sessions", justify="right")
    table.add_column("Problems", justify="right")
    table.add_column("Avg Score", justify="right")
    table.add_column("Mastery", no_wrap=True)
    table.add_column("%", justify="right")

    for app in report.apps:
        bar_str, pct = _bar(app.weighted_avg)
        if not app.file_present:
            status = "[dim]no history[/dim]"
            bar_display = "[dim]not started[/dim]"
            avg_display = "[dim]—[/dim]"
        else:
            if pct >= 70:
                color = "green"
            elif pct >= 40:
                color = "yellow"
            else:
                color = "red"
            bar_display = f"[{color}]{bar_str}[/{color}]"
            avg_display = f"{app.weighted_avg:.1f}"
            status = str(app.sessions)

        table.add_row(
            app.name,
            status if app.file_present else "[dim]—[/dim]",
            str(app.total_attempts) if app.file_present else "[dim]—[/dim]",
            avg_display,
            bar_display,
            f"{pct}%" if app.file_present else "[dim]—[/dim]",
        )

    console.print(table)
    console.print()

    # ── Section 2: Weakest topics ─────────────────────────────────────────
    if report.weakest_topics:
        wtable = Table(
            title="[bold]Weakest Topics (QEC + VQA + Flashcard)[/bold]",
            box=box.SIMPLE_HEAD,
            header_style="bold red",
        )
        wtable.add_column("Topic", style="cyan")
        wtable.add_column("Weighted Avg", justify="right")
        wtable.add_column("Bar", no_wrap=True)

        for label, avg in report.weakest_topics:
            bar_str, pct = _bar(avg)
            wtable.add_row(label, f"{avg:.1f}/10", f"[red]{bar_str}[/red] {pct}%")

        console.print(wtable)
    else:
        console.print("[dim]No topic data yet (QEC, VQA, Flashcard not used).[/dim]")
    console.print()

    # ── Section 3: Recent activity ─────────────────────────────────────────
    console.print("[bold]Recent Activity[/bold] — last 7 days")
    if report.recent_apps:
        for app_name, count in sorted(report.recent_apps.items()):
            console.print(f"  [green]●[/green] [cyan]{app_name}[/cyan]: {count} problem(s)")
    else:
        console.print("  [dim]No activity in the last 7 days.[/dim]")
    console.print()

    # ── Section 4: Streak ─────────────────────────────────────────────────
    streak = report.streak_days
    if streak == 0:
        streak_msg = "[red]0 days[/red] — no current streak"
    elif streak == 1:
        streak_msg = "[yellow]1 day[/yellow] streak"
    elif streak < 7:
        streak_msg = f"[yellow]{streak} days[/yellow] streak"
    else:
        streak_msg = f"[green]{streak} days[/green] streak \U0001f525"

    console.print(Panel(
        f"[bold]Study Streak:[/bold] {streak_msg}",
        box=box.ROUNDED,
        expand=False,
    ))
    console.print()

    # ── Section 5: mistakes by cause + confidence calibration ────────────
    from rich.markup import escape
    for text, style in signal_panel_lines(report.mistakes,
                                          report.calibration):
        if not text:
            console.print()
        elif style:
            console.print(f"[{style}]{escape(text)}[/{style}]")
        else:
            console.print(escape(text))
    console.print()


# ---------------------------------------------------------------------------
# Plain-text renderer (fallback when rich is not installed)
# ---------------------------------------------------------------------------

def _render_plain(report: DashboardReport) -> None:
    SEP = "=" * 62

    print()
    print(SEP)
    print("       QUANTUM STUDY DASHBOARD")
    print(SEP)
    print()

    # Section 1
    print("OVERALL MASTERY")
    print("-" * 62)
    fmt = "{:<18} {:>8} {:>8} {:>6}  {} {:>4}"
    print(fmt.format("App", "Sessions", "Problems", "Avg", "Mastery   ", "  %"))
    print("-" * 62)
    for app in report.apps:
        bar_str, pct = _bar(app.weighted_avg)
        if not app.file_present:
            print(f"  {app.name:<16} {'(no history)':>40}")
        else:
            avg_str = f"{app.weighted_avg:.1f}"
            print(fmt.format(
                app.name,
                app.sessions,
                app.total_attempts,
                avg_str,
                bar_str,
                f"{pct}%",
            ))
    print()

    # Section 2
    print("WEAKEST TOPICS  (QEC + VQA + Flashcard)")
    print("-" * 62)
    if report.weakest_topics:
        for label, avg in report.weakest_topics:
            bar_str, pct = _bar(avg)
            print(f"  {label:<32} {avg:4.1f}/10  {bar_str} {pct}%")
    else:
        print("  No topic data yet.")
    print()

    # Section 3
    print("RECENT ACTIVITY  (last 7 days)")
    print("-" * 62)
    if report.recent_apps:
        for app_name, count in sorted(report.recent_apps.items()):
            print(f"  * {app_name}: {count} problem(s)")
    else:
        print("  No activity in the last 7 days.")
    print()

    # Section 4
    print("STREAK")
    print("-" * 62)
    streak = report.streak_days
    print(f"  {streak} consecutive day(s) of study activity")
    print()

    # Section 5 -- mistakes by cause + confidence calibration.  Rendered from
    # the same (text, style) lines the rich view uses; nothing in them relies
    # on colour, so the two views say exactly the same thing.
    for text, _style in signal_panel_lines(report.mistakes,
                                           report.calibration):
        print(text)
    print()
    print(SEP)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quantum Study Dashboard — cross-app mastery, "
                    "retention and forgetting")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--retention", action="store_true",
                       help="only the retention / forgetting view")
    group.add_argument("--no-retention", action="store_true",
                       help="only the classic mastery report")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    """Render the dashboard.  *argv* defaults to no flags (not sys.argv) so
    that ``dashboard.main()`` stays safe to call from other tools and tests;
    the __main__ block passes the real command line."""
    args = _parse_args(list(argv) if argv is not None else [])

    try:
        import rich  # noqa: F401
        rich_available = True
    except ImportError:
        rich_available = False

    if not args.retention:
        report = build_report()
        if rich_available:
            _render_rich(report)
        else:
            _render_plain(report)

    if not args.no_retention:
        retention = build_retention()
        if rich_available:
            _render_retention_rich(retention)
        else:
            _render_retention_plain(retention)


if __name__ == "__main__":
    main(sys.argv[1:])
