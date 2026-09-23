"""Persist session history for lifetime stats and SRS topic weighting."""

from __future__ import annotations
import hashlib
import json
import math
import os
import time
import datetime
import pathlib

import journal_sync
from core.models import SessionStats, Problem, Attempt, AnswerFormat

# QUANTUM_STUDY_DATA_DIR overrides the shared suite data dir (the same override
# coach.py, quantum-quiz and math-quiz honour); the default is unchanged.
_DATA_DIR     = pathlib.Path(
    os.environ.get("QUANTUM_STUDY_DATA_DIR")
    or (pathlib.Path.home() / ".local" / "share" / "quantum-study")
).expanduser()
_HISTORY_FILE = _DATA_DIR / "trainer_history.json"
# "Flag for review" entries (shared flagging contract; read by coach.py).
_FLAGGED_FILE = _DATA_DIR / "trainer_flagged.json"
_APP_DIR_NAME = "circuit-trainer"

# Time-based SRS: 14-day half-life for exponential decay.
_HALF_LIFE_DAYS = 14.0


def save_session(stats: SessionStats, sprint: bool = False) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = _load_raw()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    session = {
        "date": str(datetime.date.today()),
        "timestamp": now_iso,
        "total": stats.total,
        "correct": stats.correct,
        "accuracy": round(stats.accuracy, 4),
        "attempts": [
            {
                "problem_id": getattr(a.problem, "problem_id", None),
                "category": a.problem.category.value,
                "difficulty": a.problem.difficulty,
                "score": a.score,
                "elapsed_secs": getattr(a, "elapsed_secs", None),
            }
            for a in stats.attempts
        ],
    }
    if sprint:
        # Extra tag for sprint sessions; readers (dashboard.py, history
        # screen) access keys via .get() so unknown keys are tolerated.
        session["sprint"] = True
    history.append(session)
    _HISTORY_FILE.write_text(json.dumps(history, indent=2))


def avg_scores_by_category() -> dict[str, float]:
    """Time-decayed average score per category across all saved sessions."""
    return _weighted_averages(key_fn=lambda a: a.get("category", ""))


def problem_score_weights() -> dict[str, float]:
    """Return per-problem SRS weights: higher weight means more practice needed.

    Uses a 14-day half-life time decay on each recorded attempt, then maps
    the weighted average score to a selection weight via::

        weight = exp(-days * log(2) / 14.0)
        avg_score = weighted_sum / weighted_count
        result[pid] = max(0.5, 2.0 - avg_score * 0.15)

    Problems never seen default to 1.25.
    """
    today = datetime.date.today()
    buckets: dict[str, list[tuple[float, float]]] = {}  # pid -> [(weight, score)]

    for session in _load_raw():
        # Determine the date for this session's attempts.
        session_date = _parse_session_date(session)
        days = max(0.0, (today - session_date).total_seconds() / 86400.0)
        time_weight = math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)

        for a in session.get("attempts", []):
            pid = a.get("problem_id")
            if not pid:
                continue
            score = float(a.get("score", 0))
            buckets.setdefault(pid, []).append((time_weight, score))

    result: dict[str, float] = {}
    for pid, pairs in buckets.items():
        weighted_sum   = sum(w * s for w, s in pairs)
        weighted_count = sum(w for w, _ in pairs)
        avg_score = weighted_sum / weighted_count if weighted_count else 0.0
        result[pid] = max(0.5, 2.0 - avg_score * 0.15)

    return result


# ── Flag for review ───────────────────────────────────────────────────────────
#
# trainer_flagged.json is a JSON list of entries:
#   {"id": str, "label": str, "category": str, "app": "circuit-trainer",
#    "timestamp": epoch float}
# Flagging is a toggle — flagging an already-flagged problem removes it.

def flagged_file() -> pathlib.Path:
    """Path of trainer_flagged.json (honours QUANTUM_STUDY_DATA_DIR)."""
    return _FLAGGED_FILE


