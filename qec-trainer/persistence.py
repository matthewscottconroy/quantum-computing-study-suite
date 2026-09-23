"""Persistence for qec-trainer — a thin adapter over the shared ``common`` package.

Five files, all under :func:`config.data_dir` (which honours
``QUANTUM_STUDY_DATA_DIR``):

===========================  ===========  ==================================
File                         schema kind  Owned by
===========================  ===========  ==================================
``qec_history.json``         history      this app (load-bearing: ``coach.py``
                                          and ``dashboard.py`` parse it)
``qec_flagged.json``         flagged      this app (``coach.py`` review queue)
``qec_settings.json``        settings     this app
``mistakes.json``            mistakes     **the whole suite** — ten writers
``confidence.json``          confidence   **the whole suite** — ten writers
===========================  ===========  ==================================

What this module is now
=======================
Everything that was duplicated in all ten apps — the data-directory resolver,
the mistake/confidence journal, the flag store, the atomic JSON writer and the
cross-process lock — lives in :mod:`common` and is *called* from here, never
re-implemented.  What is left is this app's own vocabulary: its session-history
schema, its exponential-decay mastery weighting, and the argument order its own
screens and tests already use.

Three behaviours changed, and all three are fixes the shared package makes for
every app at once (see ``common/README.md`` §3):

* **The growth cap no longer deletes other apps' rows.**  This app used to trim
  ``mistakes.json`` with ``sorted(all_rows, key=timestamp)[-MAX:]`` on the
  *merged* list, which threw away rows belonging to the other nine apps during
  a write to a file it does not own.  :func:`common.journal.trim_own` drops
  only this app's oldest rows.
* **A repeated mistake appends a new row instead of merging into the open
  one.**  ``dashboard.load_mistakes`` says it outright: "a genuine second miss
  of the same item keeps its own entry, because repetition is exactly the
  signal".  Merging destroyed the count ``coach --mistakes`` reports.
* **:func:`calibration_summary` buckets are ``{"total", "correct"}``**, not
  ``{"n", "correct"}`` — the name the other apps and the dashboard use.

Every file this app writes now carries a schema version in a sidecar
(``qec_history.json.schema.json``), migrates forward on read, refuses to be
overwritten by a build that does not understand it, and is copied to a
rotating ``.bak`` before the first write of each session.  The *data* files
themselves are byte-for-byte the same shape they always were: the sidecar
exists precisely so that ``coach.py`` and ``dashboard.py``, which require the
top level to be a plain JSON list, keep working untouched.
"""
from __future__ import annotations

import math
import time
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import flags, journal, schema
from common.jsonio import read_json_dict

import config
from config import APP_DIR_NAME
from core.models import Attempt, SessionStats  # noqa: F401  (Attempt: public re-export)

_HALF_LIFE_DAYS = 14.0   # score halves in weight every 14 days

APP_ID = APP_DIR_NAME

# ── Mistake journal / confidence contract (one definition, in common) ─────────

MISTAKE_CAUSES: tuple[str, ...] = journal.MISTAKE_CAUSES
CAUSE_LABELS: dict[str, str] = journal.CAUSE_LABELS
CONFIDENCE_LEVELS: tuple[int, ...] = journal.CONFIDENCE_LEVELS
CONFIDENCE_LABELS: dict[int, str] = journal.CONFIDENCE_LABELS

_TEXT_MAX = journal.TEXT_MAX
_NOTE_MAX = journal.NOTE_MAX


# ── Paths, resolved at call time ──────────────────────────────────────────────
#
# The module-level names (``HISTORY_FILE``, ``MISTAKES_FILE``, …) are kept as a
# backwards-compatible surface and are computed on each attribute access, so a
# test needs nothing but ``monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", tmp)``.

def history_path() -> Path:
    """``qec_history.json`` — this app's session history."""
    return config.history_file()


def flagged_path() -> Path:
    """``qec_flagged.json`` — this app's flag-for-review store."""
    return config.flagged_file()


def settings_path() -> Path:
    """``qec_settings.json`` — this app's settings blob."""
    return config.settings_file()


def mistakes_path() -> Path:
    """``mistakes.json`` — the suite-wide mistake journal."""
    return journal.mistakes_path()


def confidence_path() -> Path:
    """``confidence.json`` — the suite-wide calibration log."""
    return journal.confidence_path()


_PATHS = {
    "DATA_DIR":        config.data_dir,
    "HISTORY_FILE":    history_path,
    "FLAGGED_FILE":    flagged_path,
    "_FLAGGED_FILE":   flagged_path,
    "SETTINGS_FILE":   settings_path,
    "MISTAKES_FILE":   mistakes_path,
    "CONFIDENCE_FILE": confidence_path,
}
#: Growth caps live with the journal; read through so patching one place works.
_FROM_JOURNAL = ("MISTAKES_MAX", "CONFIDENCE_MAX")


