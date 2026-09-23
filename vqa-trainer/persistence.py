"""Persistence for vqa-trainer — a thin adapter over the shared ``common``
package.

Three groups of files, all in the suite data directory (which honours
``QUANTUM_STUDY_DATA_DIR``):

* ``vqa_history.json`` / ``vqa_flagged.json`` — this app's own files.  The
  history schema is load-bearing (``coach.py`` and ``dashboard.py`` parse it)
  and is **unchanged**; the flag file is now written in the suite's contract
  shape by :mod:`common.flags`, which reads the legacy bare-id list this app
  used to write and upgrades it in place on the first write (``coach.py``
  parses both, so the change is safe either way).
* ``mistakes.json`` / ``confidence.json`` — the suite-wide mistake journal and
  confidence-calibration log, shared by every app, owned by
  :mod:`common.journal`.
* ``vqa_settings.json`` — this app's preferences (the confidence opt-out).

What this module still is
=========================
Everything below is an **adapter**, not an implementation: it keeps this app's
call signatures (``log_mistake(item_id, category, question, your, correct)``,
``load_flagged() -> set[str]``, ``confidence_breakdown() -> {level: (correct,
total)}``) and forwards to ``common``, supplying ``app=APP_ID``.  The
duplicated journal, flag store, lock and atomic-write code that used to live
here is gone; ``common/README.md`` records which copy won each divergence.

Behaviour that changed with the migration, deliberately
-------------------------------------------------------
* the growth cap trims **only this app's** rows (the old code sorted the
  merged list and kept the newest N, which deleted other apps' rows during our
  write — a data-loss bug in eight of the ten copies);
* ``CAUSE_LABELS["didnt_know"]`` is ASCII ``"Didn't know"`` (this app was the
  only one with a typographic apostrophe);
* a confidence rating outside 1..4 records **nothing** instead of being
  clamped to 1 (a clamped rating is one the learner never gave);
* the free-text note keeps its line breaks and is capped at 500 rather than
  200 characters — the one-line fields are still collapsed and capped at 200;
* every file this app writes now carries a ``<name>.schema.json`` sidecar and
  a rotating ``.bak`` backup (see :mod:`common.schema`).  The data files
  themselves are byte-for-byte the same shape as before, which is why the
  marker is a sidecar and not a key in the payload.

Paths
-----
The module constants are an import-time snapshot (``test_config_env`` and
tooling read them); every function resolves its path again at call time
through :mod:`common.datadir`, so ``QUANTUM_STUDY_DATA_DIR`` alone is enough
to redirect the app.
"""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

import math
import time
from pathlib import Path

from common import datadir, flags, journal, schema
from common.jsonio import read_json_dict
from config import (
    APP_DIR_NAME, CONFIDENCE_FILE, DATA_DIR, FLAGGED_FILE, HISTORY_FILE,
    MISTAKES_FILE, SETTINGS_FILE,
)
from core.models import SessionStats

_HALF_LIFE_DAYS = 14.0
# Import-time snapshots of the resolved paths; kept because they are this
# app's published names.  `_FLAGGED_FILE` keeps its long-standing private one.
_FLAGGED_FILE = FLAGGED_FILE
DATA_DIR = DATA_DIR
APP_ID = APP_DIR_NAME

# --- shared journal contract (re-exported from common.journal) -------------
MISTAKE_CAUSES = journal.MISTAKE_CAUSES
CAUSE_LABELS = journal.CAUSE_LABELS
CONFIDENCE_LABELS = journal.CONFIDENCE_LABELS
#: Growth caps.  The live values live in ``common.journal``; these are the
#: names this app has always exported.
MAX_MISTAKES = journal.MISTAKES_MAX
MAX_CONFIDENCE = journal.CONFIDENCE_MAX


# ---------------------------------------------------------------------------
# Paths — resolved at call time, so the env override always wins
# ---------------------------------------------------------------------------

def history_path() -> Path:
    """``<data dir>/vqa_history.json``, resolved now."""
    return datadir.app_file(APP_ID, "history")


def flagged_path() -> Path:
    """``<data dir>/vqa_flagged.json``, resolved now."""
    return datadir.app_file(APP_ID, "flagged")


