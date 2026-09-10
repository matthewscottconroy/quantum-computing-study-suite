"""Claude response parsing: fenced / unfenced JSON, garbage rejection, clamping."""
from __future__ import annotations

import json

import pytest

from ai.response_parser import ParseError, parse_evaluation_response, parse_question_response
from core.models import Evaluation, Question

_Q = {"question": "State the spectral theorem.", "hints": ["normal operators", "orthonormal eigenbasis"]}
_E = {
    "score": 8,
    "verdict": "Correct",
    "feedback": "Good.",
    "model_answer": "A normal operator is unitarily diagonalisable.",
    "key_points_missed": ["mention uniqueness"],
    "follow_up": "Extend to compact operators.",
}
_WRAPS = {
    "unfenced": lambda s: s,
    "fenced-json": lambda s: f"```json\n{s}\n```",
    "fenced-plain": lambda s: f"```\n{s}\n```",
    "fenced-padded": lambda s: f"\n\n  ```json\n{s}\n```  \n",
}
_GARBAGE = ["", "   ", "Sure! Here is your question.", "{not json", "```json\nnope\n```", "[1, 2"]


def test_parse_question_accepts_fenced_and_unfenced():
    for name, wrap in _WRAPS.items():
        q = parse_question_response(wrap(json.dumps(_Q)))
        assert isinstance(q, Question), name
        assert q.text == _Q["question"] and q.hints == _Q["hints"], name
        assert (q.subject, q.topic, q.difficulty, q.question_type) == ("", "", "", ""), name


def test_parse_question_hints_optional_and_coerced():
    assert parse_question_response(json.dumps({"question": "Q?"})).hints == []
    assert parse_question_response(json.dumps({"question": "Q?", "hints": [1, 2]})).hints == ["1", "2"]


def test_parse_question_missing_field_raises():
    with pytest.raises(ParseError):
        parse_question_response(json.dumps({"hints": []}))


def test_garbage_is_rejected_by_both_parsers():
    for garbage in _GARBAGE:
        with pytest.raises(ParseError):
            parse_question_response(garbage)
        with pytest.raises(ParseError):
            parse_evaluation_response(garbage)


def test_parse_evaluation_round_trip():
    for name, wrap in _WRAPS.items():
        e = parse_evaluation_response(wrap(json.dumps(_E)))
        assert isinstance(e, Evaluation), name
        assert e.score == 8 and e.verdict == "Correct", name
        assert e.feedback == _E["feedback"] and e.model_answer == _E["model_answer"], name
        assert e.key_points_missed == _E["key_points_missed"], name
        assert e.follow_up == _E["follow_up"], name


def test_evaluation_score_is_clamped_and_verdict_derived():
    table = [
        (15, 10, "Correct"), (10, 10, "Correct"), (7, 7, "Correct"),
        (6, 6, "Partially correct"), (4, 4, "Partially correct"),
        (3, 3, "Incorrect"), (0, 0, "Incorrect"), (-2, 0, "Incorrect"),
        ("8", 8, "Correct"), (5.9, 5, "Partially correct"),
    ]
    for raw_score, score, verdict in table:
        e = parse_evaluation_response(json.dumps(dict(_E, score=raw_score, verdict="whatever Claude said")))
        assert (e.score, e.verdict) == (score, verdict), f"raw score {raw_score!r}"


def test_evaluation_optional_fields_default():
    data = {k: v for k, v in _E.items() if k not in ("key_points_missed", "follow_up")}
    e = parse_evaluation_response(json.dumps(data))
    assert e.key_points_missed == [] and e.follow_up == ""


def test_evaluation_missing_or_invalid_required_field_raises():
    for bad in ({"score": "high"}, {"feedback": None}, {"model_answer": None}):
        data = dict(_E)
        for k, v in bad.items():
            data.pop(k) if v is None else data.__setitem__(k, v)
        with pytest.raises(ParseError):
            parse_evaluation_response(json.dumps(data))