def __getattr__(name: str):                     # PEP 562
    """``persistence.HISTORY_FILE`` &c., resolved at the moment they are read."""
    if name in _PATHS:
        return _PATHS[name]()
    if name in _FROM_JOURNAL:
        return getattr(journal, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_PATHS) | set(_FROM_JOURNAL))


# ── Refused writes ────────────────────────────────────────────────────────────

_LAST_WRITE_ERROR: schema.SchemaError | None = None


def last_write_error() -> schema.SchemaError | None:
    """The most recent write this build refused to make, or None.

    :mod:`common.schema` will not overwrite a file written by a *newer* build:
    that is how a newer build's fields get silently deleted.  Nothing raises
    into a drill; the refusal is recorded here instead.
    """
    return _LAST_WRITE_ERROR or journal.last_write_error()


def clear_write_error() -> None:
    """Forget the last refused write (this app's and the journal's)."""
    global _LAST_WRITE_ERROR
    _LAST_WRITE_ERROR = None
    journal.clear_write_error()


def _write(path: Path, payload, kind: str) -> bool:
    """``schema.save_versioned`` that reports a refusal instead of raising."""
    global _LAST_WRITE_ERROR
    try:
        schema.save_versioned(path, payload, kind)
    except schema.SchemaTooNewError as exc:
        _LAST_WRITE_ERROR = exc
        return False
    return True


# ── Session history (existing on-disk schema — deliberately unchanged) ────────

def _load_raw() -> list:
    """Every saved session, oldest first.  Never raises; corrupt reads as ``[]``."""
    return schema.load_versioned(history_path(), "history")


def save_session(stats: SessionStats) -> bool:
    """Append one finished session.  Returns False if the write was refused."""
    sessions = _load_raw()
    sessions.append({
        "total":     stats.total,
        "correct":   stats.correct,
        "accuracy":  stats.accuracy,
        "timestamp": time.time(),
        "attempts": [
            {
                "problem_id": a.problem.id,
                "category":   a.problem.category,
                "difficulty": a.problem.difficulty,
                "score":      a.score,
                "verdict":    a.verdict.value,
                "hints_used": a.hints_used,
                "elapsed_secs": a.elapsed_secs,
            }
            for a in stats.attempts
        ],
    })
    return _write(history_path(), sessions, "history")


def _session_weight(session: dict) -> float:
    """Exponential decay by actual elapsed days."""
    ts = session.get("timestamp")
    if ts is None:
        return 0.1   # very old sessions with no timestamp get low weight
    days = (time.time() - ts) / 86400.0
    return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)


def avg_scores_by_category() -> dict[str, float]:
    sessions = _load_raw()
    buckets: dict[str, list[tuple[float, int]]] = {}
    for s in sessions:
        w = _session_weight(s)
        for a in s.get("attempts", []):
            cat = a.get("category", "")
            if cat:
                buckets.setdefault(cat, []).append((w, a.get("score", 0)))
    return {
        cat: sum(w * sc for w, sc in pairs) / sum(w for w, _ in pairs)
        for cat, pairs in buckets.items()
        if sum(w for w, _ in pairs) > 0
    }


def problem_score_weights() -> dict[str, float]:
    """Return per-problem-id weight: higher = due for more review.

    Weight 1.0 means never seen or always missed; lower means more mastered.
    """
    sessions = _load_raw()
    scores: dict[str, float] = {}
    counts: dict[str, float] = {}
    for s in sessions:
        w = _session_weight(s)
        for a in s.get("attempts", []):
            pid = a.get("problem_id", "")
            if pid:
                raw_score = a.get("score", 0)
                hints = a.get("hints_used", 0)
                effective_score = max(0, raw_score - hints * 0.5)
                scores[pid] = scores.get(pid, 0.0) + w * effective_score
                counts[pid] = counts.get(pid, 0.0) + w
    result = {}
    for pid in scores:
        if counts[pid] > 0:
            avg = scores[pid] / counts[pid]
            # Invert: score 0 → weight 2.0; score 10 → weight 0.5
            result[pid] = max(0.5, 2.0 - avg * 0.15)
    return result


# ── Flag for review (qec_flagged.json) ────────────────────────────────────────
#
# The file used to be written with a plain ``write_text`` of a bare id list.
# ``common.flags`` reads that legacy shape and upgrades it in place on the first
# write to the contract shape every other app uses
# ({id, label, category, app, timestamp}); ``coach.py`` parses both, so the
# review queue keeps working either way — and now shows the question text
# instead of the bare problem id.

def load_flagged() -> set[str]:
    """The ids currently flagged for review.  Never raises."""
    return flags.flagged_ids(flagged_path(), APP_ID)


def save_flagged(ids) -> bool:
    """Replace the flag file with *ids* (a set, or contract-shaped rows)."""
    rows = sorted(ids) if isinstance(ids, (set, frozenset)) else list(ids)
    return flags.save_flagged(flagged_path(), rows, APP_ID)


def flagged_entries() -> list[dict]:
    """Flagged items with their label, category and timestamp, oldest first."""
    return flags.load_flagged(flagged_path(), APP_ID)


