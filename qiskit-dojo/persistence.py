"""Persistence for qiskit-dojo.

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

Both analytics files are written atomically (temp file in the same directory
+ os.replace) and are capped at MAX_MISTAKES / MAX_CONFIDENCE rows, oldest
dropped first, so a decade of study cannot grow them without bound.  A
missing or corrupt file always reads as empty rather than raising.
"""
from __future__ import annotations
import json
import os
import tempfile
import time
from pathlib import Path
import journal_sync
from config import (
    HISTORY_FILE, DATA_DIR, FLAGGED_FILE, APP_DIR_NAME,
    MISTAKES_FILE, CONFIDENCE_FILE, SETTINGS_FILE,
)
from core.models import Kata, SessionStats


def _load_raw() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []


def save_session(stats: SessionStats) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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
    HISTORY_FILE.write_text(json.dumps(sessions, indent=2))


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
# Flag for review (dojo_flagged.json)
# ---------------------------------------------------------------------------

def load_flagged() -> list[dict]:
    """Flagged katas, oldest first.  A missing or corrupt file reads as empty."""
    if not FLAGGED_FILE.exists():
        return []
    try:
        data = json.loads(FLAGGED_FILE.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and e.get("id")]


def _save_flagged(entries: list[dict]) -> None:
    FLAGGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAGGED_FILE.write_text(json.dumps(entries, indent=2))


def flagged_ids() -> set[str]:
    return {str(e["id"]) for e in load_flagged()}


def is_flagged(kata_id: str) -> bool:
    return kata_id in flagged_ids()


def toggle_flag(kata: Kata) -> bool:
    """Flag `kata` for review, or unflag it if already flagged.

    Returns the new state (True = now flagged).
    """
    entries = load_flagged()
    if any(e.get("id") == kata.id for e in entries):
        _save_flagged([e for e in entries if e.get("id") != kata.id])
        return False
    entries.append({
        "id":        kata.id,
        "label":     kata.title,
        "category":  kata.section,
        "app":       APP_DIR_NAME,
        "timestamp": time.time(),
    })
    _save_flagged(entries)
    return True


def unflag(kata_id: str) -> None:
    """Remove a kata from the flagged list (no-op if it is not flagged)."""
    entries = load_flagged()
    remaining = [e for e in entries if e.get("id") != kata_id]
    if len(remaining) != len(entries):
        _save_flagged(remaining)


# ---------------------------------------------------------------------------
# Shared analytics files: mistake journal + confidence calibration
#
# Both are suite-wide (every app writes into the same mistakes.json /
# confidence.json), so every mutator here rewrites only the rows whose "app"
# is this app and passes every foreign row through untouched.
# ---------------------------------------------------------------------------

#: Cause taxonomy for the mistake journal.  ``None`` means "logged, not yet
#: categorised" — the entry still counts, it just has no diagnosis.
MISTAKE_CAUSES: tuple[str, ...] = (
    "misread",
    "didnt_know",
    "knew_but_slipped",
    "confused",
    "out_of_time",
    "other",
)

#: Human labels for the cause buttons (kept next to the taxonomy so the UI
#: and the journal can never drift apart).
CAUSE_LABELS: dict[str, str] = {
    "misread":          "Misread the task",
    "didnt_know":       "Didn't know it",
    "knew_but_slipped": "Knew it, slipped",
    "confused":         "Confused two APIs",
    "out_of_time":      "Ran out of patience",
    "other":            "Other",
}

#: Confidence levels asked before the first Run.
CONFIDENCE_LABELS: dict[int, str] = {
    1: "Guessing",
    2: "Unsure",
    3: "Fairly sure",
    4: "Certain",
}

FIELD_LIMIT    = 200        # question / your_answer / correct_answer / note
MAX_MISTAKES   = 2000       # oldest rows are dropped past this
MAX_CONFIDENCE = 5000


