"""Persistence for paper-drill sessions and paper library."""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from config import HISTORY_FILE, DATA_DIR, LIBRARY_FILE
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
