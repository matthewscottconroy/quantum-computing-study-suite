"""Mistake journal + confidence calibration (the suite-wide review contract).

Two files, both in ``config.DATA_DIR`` and both **shared with every other app in
the suite** — entries carry an ``app`` field and this module only ever rewrites
its own rows, so another app's history survives our writes:

``mistakes.json``    a JSON list of
    ``{"id", "app", "category", "question", "your_answer", "correct_answer",
       "cause", "note", "timestamp", "resolved"}``
    ``cause`` is one of :data:`CAUSES` or ``None`` ("logged, not yet categorised").

``confidence.json``  a JSON list of
    ``{"id", "app", "category", "confidence", "correct", "timestamp"}``
    ``confidence`` is 1 = guessing … 4 = certain.

Why they exist: a missed card used to become a bookmark.  The cause buckets turn
it into analysis ("nine little-endian slips this month"), and the confidence
pairing separates *right* from *right and knew it* — the confidently-wrong rows
are the unknown unknowns.

Design rules followed here (same as :mod:`persistence.schedule_store`):

* paths are read from :mod:`config` **at call time**, so ``QUANTUM_STUDY_DATA_DIR``
  and the test-suite's constant relocation both apply;
* every write is atomic (temp file in the same directory + ``os.replace``);
* every read-modify-write is serialised across processes by
  :mod:`journal_sync` (an ``fcntl.flock`` on ``mistakes.json.lock`` /
  ``confidence.json.lock``), because the two files are shared and several apps
  can be open at once — an unlocked read-modify-write silently drops rows
  another app appended between our read and our write;
* a rewrite puts other apps' rows back **exactly as they were read**, unknown
  keys included: only our own rows are normalised through the schema above;
* nothing raises into a drill — a missing, unreadable or corrupt file degrades to
  "start fresh" and a failed write returns ``False``/``None``;
* every public helper is pure Python (no Qt), so it is unit-testable on its own.

**The SM-2 schedule is not touched from here.**  A logged mistake is analysis, not
a second lapse: ``flashcard_schedule.json`` is written only by
``persistence/schedule_store.py``, exactly as before this module existed.

``flashcard_settings.json`` (private to this app) remembers the confidence
opt-out so a user who dislikes the strip is never asked again.

Growth is capped: the newest :data:`MISTAKE_LIMIT` mistakes and
:data:`CONFIDENCE_LIMIT` confidence rows *for this app* are kept on every write
(other apps' rows are never trimmed by us).
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

import config
import journal_sync

APP_NAME = "flashcard-drill"

#: Cause buckets, in the order the UI shows them.
CAUSES = ("misread", "didnt_know", "knew_but_slipped", "confused",
          "out_of_time", "other")

CAUSE_LABELS = {
    "misread":          "Misread",
    "didnt_know":       "Didn't know",
    "knew_but_slipped": "Knew but slipped",
    "confused":         "Confused",
    "out_of_time":      "Out of time",
    "other":            "Other",
}

CONFIDENCE_LABELS = {1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}
CONFIDENCE_LEVELS = (1, 2, 3, 4)

MAX_TEXT         = 200      # contract: question / answers / note are <= 200 chars
MISTAKE_LIMIT    = 2000     # newest-N kept per app on write
CONFIDENCE_LIMIT = 5000

__all__ = [
    "APP_NAME", "CAUSES", "CAUSE_LABELS", "CONFIDENCE_LABELS", "CONFIDENCE_LEVELS",
    "MAX_TEXT", "MISTAKE_LIMIT", "CONFIDENCE_LIMIT",
    "mistakes_path", "confidence_path", "settings_path",
    "clip_text", "make_mistake_entry", "load_mistakes", "save_mistakes",
    "log_mistake", "set_mistake_cause", "resolve_mistakes", "cause_counts",
    "make_confidence_entry", "load_confidence", "save_confidence",
    "log_confidence", "calibration_summary", "confidently_wrong",
    "load_settings", "save_settings", "confidence_enabled", "set_confidence_enabled",
]


# --- paths ------------------------------------------------------------------

def mistakes_path() -> Path:
    return config.MISTAKES_FILE


def confidence_path() -> Path:
    return config.CONFIDENCE_FILE


def settings_path() -> Path:
    return config.SETTINGS_FILE


# --- shared plumbing --------------------------------------------------------

def clip_text(value, limit: int = MAX_TEXT) -> str:
    """One-line, ``limit``-character form of *value* (cards wrap over many lines)."""
    text = " ".join(str(value if value is not None else "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _now() -> float:
    return time.time()


def _read_list(path: Path) -> list:
    """The JSON list at *path*; ``[]`` when absent, unreadable or not a list."""
    try:
        if not path.exists():
            return []
        raw = json.loads(path.read_text())
    except (OSError, ValueError):
        return []
    return raw if isinstance(raw, list) else []


def _write_json(path: Path, payload) -> bool:
    """Atomically replace *path* with *payload*.  ``False`` if it could not be written."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=str(path.parent),
                                        prefix=f".{path.stem}-", suffix=".json")
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(payload, fh, indent=2)
            os.replace(tmp_name, path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
        return True
    except (OSError, TypeError, ValueError):
        return False


def _as_float(value, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return default if out != out or out in (float("inf"), float("-inf")) else out


def _ident(raw) -> str | None:
    ident = raw.get("id") if isinstance(raw, dict) else None
    return ident.strip() if isinstance(ident, str) and ident.strip() else None


def _trim(entries: list[dict], app: str, limit: int) -> list[dict]:
    """Drop this app's oldest rows past *limit*; other apps' rows are untouched."""
    mine = [i for i, e in enumerate(entries) if e.get("app") == app]
    if len(mine) <= limit:
        return entries
    drop = set(mine[: len(mine) - limit])
    return [e for i, e in enumerate(entries) if i not in drop]


# --- mistake journal --------------------------------------------------------

def make_mistake_entry(
    item_id: str,
    category: str = "",
    question: str = "",
    your_answer: str = "",
    correct_answer: str = "",
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    resolved: bool = False,
    app: str = APP_NAME,
) -> dict:
    """A contract-shaped mistake entry.  Pure: nothing is read or written."""
    return {
        "id":             str(item_id),
        "app":            str(app),
        "category":       str(category or ""),
        "question":       clip_text(question),
        "your_answer":    clip_text(your_answer),
        "correct_answer": clip_text(correct_answer),
        "cause":          cause if cause in CAUSES else None,
        "note":           clip_text(note),
        "timestamp":      _as_float(timestamp, 0.0) or _now(),
        "resolved":       bool(resolved),
    }


def _normalise_mistake(raw) -> dict | None:
    """Coerce one on-disk row into a full entry, or ``None`` when unusable."""
    ident = _ident(raw)
    if ident is None:
        return None
    return make_mistake_entry(
        item_id=ident,
        category=raw.get("category", ""),
        question=raw.get("question", ""),
        your_answer=raw.get("your_answer", ""),
        correct_answer=raw.get("correct_answer", ""),
        cause=raw.get("cause"),
        note=raw.get("note", ""),
        timestamp=raw.get("timestamp"),
        resolved=bool(raw.get("resolved", False)),
        app=raw.get("app") if isinstance(raw.get("app"), str) and raw.get("app").strip()
            else APP_NAME,
    )


def load_mistakes(app: str | None = None) -> list[dict]:
    """Every journal entry in file order; *app* filters to one app's rows.

    Malformed rows are skipped, a corrupt file reads as empty.  Never raises.
    """
    out = []
    for raw in _read_list(mistakes_path()):
        entry = _normalise_mistake(raw)
        if entry is not None and (app is None or entry["app"] == app):
            out.append(entry)
    return out


def save_mistakes(entries: list[dict], app: str = APP_NAME) -> bool:
    """Replace *app*'s rows with *entries* (trimmed to the per-app cap).

    Other apps' rows are never ours to rewrite: whatever is on disk for them at
    the moment of the write is put back verbatim, unknown keys and all, even if
    *entries* carries a stale or normalised copy of it.  The whole read-merge-
    write runs under the journal lock.
    """
    with journal_sync.lock(mistakes_path(), create=True):
        clean = [e for e in (x if journal_sync.is_foreign(x, app)
                             else _normalise_mistake(x) for x in entries)
                 if e is not None]
        merged = journal_sync.merge_foreign(_read_list(mistakes_path()), clean, app)
        return _write_json(mistakes_path(), _trim(merged, app, MISTAKE_LIMIT))


def log_mistake(
    item_id: str,
    category: str = "",
    question: str = "",
    your_answer: str = "",
    correct_answer: str = "",
    cause: str | None = None,
    note: str = "",
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> dict | None:
    """Append one mistake (``cause=None`` = "not yet categorised").

    Returns the stored entry — its ``timestamp`` identifies it for a later
    :func:`set_mistake_cause` — or ``None`` when the file could not be written.
    """
    if not isinstance(item_id, str) or not item_id.strip():
        return None
    entry = make_mistake_entry(
        item_id.strip(), category, question, your_answer, correct_answer,
        cause=cause, note=note, timestamp=timestamp, resolved=False, app=app,
    )
    with journal_sync.lock(mistakes_path(), create=True):
        entries = load_mistakes()        # read inside the lock: never stale
        entries.append(entry)
        return entry if save_mistakes(entries, app) else None


def set_mistake_cause(
    item_id: str,
    cause: str | None,
    note: str | None = None,
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> bool:
    """Categorise a logged mistake; ``True`` when a row was updated and saved.

    Targets the row with *timestamp* when given, otherwise the most recent row
    for ``app`` + ``item_id``.  *note* left as ``None`` keeps the existing note.
    """
    with journal_sync.lock(mistakes_path()):
        return _set_mistake_cause_locked(item_id, cause, note, timestamp, app)


def _set_mistake_cause_locked(item_id, cause, note, timestamp, app) -> bool:
    entries = load_mistakes()            # read inside the lock: never stale
    target = None
    for entry in entries:
        if entry["app"] != app or entry["id"] != item_id:
            continue
        if timestamp is not None and entry["timestamp"] != timestamp:
            continue
        if target is None or entry["timestamp"] >= target["timestamp"]:
            target = entry
    if target is None:
        return False
    target["cause"] = cause if cause in CAUSES else None
    if note is not None:
        target["note"] = clip_text(note)
    return save_mistakes(entries, app)


def resolve_mistakes(item_id: str, app: str = APP_NAME) -> int:
    """Mark every open mistake for ``app`` + *item_id* resolved.  Returns the count."""
    with journal_sync.lock(mistakes_path()):
        return _resolve_mistakes_locked(item_id, app)


def _resolve_mistakes_locked(item_id: str, app: str) -> int:
    entries = load_mistakes()            # read inside the lock: never stale
    hits = [e for e in entries
            if e["app"] == app and e["id"] == item_id and not e["resolved"]]
    if not hits:
        return 0
    for entry in hits:
        entry["resolved"] = True
    return len(hits) if save_mistakes(entries, app) else 0


def cause_counts(app: str | None = APP_NAME, since: float | None = None) -> dict[str, int]:
    """``{cause_or_"uncategorised": n}`` — the signal the journal exists for."""
    counts: dict[str, int] = {}
    for entry in load_mistakes(app):
        if since is not None and entry["timestamp"] < since:
            continue
        key = entry["cause"] or "uncategorised"
        counts[key] = counts.get(key, 0) + 1
    return counts


# --- confidence calibration -------------------------------------------------

def make_confidence_entry(
    item_id: str,
    category: str = "",
    confidence: int = 1,
    correct: bool = False,
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> dict:
    """A contract-shaped confidence row.  Pure: nothing is read or written."""
    try:
        level = int(confidence)
    except (TypeError, ValueError):
        level = 1
    return {
        "id":         str(item_id),
        "app":        str(app),
        "category":   str(category or ""),
        "confidence": min(4, max(1, level)),
        "correct":    bool(correct),
        "timestamp":  _as_float(timestamp, 0.0) or _now(),
    }


def _normalise_confidence(raw) -> dict | None:
    ident = _ident(raw)
    if ident is None:
        return None
    level = raw.get("confidence")
    try:
        int(level)
    except (TypeError, ValueError):
        return None
    return make_confidence_entry(
        item_id=ident,
        category=raw.get("category", ""),
        confidence=level,
        correct=bool(raw.get("correct", False)),
        timestamp=raw.get("timestamp"),
        app=raw.get("app") if isinstance(raw.get("app"), str) and raw.get("app").strip()
            else APP_NAME,
    )


def load_confidence(app: str | None = None) -> list[dict]:
    """Every confidence row in file order; *app* filters to one app's rows."""
    out = []
    for raw in _read_list(confidence_path()):
        entry = _normalise_confidence(raw)
        if entry is not None and (app is None or entry["app"] == app):
            out.append(entry)
    return out


def save_confidence(entries: list[dict], app: str = APP_NAME) -> bool:
    """Replace *app*'s rows with *entries*; other apps' rows survive verbatim."""
    with journal_sync.lock(confidence_path(), create=True):
        clean = [e for e in (x if journal_sync.is_foreign(x, app)
                             else _normalise_confidence(x) for x in entries)
                 if e is not None]
        merged = journal_sync.merge_foreign(_read_list(confidence_path()), clean, app)
        return _write_json(confidence_path(), _trim(merged, app, CONFIDENCE_LIMIT))


def log_confidence(
    item_id: str,
    category: str = "",
    confidence: int = 1,
    correct: bool = False,
    timestamp: float | None = None,
    app: str = APP_NAME,
) -> dict | None:
    """Record one confidence/outcome pairing.  ``None`` if it could not be written."""
    if not isinstance(item_id, str) or not item_id.strip():
        return None
    entry = make_confidence_entry(item_id.strip(), category, confidence, correct,
                                  timestamp=timestamp, app=app)
    with journal_sync.lock(confidence_path(), create=True):
        entries = load_confidence()      # read inside the lock: never stale
        entries.append(entry)
        return entry if save_confidence(entries, app) else None


def calibration_summary(app: str | None = APP_NAME) -> dict[int, dict]:
    """``{level: {"n", "correct", "accuracy"}}`` for levels 1-4 (levels with rows only)."""
    out: dict[int, dict] = {}
    for entry in load_confidence(app):
        bucket = out.setdefault(entry["confidence"], {"n": 0, "correct": 0, "accuracy": 0.0})
        bucket["n"] += 1
        bucket["correct"] += 1 if entry["correct"] else 0
    for bucket in out.values():
        bucket["accuracy"] = bucket["correct"] / bucket["n"] if bucket["n"] else 0.0
    return out


def confidently_wrong(app: str | None = APP_NAME, threshold: int = 3) -> list[dict]:
    """Rows answered wrongly at confidence >= *threshold* — the unknown unknowns."""
    return [e for e in load_confidence(app)
            if not e["correct"] and e["confidence"] >= threshold]


# --- app settings (confidence opt-out) --------------------------------------

_DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """``flashcard_settings.json`` merged over the defaults.  Never raises."""
    settings = dict(_DEFAULT_SETTINGS)
    try:
        path = settings_path()
        if path.exists():
            raw = json.loads(path.read_text())
            if isinstance(raw, dict):
                settings.update({k: v for k, v in raw.items() if isinstance(k, str)})
    except (OSError, ValueError):
        pass
    return settings


def save_settings(values: dict) -> bool:
    """Merge *values* into the settings file (atomically).  Never raises."""
    settings = load_settings()
    settings.update(values or {})
    return _write_json(settings_path(), settings)


def confidence_enabled() -> bool:
    """False once the user has clicked "Don't ask" on the confidence strip."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_enabled(enabled: bool) -> bool:
    return save_settings({"confidence_prompt": bool(enabled)})
