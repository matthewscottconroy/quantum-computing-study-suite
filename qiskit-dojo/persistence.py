"""Persistence for qiskit-dojo — a thin layer over the shared ``common`` package.

Everything cross-cutting now lives in ``common/`` and is imported, not copied:

=========================  ====================================================
``common.datadir``         where the data directory is (env-overridable, and
                           resolved on **every call**, never frozen at import)
``common.journal``         mistakes.json / confidence.json — the suite-wide
                           journal all ten apps append to
``common.flags``           dojo_flagged.json — the flag-for-review store
``common.schema``          version sidecars, forward migration, rotating
                           backups, and the refusal to overwrite a file written
                           by a newer build
=========================  ====================================================

What is left here is what is genuinely this app's own: the session-history
schema, the kata-selection weighting, the Qiskit-specific cause labels, and
two policies the dojo needs that the shared journal deliberately does not
have (see "Local policy" below).

Session history schema (integrated against by the coach app — do not change):
    list of {
        "timestamp": <epoch float>,
        "total": int,
        "passed": int,
        "attempts": [
            {"kata_id": str, "section": str, "passed": bool, "tries": int}
        ],
    }

Flagged-for-review schema (dojo_flagged.json, shared flagging contract —
read by coach.py's review queue):
    list of {
        "id": str,            # kata id
        "label": str,         # kata title
        "category": str,      # kata section
        "app": "qiskit-dojo",
        "timestamp": <epoch float>,
    }
Flagging is a toggle: flagging an already-flagged kata removes it.

Mistake journal (mistakes.json, suite-wide — every app appends to the same
file and only ever edits its own rows, matched on app + id):
    list of {
        "id": str,               # kata id
        "app": "qiskit-dojo",
        "category": str,         # kata section
        "question": str,         # <= 200 chars
        "your_answer": str,      # <= 200 chars
        "correct_answer": str,   # <= 200 chars
        "cause": str | None,     # one of MISTAKE_CAUSES, None = not categorised
        "note": str,             # <= 200 chars, "" when absent
        "timestamp": <epoch float>,
        "resolved": bool,
    }

Confidence calibration (confidence.json, suite-wide, append-only):
    list of {
        "id": str, "app": "qiskit-dojo", "category": str,
        "confidence": int (1 guessing .. 4 certain),
        "correct": bool, "timestamp": <epoch float>,
    }

App-local UI preferences live in dojo_settings.json (a flat dict); the only
key today is "confidence_prompt" (bool, default True).

Local policy (kept as adapters over ``common``, never as forked logic)
======================================================================
1. **A repeat failure folds into the kata's open row.**  ``common.journal``
   appends every miss, because in a quiz three misses of one card is three
   real signals.  A dojo is not a quiz: you press Run while you iterate, and
   the screen re-journals on every failed run, so appending would turn one
   stuck kata into thirty rows and drown ``coach --mistakes``.  :func:`log_mistake`
   therefore refreshes the open row — using ``journal.lock`` /
   ``journal.load_mistakes`` / ``journal.save_mistakes``, so the locking,
   foreign-row preservation, trimming and versioning are all the shared ones.
2. **A confidence rating is clamped, not rejected.**  ``journal.log_confidence``
   records nothing for a rating outside 1..4, meaning "the strip was skipped".
   This app decides that upstream — the kata screen only logs when the strip
   was used — and its documented contract is that :func:`log_confidence`
   always returns the row it stored, so it goes through the pure builder
   (which clamps) and ``journal.save_confidence``.
3. **The cause labels are Qiskit's.**  The *taxonomy* (the keys written to
   disk) is ``common.journal.MISTAKE_CAUSES``, unchanged.  Only the button
   wording is local: "Confused two APIs" is the dojo's failure mode, and it
   would be meaningless in math-quiz.

Schema versioning
=================
Every file this app writes carries a ``<name>.schema.json`` sidecar recording
its version, and every write first rotates ``<name>.bak`` → ``.bak.1`` →
``.bak.2``.  A file written by a *newer* build raises
``common.schema.SchemaTooNewError`` instead of being overwritten with this
build's narrower view of it; the journal helpers swallow that and record it in
:func:`last_write_error`, while :func:`save_session` and :func:`save_settings`
let it propagate to their callers (both are already wrapped in try/except by
the UI, which is how "nothing happened" reaches the screen).

A missing or corrupt file always reads as empty rather than raising.
"""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

