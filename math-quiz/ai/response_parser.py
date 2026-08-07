"""Parse and validate raw Claude JSON responses into typed dataclasses."""

from __future__ import annotations
import json
from core.models import Question, Evaluation


class ParseError(Exception):
    pass


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        inner = parts[1]
        if inner.startswith("json"):
            inner = inner[4:]
        text = inner.strip()
    return text


def _load(raw: str) -> dict:
    text = _strip_fences(raw)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON from Claude: {exc}\nRaw:\n{raw[:400]}") from exc


def parse_question_response(raw: str) -> Question:
    data = _load(raw)
    try:
        return Question(
            subject="",
            topic="",
            difficulty="",
            question_type="",
            text=str(data["question"]),
            hints=[str(h) for h in data.get("hints", [])],
        )
    except KeyError as exc:
        raise ParseError(f"Missing field in question response: {exc}") from exc


def parse_evaluation_response(raw: str) -> Evaluation:
    data = _load(raw)
    try:
        score = max(0, min(10, int(data["score"])))
        return Evaluation(
            score=score,
            verdict=_verdict_from_score(score),
            feedback=str(data["feedback"]),
            model_answer=str(data["model_answer"]),
            key_points_missed=[str(p) for p in data.get("key_points_missed", [])],
            follow_up=str(data.get("follow_up", "")),
        )
    except (KeyError, ValueError) as exc:
        raise ParseError(f"Missing/invalid field in evaluation response: {exc}") from exc


def _verdict_from_score(score: int) -> str:
    if score >= 7:
        return "Correct"
    if score >= 4:
        return "Partially correct"
    return "Incorrect"
