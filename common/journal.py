"""The suite-wide mistake journal and confidence-calibration log.

Two files in the data directory, written by **all ten apps at once**::

    mistakes.json    [ {id, app, category, question, your_answer,
                        correct_answer, cause, note, timestamp, resolved}, … ]
    confidence.json  [ {id, app, category, confidence, correct, timestamp}, … ]

Why they exist: a wrong answer used to become a bookmark.  The ``cause``
buckets turn it into analysis ("nine little-endian slips this month"), and the
confidence pairing separates *right* from *right and knew it* — the
confidently-wrong rows are the unknown unknowns.  ``coach.py --mistakes`` and
``dashboard.py`` read both files; **their on-disk shape is load-bearing and is
not changed here.**

The three invariants
====================
1. **Locked.**  Every read-modify-write runs inside
   :func:`common.locking.lock` on a ``<file>.lock`` sidecar, and re-reads the
   file *inside* the lock.  An unlocked read-modify-write drops rows another
   app appended between the read and the write; measured, three processes
   appending 60 rows each kept 103 of 180.
2. **Foreign rows survive verbatim.**  A rewrite puts back every row this app
   does not own exactly as it was read, unknown keys included
   (:func:`merge_foreign`).  Apps normalise rows through their own schema on
   load, which would otherwise silently drop a key another app added.
3. **Nothing raises into a drill.**  A missing, corrupt or unreadable file
   reads as empty; a refused write (see :mod:`common.schema`) is recorded in
   :func:`last_write_error` and reported as "nothing happened".

Divergences between the ten copies, and what was chosen
=======================================================
================================  =======================================
Divergence                        Canonical here, and why
================================  =======================================
``log_mistake`` merges a repeat   **Append.**  qec-trainer merged a re-log
into the open row (qec-trainer)   into the open row; eight apps appended.
vs appends a new row (the rest)   ``dashboard.load_mistakes`` says it
                                  outright: "a genuine second miss of the
                                  same item keeps its own entry, because
                                  repetition is exactly the signal".
                                  Merging destroys the count.
Growth cap trims the newest N     **Trim our own rows only.**  Eight apps
rows of the *whole file* (eight   sorted the merged list by timestamp and
apps) vs only this app's rows     kept the newest N — which silently
(paper-drill)                     deletes *other apps'* rows during our
                                  write, on a file we do not own.  That is
                                  a data-loss bug; paper-drill's
                                  ``_trim_own`` is right.
``set_mistake_cause(note="")``    **``note=None`` leaves the note alone,**
always overwrote the note         ``note=""`` clears it.  paper-drill's
(paper-drill) vs left it when     signature (``note: str = ""``) wiped a
None (qec, vqa)                   note whenever a cause was picked after
                                  it had been typed.
Unknown cause raises ValueError   **Never raise.**  A stray cause value
(math-quiz, exam-sim) vs is       must not lose the mistake itself; it is
stored as None (six apps) vs is   stored as None ("logged, not yet
lower-cased first (vqa)           categorised").  The vqa normalisation
                                  (strip + lower-case) is kept, so
                                  ``"Misread"`` matches.
``calibration_summary`` buckets   **``{"total", "correct"}``** (qiskit-dojo,
``{"n", "correct"}`` (qec) vs     math-quiz).  ``n`` is not self-describing
``{"total", "correct"}``          next to ``correct``.
``CAUSE_LABELS["didnt_know"]``    **ASCII ``"Didn't know"``** — seven of the
uses a typographic apostrophe     ten copies, and exam-sim's longer
(vqa) or different wording        wordings ("Knew it, slipped") were a
(exam-sim)                        local rewrite, not a considered change.
Text clipping truncates hard      **Collapse whitespace and add ``…``** for
(qec, vqa) vs collapses           the one-line fields; the note keeps its
whitespace and adds ``…``         line breaks (it is prose the user typed)
(paper-drill, quantum-quiz)       and is truncated without reflowing.
``log_confidence`` clamps a bad   **Reject.**  Clamping fabricates a rating
rating to 1..4 (vqa) vs rejects   the user never gave; ``None`` means "the
it (qec, paper-drill)             strip was skipped" and records nothing.
                                  The *pure builder* still clamps, so a row
                                  is always schema-valid once built.
================================  =======================================
"""
from __future__ import annotations

import time
from typing import Any

from common import datadir, schema
from common.jsonio import read_json_list
from common.locking import lock

# ---------------------------------------------------------------------------
# The contract
# ---------------------------------------------------------------------------

#: The cause taxonomy.  Identical in all ten copies; this is it.
MISTAKE_CAUSES: tuple[str, ...] = (
    "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time",
    "other",
)

