"""Persist session history for lifetime stats and SRS topic weighting.

Everything that is *shared with the other nine apps* now lives in the
repository-level ``common`` package and is only adapted here:

============================  ==================================================
This module still owns        Delegated to ``common``
============================  ==================================================
``trainer_history.json``      the data directory (:mod:`common.datadir`)
(the SRS weighting and the    the mistake journal and the confidence log
time-decay formula)           (:mod:`common.journal`)
``flag_id_for`` — the id      ``trainer_flagged.json`` (:mod:`common.flags`)
scheme that joins flags,      schema versions, forward migration and the
mistakes and confidence       rotating backups (:mod:`common.schema`)
rows, and that ``coach.py``
reads
============================  ==================================================

Two deliberate app-local behaviours are kept as *adapters* over the shared
code rather than forks of it — see ``circuit-trainer/README.md``:

* the confidence rating is validated **strictly** (a plain ``int`` in 1..4;
  ``"3"``, ``2.7`` and ``True`` are caller bugs and record nothing), which is
  narrower than :func:`common.journal.coerce_confidence`;
* :func:`update_mistake` can amend the *note alone* and keep whatever cause the
  row already carries, which :func:`common.journal.set_mistake_cause` does not
  offer (it always writes a cause).

Every file this app writes now goes through :func:`common.schema.save_versioned`:
an unmarked file is read as v1, a file written by a newer build is refused
rather than silently downgraded, and the state the session started from is kept
in ``<name>.bak`` (three generations).  The JSON inside every file is byte-for-
byte the shape ``coach.py`` and ``dashboard.py`` already parse; the version
marker lives in a ``<name>.schema.json`` sidecar precisely so those readers
never see it.
"""

from __future__ import annotations
import hashlib
import datetime
import math
import pathlib

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir, flags, journal, locking, schema
from common.jsonio import read_json_dict

from core.models import SessionStats, Problem, Attempt, AnswerFormat

#: The app directory name — what ``coach.py`` and ``dashboard.py`` group by,
#: and the owner stamped on every row this app writes to a shared file.
APP = "circuit-trainer"
_APP_DIR_NAME = APP                    # historical alias

# Time-based SRS: 14-day half-life for exponential decay.
_HALF_LIFE_DAYS = 14.0

# Re-exported so callers (and tests) can keep using the names they always had.
MISTAKE_CAUSES = journal.MISTAKE_CAUSES
CONFIDENCE_LEVELS = journal.CONFIDENCE_LEVELS

_FIELD_LIMIT = journal.TEXT_MAX        # 200 — question / answers
_NOTE_LIMIT = journal.NOTE_MAX         # 500 — the user's own note

_UNSET = object()


# ── Where the files live (resolved at call time, never cached) ───────────────
#
# The ten apps used to freeze the directory into a module constant at import
# time, so a test had to monkeypatch a private name to redirect it.  These are
# functions now: setting QUANTUM_STUDY_DATA_DIR is enough, at any point.

def data_dir() -> pathlib.Path:
    """The suite data directory (honours ``QUANTUM_STUDY_DATA_DIR``)."""
    return datadir.data_dir()


def history_file() -> pathlib.Path:
    """Path of ``trainer_history.json``."""
    return datadir.app_file(APP, "history")


def flagged_file() -> pathlib.Path:
    """Path of ``trainer_flagged.json`` (the shared flagging contract)."""
    return datadir.app_file(APP, "flagged")


def mistakes_file() -> pathlib.Path:
    """Path of the suite-wide ``mistakes.json``."""
    return journal.mistakes_path()


def confidence_file() -> pathlib.Path:
    """Path of the suite-wide ``confidence.json``."""
    return journal.confidence_path()


def prefs_file() -> pathlib.Path:
    """Path of ``trainer_prefs.json`` (this app's own UI state)."""
    return datadir.app_file(APP, "settings")


# ── Session history ──────────────────────────────────────────────────────────

def save_session(stats: SessionStats, sprint: bool = False) -> None:
    """Append one session to ``trainer_history.json``.

    The JSON shape is unchanged — ``coach.py`` and ``dashboard.py`` parse it —
    but the write is now atomic, version-stamped and preceded by a backup of
    the state this process started from.
    """
    datadir.ensure_data_dir()
    path = history_file()
    # Read-modify-write on a file two windows of this app can share, so it is
    # taken under the same advisory lock the shared journals use: without it,
    # two sessions finishing at once lose one of them.
    with locking.lock(path, create=True):
        _append_session(path, stats, sprint)