def flag_id_for(problem: Problem) -> str:
    """Stable identifier for a problem: its problem_id when set (the
    deterministic generators -- gate_sequence, notation, gate_identity and
    the Kraus-identification noise problem -- set one), else a hash of the
    category + question text (randomly generated problems have no id)."""
    pid = getattr(problem, "problem_id", None)
    if pid:
        return str(pid)
    raw = f"{problem.category.value}\n{problem.question_text}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def flag_label_for(problem: Problem) -> str:
    """Short human title: category plus the start of the question text."""
    snippet = " ".join(problem.question_text.split())
    if len(snippet) > 70:
        snippet = snippet[:67].rstrip() + "…"
    return f"{problem.category.value}: {snippet}" if snippet else problem.category.value


def load_flagged() -> list[dict]:
    """All flagged entries (oldest first). Never raises."""
    path = _FLAGGED_FILE
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and e.get("id")]


def is_flagged(flag_id: str) -> bool:
    return any(e.get("id") == flag_id for e in load_flagged())


def toggle_flag(problem: Problem) -> bool:
    """Flag the problem, or unflag it if already flagged. Returns new state."""
    flag_id = flag_id_for(problem)
    entries = load_flagged()
    if any(e.get("id") == flag_id for e in entries):
        _save_flagged([e for e in entries if e.get("id") != flag_id])
        return False
    entries.append({
        "id":        flag_id,
        "label":     flag_label_for(problem),
        "category":  problem.category.value,
        "app":       _APP_DIR_NAME,
        "timestamp": time.time(),
    })
    _save_flagged(entries)
    return True


def unflag(flag_id: str) -> bool:
    """Remove a flagged entry by id. Returns True if something was removed."""
    entries = load_flagged()
    kept = [e for e in entries if e.get("id") != flag_id]
    if len(kept) == len(entries):
        return False
    _save_flagged(kept)
    return True


def _save_flagged(entries: list[dict]) -> None:
    _FLAGGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    _FLAGGED_FILE.write_text(json.dumps(entries, indent=2))


# ── Mistake journal & confidence calibration ─────────────────────────────────
#
# Two suite-wide files (the same shape in every study app), both keyed by
# flag_id_for(problem) so a flag, a mistake and a confidence rating for the
# same problem all carry the identical id:
#
#   mistakes.json    [{"id", "app", "category", "question", "your_answer",
#                      "correct_answer", "cause", "note", "timestamp",
#                      "resolved"}]
#   confidence.json  [{"id", "app", "category", "confidence", "correct",
#                      "timestamp"}]
#
# A wrong answer is logged immediately with cause=None ("logged but not yet
# categorised"); picking a cause in the UI updates that same entry.  Answering
# the same item correctly later flips resolved to True.
#
# Both files are SHARED with the other nine apps, and several apps can be open
# at once, so every read-modify-write below runs inside journal_sync.lock() --
# an flock on "<file>.lock" held from the read to the replace.  Unlocked, the
# read goes stale and the second writer drops the rows the first just added.
# A rewrite also puts every row belonging to another app back exactly as it was
# read (unknown keys included); only this app's rows are ours to reshape.
#
# Both files: honour QUANTUM_STUDY_DATA_DIR, tolerate a missing or corrupt file
# (treated as empty, rewritten valid on the next write), are written with an
# atomic temp-file + os.replace, and are capped at the newest _MAX_* entries so
# they cannot grow without bound.

_MISTAKES_FILE   = _DATA_DIR / "mistakes.json"
_CONFIDENCE_FILE = _DATA_DIR / "confidence.json"
# App-owned UI state (the confidence-prompt opt-out). Nothing outside
# circuit-trainer reads this file; the shared schemas above are untouched.
_PREFS_FILE      = _DATA_DIR / "trainer_prefs.json"

