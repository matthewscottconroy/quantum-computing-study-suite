"""Persistence for paper-drill sessions, paper library, review flags, the
mistake journal, and confidence calibration."""
from __future__ import annotations
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
import journal_sync
from config import (
    HISTORY_FILE, DATA_DIR, LIBRARY_FILE, FLAGGED_FILE, APP_ID,
    MISTAKES_FILE, CONFIDENCE_FILE, SETTINGS_FILE,
)
from core.models import SessionStats


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
        "title":   stats.title,
        "total":   stats.total,
        "average": stats.average,
        "scores":  stats.scores,
    })
    HISTORY_FILE.write_text(json.dumps(sessions, indent=2))


# ---------------------------------------------------------------------------
# Paper library
# ---------------------------------------------------------------------------

def _load_library_raw() -> list[dict]:
    if not LIBRARY_FILE.exists():
        return []
    try:
        return json.loads(LIBRARY_FILE.read_text())
    except Exception:
        return []


def load_library() -> list[dict]:
    """Return list of saved papers: {id, title, text, q_count, saved_at}."""
    return _load_library_raw()


def save_paper(title: str, text: str, q_count: int) -> str:
    """Save a paper to the library and return its new ID."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    library = _load_library_raw()
    paper_id = str(uuid.uuid4())[:8]
    library.append({
        "id":       paper_id,
        "title":    title,
        "text":     text,
        "q_count":  q_count,
        "saved_at": datetime.now(tz=timezone.utc).isoformat(),
    })
    LIBRARY_FILE.write_text(json.dumps(library, indent=2))
    return paper_id


def delete_paper(paper_id: str) -> None:
    """Remove a paper from the library by ID."""
    library = _load_library_raw()
    library = [p for p in library if p.get("id") != paper_id]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LIBRARY_FILE.write_text(json.dumps(library, indent=2))


# ---------------------------------------------------------------------------
# Flag for review
#
# Shared suite contract: entries are appended to <prefix>_flagged.json, here
# ``paper_flagged.json``.  Each entry is
#   {"id": str, "label": str, "category": str, "app": str, "timestamp": float}
# with id = hash of (paper title + question text), label = the question text
# truncated, category = the paper title, app = "paper-drill".
# Flagging is a toggle: flagging an already-flagged item removes it.
# ---------------------------------------------------------------------------

FLAG_LABEL_MAX = 80


def make_flag_id(paper_title: str, question_text: str) -> str:
    """Stable id for a (paper, question) pair — questions are generated
    on the fly, so the hash is the only durable identity they have.

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
    text = " ".join(question_text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def load_flagged() -> list[dict]:
    """Return flagged entries (malformed file or entries are ignored)."""
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


def is_flagged(flag_id: str) -> bool:
    return any(e.get("id") == flag_id for e in load_flagged())


def toggle_flag(flag_id: str, label: str, category: str) -> bool:
    """Flag the item if unflagged, unflag it if flagged.  Returns new state."""
    entries = load_flagged()
    remaining = [e for e in entries if e.get("id") != flag_id]
    if len(remaining) != len(entries):
        _save_flagged(remaining)
        return False
    entries.append({
        "id":        flag_id,
        "label":     label,
        "category":  category,
        "app":       APP_ID,
        "timestamp": time.time(),
    })
    _save_flagged(entries)
    return True


def unflag(flag_id: str) -> None:
    """Remove a flagged entry by id (no-op if absent)."""
    entries = load_flagged()
    remaining = [e for e in entries if e.get("id") != flag_id]
    if len(remaining) != len(entries):
        _save_flagged(remaining)


# ---------------------------------------------------------------------------
# Learning signals — mistake journal + confidence calibration
#
# Two suite-wide stores live beside the per-app files in DATA_DIR:
#
#   mistakes.json    a wrong answer becomes *analysis*, not just a bookmark.
#                    Every entry carries a cause category, so a month of drills
#                    answers "what kind of mistake do I keep making?" rather
#                    than only "which questions did I get wrong?".
#       {"id", "app", "category", "question", "your_answer", "correct_answer",
#        "cause", "note", "timestamp", "resolved"}
#
#   confidence.json  pairs a pre-answer confidence rating with the grade, so
#                    the *confidently wrong* topics — the unknown unknowns —
#                    can be separated from the merely unknown.
#       {"id", "app", "category", "confidence", "correct", "timestamp"}
#
# Both files are shared with the other nine apps: reads keep every app's rows
# and writes only ever touch rows whose "app" is APP_ID.  Both are written
# atomically (temp file + os.replace) so a crash mid-write cannot truncate
# another app's data, and both tolerate a missing or corrupt file by starting
# from an empty list.
# ---------------------------------------------------------------------------

MISTAKE_TEXT_MAX = 200          # per the shared contract: question/answers <= 200 chars
MISTAKE_NOTE_MAX = 200
MISTAKE_CAUSES = (
    "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other",
)
MISTAKE_CAUSE_LABELS = {
    "misread":          "Misread",
    "didnt_know":       "Didn't know",
    "knew_but_slipped": "Knew but slipped",
    "confused":         "Confused",
    "out_of_time":      "Out of time",
    "other":            "Other",
}
# A graded answer below this score counts as a mistake (matches Verdict.INCORRECT).
MISTAKE_SCORE_THRESHOLD = 4
# Growth caps.  Trimming only ever drops *this app's* oldest rows — another
# app's entries are never discarded to make room for ours.
MISTAKES_MAX_ENTRIES = 2000
CONFIDENCE_MAX_ENTRIES = 5000

CONFIDENCE_LEVELS = {1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}
# Ratings at or above this level count as "confident" for the confidently-wrong tally.
CONFIDENT_LEVEL = 3

SETTING_CONFIDENCE_PROMPT = "confidence_prompt"


def _atomic_write_json(path: Path, payload) -> None:
    """Write JSON to ``path`` via a temp file + os.replace (never a partial file)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2))
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _load_json_list(path: Path) -> list[dict]:
    """Entries from a JSON-list file; missing/corrupt/foreign shapes read empty."""
    path = Path(path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and e.get("id")]


def clip_text(text, limit: int = MISTAKE_TEXT_MAX) -> str:
    """One-line, length-capped copy of ``text`` (ellipsis when truncated)."""
    flat = " ".join(str(text or "").split())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1].rstrip() + "…"


def normalise_cause(cause):
    """Return a known cause string, or None for anything unrecognised."""
    return cause if cause in MISTAKE_CAUSES else None


# ---------------------------------------------------------------------------
# Mistake journal
# ---------------------------------------------------------------------------

def make_mistake_entry(item_id: str, category: str, question: str,
                       your_answer: str, correct_answer: str,
                       cause=None, note: str = "", timestamp=None,
                       resolved: bool = False) -> dict:
    """Build a contract-shaped mistake entry (pure — nothing is written)."""
    return {
        "id":             str(item_id),
        "app":            APP_ID,
        "category":       clip_text(category, MISTAKE_TEXT_MAX),
        "question":       clip_text(question, MISTAKE_TEXT_MAX),
        "your_answer":    clip_text(your_answer, MISTAKE_TEXT_MAX),
        "correct_answer": clip_text(correct_answer, MISTAKE_TEXT_MAX),
        "cause":          normalise_cause(cause),
        "note":           clip_text(note, MISTAKE_NOTE_MAX),
        "timestamp":      float(timestamp if timestamp is not None else time.time()),
        "resolved":       bool(resolved),
    }


def load_mistakes() -> list[dict]:
    """Every app's mistake entries, oldest first (bad files read as empty)."""
    return _load_json_list(MISTAKES_FILE)


def _trim_own(entries: list[dict], cap: int) -> list[dict]:
    """Drop this app's oldest rows until the file is back under ``cap``."""
    excess = len(entries) - cap
    if excess <= 0:
        return entries
    mine = [i for i, e in enumerate(entries) if e.get("app") == APP_ID]
    drop = set(mine[:excess])
    return [e for i, e in enumerate(entries) if i not in drop]


def _save_mistakes(entries: list[dict]) -> None:
    """Rewrite the shared journal under its lock.

    mistakes.json belongs to all ten apps at once, so two things hold here:
    the whole read-modify-write is serialised by journal_sync.lock() (without
    it the read goes stale and whichever app writes last drops the other's new
    rows), and every row owned by another app is written back exactly as it is
    on disk, unknown keys included.
    """
    with journal_sync.lock(MISTAKES_FILE, create=True):
        rows = journal_sync.merge_foreign(_load_json_list(MISTAKES_FILE),
                                          entries, APP_ID)
        _atomic_write_json(MISTAKES_FILE, _trim_own(rows, MISTAKES_MAX_ENTRIES))


def mistakes_for(item_id: str) -> list[dict]:
    """This app's entries for one item id, oldest first."""
    return [e for e in load_mistakes()
            if e.get("app") == APP_ID and e.get("id") == item_id]


def log_mistake(item_id: str, category: str, question: str, your_answer: str,
                correct_answer: str, cause=None, note: str = "") -> dict:
    """Append a mistake entry and return it.

    Called the moment an answer is graded wrong, with ``cause=None``: skipping
    the "What went wrong?" row must still leave the mistake on record.  The
    cause is filled in afterwards by :func:`set_mistake_cause`.
    """
    entry = make_mistake_entry(item_id, category, question, your_answer,
                               correct_answer, cause=cause, note=note)
    with journal_sync.lock(MISTAKES_FILE, create=True):
        entries = load_mistakes()    # read inside the lock: never stale
        entries.append(entry)
        _save_mistakes(entries)
    return entry


def set_mistake_cause(item_id: str, cause, note: str = "") -> bool:
    """Categorise this app's most recent open entry for ``item_id``.

    Updates the newest unresolved row (falling back to the newest row of any
    state) so re-categorising, or adding a note after picking a cause, edits
    one entry instead of piling up duplicates.  Returns False when there is
    nothing to update.
    """
    with journal_sync.lock(MISTAKES_FILE):
        entries = load_mistakes()    # read inside the lock: never stale
        matches = [i for i, e in enumerate(entries)
                   if e.get("app") == APP_ID and e.get("id") == item_id]
        if not matches:
            return False
        open_matches = [i for i in matches if not entries[i].get("resolved")]
        idx = (open_matches or matches)[-1]
        entries[idx]["cause"] = normalise_cause(cause)
        entries[idx]["note"] = clip_text(note, MISTAKE_NOTE_MAX)
        _save_mistakes(entries)
        return True


def resolve_mistake(item_id: str) -> int:
    """Mark this app's entries for ``item_id`` resolved; returns how many changed."""
    with journal_sync.lock(MISTAKES_FILE):
        entries = load_mistakes()    # read inside the lock: never stale
        changed = 0
        for entry in entries:
            if (entry.get("app") == APP_ID and entry.get("id") == item_id
                    and not entry.get("resolved")):
                entry["resolved"] = True
                changed += 1
        if changed:
            _save_mistakes(entries)
        return changed


def cause_counts(entries=None, app: str | None = APP_ID,
                 include_resolved: bool = True) -> dict[str, int]:
    """Tally of causes — the payload of the journal ("six misreads this month").

    Uncategorised entries are counted under the key ``"uncategorised"``.
    """
    rows = load_mistakes() if entries is None else entries
    counts: dict[str, int] = {}
    for entry in rows:
        if app is not None and entry.get("app") != app:
            continue
        if not include_resolved and entry.get("resolved"):
            continue
        key = normalise_cause(entry.get("cause")) or "uncategorised"
        counts[key] = counts.get(key, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Confidence calibration
# ---------------------------------------------------------------------------

def make_confidence_entry(item_id: str, category: str, confidence: int,
                          correct: bool, timestamp=None) -> dict:
    """Build a contract-shaped confidence entry (pure — nothing is written)."""
    return {
        "id":         str(item_id),
        "app":        APP_ID,
        "category":   clip_text(category, MISTAKE_TEXT_MAX),
        "confidence": int(confidence),
        "correct":    bool(correct),
        "timestamp":  float(timestamp if timestamp is not None else time.time()),
    }


def load_confidence() -> list[dict]:
    """Every app's confidence rows, oldest first (bad files read as empty)."""
    return _load_json_list(CONFIDENCE_FILE)


def log_confidence(item_id: str, category: str, confidence, correct: bool):
    """Record a (pre-answer confidence, graded outcome) pair.

    Returns the stored entry, or None when ``confidence`` is not 1–4 (the
    rating is optional, so "no rating" is a normal, silent no-op).
    """
    try:
        level = int(confidence)
    except (TypeError, ValueError):
        return None
    if level not in CONFIDENCE_LEVELS:
        return None
    entry = make_confidence_entry(item_id, category, level, correct)
    with journal_sync.lock(CONFIDENCE_FILE, create=True):
        entries = load_confidence()  # read inside the lock: never stale
        entries.append(entry)
        rows = journal_sync.merge_foreign(_load_json_list(CONFIDENCE_FILE),
                                          entries, APP_ID)
        _atomic_write_json(CONFIDENCE_FILE, _trim_own(rows, CONFIDENCE_MAX_ENTRIES))
    return entry


def confidently_wrong(entries=None, app: str | None = APP_ID) -> list[dict]:
    """Rows rated 'fairly sure' or 'certain' that turned out wrong."""
    rows = load_confidence() if entries is None else entries
    return [e for e in rows
            if (app is None or e.get("app") == app)
            and not e.get("correct")
            and isinstance(e.get("confidence"), int)
            and e["confidence"] >= CONFIDENT_LEVEL]


# ---------------------------------------------------------------------------
# App settings (this app only) — currently just the confidence-strip opt-out
# ---------------------------------------------------------------------------

def load_settings() -> dict:
    """Saved UI preferences; a missing or corrupt file reads as {}."""
    if not SETTINGS_FILE.exists():
        return {}
    try:
        data = json.loads(SETTINGS_FILE.read_text())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> None:
    _atomic_write_json(SETTINGS_FILE, settings)


def confidence_prompt_enabled() -> bool:
    """True unless the learner has switched the confidence strip off."""
    return bool(load_settings().get(SETTING_CONFIDENCE_PROMPT, True))


def set_confidence_prompt_enabled(enabled: bool) -> None:
    settings = load_settings()
    settings[SETTING_CONFIDENCE_PROMPT] = bool(enabled)
    save_settings(settings)