def _append_session(path: pathlib.Path, stats: SessionStats, sprint: bool) -> None:
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
    _save_versioned(path, history, "history")


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
# The store itself is common.flags: atomic, locked, rows it does not
# understand are written back untouched, and the legacy bare-id list form that
# three other apps still use is read (and upgraded) rather than discarded.

def flag_id_for(problem: Problem) -> str:
    """Stable identifier for a problem: its problem_id when set (the
    deterministic generators -- gate_sequence, notation, gate_identity and
    the Kraus-identification noise problem -- set one), else a hash of the
    category + question text (randomly generated problems have no id).

    This stays app-local on purpose.  The id is the join key between
    ``trainer_flagged.json``, ``mistakes.json``, ``confidence.json`` and
    ``coach.py``'s review queue, so it is on-disk state: swapping it for
    ``common.flags.make_id`` (sha256) would orphan every flag and every
    journalled mistake already on disk.
    """
    pid = getattr(problem, "problem_id", None)
    if pid:
        return str(pid)
    raw = f"{problem.category.value}\n{problem.question_text}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def flag_label_for(problem: Problem) -> str:
    """Short human title: category plus the start of the question text."""
    snippet = " ".join(problem.question_text.split())
    if not snippet:
        return problem.category.value
    return flags.make_label(f"{problem.category.value}: {snippet}")


def load_flagged() -> list[dict]:
    """All flagged entries (oldest first). Never raises."""
    return flags.load_flagged(flagged_file(), APP)


def is_flagged(flag_id: str) -> bool:
    return flags.is_flagged(flagged_file(), flag_id, APP)


def toggle_flag(problem: Problem) -> bool:
    """Flag the problem, or unflag it if already flagged. Returns new state."""
    return flags.toggle_flag(flagged_file(), flag_id_for(problem),
                             flag_label_for(problem), problem.category.value,
                             app=APP)


def unflag(flag_id: str) -> bool:
    """Remove a flagged entry by id. Returns True if something was removed."""
    return flags.unflag(flagged_file(), flag_id, app=APP)


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
# common.journal owns the read-modify-write: an flock held from the read to the
# replace (so a second app cannot drop rows we just appended), every foreign
# row written back exactly as it was read, and a growth cap that only ever
# trims THIS app's own rows.  The previous copy here capped the *merged* list,
# which deleted other apps' rows during our own write.

def clip_field(text: object, limit: int = _FIELD_LIMIT) -> str:
    """Collapse whitespace and truncate to `limit` characters (ellipsis included)."""
    return journal.clip_text(text, limit)


def normalise_cause(cause: object) -> str | None:
    """Return a valid cause string, or None for anything unrecognised."""
    return journal.normalise_cause(cause)


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
    return journal.make_mistake_entry(
        flag_id_for(problem), APP,
        category=problem.category.value,
        question=problem.question_text,
        your_answer=your_answer,
        correct_answer=correct_answer,
        cause=cause, note=note, timestamp=timestamp, resolved=resolved,
    )


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
    """Every mistake entry, oldest first. Never raises.

    Unfiltered by app on purpose: the history screen's journal summary counts
    the whole file, exactly as it always has.
    """
    return [e for e in journal.load_mistakes() if e.get("id")]


def append_mistake(entry: dict) -> dict:
    """Append a prepared entry to mistakes.json (this app's oldest trimmed)."""
    return journal.log_mistake(entry)


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

    ``common.journal.set_mistake_cause`` always writes a cause, so a note-only
    update reads the row's current cause back and re-writes it.  Both steps run
    inside one lock on ``mistakes.json`` (``common.locking.lock`` is
    re-entrant), so the pair is still a single atomic read-modify-write.
    """
    if cause is _UNSET and note is _UNSET:
        return _latest_own_mistake(item_id)
    with journal.lock(journal.mistakes_path(), create=True):
        if cause is _UNSET:
            row = _latest_own_mistake(item_id)
            if row is None:
                return None
            cause = row.get("cause")
        return journal.set_mistake_cause(
            item_id, cause, None if note is _UNSET else note, app=APP)


def _latest_own_mistake(item_id: str) -> dict | None:
    """The row ``set_mistake_cause`` would edit: newest open, else newest."""
    mine = [r for r in journal.load_mistakes(APP)
            if str(r.get("id")) == str(item_id)]
    if not mine:
        return None
    open_rows = [r for r in mine if not r.get("resolved")]
    return (open_rows or mine)[-1]


def resolve_mistake(item_id: str) -> int:
    """Mark every open mistake for `item_id` resolved. Returns how many changed."""
    return journal.resolve_mistakes(item_id, APP)


def mistake_cause_counts(include_resolved: bool = True) -> dict[str, int]:
    """How many mistakes fall under each cause (uncategorised ones under "")."""
    counts = journal.cause_counts(include_resolved=include_resolved,
                                  entries=load_mistakes())
    uncategorised = counts.pop(journal.UNCATEGORISED, None)
    if uncategorised:
        counts[""] = uncategorised
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
    a bool is a caller bug and is rejected rather than silently rounded.  This
    is stricter than ``common.journal`` (whose builder clamps and whose
    ``coerce_confidence`` accepts ``"3"`` and ``2.7``); the strictness is kept
    because a rating that was never given must never reach the calibration
    report.
    """
    _require_rating(confidence)
    return journal.make_confidence_entry(item_id, APP, category, confidence,
                                         correct, timestamp)


