"""Persistence for problem-trainer sessions and review flags.

Both files live in the shared suite data directory,
~/.local/share/quantum-study/ by default; setting QUANTUM_STUDY_DATA_DIR
relocates them (see config.DATA_DIR).

Schema (consumed by the suite coach — do not change):
~/.local/share/quantum-study/problems_history.json:
[
  {
    "timestamp": epoch float,
    "total": int,
    "avg_score": float (0-10 scale),
    "attempts": [
      {"problem_id": str, "kind": "problem"|"derivation", "score": float}
    ]
  },
  ...
]

Review flags (suite-wide flagging contract; toggle semantics):
~/.local/share/quantum-study/problems_flagged.json:
[
  {
    "id": str,            # problem or derivation id
    "label": str,         # short human title
    "category": str,      # problem topic, or "derivation"
    "app": "problem-trainer",
    "timestamp": epoch float
  },
  ...
]

Two further files are suite-wide and shared with the other study apps (every
entry carries an "app" field, so writes here never disturb another app's rows):
~/.local/share/quantum-study/mistakes.json    — the mistake journal
~/.local/share/quantum-study/confidence.json  — confidence calibration
plus this app's own small preference file, problems_settings.json.  Their
schemas are documented above each section below.  All writes go through
_atomic_write_json (temp file + os.replace), and every reader tolerates a
missing or corrupt file by starting fresh.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
import journal_sync
from config import (
    HISTORY_FILE, DATA_DIR, FLAGGED_FILE,
    MISTAKES_FILE, CONFIDENCE_FILE, SETTINGS_FILE,
)
from core.models import SessionStats

APP_NAME_KEY = "problem-trainer"     # value of the "app" field in flag entries

# Growth caps for the two shared analytics files.  They are append-only logs
# written by ten apps, so they are trimmed to the newest N entries on write
# (oldest first is dropped); the caps are generous enough that a normal study
# history is never touched.
MAX_MISTAKES   = 2000
MAX_CONFIDENCE = 5000

MISTAKE_CAUSES = (
    "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other",
)
TEXT_FIELD_MAX = 200                 # question / your_answer / correct_answer cap


def _atomic_write_json(path: Path, payload) -> None:
    """Write JSON to `path` via a temp file + os.replace (never a partial file)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    os.replace(tmp, path)


def _load_json_list(path: Path) -> list:
    """The JSON list stored at `path`; [] when missing, corrupt or not a list."""
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text())
    except Exception:
        return []
    return data if isinstance(data, list) else []


def _clip(value, limit: int = TEXT_FIELD_MAX) -> str:
    """Coerce to str and clip to `limit` characters (ellipsis marks the cut)."""
    text = "" if value is None else str(value)
    return text if len(text) <= limit else text[: limit - 1] + "\u2026"


def _load_raw() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def load_history() -> list[dict]:
    return _load_raw()


def save_session(stats: SessionStats) -> None:
    if stats.total == 0:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sessions = _load_raw()
    sessions.append({
        "timestamp": time.time(),
        "total":     stats.total,
        "avg_score": round(stats.avg_score, 2),
        "attempts": [
            {
                "problem_id": a.problem_id,
                "kind":       a.kind,
                "score":      round(float(a.score), 2),
            }
            for a in stats.attempts
        ],
    })
    _atomic_write_json(HISTORY_FILE, sessions)


# ---------------------------------------------------------------------------
# Review flags
# ---------------------------------------------------------------------------

def _normalize_flag(entry) -> dict | None:
    """Coerce one stored entry to the contract schema; None if unusable."""
    if isinstance(entry, str) and entry.strip():
        return {"id": entry.strip(), "label": entry.strip(), "category": "",
                "app": APP_NAME_KEY, "timestamp": 0.0}
    if isinstance(entry, dict):
        ident = entry.get("id") or entry.get("problem_id")
        if not ident:
            return None
        ts = entry.get("timestamp", 0.0)
        return {
            "id":        str(ident),
            "label":     str(entry.get("label") or ident),
            "category":  str(entry.get("category") or ""),
            "app":       str(entry.get("app") or APP_NAME_KEY),
            "timestamp": float(ts) if isinstance(ts, (int, float)) else 0.0,
        }
    return None


