"""Persistence for paper-drill.

Six files, all in the shared suite data directory:

===========================  =========  ====================================
file                         kind       owner
===========================  =========  ====================================
``paper_history.json``       history    this app (coach.py / dashboard.py read it)
``paper_library.json``       library    this app
``paper_flagged.json``       flagged    this app (coach.py --review reads it)
``paper_settings.json``      settings   this app
``mistakes.json``            mistakes   **all ten apps**
``confidence.json``          confidence **all ten apps**
===========================  =========  ====================================

Almost none of the machinery lives here any more.  The mistake journal, the
confidence log, the flag store, the data-directory rule, atomic writes and the
cross-process lock were a near-identical copy in each of the ten apps; they are
now ``common.journal``, ``common.flags``, ``common.datadir``, ``common.jsonio``
and ``common.locking``, and this module is the thin app-shaped face of them:

* it supplies ``app="paper-drill"`` so the shared rows carry the right owner;
* it keeps this app's *own* vocabulary — ``make_flag_id`` (the identity of a
  generated question), ``MISTAKE_SCORE_THRESHOLD``, the library;
* it keeps the call signatures the screens and
  ``tests/test_journal_concurrency.py`` already use.

Every file this app writes now goes through :mod:`common.schema`, so it carries
a version marker in a sidecar (``paper_history.json.schema.json``), migrates
forward when the format changes, is refused rather than downgraded when a newer
build wrote it, and is copied to a rotating ``.bak`` before the first write of
each session.  **No on-disk format changed**: the marker is a separate file
precisely because ``coach._load_list`` and ``dashboard._load`` require the top
level of these files to be a plain JSON list.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import flags, journal, schema
from common.jsonio import read_json_dict
from common.locking import lock

import config
from config import APP_ID
from core.models import SessionStats

# ---------------------------------------------------------------------------
# Schema kinds
#
# ``history``, ``flagged``, ``settings``, ``mistakes`` and ``confidence`` are
# registered by common.schema for the whole suite.  The paper library is this
# app's alone, so this app registers it — idempotently, because a test that
# reloads this module must not trip over "already registered".
# ---------------------------------------------------------------------------

LIBRARY_KIND = "paper_library"

if LIBRARY_KIND not in schema.kinds():
    schema.register(schema.FileSchema(
        LIBRARY_KIND,
        description="paper-drill's saved papers: [{id,title,text,q_count,saved_at}]",
    ))


# ---------------------------------------------------------------------------
# Paths — resolved at call time, so QUANTUM_STUDY_DATA_DIR is always honoured
# ---------------------------------------------------------------------------

def history_path() -> Path:
    return config.history_file()


def library_path() -> Path:
    return config.library_file()


def flagged_path() -> Path:
    return config.flagged_file()


def settings_path() -> Path:
    return config.settings_file()


def mistakes_path() -> Path:
    return journal.mistakes_path()


def confidence_path() -> Path:
    return journal.confidence_path()


# ---------------------------------------------------------------------------
# Refused writes
#
# common.schema refuses to overwrite a file written by a *newer* build rather
# than silently deleting the fields that build added.  A drill must not crash
# for that, so the helpers below swallow the refusal and record it here; the
# journal keeps its own (journal.last_write_error()) for the two shared files.
# ---------------------------------------------------------------------------

_LAST_WRITE_ERROR: schema.SchemaError | None = None


def last_write_error() -> schema.SchemaError | None:
    """The most recent refused write (this app's files, or the shared journal)."""
    return _LAST_WRITE_ERROR or journal.last_write_error()


def clear_write_error() -> None:
    global _LAST_WRITE_ERROR
    _LAST_WRITE_ERROR = None
    journal.clear_write_error()


def _save_versioned(path: Path, payload, kind: str) -> bool:
    """``schema.save_versioned`` that reports a refusal instead of raising."""
    global _LAST_WRITE_ERROR
    try:
        schema.save_versioned(path, payload, kind)
    except schema.SchemaTooNewError as exc:
        _LAST_WRITE_ERROR = exc
        return False
    return True


# ---------------------------------------------------------------------------
# Session history  (paper_history.json)
# ---------------------------------------------------------------------------

def _load_raw() -> list[dict]:
    """Saved sessions, oldest first.  A missing or corrupt file reads as ``[]``."""
    rows = schema.load_versioned(history_path(), "history")
    return [r for r in rows if isinstance(r, dict)]


def save_session(stats: SessionStats) -> bool:
    """Append one finished session.  False when the write was refused."""
    path = history_path()
    with lock(path, create=True):
        sessions = _load_raw()          # read inside the lock: never stale
        sessions.append({
            "title":   stats.title,
            "total":   stats.total,
            "average": stats.average,
            "scores":  stats.scores,
        })
        return _save_versioned(path, sessions, "history")


# ---------------------------------------------------------------------------
# Paper library  (paper_library.json)
# ---------------------------------------------------------------------------

def _load_library_raw() -> list[dict]:
    rows = schema.load_versioned(library_path(), LIBRARY_KIND)
    return [r for r in rows if isinstance(r, dict)]


def load_library() -> list[dict]:
    """Return list of saved papers: {id, title, text, q_count, saved_at}."""
    return _load_library_raw()


def save_paper(title: str, text: str, q_count: int) -> str:
    """Save a paper to the library and return its new ID."""
    path = library_path()
    paper_id = str(uuid.uuid4())[:8]
    with lock(path, create=True):
        library = _load_library_raw()   # read inside the lock: never stale
        library.append({
            "id":       paper_id,
            "title":    title,
            "text":     text,
            "q_count":  q_count,
            "saved_at": datetime.now(tz=timezone.utc).isoformat(),
        })
        _save_versioned(path, library, LIBRARY_KIND)
    return paper_id


def delete_paper(paper_id: str) -> None:
    """Remove a paper from the library by ID."""
    path = library_path()
    with lock(path, create=True):
        library = [p for p in _load_library_raw() if p.get("id") != paper_id]
        _save_versioned(path, library, LIBRARY_KIND)


# ---------------------------------------------------------------------------
# Flag for review  (paper_flagged.json)
#
# The store itself is common.flags: the shared contract entry
# ``{"id", "label", "category", "app", "timestamp"}``, read tolerantly (legacy
# bare-id files included), rewritten from the *raw* list so a row this app does
# not understand is never deleted, written atomically under the lock.
#
# Only the *identity* of a flagged item stays here, because it is this app's
# own: see make_flag_id.
# ---------------------------------------------------------------------------

FLAG_LABEL_MAX = flags.LABEL_MAX          # 80


def make_flag_id(paper_title: str, question_text: str) -> str:
    """Stable id for a (paper, question) pair — questions are generated
    on the fly, so the hash is the only durable identity they have.

    Kept app-local rather than using ``common.flags.make_id``: the two hash
    differently (``make_id`` collapses *all* whitespace inside each part, this
    only strips the ends), and the digest is written into ``paper_flagged.json``
    and into every ``mistakes.json`` row this app has ever logged.  Changing it
    would orphan the flags and the mistake history already on disk, so the
    existing function is the contract, not an implementation detail.

    Design note (not a bug): the key is the *title* plus the question text,
    not the paper body.  Two papers that share a title — e.g. both left as
    the default "Untitled Paper" — and that happen to yield the identical
    question therefore map to one id, and one flag toggles both.  Keying on
    the title is deliberate: it is what the learner sees in the review list,
    and it survives re-pasting the same paper with whitespace differences.
    """
    key = f"{paper_title.strip()}\n{question_text.strip()}".encode("utf-8")
    return "paper-" + hashlib.sha256(key).hexdigest()[:16]


def make_flag_label(question_text: str, limit: int = FLAG_LABEL_MAX) -> str:
    """Question text collapsed to one line and truncated for list display.

    Only this label is persisted (the shared contract has no body field), so
    a question longer than ``limit`` cannot be recovered in full from the
    review list — the review flag points you back at the paper, not the
    exact prompt.
    """
    return flags.make_label(question_text, limit)


def load_flagged() -> list[dict]:
    """Flagged entries in the contract shape (a bad file reads as empty)."""
    return flags.load_flagged(flagged_path(), APP_ID)


def is_flagged(flag_id: str) -> bool:
    return flags.is_flagged(flagged_path(), flag_id, APP_ID)


def _note_flag_refusal(path: Path) -> None:
    """Record a refused flag write so the app can report it.

    ``common.flags.save_flagged`` refuses to overwrite a newer file — correctly
    — but returns False without saying why, and there is no ``last_write_error``
    on that module.  Asking ``check_writable`` the same question it asks costs
    a stat and keeps :func:`last_write_error` honest about all six files.
    """
    global _LAST_WRITE_ERROR
    try:
        schema.check_writable(path, "flagged")
    except schema.SchemaTooNewError as exc:
        _LAST_WRITE_ERROR = exc


def toggle_flag(flag_id: str, label: str, category: str) -> bool:
    """Flag the item if unflagged, unflag it if flagged.  Returns new state."""
    path = flagged_path()
    _note_flag_refusal(path)
    return flags.toggle_flag(path, flag_id, label, category, app=APP_ID)


def unflag(flag_id: str) -> None:
    """Remove a flagged entry by id (no-op if absent)."""
    path = flagged_path()
    if flags.is_flagged(path, flag_id, APP_ID):
        _note_flag_refusal(path)          # only a real removal is a real write
    flags.unflag(path, flag_id, app=APP_ID)


# ---------------------------------------------------------------------------
# Learning signals — mistake journal + confidence calibration
#
# Both files are shared with the other nine apps.  common.journal owns the
# rules: every read-modify-write runs inside a lock on a ``<file>.lock``
# sidecar and re-reads the file *inside* it; every row another app owns is
# written back verbatim, unknown keys included; growth is capped by dropping
# only **our own** oldest rows, never another app's.
#
# The names below are re-exported so the screens (and
# tests/test_journal_concurrency.py, which imports this module by path) keep
# working unchanged.
# ---------------------------------------------------------------------------

MISTAKE_TEXT_MAX      = journal.TEXT_MAX          # 200
MISTAKE_NOTE_MAX      = journal.NOTE_MAX          # 500
MISTAKE_CAUSES        = journal.MISTAKE_CAUSES
MISTAKE_CAUSE_LABELS  = journal.CAUSE_LABELS
UNCATEGORISED         = journal.UNCATEGORISED
CONFIDENCE_LEVELS     = journal.CONFIDENCE_LABELS  # {1: "Guessing", … 4: "Certain"}
CONFIDENT_LEVEL       = journal.CONFIDENT_LEVEL
#: Back-compat aliases.  The live caps are journal.MISTAKES_MAX /
#: journal.CONFIDENCE_MAX — patch those, not these, to change the behaviour.
MISTAKES_MAX_ENTRIES   = journal.MISTAKES_MAX      # 2000
CONFIDENCE_MAX_ENTRIES = journal.CONFIDENCE_MAX    # 5000

#: A graded answer below this score counts as a mistake (matches
#: Verdict.INCORRECT).  App-specific: paper-drill grades out of ten.
MISTAKE_SCORE_THRESHOLD = 4

SETTING_CONFIDENCE_PROMPT = "confidence_prompt"

clip_text = journal.clip_text
clip_note = journal.clip_note
normalise_cause = journal.normalise_cause


def make_mistake_entry(item_id: str, category: str, question: str,
                       your_answer: str, correct_answer: str,
                       cause=None, note: str = "", timestamp=None,
                       resolved: bool = False) -> dict:
    """Build a contract-shaped mistake entry (pure — nothing is written)."""
    return journal.make_mistake_entry(
        item_id, APP_ID, category=category, question=question,
        your_answer=your_answer, correct_answer=correct_answer,
        cause=cause, note=note, timestamp=timestamp, resolved=resolved)


def load_mistakes() -> list[dict]:
    """Every app's mistake entries, oldest first (bad files read as empty)."""
    return journal.load_mistakes()


def _save_mistakes(entries: list[dict]) -> bool:
    """Rewrite the shared journal (foreign rows preserved, our oldest trimmed)."""
    return journal.save_mistakes(entries, APP_ID)


def mistakes_for(item_id: str) -> list[dict]:
    """This app's entries for one item id, oldest first."""
    return journal.mistakes_for(item_id, APP_ID)


def log_mistake(item_id: str, category: str, question: str, your_answer: str,
                correct_answer: str, cause=None, note: str = "") -> dict:
    """Append a mistake entry and return it.

    Called the moment an answer is graded wrong, with ``cause=None``: skipping
    the "What went wrong?" row must still leave the mistake on record.  The
    cause is filled in afterwards by :func:`set_mistake_cause`.  A repeat slip
    on the same item is its own row — repetition is the signal.
    """
    return journal.log_mistake(make_mistake_entry(
        item_id, category, question, your_answer, correct_answer,
        cause=cause, note=note))


def set_mistake_cause(item_id: str, cause, note: str | None = None) -> bool:
    """Categorise this app's most recent open entry for ``item_id``.

    Updates the newest unresolved row (falling back to the newest row of any
    state) so re-categorising, or adding a note after picking a cause, edits
    one entry instead of piling up duplicates.  Returns False when there is
    nothing to update.

    ``note=None`` (the default) **keeps** the note that is already there;
    ``note=""`` clears it.  The old default of ``""`` wiped the note whenever a
    cause was picked after the note had been typed.
    """
    return journal.set_mistake_cause(item_id, cause, note, app=APP_ID) is not None


def resolve_mistake(item_id: str) -> int:
    """Mark this app's entries for ``item_id`` resolved; returns how many changed."""
    return journal.resolve_mistakes(item_id, APP_ID)


def cause_counts(entries=None, app: str | None = APP_ID,
                 include_resolved: bool = True) -> dict[str, int]:
    """Tally of causes — the payload of the journal ("six misreads this month").

    Uncategorised entries are counted under the key ``"uncategorised"``.
    """
    return journal.cause_counts(app, include_resolved=include_resolved,
                                entries=entries)


def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, timestamp=None) -> dict:
    """Build a contract-shaped confidence entry (pure — nothing is written)."""
    return journal.make_confidence_entry(item_id, APP_ID, category=category,
                                         confidence=confidence, correct=correct,
                                         timestamp=timestamp)


