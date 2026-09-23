"""The flag-for-review store — ``<prefix>_flagged.json``.

One file per app (``quiz_flagged.json``, ``qec_flagged.json``, …), all of the
same shape, all read by ``coach.py``'s review queue::

    [ {"id": str, "label": str, "category": str, "app": str,
       "timestamp": float}, … ]

``id``         stable identity of the flagged item (a bank id, or a hash of a
               generated question — generated items have no other identity).
``label``      one line shown in the review list, whitespace-collapsed and
               truncated; the *only* text persisted, so a long question cannot
               be recovered in full from the flag alone.
``category``   the app's own grouping (subject, section, chapter, paper title).
``app``        the app directory name, so one queue can merge ten files.
``timestamp``  epoch seconds; ``coach.py`` orders the queue by it.

Flagging is a **toggle**: flagging an already-flagged item unflags it.

Reconciled divergences
======================
* **Shape.**  Seven apps store the list of objects above; three
  (flashcard-drill's ``flagged_cards.json``, ``qec_flagged.json``,
  ``vqa_flagged.json``) store a bare ``["id", "id"]`` list.  ``coach.py``
  parses both and calls the bare form legacy, so this module **reads** both
  and **writes** the object form, upgrading a legacy file the first time it is
  written.  :func:`load_flagged` returns objects either way, so callers never
  branch.  (A bare id carries no label, category or time; the upgrade fills
  ``label`` from the id, ``category`` with ``""`` and ``timestamp`` with 0.0 —
  0.0 rather than "now" so a ten-month-old flag does not jump to the top of
  the review queue on the day the file is rewritten.)
* **Unparseable rows.**  Five copies rewrote the file from the *filtered* list,
  which deleted rows they did not understand — including another app's, if a
  file were ever shared.  **Kept:** the raw list is the basis of every
  rewrite, exactly as quantum-quiz did it, so an unknown row survives.
* **Atomicity.**  Four copies used a plain ``write_text``, which truncates the
  file before writing: a crash mid-write lost every flag. **Kept:** the atomic
  temp-file + ``os.replace`` write the other six used.
* **Locking.**  A per-app file is not contended the way ``mistakes.json`` is —
  but two windows of the *same* app are, and ``launch.py`` invites that.  The
  rewrite is taken under the same advisory lock; it costs microseconds.
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

from common import schema
from common.jsonio import read_json_list
from common.locking import lock

#: Default cap for :func:`make_label`.
LABEL_MAX = 80


def make_label(text: object, limit: int = LABEL_MAX) -> str:
    """Collapse *text* to one line and truncate it with an ellipsis."""
    flat = " ".join(str("" if text is None else text).split())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1].rstrip() + "…"


def make_id(*parts: object, prefix: str = "") -> str:
    """A stable id for an item that has no natural one.

    Generated questions exist only for as long as the session that made them,
    so the only durable identity they have is a hash of their text.  Parts are
    whitespace-normalised first, so re-pasting the same paper with different
    spacing still matches.
    """
    key = "\n".join(" ".join(str(p).split()) for p in parts)
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}" if prefix else digest


def _normalise(row: object, app: str) -> dict | None:
    """One stored row coerced to the contract shape, or None if unusable."""
    if isinstance(row, str) and row.strip():           # legacy bare-id file
        ident = row.strip()
        return {"id": ident, "label": ident, "category": "", "app": app,
                "timestamp": 0.0}
    if isinstance(row, dict):
        # Three id keys: the contract's "id", plus the two an app's own store
        # used before the contract existed.
        key = row.get("id") or row.get("problem_id") or row.get("question_id")
        if not key:
            return None
        ident = str(key)
        ts = row.get("timestamp", 0.0)
        return {
            "id":        ident,
            "label":     str(row.get("label") or ident),
            "category":  str(row.get("category") or ""),
            "app":       str(row.get("app") or app),
            "timestamp": float(ts) if isinstance(ts, (int, float)) and not isinstance(ts, bool) else 0.0,
        }
    return None


def _matches(row: object, flag_id: str) -> bool:
    if isinstance(row, str):
        return row.strip() == flag_id
    return isinstance(row, dict) and str(row.get("id")) == flag_id


def load_raw(path) -> list:
    """The file's top-level list exactly as stored (legacy shapes included)."""
    return read_json_list(path)