#: Button labels, kept beside the taxonomy so the UI and the journal cannot
#: drift apart.
CAUSE_LABELS: dict[str, str] = {
    "misread":          "Misread",
    "didnt_know":       "Didn't know",
    "knew_but_slipped": "Knew but slipped",
    "confused":         "Confused",
    "out_of_time":      "Out of time",
    "other":            "Other",
}

#: Key used by :func:`cause_counts` for rows with ``cause=None``.
UNCATEGORISED = "uncategorised"

#: Valid confidence ratings and their labels (1 = guessing … 4 = certain).
CONFIDENCE_LEVELS: tuple[int, ...] = (1, 2, 3, 4)
CONFIDENCE_LABELS: dict[int, str] = {
    1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain",
}

#: At or above this rating, a wrong answer is "confidently wrong".
CONFIDENT_LEVEL = 3

#: Field caps, per the shared contract.
TEXT_MAX = 200          # category / question / your_answer / correct_answer
NOTE_MAX = 500          # the user's own note

#: Growth caps.  Both files are append-only logs; each app keeps at most this
#: many of **its own** rows, so a few years of study cannot grow them without
#: bound and no app can trim another's.
MISTAKES_MAX = 2000
CONFIDENCE_MAX = 5000

#: The keys a mistake row has.  Order is the order they are written in.
MISTAKE_KEYS: tuple[str, ...] = (
    "id", "app", "category", "question", "your_answer", "correct_answer",
    "cause", "note", "timestamp", "resolved",
)
CONFIDENCE_KEYS: tuple[str, ...] = (
    "id", "app", "category", "confidence", "correct", "timestamp",
)


# ---------------------------------------------------------------------------
# Pure helpers (no I/O, no Qt — unit-testable on their own)
# ---------------------------------------------------------------------------

def clip_text(value: object, limit: int = TEXT_MAX) -> str:
    """One-line, length-capped copy of *value* (ellipsis when truncated).

    Used for the fields that are shown in a one-line list: a question with a
    newline in it would break the row, so whitespace is collapsed first.
    """
    flat = " ".join(str("" if value is None else value).split())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1].rstrip() + "…"


def clip_note(value: object, limit: int = NOTE_MAX) -> str:
    """Length-capped copy of a user-written note, **keeping its line breaks**.

    The note is prose the learner typed into a multi-line box; reflowing it
    into one line (as some copies did) destroys deliberate structure.
    """
    text = str("" if value is None else value).rstrip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def normalise_cause(cause: object) -> str | None:
    """A recognised cause, or None (= "logged but not yet categorised").

    Never raises: an unrecognised value must not cost us the mistake itself.
    Case and surrounding space are forgiven, so ``"Misread "`` matches.
    """
    if cause is None:
        return None
    text = str(cause).strip().lower()
    return text if text in MISTAKE_CAUSES else None


def coerce_confidence(value: object) -> int | None:
    """*value* as a rating in 1..4, or None when it is not one.

    None means "the user skipped the strip", which records nothing.
    """
    # bool is an int subclass; True is not a confidence rating.
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return None
    return rating if rating in CONFIDENCE_LEVELS else None


def _now(timestamp: float | None) -> float:
    return float(time.time() if timestamp is None else timestamp)


def make_mistake_entry(item_id: str, app: str, category: str = "",
                       question: str = "", your_answer: str = "",
                       correct_answer: str = "", cause: object = None,
                       note: str = "", timestamp: float | None = None,
                       resolved: bool = False) -> dict:
    """Build one mistake row in the suite-wide schema.  Pure: writes nothing.

    *app* is the **app directory name** ("qec-trainer"), which is what
    ``coach.py`` and ``dashboard.py`` group by; it is required rather than
    defaulted because a row with the wrong owner is written back by the wrong
    app's merge and is effectively lost.
    """
    return {
        "id":             str(item_id),
        "app":            str(app),
        "category":       clip_text(category),
        "question":       clip_text(question),
        "your_answer":    clip_text(your_answer),
        "correct_answer": clip_text(correct_answer),
        "cause":          normalise_cause(cause),
        "note":           clip_note(note),
        "timestamp":      _now(timestamp),
        "resolved":       bool(resolved),
    }


