"""Persistence for paper-drill sessions, paper library, and review flags."""
from __future__ import annotations
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from config import HISTORY_FILE, DATA_DIR, LIBRARY_FILE, FLAGGED_FILE, APP_ID
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