def load_flagged() -> list[dict]:
    """All flag entries (oldest first), each normalized to the contract schema."""
    if not FLAGGED_FILE.exists():
        return []
    try:
        data = json.loads(FLAGGED_FILE.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    out: list[dict] = []
    for e in data:
        n = _normalize_flag(e)
        if n is not None:
            out.append(n)
    return out


def save_flagged(entries: list[dict]) -> None:
    _atomic_write_json(FLAGGED_FILE, entries)


def flagged_ids() -> set[str]:
    return {e["id"] for e in load_flagged()}


def is_flagged(item_id: str) -> bool:
    return item_id in flagged_ids()


def toggle_flag(item_id: str, label: str = "", category: str = "") -> bool:
    """Flag `item_id` for review, or unflag it if already flagged.

    Returns the new state (True = now flagged).
    """
    entries = load_flagged()
    remaining = [e for e in entries if e["id"] != item_id]
    if len(remaining) != len(entries):
        save_flagged(remaining)
        return False
    entries.append({
        "id":        item_id,
        "label":     label or item_id,
        "category":  category,
        "app":       APP_NAME_KEY,
        "timestamp": time.time(),
    })
    save_flagged(entries)
    return True


def unflag(item_id: str) -> None:
    entries = load_flagged()
    remaining = [e for e in entries if e["id"] != item_id]
    if len(remaining) != len(entries):
        save_flagged(remaining)


# ---------------------------------------------------------------------------
# Mistake journal  —  <data dir>/mistakes.json  (suite-wide, shared by all apps)
# ---------------------------------------------------------------------------
# [
#   {
#     "id": str,              # stable item id: "<problem_id>:<part_id>" or
#                             #                 "<derivation_id>:<step_id>"
#     "app": "problem-trainer",
#     "category": str,        # problem topic, or "derivation"
#     "question": str,        # <= 200 chars
#     "your_answer": str,     # <= 200 chars
#     "correct_answer": str,  # <= 200 chars
#     "cause": str|None,      # one of MISTAKE_CAUSES, or None = not categorised
#     "note": str,
#     "timestamp": float,     # epoch
#     "resolved": bool        # True once the same item is answered correctly
#   },
#   ...
# ]
# A wrong answer is only a bookmark; the cause is the payload — "nine
# little-endian slips this month" is the signal worth acting on.

MISTAKE_KEYS = ("id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved")


def normalize_cause(cause) -> str | None:
    """A valid cause string, or None (unknown/blank causes become None)."""
    if isinstance(cause, str) and cause in MISTAKE_CAUSES:
        return cause
    return None


def make_mistake_entry(item_id: str, category: str = "", question: str = "",
                       your_answer: str = "", correct_answer: str = "",
                       cause: str | None = None, note: str = "",
                       timestamp: float | None = None,
                       resolved: bool = False,
                       app: str = APP_NAME_KEY) -> dict:
    """One mistake-journal entry in contract order, with every field coerced."""
    return {
        "id":             str(item_id),
        "app":            str(app),
        "category":       str(category or ""),
        "question":       _clip(question),
        "your_answer":    _clip(your_answer),
        "correct_answer": _clip(correct_answer),
        "cause":          normalize_cause(cause),
        "note":           _clip(note),
        "timestamp":      float(timestamp if timestamp is not None else time.time()),
        "resolved":       bool(resolved),
    }


def _normalize_mistake(entry) -> dict | None:
    """Coerce a stored entry to the contract schema; None if unusable."""
    if not isinstance(entry, dict):
        return None
    ident = entry.get("id")
    if not ident:
        return None
    ts = entry.get("timestamp", 0.0)
    return make_mistake_entry(
        item_id=ident,
        category=entry.get("category", ""),
        question=entry.get("question", ""),
        your_answer=entry.get("your_answer", ""),
        correct_answer=entry.get("correct_answer", ""),
        cause=entry.get("cause"),
        note=entry.get("note", ""),
        timestamp=float(ts) if isinstance(ts, (int, float)) else 0.0,
        resolved=bool(entry.get("resolved", False)),
        app=entry.get("app") or APP_NAME_KEY,
    )


def load_mistakes() -> list[dict]:
    """Every mistake entry (all apps), oldest first, normalized to the schema."""
    out: list[dict] = []
    for raw in _load_json_list(MISTAKES_FILE):
        norm = _normalize_mistake(raw)
        if norm is not None:
            out.append(norm)
    return out


def save_mistakes(entries: list[dict]) -> None:
    """Rewrite the journal atomically, keeping only the newest MAX_MISTAKES.

    mistakes.json is shared with the other nine apps, which has two
    consequences this function has to honour:

    * the whole read-merge-write runs under journal_sync.lock() — unlocked, the
      list in *entries* goes stale the moment another app appends to the file
      and this write would silently drop that app's new rows;
    * only OUR rows come from *entries*.  :func:`load_mistakes` normalises every
      row it reads through this app's schema, so a foreign row in *entries* has
      already lost any key this app does not know about; the copy on disk is
      written back instead, byte for byte.
    """
    with journal_sync.lock(MISTAKES_FILE, create=True):
        rows = journal_sync.merge_foreign(_load_json_list(MISTAKES_FILE),
                                          list(entries), APP_NAME_KEY)
        _atomic_write_json(MISTAKES_FILE, rows[-MAX_MISTAKES:])


def app_mistakes(app: str = APP_NAME_KEY) -> list[dict]:
    return [e for e in load_mistakes() if e["app"] == app]


def find_mistake(item_id: str, app: str = APP_NAME_KEY) -> dict | None:
    """The newest entry for this app+id, or None."""
    matches = [e for e in load_mistakes() if e["app"] == app and e["id"] == item_id]
    return matches[-1] if matches else None


def log_mistake(item_id: str, category: str = "", question: str = "",
                your_answer: str = "", correct_answer: str = "",
                cause: str | None = None, note: str = "") -> dict:
    """Record (or refresh) an unresolved mistake for app+item_id.

    An existing *unresolved* entry for the same app+id is updated in place so
    a second wrong attempt at the same part does not pile up duplicates; a
    previously resolved entry is reopened.  Returns the stored entry.
    """
    with journal_sync.lock(MISTAKES_FILE, create=True):
        return _log_mistake_locked(item_id, category, question, your_answer,
                                   correct_answer, cause, note)


def _log_mistake_locked(item_id: str, category: str, question: str,
                        your_answer: str, correct_answer: str,
                        cause: str | None, note: str) -> dict:
    entries = load_mistakes()        # read inside the lock: never stale
    entry = make_mistake_entry(item_id, category, question, your_answer,
                               correct_answer, cause, note)
    hits = [i for i, e in enumerate(entries)
            if e["app"] == APP_NAME_KEY and e["id"] == item_id]
    if hits:
        i = hits[-1]                       # newest entry for this item
        # Keep a cause/note the user already supplied unless a new one came in.
        entry["cause"] = normalize_cause(cause) or entries[i]["cause"]
        entry["note"] = _clip(note) or entries[i]["note"]
        entries[i] = entry
    else:
        entries.append(entry)
    save_mistakes(entries)
    return entry


def set_mistake_cause(item_id: str, cause: str | None, note: str | None = None) -> dict | None:
    """Categorise the stored mistake for app+item_id. Returns the entry or None."""
    with journal_sync.lock(MISTAKES_FILE):
        entries = load_mistakes()    # read inside the lock: never stale
        target = None
        for e in entries:
            if e["app"] == APP_NAME_KEY and e["id"] == item_id:
                target = e
        if target is None:
            return None
        target["cause"] = normalize_cause(cause)
        if note is not None:
            target["note"] = _clip(note)
        save_mistakes(entries)
        return target


def resolve_mistake(item_id: str) -> bool:
    """Mark this app's entries for `item_id` resolved. True if anything changed."""
    with journal_sync.lock(MISTAKES_FILE):
        entries = load_mistakes()    # read inside the lock: never stale
        changed = False
        for e in entries:
            if e["app"] == APP_NAME_KEY and e["id"] == item_id and not e["resolved"]:
                e["resolved"] = True
                changed = True
        if changed:
            save_mistakes(entries)
        return changed


# ---------------------------------------------------------------------------
# Confidence calibration  —  <data dir>/confidence.json  (suite-wide)
# ---------------------------------------------------------------------------
# [
#   {"id": str, "app": str, "category": str,
#    "confidence": int 1-4, "correct": bool, "timestamp": float},
#   ...
# ]
# 1 = guessing, 2 = unsure, 3 = fairly sure, 4 = certain.  Pairing a rating
# made *before* the answer is graded with the outcome surfaces the confidently
# wrong topics — the unknown unknowns a plain score never shows.

CONFIDENCE_KEYS = ("id", "app", "category", "confidence", "correct", "timestamp")

CONFIDENCE_LABELS = {
    1: "Guessing",
    2: "Unsure",
    3: "Fairly sure",
    4: "Certain",
}


def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, timestamp: float | None = None,
                          app: str = APP_NAME_KEY) -> dict:
    """One calibration row in contract order; confidence is clamped to 1–4."""
    try:
        level = int(confidence)
    except (TypeError, ValueError):
        level = 1
    level = max(1, min(4, level))
    return {
        "id":         str(item_id),
        "app":        str(app),
        "category":   str(category or ""),
        "confidence": level,
        "correct":    bool(correct),
        "timestamp":  float(timestamp if timestamp is not None else time.time()),
    }