import time
from pathlib import Path

from common import datadir, flags, journal, schema
from common.jsonio import read_json_dict

from config import (
    HISTORY_FILE, DATA_DIR, FLAGGED_FILE, APP_DIR_NAME,
    MISTAKES_FILE, CONFIDENCE_FILE, SETTINGS_FILE,
)
from core.models import Kata, SessionStats

#: Re-exported so a caller that already imports this module can ask whether
#: its last write was refused as too new, without importing ``common``.
last_write_error = journal.last_write_error
clear_write_error = journal.clear_write_error
SchemaTooNewError = schema.SchemaTooNewError


# ---------------------------------------------------------------------------
# Paths — resolved on every call, so QUANTUM_STUDY_DATA_DIR is always honoured
#
# The module constants above (HISTORY_FILE &c.) are import-time snapshots kept
# for compatibility; these functions are what the code below actually uses.
# ---------------------------------------------------------------------------

def history_path() -> Path:
    """``<data dir>/dojo_history.json``, resolved now."""
    return datadir.app_file(APP_DIR_NAME, "history")


def flagged_path() -> Path:
    """``<data dir>/dojo_flagged.json``, resolved now."""
    return datadir.app_file(APP_DIR_NAME, "flagged")


def settings_path() -> Path:
    """``<data dir>/dojo_settings.json``, resolved now."""
    return datadir.app_file(APP_DIR_NAME, "settings")


mistakes_path = journal.mistakes_path
confidence_path = journal.confidence_path


# ---------------------------------------------------------------------------
# Session history (dojo_history.json)
# ---------------------------------------------------------------------------

def _load_raw() -> list:
    """Every stored session, oldest first; [] if missing or corrupt.

    Goes through ``schema.load_versioned``, so an older file is migrated
    forward in memory before anything here sees it.
    """
    return schema.load_versioned(history_path(), "history")


def save_session(stats: SessionStats) -> None:
    """Append one session to dojo_history.json (atomic, backed up, stamped)."""
    datadir.ensure_data_dir()
    sessions = _load_raw()
    sessions.append({
        "timestamp": time.time(),
        "total":     stats.total,
        "passed":    stats.passed,
        "attempts": [
            {
                "kata_id": a.kata.id,
                "section": a.kata.section,
                "passed":  a.passed,
                "tries":   a.tries,
            }
            for a in stats.attempts
        ],
    })
    schema.save_versioned(history_path(), sessions, "history")


def pass_rates_by_section() -> dict[str, float]:
    """Lifetime pass rate per section, 0.0–1.0."""
    buckets: dict[str, list[bool]] = {}
    for s in _load_raw():
        for a in s.get("attempts", []):
            sec = a.get("section", "")
            if sec:
                buckets.setdefault(sec, []).append(bool(a.get("passed", False)))
    return {
        sec: sum(vals) / len(vals)
        for sec, vals in buckets.items()
        if vals
    }


def kata_weights() -> dict[str, float]:
    """Per-kata selection weight: katas failed recently come up more often."""
    stats: dict[str, list[bool]] = {}
    for s in _load_raw():
        for a in s.get("attempts", []):
            kid = a.get("kata_id", "")
            if kid:
                stats.setdefault(kid, []).append(bool(a.get("passed", False)))
    weights: dict[str, float] = {}
    for kid, results in stats.items():
        recent = results[-3:]
        rate = sum(recent) / len(recent)
        weights[kid] = max(0.5, 2.0 - rate * 1.5)   # 2.0 never-passed → 0.5 solid
    return weights


# ---------------------------------------------------------------------------
# Flag for review (dojo_flagged.json) — common.flags does the work
# ---------------------------------------------------------------------------

def load_flagged() -> list[dict]:
    """Flagged katas, oldest first.  A missing or corrupt file reads as empty."""
    return flags.load_flagged(flagged_path(), APP_DIR_NAME)


def flagged_ids() -> set[str]:
    return flags.flagged_ids(flagged_path(), APP_DIR_NAME)


def is_flagged(kata_id: str) -> bool:
    return flags.is_flagged(flagged_path(), kata_id, APP_DIR_NAME)