def load_confidence() -> list[dict]:
    """Every app's confidence rows, oldest first (bad files read as empty)."""
    return journal.load_confidence()


def log_confidence(item_id: str, category: str, confidence, correct: bool):
    """Record a (pre-answer confidence, graded outcome) pair.

    Returns the stored entry, or None when ``confidence`` is not 1–4 (the
    rating is optional, so "no rating" is a normal, silent no-op).  A rating
    outside the range is rejected rather than clamped: clamping would invent a
    rating the learner never gave and then report on it.
    """
    return journal.log_confidence(item_id, APP_ID, category=category,
                                  confidence=confidence, correct=correct)


def confidently_wrong(entries=None, app: str | None = APP_ID) -> list[dict]:
    """Rows rated 'fairly sure' or 'certain' that turned out wrong."""
    return journal.confidently_wrong(app, entries=entries)


def calibration_summary(entries=None, app: str | None = APP_ID):
    """``{rating: {"total": n, "correct": c}}`` — how well-calibrated we are."""
    return journal.calibration_summary(app, entries=entries)


# ---------------------------------------------------------------------------
# App settings (this app only) — currently just the confidence-strip opt-out
# ---------------------------------------------------------------------------

def load_settings() -> dict:
    """Saved UI preferences; a missing or corrupt file reads as {}."""
    data = schema.load_versioned(settings_path(), "settings",
                                 reader=read_json_dict)
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> bool:
    """Write the preferences file.  False when the write was refused."""
    return _save_versioned(settings_path(), settings, "settings")