def toggle_flag(problem_id: str, label: str = "", category: str = "") -> bool:
    """Flag the problem, or unflag it if it is already flagged.

    Returns the **new** state.  *label* and *category* are stored so the review
    queue in ``coach.py`` can show the question rather than the bare id; they
    are ignored when the item is being unflagged.
    """
    return flags.toggle_flag(flagged_path(), problem_id, label, category,
                             app=APP_ID)


# ── Mistake journal (shared mistakes.json) ────────────────────────────────────

def make_mistake_entry(item_id: str, category: str, question: str,
                       your_answer: str, correct_answer: str,
                       cause: str | None = None, note: str = "",
                       timestamp: float | None = None,
                       resolved: bool = False,
                       app: str = APP_ID) -> dict:
    """Build one mistake record in the suite-wide schema (pure; writes nothing).

    ``cause`` is one of :data:`MISTAKE_CAUSES`, or None for "logged but not yet
    categorised".  Anything unrecognised is stored as None rather than
    rejected, so a stray value can never lose the mistake itself.
    """
    return journal.make_mistake_entry(
        item_id, app, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer, cause=cause,
        note=note, timestamp=timestamp, resolved=resolved)


def load_mistakes() -> list[dict]:
    """Every mistake record in the shared journal (all apps).  Never raises."""
    return journal.load_mistakes()


def save_mistakes(entries: list[dict], app: str = APP_ID) -> bool:
    """Rewrite the journal, keeping every other app's rows exactly as stored.

    Locked for the whole read-modify-write, written atomically, and capped by
    dropping only **this app's** oldest rows.
    """
    return journal.save_mistakes(entries, app)


def log_mistake(entry: dict) -> dict:
    """Append one prepared mistake row.  Returns the record as stored.

    A repeat is a new row, not an update: three slips on the same item are the
    signal ``coach --mistakes`` counts.
    """
    return journal.log_mistake(entry)


def set_mistake_cause(item_id: str, cause: str | None, note: str | None = None,
                      app: str = APP_ID) -> dict | None:
    """Attach a cause (and optional note) to the newest record for app+id.

    ``note=None`` leaves the existing note alone; ``note=""`` clears it.
    Returns the updated record, or None when there is nothing to update.
    """
    return journal.set_mistake_cause(item_id, cause, note, app=app)


def resolve_mistake(item_id: str, app: str = APP_ID) -> int:
    """Mark every open mistake for app+id resolved.  Returns how many changed."""
    return journal.resolve_mistakes(item_id, app)


def open_mistakes(app: str | None = APP_ID) -> list[dict]:
    """Unresolved mistakes, newest first; *app* None means every app."""
    return journal.open_mistakes(app)


def cause_counts(app: str | None = APP_ID) -> dict[str, int]:
    """How many mistakes each recognised cause accounts for."""
    return journal.cause_counts(app, include_uncategorised=False)


# ── Confidence calibration (shared confidence.json) ───────────────────────────

def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, timestamp: float | None = None,
                          app: str = APP_ID) -> dict:
    """Build one calibration record (pure; the rating is clamped to 1–4)."""
    return journal.make_confidence_entry(item_id, app, category=category,
                                         confidence=confidence,
                                         correct=correct, timestamp=timestamp)


def load_confidence() -> list[dict]:
    """Every confidence record (all apps).  Never raises."""
    return journal.load_confidence()


def save_confidence(entries: list[dict], app: str = APP_ID) -> bool:
    """Rewrite the calibration log (same shared-file contract as the journal)."""
    return journal.save_confidence(entries, app)


def log_confidence(item_id: str, category: str, confidence, correct: bool,
                   timestamp: float | None = None,
                   app: str = APP_ID) -> dict | None:
    """Record one confidence/outcome pairing.

    A rating outside 1–4 — including None, meaning "the user skipped the
    strip" — records nothing and returns None.
    """
    return journal.log_confidence(item_id, app, category=category,
                                  confidence=confidence, correct=correct,
                                  timestamp=timestamp)


def calibration_summary(app: str | None = APP_ID) -> dict[int, dict[str, int]]:
    """``{rating: {"total": n, "correct": c}}`` — the confidently-wrong report."""
    return journal.calibration_summary(app)


def confidently_wrong(app: str | None = APP_ID, *,
                      min_confidence: int = journal.CONFIDENT_LEVEL) -> list[dict]:
    """Rows the learner was sure about and got wrong — the unknown unknowns."""
    return journal.confidently_wrong(app, min_confidence=min_confidence)


# ── App-local settings (opt-outs) ─────────────────────────────────────────────

_DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """The settings blob merged over the defaults.  Unknown keys are kept."""
    data = schema.load_versioned(settings_path(), "settings",
                                 reader=read_json_dict)
    merged = dict(_DEFAULT_SETTINGS)
    if isinstance(data, dict):
        merged.update(data)
    return merged


def save_settings(settings: dict) -> bool:
    return _write(settings_path(), dict(settings), "settings")


def confidence_prompt_enabled() -> bool:
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