def toggle_flag(kata: Kata) -> bool:
    """Flag `kata` for review, or unflag it if already flagged.

    Returns the new state (True = now flagged).
    """
    return flags.toggle_flag(flagged_path(), kata.id, kata.title, kata.section,
                             app=APP_DIR_NAME)


def unflag(kata_id: str) -> None:
    """Remove a kata from the flagged list (no-op if it is not flagged)."""
    flags.unflag(flagged_path(), kata_id, app=APP_DIR_NAME)


# ---------------------------------------------------------------------------
# Shared analytics files: mistake journal + confidence calibration
#
# Both are suite-wide (every app writes into the same mistakes.json /
# confidence.json).  ``common.journal`` holds the lock across every
# read-modify-write, writes every foreign row back verbatim, and trims only
# this app's own rows.
# ---------------------------------------------------------------------------

#: Cause taxonomy for the mistake journal — the shared one, unchanged.
#: ``None`` means "logged, not yet categorised".
MISTAKE_CAUSES: tuple[str, ...] = journal.MISTAKE_CAUSES

#: Human labels for the cause buttons.  Qiskit's wording, on the shared
#: taxonomy: "Confused two APIs" is this app's failure mode and would mean
#: nothing in math-quiz, so the labels stay local while the keys do not.
CAUSE_LABELS: dict[str, str] = {
    "misread":          "Misread the task",
    "didnt_know":       "Didn't know it",
    "knew_but_slipped": "Knew it, slipped",
    "confused":         "Confused two APIs",
    "out_of_time":      "Ran out of patience",
    "other":            "Other",
}

#: Confidence levels asked before the first Run (the shared labels).
CONFIDENCE_LABELS: dict[int, str] = journal.CONFIDENCE_LABELS

FIELD_LIMIT    = journal.TEXT_MAX          # 200: question / answers / note
MAX_MISTAKES   = journal.MISTAKES_MAX      # the cap now lives in common.journal
MAX_CONFIDENCE = journal.CONFIDENCE_MAX

#: Collapse whitespace and trim to `limit` characters (ellipsis included).
#: Journal fields are meant to be scannable one-liners, so embedded newlines
#: and runs of spaces are squashed rather than stored verbatim.
clip = journal.clip_text


# ------------------------------------------------------------ mistake journal

def make_mistake_entry(kata_id: str, category: str, question: str,
                       your_answer: str, correct_answer: str,
                       cause: str | None = None, note: str = "",
                       timestamp: float | None = None,
                       resolved: bool = False) -> dict:
    """A journal row in the documented shape.  Pure — touches no disk.

    The note is held to this app's 200-character limit rather than the shared
    500, because the note box on the kata screen is a 200-character
    ``QLineEdit``: what is stored should be what can be typed.
    """
    entry = journal.make_mistake_entry(
        kata_id, APP_DIR_NAME, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer, cause=cause,
        note=note, timestamp=timestamp, resolved=resolved,
    )
    entry["note"] = clip(note, FIELD_LIMIT)
    return entry


def load_mistakes() -> list[dict]:
    """Every journal row on disk (all apps), oldest first."""
    return [row for row in journal.load_mistakes() if row.get("id")]


def mistakes_for_app(app: str = APP_DIR_NAME) -> list[dict]:
    """Journal rows written by `app` (this app by default)."""
    return [row for row in load_mistakes() if row.get("app") == app]


def _open_index(rows: list[dict], kata_id: str) -> int:
    """Index of this app's newest unresolved row for `kata_id`, or -1."""
    for i in range(len(rows) - 1, -1, -1):
        row = rows[i]
        if (row.get("app") == APP_DIR_NAME and str(row.get("id")) == str(kata_id)
                and not row.get("resolved")):
            return i
    return -1