# Allowed "cause" values; None means "logged but not yet categorised".
MISTAKE_CAUSES = (
    "misread",
    "didnt_know",
    "knew_but_slipped",
    "confused",
    "out_of_time",
    "other",
)
CONFIDENCE_LEVELS = (1, 2, 3, 4)   # 1=guessing, 2=unsure, 3=fairly sure, 4=certain

_FIELD_LIMIT     = 200    # per the shared contract: question/answers <= 200 chars
_NOTE_LIMIT      = 500
_MAX_MISTAKES    = 2000   # newest kept; older entries dropped on write
_MAX_CONFIDENCE  = 5000

_UNSET = object()


def mistakes_file() -> pathlib.Path:
    """Path of mistakes.json (honours QUANTUM_STUDY_DATA_DIR)."""
    return _MISTAKES_FILE


def confidence_file() -> pathlib.Path:
    """Path of confidence.json (honours QUANTUM_STUDY_DATA_DIR)."""
    return _CONFIDENCE_FILE


def prefs_file() -> pathlib.Path:
    """Path of trainer_prefs.json (this app's own UI state)."""
    return _PREFS_FILE


def clip_field(text: object, limit: int = _FIELD_LIMIT) -> str:
    """Collapse whitespace and truncate to `limit` characters (ellipsis included)."""
    s = " ".join(str(text or "").split())
    if len(s) > limit:
        s = s[: max(0, limit - 1)].rstrip() + "…"
    return s


def normalise_cause(cause: object) -> str | None:
    """Return a valid cause string, or None for anything unrecognised."""
    return cause if cause in MISTAKE_CAUSES else None


# ── Mistake journal ───────────────────────────────────────────────────────────

def make_mistake_entry(
    problem: Problem,
    your_answer: object = "",
    correct_answer: object = "",
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    resolved: bool = False,
) -> dict:
    """Build a mistake-journal entry (pure; no I/O, no Qt)."""
    return {
        "id":             flag_id_for(problem),
        "app":            _APP_DIR_NAME,
        "category":       problem.category.value,
        "question":       clip_field(problem.question_text),
        "your_answer":    clip_field(your_answer),
        "correct_answer": clip_field(correct_answer),
        "cause":          normalise_cause(cause),
        "note":           clip_field(note, _NOTE_LIMIT),
        "timestamp":      float(time.time() if timestamp is None else timestamp),
        "resolved":       bool(resolved),
    }


def answer_texts_for(attempt: Attempt) -> tuple[str, str]:
    """(your_answer, correct_answer) as human text for a graded attempt (pure).

    Multiple choice resolves the indices to their choice labels; free-form uses
    the typed answer and Claude's model answer (falling back to the worked
    solution) as the reference.
    """
    problem = attempt.problem
    choices = problem.choices or []
    if problem.answer_format is not AnswerFormat.FREE_FORM and choices:
        raw = (attempt.user_answer or "").strip()
        if raw.isdigit() and 0 <= int(raw) < len(choices):
            yours = choices[int(raw)]
        else:
            yours = "(no answer)"
        try:
            correct = choices[int(problem.correct_answer)]
        except (TypeError, ValueError, IndexError):
            correct = str(problem.correct_answer)
        return yours, correct
    yours = (attempt.user_answer or "").strip() or "(no answer)"
    correct = attempt.model_answer or " ".join(problem.solution_steps or [])
    return yours, correct


def load_mistakes() -> list[dict]:
    """Every mistake entry, oldest first. Never raises."""
    return [e for e in _load_json_list(_MISTAKES_FILE) if e.get("id")]


def _write_mistakes(entries: list[dict]) -> None:
    """Write the journal back.  Call only while holding the journal lock.

    Rows written by another app are taken from disk as they are right now, so a
    concurrent app's new or amended rows survive our rewrite untouched.
    """
    _write_json_list(_MISTAKES_FILE,
                     journal_sync.merge_foreign(_load_json_list(_MISTAKES_FILE),
                                                entries, _APP_DIR_NAME))