def make_confidence_entry(item_id: str, app: str, category: str = "",
                          confidence: object = 1, correct: bool = False,
                          timestamp: float | None = None) -> dict:
    """Build one calibration row.  Pure.  The rating is **clamped** to 1..4.

    Clamping here and rejecting in :func:`log_confidence` is deliberate: a row
    that exists is always schema-valid, and the decision not to record an
    absent rating belongs with the write, not with the builder.
    """
    rating = coerce_confidence(confidence)
    if rating is None:
        # Out of range but still a number: clamp it.  Anything else (None, a
        # word, an object) has no defensible rating, so record the floor.
        try:
            rating = max(1, min(4, int(confidence)))    # type: ignore[call-overload]
        except (TypeError, ValueError):
            rating = 1
    return {
        "id":         str(item_id),
        "app":        str(app),
        "category":   clip_text(category),
        "confidence": rating,
        "correct":    bool(correct),
        "timestamp":  _now(timestamp),
    }


# ---------------------------------------------------------------------------
# Foreign-row preservation
# ---------------------------------------------------------------------------

def row_app(row: object) -> str | None:
    """The ``app`` field of *row*, or None when it has no usable one."""
    if not isinstance(row, dict):
        return None
    app = row.get("app")
    if isinstance(app, str) and app.strip():
        return app.strip()
    return None


def is_foreign(row: object, app: str) -> bool:
    """True when *row* was written by a different app in the suite.

    A row with no ``app`` field is *not* foreign: the loaders claim it for
    themselves, so treating it as foreign would write it twice.
    """
    owner = row_app(row)
    return owner is not None and owner != app


def merge_foreign(disk_rows: list, entries: list, app: str) -> list:
    """The rows to write: *entries*, with foreign rows taken from *disk_rows*.

    ``entries`` is this app's view of the file, which may be stale and whose
    foreign rows may have been normalised through this app's schema on load.
    Every row in it that belongs to another app is swapped for the copy that
    is on disk right now — same keys, same values, unknown keys intact — and
    any foreign row that has appeared since (one this app has never seen) is
    kept as well.  Rows this app owns are written exactly as given: they are
    the caller's to normalise, trim or drop.

    Matching is by ``(app, id)``, consuming disk rows in order, so repeated
    ids map one-to-one and nothing is ever duplicated.  A foreign row that is
    not on disk at all (a test seeding one, say) is written as given.
    """
    pool: dict[tuple, list] = {}
    on_disk: list = []
    for row in disk_rows:
        if is_foreign(row, app):
            pool.setdefault((row_app(row), str(row.get("id"))), []).append(row)
            on_disk.append(row)

    out: list = []
    taken: set[int] = set()
    for row in entries:
        if not is_foreign(row, app):
            out.append(row)                       # ours, or unowned: as given
            continue
        bucket = pool.get((row_app(row), str(row.get("id"))))
        if bucket:
            current = bucket.pop(0)
            taken.add(id(current))
            out.append(current)                   # verbatim from disk
        else:
            out.append(row)                       # not on disk: keep the caller's
    out.extend(row for row in on_disk if id(row) not in taken)
    return out


def trim_own(rows: list, app: str, cap: int) -> list:
    """Drop *app*'s oldest rows until the file is back under *cap*.

    Only this app's rows are ever dropped.  The file is shared; trimming by a
    global timestamp order — as eight of the ten copies did — deletes other
    apps' history during our write.
    """
    excess = len(rows) - cap
    if excess <= 0:
        return rows
    mine = [i for i, row in enumerate(rows) if not is_foreign(row, app)]
    drop = set(mine[:excess])
    return [row for i, row in enumerate(rows) if i not in drop]


# ---------------------------------------------------------------------------
# Refused writes
# ---------------------------------------------------------------------------

_LAST_WRITE_ERROR: schema.SchemaError | None = None


def last_write_error() -> schema.SchemaError | None:
    """The most recent refused write, or None.

    :mod:`common.schema` refuses to overwrite a file written by a *newer*
    build.  The helpers below swallow that (a drill must not crash) and record
    it here, so a UI can say "your journal was written by a newer version of
    the suite and is not being updated" instead of losing writes in silence.
    """
    return _LAST_WRITE_ERROR


def clear_write_error() -> None:
    """Forget the last refused write."""
    global _LAST_WRITE_ERROR
    _LAST_WRITE_ERROR = None


def _save(path, rows: list, kind: str) -> bool:
    """``schema.save_versioned`` that reports refusal instead of raising."""
    global _LAST_WRITE_ERROR
    try:
        schema.save_versioned(path, rows, kind)
    except schema.SchemaTooNewError as exc:
        _LAST_WRITE_ERROR = exc
        return False
    return True


# ---------------------------------------------------------------------------
# Mistake journal
# ---------------------------------------------------------------------------

def mistakes_path():
    """Path of ``mistakes.json``, resolved now (honours the env override)."""
    return datadir.mistakes_file()