def log_mistake(entry: dict) -> dict:
    """Record `entry`, folding it into this kata's open row if there is one.

    One kata failed five times is one journal row, not five: a repeat failure
    refreshes what went wrong and the timestamp but keeps any cause and note
    already chosen (the UI re-logs on every failed Run).  Returns the row as
    stored.

    See "Local policy" in the module docstring for why this app folds where
    ``journal.log_mistake`` appends.  Everything underneath — the lock, the
    stale-read-proof re-read, foreign rows, the growth cap, the version
    sidecar and the backup — is ``common.journal``'s.
    """
    with journal.lock(mistakes_path(), create=True):
        rows = load_mistakes()           # read inside the lock: never stale
        idx = _open_index(rows, entry.get("id", ""))
        if idx < 0:
            rows.append(entry)
            stored = entry
        else:
            stored = dict(rows[idx])
            stored.update({
                "category":       entry.get("category", stored.get("category", "")),
                "question":       entry.get("question", stored.get("question", "")),
                "your_answer":    entry.get("your_answer", stored.get("your_answer", "")),
                "correct_answer": entry.get("correct_answer",
                                            stored.get("correct_answer", "")),
                "timestamp":      entry.get("timestamp", time.time()),
                "resolved":       False,
            })
            if entry.get("cause"):
                stored["cause"] = entry["cause"]
            if entry.get("note"):
                stored["note"] = entry["note"]
            rows[idx] = stored
        journal.save_mistakes(rows, APP_DIR_NAME)
    return stored


def set_mistake_cause(kata_id: str, cause: str | None,
                      note: str | None = None) -> bool:
    """Categorise this kata's open journal row.  True if a row was updated.

    `cause` outside MISTAKE_CAUSES clears the diagnosis back to None;
    `note=None` leaves any existing note alone, `note=""` clears it.
    """
    row = journal.set_mistake_cause(kata_id, cause, note, app=APP_DIR_NAME)
    return row is not None


def resolve_mistakes(kata_id: str) -> int:
    """Mark this app's rows for `kata_id` resolved.  Returns how many changed."""
    return journal.resolve_mistakes(kata_id, APP_DIR_NAME)


def mistake_cause_counts(unresolved_only: bool = True,
                         app: str | None = APP_DIR_NAME) -> dict[str, int]:
    """How many journal rows fall under each cause — the point of the journal.

    Uncategorised rows are counted under the key ``""`` (this app's history
    view keys off that); `app=None` counts the whole suite.
    """
    counts = journal.cause_counts(app, include_resolved=not unresolved_only)
    if journal.UNCATEGORISED in counts:
        counts[""] = counts.pop(journal.UNCATEGORISED)
    return counts


# ------------------------------------------------------ confidence calibration

def make_confidence_entry(kata_id: str, category: str, confidence: int,
                          correct: bool,
                          timestamp: float | None = None) -> dict:
    """A calibration row in the documented shape.  Pure — touches no disk."""
    return journal.make_confidence_entry(kata_id, APP_DIR_NAME, category,
                                         confidence, correct, timestamp)


def load_confidence() -> list[dict]:
    """Every calibration row on disk (all apps), oldest first."""
    return [row for row in journal.load_confidence() if row.get("id")]


def confidence_for_app(app: str = APP_DIR_NAME) -> list[dict]:
    return [row for row in load_confidence() if row.get("app") == app]


def log_confidence(kata_id: str, category: str, confidence: int,
                   correct: bool) -> dict:
    """Append one confidence/outcome pairing.  Returns the row as stored.

    Unlike ``journal.log_confidence`` this always stores something: the kata
    screen has already decided whether the strip was used, so a rating that
    arrives here is a rating the learner gave and is clamped into 1..4 rather
    than dropped (see "Local policy").
    """
    entry = make_confidence_entry(kata_id, category, confidence, correct)
    with journal.lock(confidence_path(), create=True):
        rows = load_confidence()     # read inside the lock: never stale
        rows.append(entry)
        journal.save_confidence(rows, APP_DIR_NAME)
    return entry


def calibration_summary(app: str | None = APP_DIR_NAME) -> dict[int, dict[str, int]]:
    """{level: {"total": n, "correct": n}} for levels 1-4 that have data."""
    return journal.calibration_summary(app)


def confidently_wrong(app: str | None = APP_DIR_NAME,
                      threshold: int = journal.CONFIDENT_LEVEL) -> list[dict]:
    """Rows rated `threshold`+ that turned out wrong — the unknown unknowns."""
    return journal.confidently_wrong(app, min_confidence=threshold)


# -------------------------------------------------------------- app settings

def load_settings() -> dict:
    """App-local UI preferences; {} if missing or corrupt."""
    data = schema.load_versioned(settings_path(), "settings",
                                 reader=read_json_dict)
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> None:
    """Rewrite dojo_settings.json (atomic, backed up, version-stamped)."""
    schema.save_versioned(settings_path(), dict(settings), "settings")


def confidence_prompt_enabled() -> bool:
    """Whether to offer the pre-run confidence strip (default: yes)."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