def clip(text: object, limit: int = FIELD_LIMIT) -> str:
    """Collapse whitespace and trim to `limit` characters (ellipsis included).

    Journal fields are meant to be scannable one-liners, so embedded newlines
    and runs of spaces are squashed rather than stored verbatim.
    """
    s = " ".join(str(text if text is not None else "").split())
    if len(s) <= limit:
        return s
    return s[: max(0, limit - 1)].rstrip() + "…"


def _atomic_write_json(path: Path, payload) -> None:
    """Write `payload` as JSON to `path` via temp file + os.replace.

    A crash mid-write leaves the previous file intact instead of a truncated
    one, and readers never observe a half-written list.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp",
                               dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_json_dicts(path: Path) -> list[dict]:
    """Every dict row in the JSON list at `path`; [] if missing or corrupt."""
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


# ------------------------------------------------------------ mistake journal

def make_mistake_entry(kata_id: str, category: str, question: str,
                       your_answer: str, correct_answer: str,
                       cause: str | None = None, note: str = "",
                       timestamp: float | None = None,
                       resolved: bool = False) -> dict:
    """A journal row in the documented shape.  Pure — touches no disk."""
    return {
        "id":             str(kata_id),
        "app":            APP_DIR_NAME,
        "category":       str(category or ""),
        "question":       clip(question),
        "your_answer":    clip(your_answer),
        "correct_answer": clip(correct_answer),
        "cause":          cause if cause in MISTAKE_CAUSES else None,
        "note":           clip(note),
        "timestamp":      float(timestamp) if timestamp is not None else time.time(),
        "resolved":       bool(resolved),
    }


def load_mistakes() -> list[dict]:
    """Every journal row on disk (all apps), oldest first."""
    return [row for row in _load_json_dicts(MISTAKES_FILE) if row.get("id")]


def mistakes_for_app(app: str = APP_DIR_NAME) -> list[dict]:
    """Journal rows written by `app` (this app by default)."""
    return [row for row in load_mistakes() if row.get("app") == app]


def _save_mistakes(rows: list[dict]) -> None:
    """Rewrite the shared journal under its lock.

    mistakes.json is written by all ten apps, so this does two things a plain
    replace cannot: it holds journal_sync.lock() across the whole
    read-modify-write (an unlocked one reads a stale list and silently drops
    rows another app appended in between), and it writes every row owned by
    another app back exactly as it is on disk, unknown keys included.
    """
    with journal_sync.lock(MISTAKES_FILE, create=True):
        merged = journal_sync.merge_foreign(_load_json_dicts(MISTAKES_FILE),
                                            rows, APP_DIR_NAME)
        _atomic_write_json(MISTAKES_FILE, merged[-MAX_MISTAKES:])


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
    """
    with journal_sync.lock(MISTAKES_FILE, create=True):
        return _log_mistake_locked(entry)


def _log_mistake_locked(entry: dict) -> dict:
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
    _save_mistakes(rows)
    return stored


def set_mistake_cause(kata_id: str, cause: str | None,
                      note: str | None = None) -> bool:
    """Categorise this kata's open journal row.  True if a row was updated.

    `cause` outside MISTAKE_CAUSES clears the diagnosis back to None;
    `note=None` leaves any existing note alone.
    """
    with journal_sync.lock(MISTAKES_FILE):
        rows = load_mistakes()       # read inside the lock: never stale
        idx = _open_index(rows, kata_id)
        if idx < 0:
            return False
        row = dict(rows[idx])
        row["cause"] = cause if cause in MISTAKE_CAUSES else None
        if note is not None:
            row["note"] = clip(note)
        rows[idx] = row
        _save_mistakes(rows)
        return True


def resolve_mistakes(kata_id: str) -> int:
    """Mark this app's rows for `kata_id` resolved.  Returns how many changed."""
    with journal_sync.lock(MISTAKES_FILE):
        rows = load_mistakes()       # read inside the lock: never stale
        changed = 0
        for i, row in enumerate(rows):
            if (row.get("app") == APP_DIR_NAME and str(row.get("id")) == str(kata_id)
                    and not row.get("resolved")):
                updated = dict(row)
                updated["resolved"] = True
                rows[i] = updated
                changed += 1
        if changed:
            _save_mistakes(rows)
        return changed