def confidence_prompt_enabled() -> bool:
    """True unless the learner has switched the confidence strip off."""
    return bool(load_settings().get(SETTING_CONFIDENCE_PROMPT, True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    path = settings_path()
    with lock(path, create=True):
        settings = load_settings()      # read inside the lock: never stale
        settings[SETTING_CONFIDENCE_PROMPT] = bool(enabled)
        _save_versioned(path, settings, "settings")


__all__ = [
    # paths
    "history_path", "library_path", "flagged_path", "settings_path",
    "mistakes_path", "confidence_path",
    # history + library
    "save_session", "load_library", "save_paper", "delete_paper",
    # flags
    "FLAG_LABEL_MAX", "make_flag_id", "make_flag_label", "load_flagged",
    "is_flagged", "toggle_flag", "unflag",
    # journal
    "MISTAKE_TEXT_MAX", "MISTAKE_NOTE_MAX", "MISTAKE_CAUSES",
    "MISTAKE_CAUSE_LABELS", "UNCATEGORISED", "MISTAKE_SCORE_THRESHOLD",
    "MISTAKES_MAX_ENTRIES", "CONFIDENCE_MAX_ENTRIES",
    "CONFIDENCE_LEVELS", "CONFIDENT_LEVEL",
    "clip_text", "clip_note", "normalise_cause",
    "make_mistake_entry", "load_mistakes", "mistakes_for", "log_mistake",
    "set_mistake_cause", "resolve_mistake", "cause_counts",
    "make_confidence_entry", "load_confidence", "log_confidence",
    "confidently_wrong", "calibration_summary",
    # settings
    "SETTING_CONFIDENCE_PROMPT", "load_settings", "save_settings",
    "confidence_prompt_enabled", "set_confidence_prompt_enabled",
    # schema
    "LIBRARY_KIND", "last_write_error", "clear_write_error",
]