def _write_confidence(rows: list[dict]) -> None:
    """Write the calibration log back (same contract as _write_mistakes)."""
    _write_json_list(_CONFIDENCE_FILE,
                     journal_sync.merge_foreign(_load_json_list(_CONFIDENCE_FILE),
                                                rows, _APP_DIR_NAME))


def append_mistake(entry: dict) -> dict:
    """Append a prepared entry to mistakes.json (newest _MAX_MISTAKES kept)."""
    with journal_sync.lock(_MISTAKES_FILE, create=True):
        entries = load_mistakes()      # read inside the lock: never stale
        entries.append(entry)
        _write_mistakes(entries[-_MAX_MISTAKES:])
    return entry


def log_mistake_for_attempt(
    attempt: Attempt, cause: str | None = None, note: str = ""
) -> dict:
    """Record a wrong answer. Returns the stored entry."""
    yours, correct = answer_texts_for(attempt)
    return append_mistake(
        make_mistake_entry(attempt.problem, yours, correct, cause=cause, note=note)
    )


def update_mistake(item_id: str, cause=_UNSET, note=_UNSET) -> dict | None:
    """Update the most recent entry for `item_id` (this app). Returns it, or None.

    Used by the "What went wrong?" row: the mistake is already logged with
    cause=None, and choosing a cause (or typing a note) amends that entry
    instead of adding a second one.
    """
    with journal_sync.lock(_MISTAKES_FILE):
        entries = load_mistakes()      # read inside the lock: never stale
        for entry in reversed(entries):
            if entry.get("id") == item_id and entry.get("app") == _APP_DIR_NAME:
                if cause is not _UNSET:
                    entry["cause"] = normalise_cause(cause)
                if note is not _UNSET:
                    entry["note"] = clip_field(note, _NOTE_LIMIT)
                _write_mistakes(entries)
                return entry
        return None


def resolve_mistake(item_id: str) -> int:
    """Mark every open mistake for `item_id` resolved. Returns how many changed."""
    with journal_sync.lock(_MISTAKES_FILE):
        entries = load_mistakes()      # read inside the lock: never stale
        changed = 0
        for entry in entries:
            if (entry.get("id") == item_id
                    and entry.get("app") == _APP_DIR_NAME
                    and not entry.get("resolved")):
                entry["resolved"] = True
                changed += 1
        if changed:
            _write_mistakes(entries)
        return changed


def mistake_cause_counts(include_resolved: bool = True) -> dict[str, int]:
    """How many mistakes fall under each cause (uncategorised ones under "")."""
    counts: dict[str, int] = {}
    for entry in load_mistakes():
        if not include_resolved and entry.get("resolved"):
            continue
        key = normalise_cause(entry.get("cause")) or ""
        counts[key] = counts.get(key, 0) + 1
    return counts


# ── Confidence calibration ────────────────────────────────────────────────────

def make_confidence_entry(
    item_id: str,
    category: str,
    confidence: int,
    correct: bool,
    timestamp: float | None = None,
) -> dict:
    """Build a confidence row (pure). Raises ValueError on a bad rating.

    The rating must be a plain int in CONFIDENCE_LEVELS -- a float, a string or
    a bool is a caller bug and is rejected rather than silently rounded.
    """
    if (isinstance(confidence, bool)
            or not isinstance(confidence, int)
            or confidence not in CONFIDENCE_LEVELS):
        raise ValueError(f"confidence must be one of {CONFIDENCE_LEVELS}, got {confidence!r}")
    level = int(confidence)
    return {
        "id":         str(item_id),
        "app":        _APP_DIR_NAME,
        "category":   str(category),
        "confidence": level,
        "correct":    bool(correct),
        "timestamp":  float(time.time() if timestamp is None else timestamp),
    }


def load_confidence() -> list[dict]:
    """Every confidence row, oldest first. Never raises."""
    return [e for e in _load_json_list(_CONFIDENCE_FILE) if e.get("id")]