def load_flagged(path, app: str) -> list[dict]:
    """Flagged entries in the contract shape, oldest first.

    Tolerates a missing, corrupt, legacy-shaped or partly-broken file: rows
    that cannot be understood are skipped here but are **not** removed from
    the file (see :func:`save_flagged`).
    """
    out: list[dict] = []
    for row in load_raw(path):
        entry = _normalise(row, app)
        if entry is not None:
            out.append(entry)
    return out


def flagged_ids(path, app: str = "") -> set[str]:
    """Just the ids — what a screen needs to draw the flag glyph."""
    return {e["id"] for e in load_flagged(path, app)}


def is_flagged(path, flag_id: str, app: str = "") -> bool:
    """True when *flag_id* is in the file."""
    return any(_matches(row, str(flag_id)) for row in load_raw(path))


def save_flagged(path, rows: list, app: str) -> bool:
    """Rewrite the file atomically, under the lock, with a version stamp.

    *rows* may mix contract-shaped dicts and legacy bare ids; everything is
    normalised to the contract shape on the way out, which is how a legacy
    file upgrades itself.  Returns False when the write was refused because
    the file was written by a newer build.
    """
    normalised = [e for e in (_normalise(r, app) for r in rows) if e is not None]
    with lock(path, create=True):
        try:
            schema.save_versioned(path, normalised, "flagged")
        except schema.SchemaTooNewError:
            return False
    return True


def toggle_flag(path, flag_id: str, label: str = "", category: str = "", *,
                app: str) -> bool:
    """Flag the item, or unflag it if it is already flagged.

    Returns the **new** state (True = now flagged).  The whole read-modify-
    write is under the lock, so two windows of the same app cannot each decide
    "not flagged yet" and write conflicting files.
    """
    flag_id = str(flag_id)
    with lock(path, create=True):
        raw = load_raw(path)
        if any(_matches(row, flag_id) for row in raw):
            save_flagged(path, [r for r in raw if not _matches(r, flag_id)], app)
            return False
        raw.append({
            "id":        flag_id,
            "label":     make_label(label or flag_id),
            "category":  str(category or ""),
            "app":       app,
            "timestamp": time.time(),
        })
        save_flagged(path, raw, app)
        return True


def unflag(path, flag_id: str, *, app: str) -> bool:
    """Remove one entry.  Returns True when something was removed."""
    flag_id = str(flag_id)
    with lock(path):
        raw = load_raw(path)
        remaining = [r for r in raw if not _matches(r, flag_id)]
        if len(remaining) == len(raw):
            return False
        save_flagged(path, remaining, app)
        return True


def flag(path, flag_id: str, label: str = "", category: str = "", *,
         app: str) -> bool:
    """Flag the item if it is not flagged.  Returns True when it was added."""
    flag_id = str(flag_id)
    with lock(path, create=True):
        raw = load_raw(path)
        if any(_matches(row, flag_id) for row in raw):
            return False
        raw.append({
            "id":        flag_id,
            "label":     make_label(label or flag_id),
            "category":  str(category or ""),
            "app":       app,
            "timestamp": time.time(),
        })
        save_flagged(path, raw, app)
        return True


def flagged_path(app: str) -> Path:
    """The flagged file for *app*, resolved now (honours the env override)."""
    from common import datadir                     # local: keeps the cycle out
    return datadir.app_file(app, "flagged")


__all__ = [
    "LABEL_MAX", "make_label", "make_id",
    "load_raw", "load_flagged", "flagged_ids", "is_flagged",
    "save_flagged", "toggle_flag", "flag", "unflag", "flagged_path",
]