def _require_rating(confidence: object) -> None:
    if (isinstance(confidence, bool)
            or not isinstance(confidence, int)
            or confidence not in CONFIDENCE_LEVELS):
        raise ValueError(
            f"confidence must be one of {CONFIDENCE_LEVELS}, got {confidence!r}")


def load_confidence() -> list[dict]:
    """Every confidence row, oldest first. Never raises."""
    return [e for e in journal.load_confidence() if e.get("id")]


def log_confidence(
    item_id: str, category: str, confidence: int | None, correct: bool
) -> dict | None:
    """Record one confidence/outcome pairing. Returns the row, or None if the
    rating was missing or out of range (the strip is optional and skippable)."""
    try:
        _require_rating(confidence)
    except ValueError:
        return None
    return journal.log_confidence(item_id, APP, category, confidence, correct)


def calibration_by_level() -> dict[int, tuple[int, int]]:
    """{confidence level: (correct, total)} across all recorded pairings.

    Level 4 with a low ratio is the "confidently wrong" signal.
    """
    summary = journal.calibration_summary(entries=load_confidence())
    return {level: (bucket["correct"], bucket["total"])
            for level, bucket in summary.items()}


# ── App preferences (opt-outs) ────────────────────────────────────────────────

def load_prefs() -> dict:
    """circuit-trainer UI preferences. Never raises."""
    data = schema.load_versioned(prefs_file(), "settings", reader=read_json_dict)
    return data if isinstance(data, dict) else {}


def save_prefs(prefs: dict) -> None:
    _save_versioned(prefs_file(), prefs, "settings")


def confidence_prompt_enabled() -> bool:
    """True unless the user has opted out of the confidence strip."""
    return bool(load_prefs().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    prefs = load_prefs()
    prefs["confidence_prompt"] = bool(enabled)
    save_prefs(prefs)


# ── Schema-versioned writes ───────────────────────────────────────────────────

def _save_versioned(path: pathlib.Path, payload, kind: str) -> bool:
    """``schema.save_versioned`` that reports a refusal instead of raising.

    A file written by a newer build of the suite is left exactly as it is --
    overwriting it with this build's narrower view of it is how the newer
    build's fields get silently deleted.  The refusal is recorded in
    :func:`last_write_error`; an OSError still propagates, because the callers
    in ``ui/main_window.py`` already treat "the disk said no" as a non-fatal
    event and the session must not pretend the write happened.
    """
    global _LAST_WRITE_ERROR
    try:
        schema.save_versioned(path, payload, kind)
    except schema.SchemaTooNewError as exc:
        _LAST_WRITE_ERROR = exc
        return False
    return True


_LAST_WRITE_ERROR: schema.SchemaError | None = None


def last_write_error() -> schema.SchemaError | None:
    """The most recent write this app refused, or one ``common.journal``
    refused, whichever is newer.  None when nothing has been refused."""
    return _LAST_WRITE_ERROR or journal.last_write_error()


def clear_write_error() -> None:
    """Forget the last refused write (both here and in ``common.journal``)."""
    global _LAST_WRITE_ERROR
    _LAST_WRITE_ERROR = None
    journal.clear_write_error()


def restore_backup(path: pathlib.Path, generation: int = 0) -> bool:
    """Put a ``<name>.bak`` generation back over *path*.  0 is the newest.

    Exposed so a wedged data directory can be recovered without leaving the
    repository: ``python -c "import persistence as p;
    p.restore_backup(p.mistakes_file())"``.
    """
    return schema.restore_backup(path, generation)


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
    """``trainer_history.json`` as stored, migrated forward in memory."""
    rows = schema.load_versioned(history_file(), "history")
    return rows if isinstance(rows, list) else []