def confidence_path():
    """Path of ``confidence.json``, resolved now."""
    return datadir.confidence_file()


def load_mistakes(app: str | None = None) -> list[dict]:
    """Every mistake row (all apps unless *app* is given), oldest first.

    Never raises: a missing or corrupt file reads as ``[]``.
    """
    rows = [r for r in schema.load_versioned(mistakes_path(), "mistakes")
            if isinstance(r, dict)]
    if app is None:
        return rows
    return [r for r in rows if r.get("app") == app]


def save_mistakes(entries: list[dict], app: str) -> bool:
    """Rewrite the journal for owning *app*.  Returns False if it was refused.

    Locked, foreign rows preserved verbatim, this app's oldest rows trimmed to
    :data:`MISTAKES_MAX`, written atomically, sidecar stamped.  Re-entrant:
    the mutators below call it from inside their own lock.
    """
    with lock(mistakes_path(), create=True):
        path = mistakes_path()
        rows = merge_foreign(read_json_list(path), list(entries), app)
        return _save(path, trim_own(rows, app, MISTAKES_MAX), "mistakes")


def log_mistake(entry: dict) -> dict:
    """Append one prepared mistake row (from :func:`make_mistake_entry`).

    Repeats are **kept, not merged**: three slips on the same item are three
    rows, which is the signal ``coach --mistakes`` counts.  Returns the row as
    stored (the same dict), whether or not the write was refused — check
    :func:`last_write_error` if you need to know.
    """
    app = row_app(entry) or ""
    with lock(mistakes_path(), create=True):
        rows = load_mistakes()               # read inside the lock: never stale
        rows.append(entry)
        save_mistakes(rows, app)
    return entry


def set_mistake_cause(item_id: str, cause: object, note: str | None = None,
                      *, app: str) -> dict | None:
    """Categorise this app's most recent row for *item_id*.

    Targets the newest **unresolved** row, falling back to the newest row of
    any state, so re-categorising an item that was later answered correctly
    edits one row instead of piling up duplicates.

    ``note=None`` (the default) leaves the existing note alone; ``note=""``
    clears it.  Returns the updated row, or None when there is nothing to
    update.

    *app* is keyword-only and has no default on purpose: a missing owner would
    match no row and silently do nothing.
    """
    with lock(mistakes_path()):
        rows = load_mistakes()               # read inside the lock: never stale
        matches = [i for i, r in enumerate(rows)
                   if r.get("app") == app and str(r.get("id")) == str(item_id)]
        if not matches:
            return None
        open_matches = [i for i in matches if not rows[i].get("resolved")]
        idx = (open_matches or matches)[-1]
        rows[idx]["cause"] = normalise_cause(cause)
        if note is not None:
            rows[idx]["note"] = clip_note(note)
        save_mistakes(rows, app)
        return rows[idx]


def resolve_mistakes(item_id: str, app: str) -> int:
    """Mark every open row for *app* + *item_id* resolved.  Returns the count.

    Called when the learner finally gets the item right: the mistake stays in
    the journal (it happened) but drops out of the open-mistakes report.
    """
    with lock(mistakes_path()):
        rows = load_mistakes()               # read inside the lock: never stale
        changed = 0
        for row in rows:
            if (row.get("app") == app and str(row.get("id")) == str(item_id)
                    and not row.get("resolved")):
                row["resolved"] = True
                changed += 1
        if changed:
            save_mistakes(rows, app)
        return changed


def open_mistakes(app: str | None = None) -> list[dict]:
    """Unresolved rows, newest first; *app* None means the whole suite."""
    rows = [r for r in load_mistakes(app) if not r.get("resolved")]
    return sorted(rows, key=lambda r: r.get("timestamp") or 0.0, reverse=True)


def mistakes_for(item_id: str, app: str | None = None) -> list[dict]:
    """Every row for one item id, oldest first."""
    return [r for r in load_mistakes(app) if str(r.get("id")) == str(item_id)]