def settings_path() -> Path:
    """``<data dir>/vqa_settings.json``, resolved now."""
    return datadir.app_file(APP_ID, "settings")


def mistakes_path() -> Path:
    """``<data dir>/mistakes.json``, resolved now."""
    return journal.mistakes_path()


def confidence_path() -> Path:
    """``<data dir>/confidence.json``, resolved now."""
    return journal.confidence_path()


def last_write_error():
    """The last write refused because a file is newer than this build, or None.

    :mod:`common.schema` refuses to overwrite a file written by a newer
    version of the suite rather than silently dropping its fields.  The
    journal helpers swallow that so a drill cannot crash; this is how a screen
    can find out it happened.
    """
    return journal.last_write_error()


# ==========================================================================
# Session history  (vqa_history.json — schema unchanged, parsed by coach.py)
# ==========================================================================

def _load_raw() -> list[dict]:
    """Every saved session, oldest first.  Missing/corrupt files read as []."""
    return schema.load_versioned(history_path(), "history")


def save_session(stats: SessionStats) -> None:
    """Append one finished session.  Atomic, versioned, backed up once a run."""
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
    try:
        schema.save_versioned(history_path(), sessions, "history")
    except schema.SchemaTooNewError:
        pass          # a newer build owns this file; never overwrite it


# ==========================================================================
# Flag for review  (vqa_flagged.json — common.flags owns the file)
# ==========================================================================

def load_flagged() -> set[str]:
    """The flagged problem ids.  Reads the legacy bare-id list too."""
    return flags.flagged_ids(flagged_path(), APP_ID)


def save_flagged(ids: set[str]) -> None:
    """Replace the flag file with exactly *ids* (sorted, contract shape)."""
    flags.save_flagged(flagged_path(), sorted(ids), APP_ID)


def toggle_flag(problem_id: str) -> bool:
    """Flag or unflag one problem; returns the new state.

    Locked and atomic: two windows of this app cannot each decide "not flagged
    yet" and write conflicting files, and a crash mid-write no longer empties
    the file.
    """
    return flags.toggle_flag(flagged_path(), problem_id, app=APP_ID)


# ==========================================================================
# Recency-weighted scoring over the history
# ==========================================================================

def _session_weight(session: dict) -> float:
    ts = session.get("timestamp")
    if ts is None:
        return 0.1
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
    """Per-problem weight: higher = due for more review."""
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
            result[pid] = max(0.5, 2.0 - avg * 0.15)
    return result


# ==========================================================================
# Mistake journal  (shared suite file: mistakes.json)
# --------------------------------------------------------------------------
# A wrong answer should become analysis, not just a bookmark: the `cause`
# field is the payload ("nine little-endian slips this month"), not the count
# of flagged items. Every row carries `app` so one file serves the whole suite.
# ==========================================================================

normalise_cause = journal.normalise_cause


def make_mistake_entry(
    item_id: str,
    category: str,
    question: str,
    your_answer: str,
    correct_answer: str,
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    resolved: bool = False,
    app: str | None = None,
) -> dict:
    """Build one mistake-journal row.  Pure: no I/O, no Qt."""
    return journal.make_mistake_entry(
        item_id, app or APP_ID, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer, cause=cause,
        note=note, timestamp=timestamp, resolved=resolved)


def load_mistakes() -> list[dict]:
    """Every mistake row in the shared file (all apps).  Never raises."""
    return journal.load_mistakes()


def save_mistakes(entries: list[dict]) -> None:
    """Atomically replace the journal, keeping this app's newest rows.

    mistakes.json is shared with the other nine apps and several can be open
    at once, so the whole read-merge-write is serialised by an flock and rows
    owned by another app are written back exactly as they are on disk —
    unknown keys and all.  Only *our* oldest rows are ever trimmed.
    """
    journal.save_mistakes(entries, APP_ID)


def log_mistake(
    item_id: str,
    category: str,
    question: str,
    your_answer: str,
    correct_answer: str,
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    app: str | None = None,
) -> dict:
    """Append one mistake.  Returns the stored row.  Repeats are kept, not
    merged: three slips on the same item are three rows, which is the signal."""
    entry = make_mistake_entry(item_id, category, question, your_answer,
                               correct_answer, cause, note, timestamp, app=app)
    return journal.log_mistake(entry)


