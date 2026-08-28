"""Persistence for exam-sim.

Schemas (shared with the coach app — do not change):

exam_history.json: list of
    {"timestamp": epoch float, "mode": "full"|"sprint", "total": int,
     "correct": int, "duration_secs": float,
     "sections": {"<section>": {"total": n, "correct": n}}}

exam_missed.json: list of
    {"question_id", "section", "question", "correct_answer", "chosen", "timestamp"}
Appended on a miss; an entry is removed when the question is later answered
correctly in Review mode.
"""
from __future__ import annotations
import json
import time
from config import DATA_DIR, HISTORY_FILE, MISSED_FILE
from core.models import ExamResult, Question


def _load_json(path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def load_history() -> list[dict]:
    return _load_json(HISTORY_FILE)


def save_result(result: ExamResult) -> None:
    """Append a finished full/sprint session to exam_history.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.append({
        "timestamp":     time.time(),
        "mode":          result.mode,
        "total":         result.total,
        "correct":       result.correct,
        "duration_secs": result.duration_secs,
        "sections":      result.section_breakdown(),
    })
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def load_missed() -> list[dict]:
    return _load_json(MISSED_FILE)


def _save_missed(entries: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MISSED_FILE.write_text(json.dumps(entries, indent=2))


def record_miss(question: Question, chosen_index: int | None) -> None:
    """Append a missed question (deduped by question_id, keeping the latest miss)."""
    entries = [e for e in load_missed() if e.get("question_id") != question.id]
    chosen = ""
    if chosen_index is not None and 0 <= chosen_index < len(question.options):
        chosen = question.options[chosen_index]
    entries.append({
        "question_id":    question.id,
        "section":        question.section,
        "question":       question.question,
        "correct_answer": question.options[question.correct_index],
        "chosen":         chosen,
        "timestamp":      time.time(),
    })
    _save_missed(entries)


def record_misses(result: ExamResult) -> None:
    for attempt in result.missed:
        record_miss(attempt.question, attempt.chosen_index)


def resolve_missed(question_id: str) -> None:
    """Remove a question from exam_missed.json (answered correctly in Review mode)."""
    entries = [e for e in load_missed() if e.get("question_id") != question_id]
    _save_missed(entries)