def cause_counts(app: str | None = None, *, include_resolved: bool = True,
                 include_uncategorised: bool = True,
                 entries: list[dict] | None = None) -> dict[str, int]:
    """Tally of causes — the payload of the journal.

    Uncategorised rows are counted under :data:`UNCATEGORISED` unless
    *include_uncategorised* is False.  Pass *entries* to count a list you
    already have instead of re-reading the file.
    """
    rows = load_mistakes(app) if entries is None else entries
    counts: dict[str, int] = {}
    for row in rows:
        if app is not None and entries is not None and row.get("app") != app:
            continue
        if not include_resolved and row.get("resolved"):
            continue
        key = normalise_cause(row.get("cause"))
        if key is None:
            if not include_uncategorised:
                continue
            key = UNCATEGORISED
        counts[key] = counts.get(key, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Confidence calibration
# ---------------------------------------------------------------------------

def load_confidence(app: str | None = None) -> list[dict]:
    """Every calibration row (all apps unless *app* is given), oldest first."""
    rows = [r for r in schema.load_versioned(confidence_path(), "confidence")
            if isinstance(r, dict)]
    if app is None:
        return rows
    return [r for r in rows if r.get("app") == app]


def save_confidence(entries: list[dict], app: str) -> bool:
    """Rewrite the calibration log for owning *app*.  Same contract as
    :func:`save_mistakes`."""
    with lock(confidence_path(), create=True):
        path = confidence_path()
        rows = merge_foreign(read_json_list(path), list(entries), app)
        return _save(path, trim_own(rows, app, CONFIDENCE_MAX), "confidence")


def log_confidence(item_id: str, app: str, category: str = "",
                   confidence: object = None, correct: bool = False,
                   timestamp: float | None = None) -> dict | None:
    """Record one (pre-answer confidence, graded outcome) pair.

    A rating outside 1..4 — including None, meaning "the user skipped the
    strip" — records **nothing** and returns None.  Clamping it, as one copy
    did, invents a rating the learner never gave and then reports on it.
    """
    if coerce_confidence(confidence) is None:
        return None
    entry = make_confidence_entry(item_id, app, category, confidence, correct,
                                  timestamp)
    with lock(confidence_path(), create=True):
        rows = load_confidence()             # read inside the lock: never stale
        rows.append(entry)
        save_confidence(rows, app)
    return entry


def calibration_summary(app: str | None = None,
                        entries: list[dict] | None = None
                        ) -> dict[int, dict[str, int]]:
    """``{rating: {"total": n, "correct": c}}`` for the ratings that have data.

    Rating 4 with a poor ``correct/total`` ratio is the confidently-wrong
    signal the whole feature exists for.
    """
    rows = load_confidence(app) if entries is None else entries
    out: dict[int, dict[str, int]] = {}
    for row in rows:
        if app is not None and entries is not None and row.get("app") != app:
            continue
        rating = coerce_confidence(row.get("confidence"))
        if rating is None:
            continue
        bucket = out.setdefault(rating, {"total": 0, "correct": 0})
        bucket["total"] += 1
        if row.get("correct"):
            bucket["correct"] += 1
    return dict(sorted(out.items()))


def confidently_wrong(app: str | None = None, *,
                      min_confidence: int = CONFIDENT_LEVEL,
                      entries: list[dict] | None = None) -> list[dict]:
    """Rows rated *min_confidence* or higher that turned out wrong.

    The unknown unknowns: the learner was sure and was not right.
    """
    rows = load_confidence(app) if entries is None else entries
    out: list[dict] = []
    for row in rows:
        if app is not None and entries is not None and row.get("app") != app:
            continue
        rating = coerce_confidence(row.get("confidence"))
        if rating is not None and rating >= min_confidence and not row.get("correct"):
            out.append(row)
    return out


def confidently_wrong_by_category(app: str | None = None, *,
                                  min_confidence: int = CONFIDENT_LEVEL
                                  ) -> dict[str, int]:
    """Per-category count of "sure and wrong" — where to study next."""
    counts: dict[str, int] = {}
    for row in confidently_wrong(app, min_confidence=min_confidence):
        key = str(row.get("category") or "")
        counts[key] = counts.get(key, 0) + 1
    return counts


__all__ = [
    "MISTAKE_CAUSES", "CAUSE_LABELS", "UNCATEGORISED",
    "CONFIDENCE_LEVELS", "CONFIDENCE_LABELS", "CONFIDENT_LEVEL",
    "TEXT_MAX", "NOTE_MAX", "MISTAKES_MAX", "CONFIDENCE_MAX",
    "MISTAKE_KEYS", "CONFIDENCE_KEYS",
    "clip_text", "clip_note", "normalise_cause", "coerce_confidence",
    "make_mistake_entry", "make_confidence_entry",
    "row_app", "is_foreign", "merge_foreign", "trim_own",
    "last_write_error", "clear_write_error",
    "mistakes_path", "confidence_path",
    "load_mistakes", "save_mistakes", "log_mistake", "set_mistake_cause",
    "resolve_mistakes", "open_mistakes", "mistakes_for", "cause_counts",
    "load_confidence", "save_confidence", "log_confidence",
    "calibration_summary", "confidently_wrong", "confidently_wrong_by_category",
    "lock",
]