def load_confidence() -> list[dict]:
    """Every calibration row (all apps), oldest first; bad rows are dropped."""
    out: list[dict] = []
    for raw in _load_json_list(CONFIDENCE_FILE):
        if not isinstance(raw, dict) or not raw.get("id"):
            continue
        if not isinstance(raw.get("confidence"), (int, float)):
            continue
        ts = raw.get("timestamp", 0.0)
        out.append(make_confidence_entry(
            item_id=raw["id"],
            category=raw.get("category", ""),
            confidence=raw["confidence"],
            correct=bool(raw.get("correct", False)),
            timestamp=float(ts) if isinstance(ts, (int, float)) else 0.0,
            app=raw.get("app") or APP_NAME_KEY,
        ))
    return out


def save_confidence(entries: list[dict]) -> None:
    """Rewrite calibration atomically, keeping the newest MAX_CONFIDENCE rows.

    Locked and foreign-row preserving, exactly like :func:`save_mistakes`.
    """
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        rows = journal_sync.merge_foreign(_load_json_list(CONFIDENCE_FILE),
                                          list(entries), APP_NAME_KEY)
        _atomic_write_json(CONFIDENCE_FILE, rows[-MAX_CONFIDENCE:])


def log_confidence(item_id: str, category: str, confidence: int,
                   correct: bool) -> dict:
    """Append one pre-answer confidence rating paired with its outcome."""
    entry = make_confidence_entry(item_id, category, confidence, correct)
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        entries = load_confidence()  # read inside the lock: never stale
        entries.append(entry)
        save_confidence(entries)
    return entry