def mistake_cause_counts(unresolved_only: bool = True,
                         app: str | None = APP_DIR_NAME) -> dict[str, int]:
    """How many journal rows fall under each cause — the point of the journal.

    Uncategorised rows are counted under the key ``""``.  `app=None` counts
    the whole suite.
    """
    counts: dict[str, int] = {}
    for row in load_mistakes():
        if app is not None and row.get("app") != app:
            continue
        if unresolved_only and row.get("resolved"):
            continue
        cause = row.get("cause")
        key = cause if cause in MISTAKE_CAUSES else ""
        counts[key] = counts.get(key, 0) + 1
    return counts


# ------------------------------------------------------ confidence calibration

def make_confidence_entry(kata_id: str, category: str, confidence: int,
                          correct: bool,
                          timestamp: float | None = None) -> dict:
    """A calibration row in the documented shape.  Pure — touches no disk."""
    try:
        level = int(confidence)
    except (TypeError, ValueError):
        level = 1
    level = min(4, max(1, level))
    return {
        "id":         str(kata_id),
        "app":        APP_DIR_NAME,
        "category":   str(category or ""),
        "confidence": level,
        "correct":    bool(correct),
        "timestamp":  float(timestamp) if timestamp is not None else time.time(),
    }


def load_confidence() -> list[dict]:
    """Every calibration row on disk (all apps), oldest first."""
    return [row for row in _load_json_dicts(CONFIDENCE_FILE) if row.get("id")]


def confidence_for_app(app: str = APP_DIR_NAME) -> list[dict]:
    return [row for row in load_confidence() if row.get("app") == app]


def log_confidence(kata_id: str, category: str, confidence: int,
                   correct: bool) -> dict:
    """Append one confidence/outcome pairing.  Returns the row as stored."""
    entry = make_confidence_entry(kata_id, category, confidence, correct)
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        rows = load_confidence()     # read inside the lock: never stale
        rows.append(entry)
        merged = journal_sync.merge_foreign(_load_json_dicts(CONFIDENCE_FILE),
                                            rows, APP_DIR_NAME)
        _atomic_write_json(CONFIDENCE_FILE, merged[-MAX_CONFIDENCE:])
    return entry


def calibration_summary(app: str | None = APP_DIR_NAME) -> dict[int, dict[str, int]]:
    """{level: {"total": n, "correct": n}} for levels 1-4 that have data."""
    out: dict[int, dict[str, int]] = {}
    for row in load_confidence():
        if app is not None and row.get("app") != app:
            continue
        try:
            level = int(row.get("confidence"))
        except (TypeError, ValueError):
            continue
        if level not in (1, 2, 3, 4):
            continue
        bucket = out.setdefault(level, {"total": 0, "correct": 0})
        bucket["total"] += 1
        if row.get("correct"):
            bucket["correct"] += 1
    return out


def confidently_wrong(app: str | None = APP_DIR_NAME,
                      threshold: int = 3) -> list[dict]:
    """Rows rated `threshold`+ that turned out wrong — the unknown unknowns."""
    out = []
    for row in load_confidence():
        if app is not None and row.get("app") != app:
            continue
        try:
            level = int(row.get("confidence"))
        except (TypeError, ValueError):
            continue
        if level >= threshold and not row.get("correct"):
            out.append(row)
    return out


# -------------------------------------------------------------- app settings

def load_settings() -> dict:
    """App-local UI preferences; {} if missing or corrupt."""
    try:
        if not SETTINGS_FILE.exists():
            return {}
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> None:
    _atomic_write_json(SETTINGS_FILE, dict(settings))


def confidence_prompt_enabled() -> bool:
    """Whether to offer the pre-run confidence strip (default: yes)."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