def set_mistake_cause(item_id: str, cause: str | None, note: str | None = None,
                      app: str | None = None) -> dict | None:
    """Categorise the most recent journal row for app+id.  Returns it, or None.

    ``note=None`` leaves the existing note alone; ``note=""`` clears it.
    """
    return journal.set_mistake_cause(item_id, cause, note, app=app or APP_ID)


def resolve_mistakes(item_id: str, app: str | None = None) -> int:
    """Mark every journal row for app+id resolved (the item was later answered
    correctly).  Returns how many rows changed."""
    return journal.resolve_mistakes(item_id, app or APP_ID)


def mistake_cause_counts(app: str | None = None,
                         unresolved_only: bool = False) -> dict[str, int]:
    """Cause histogram — the reason the journal exists.  ``app=None`` = this
    app; pass ``app=""`` for the whole suite.  Uncategorised rows count under
    ``""`` (this app's key; ``common.journal`` calls it ``"uncategorised"``)."""
    if app is None:
        app = APP_ID
    counts = journal.cause_counts(app or None,
                                  include_resolved=not unresolved_only)
    uncategorised = counts.pop(journal.UNCATEGORISED, 0)
    if uncategorised:
        counts[""] = uncategorised
    return counts


# ==========================================================================
# Confidence calibration  (shared suite file: confidence.json)
# --------------------------------------------------------------------------
# Rated BEFORE the answer is graded, so "confidently wrong" topics — the
# unknown unknowns — become visible instead of hiding inside the accuracy.
# ==========================================================================

def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, timestamp: float | None = None,
                          app: str | None = None) -> dict:
    """Build one calibration row.  Pure.  Confidence is clamped to 1..4."""
    return journal.make_confidence_entry(item_id, app or APP_ID,
                                         category=category,
                                         confidence=confidence,
                                         correct=correct, timestamp=timestamp)


def load_confidence() -> list[dict]:
    """Every calibration row in the shared file (all apps).  Never raises."""
    return journal.load_confidence()


def save_confidence(entries: list[dict]) -> None:
    """Atomically replace the log, keeping this app's newest rows.

    Same shared-file contract as :func:`save_mistakes`: locked, and other
    apps' rows are preserved verbatim.
    """
    journal.save_confidence(entries, APP_ID)


def log_confidence(item_id: str, category: str, confidence: int, correct: bool,
                   timestamp: float | None = None,
                   app: str | None = None) -> dict | None:
    """Record one (confidence, correct) pairing once the answer is graded.

    A rating outside 1..4 — including None, meaning "the strip was skipped" —
    records nothing and returns None.
    """
    return journal.log_confidence(item_id, app or APP_ID, category=category,
                                  confidence=confidence, correct=correct,
                                  timestamp=timestamp)


def confidence_breakdown(app: str | None = None) -> dict[int, tuple[int, int]]:
    """``{level: (correct, total)}`` for levels seen.  Level 4 with a low ratio
    is the confidently-wrong signal."""
    if app is None:
        app = APP_ID
    summary = journal.calibration_summary(app or None)
    return {level: (b["correct"], b["total"]) for level, b in summary.items()}


# ==========================================================================
# App settings  (vqa_settings.json) — small, additive, never load-bearing
# ==========================================================================

_DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """This app's preferences; missing/corrupt files fall back to the defaults."""
    settings = dict(_DEFAULT_SETTINGS)
    stored = schema.load_versioned(settings_path(), "settings",
                                   reader=read_json_dict)
    if isinstance(stored, dict):
        settings.update(stored)
    return settings


def save_settings(settings: dict) -> None:
    """Replace the settings file.  Atomic, versioned, backed up once a run."""
    try:
        schema.save_versioned(settings_path(), dict(settings), "settings")
    except schema.SchemaTooNewError:
        pass          # a newer build owns this file; never overwrite it


def confidence_prompt_enabled() -> bool:
    """False once the user has opted out of the confidence strip."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