def confidence_summary(app: str = APP_NAME_KEY) -> dict[int, tuple[int, int]]:
    """{confidence level: (correct, total)} for this app — calibration at a glance."""
    out: dict[int, tuple[int, int]] = {}
    for e in load_confidence():
        if e["app"] != app:
            continue
        hit, total = out.get(e["confidence"], (0, 0))
        out[e["confidence"]] = (hit + (1 if e["correct"] else 0), total + 1)
    return out


# ---------------------------------------------------------------------------
# App-local settings  —  <data dir>/problems_settings.json
# ---------------------------------------------------------------------------
# A small dict of this app's UI preferences.  Separate from the shared suite
# files so nothing the coach parses is touched.

DEFAULT_SETTINGS = {"confidence_prompt": True}


def load_settings() -> dict:
    """Stored settings merged over the defaults; defaults if missing/corrupt."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text())
            if isinstance(data, dict):
                settings.update(data)
    except Exception:
        pass
    return settings


def save_settings(settings: dict) -> None:
    _atomic_write_json(SETTINGS_FILE, dict(settings))


def confidence_prompt_enabled() -> bool:
    """False once the user has opted out of the confidence strip."""
    return bool(load_settings().get("confidence_prompt", True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings["confidence_prompt"] = bool(enabled)
    save_settings(settings)