def log_confidence(
    item_id: str, category: str, confidence: int | None, correct: bool
) -> dict | None:
    """Record one confidence/outcome pairing. Returns the row, or None if the
    rating was missing or out of range (the strip is optional and skippable)."""
    if confidence is None:
        return None
    try:
        entry = make_confidence_entry(item_id, category, confidence, correct)
    except (TypeError, ValueError):
        return None
    with journal_sync.lock(_CONFIDENCE_FILE, create=True):
        rows = load_confidence()       # read inside the lock: never stale
        rows.append(entry)
        _write_confidence(rows[-_MAX_CONFIDENCE:])
    return entry


def calibration_by_level() -> dict[int, tuple[int, int]]:
    """{confidence level: (correct, total)} across all recorded pairings.

    Level 4 with a low ratio is the "confidently wrong" signal.
    """
    out: dict[int, tuple[int, int]] = {}
    for row in load_confidence():
        level = row.get("confidence")
        if level not in CONFIDENCE_LEVELS:
            continue
        ok, total = out.get(level, (0, 0))
        out[level] = (ok + (1 if row.get("correct") else 0), total + 1)
    return out


# ── App preferences (opt-outs) ────────────────────────────────────────────────

def load_prefs() -> dict:
    """circuit-trainer UI preferences. Never raises."""
    if not _PREFS_FILE.exists():
        return {}
    try:
        data = json.loads(_PREFS_FILE.read_text())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_prefs(prefs: dict) -> None:
    _write_json(_PREFS_FILE, prefs)


def confidence_prompt_enabled() -> bool:
    """True unless the user has opted out of the confidence strip."""
    return bool(load_prefs().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    prefs = load_prefs()
    prefs["confidence_prompt"] = bool(enabled)
    save_prefs(prefs)


# ── Shared JSON-file internals ────────────────────────────────────────────────

def _load_json_list(path: pathlib.Path) -> list[dict]:
    """Read a JSON list of dicts; a missing or corrupt file reads as empty."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict)]


def _write_json(path: pathlib.Path, data) -> None:
    """Atomic write: serialise to a temp file in the same dir, then replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2))
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _write_json_list(path: pathlib.Path, entries: list[dict]) -> None:
    _write_json(path, entries)


# ── Internals ─────────────────────────────────────────────────────────────────

def _parse_session_date(session: dict) -> datetime.date:
    """Return a date for the session, preferring the ISO timestamp if present."""
    ts = session.get("timestamp")
    if ts:
        try:
            return datetime.datetime.fromisoformat(ts).date()
        except Exception:
            pass
    date_str = session.get("date", "")
    if date_str:
        try:
            return datetime.date.fromisoformat(date_str)
        except Exception:
            pass
    return datetime.date.today()


def _weighted_averages(key_fn) -> dict[str, float]:
    today = datetime.date.today()
    all_attempts_with_dates: list[tuple[dict, datetime.date]] = []
    for session in _load_raw():
        session_date = _parse_session_date(session)
        for a in session.get("attempts", []):
            all_attempts_with_dates.append((a, session_date))

    if not all_attempts_with_dates:
        return {}

    buckets: dict[str, list[tuple[float, float]]] = {}
    for a, session_date in all_attempts_with_dates:
        key = key_fn(a)
        if not key:
            continue
        score = float(a.get("score", 0))
        days = max(0.0, (today - session_date).total_seconds() / 86400.0)
        weight = math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)
        buckets.setdefault(key, []).append((weight, score))

    return {
        k: sum(w * s for w, s in pairs) / sum(w for w, _ in pairs)
        for k, pairs in buckets.items()
    }


def _load_raw() -> list[dict]:
    if not _HISTORY_FILE.exists():
        return []
    try:
        return json.loads(_HISTORY_FILE.read_text())
    except Exception:
        return []
