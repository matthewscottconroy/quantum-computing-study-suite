"""Claude response parsing round-trips; fenced / unfenced JSON; garbage rejection."""
from __future__ import annotations

import json

import pytest

from ai.response_parser import ParseError, parse_evaluation_response, parse_question_response
from core.models import Evaluation, Question

_Q = {"question": "Explain phase kickback.", "hints": ["eigenstate", "controlled-U", "global→relative"]}
_E = {
    "score": 9,
    "verdict": "Correct",
    "feedback": "Clear and precise.",
    "model_answer": "Phase kickback moves an eigenphase onto the control ...",
    "key_points_missed": [],
    "follow_up": "How does this power QPE?",
}
_WRAPS = {
    "unfenced": lambda s: s,
    "fenced-json": lambda s: f"```json\n{s}\n```",
    "fenced-plain": lambda s: f"```\n{s}\n```",
    "fenced-padded": lambda s: f"\n ```json\n{s}\n``` \n",
}
_GARBAGE = ["", "  ", "Here is the JSON you asked for.", "{'single': 'quotes'}", "```json\n{oops\n```", "[1,"]


def test_question_round_trip():
    for name, wrap in _WRAPS.items():
        q = parse_question_response(wrap(json.dumps(_Q)))
        assert isinstance(q, Question), name
        assert q.text == _Q["question"] and q.hints == _Q["hints"], name
        assert (q.subject, q.topic, q.difficulty, q.question_type) == ("", "", "", ""), name


def test_question_hints_optional_and_coerced():
    assert parse_question_response(json.dumps({"question": "Q?"})).hints == []
    assert parse_question_response(json.dumps({"question": "Q?", "hints": [3]})).hints == ["3"]


def test_question_missing_field_raises():
    with pytest.raises(ParseError):
        parse_question_response(json.dumps({"hints": ["h"]}))


def test_garbage_is_rejected_by_both_parsers():
    for garbage in _GARBAGE:
        with pytest.raises(ParseError):
            parse_question_response(garbage)
        with pytest.raises(ParseError):
            parse_evaluation_response(garbage)


def test_evaluation_round_trip():
    for name, wrap in _WRAPS.items():
        e = parse_evaluation_response(wrap(json.dumps(_E)))
        assert isinstance(e, Evaluation), name
        assert e.score == 9 and e.verdict == "Correct", name
        assert e.feedback == _E["feedback"] and e.model_answer == _E["model_answer"], name
        assert e.key_points_missed == [] and e.follow_up == _E["follow_up"], name


def test_evaluation_score_clamped_and_verdict_derived():
    table = [
        (12, 10, "Correct"), (7, 7, "Correct"), (6, 6, "Partially correct"),
        (4, 4, "Partially correct"), (3, 3, "Incorrect"), (-1, 0, "Incorrect"),
        ("8", 8, "Correct"), (6.7, 6, "Partially correct"),
    ]
    for raw_score, score, verdict in table:
        e = parse_evaluation_response(json.dumps(dict(_E, score=raw_score, verdict="ignored")))
        assert (e.score, e.verdict) == (score, verdict), f"raw score {raw_score!r}"


def test_evaluation_optional_fields_default():
    data = {k: v for k, v in _E.items() if k not in ("key_points_missed", "follow_up")}
    e = parse_evaluation_response(json.dumps(data))
    assert e.key_points_missed == [] and e.follow_up == ""


def test_evaluation_missing_or_invalid_required_field_raises():
    for bad in ({"score": "excellent"}, {"feedback": None}, {"model_answer": None}):
        data = dict(_E)
        for k, v in bad.items():
            data.pop(k) if v is None else data.__setitem__(k, v)
        with pytest.raises(ParseError):
            parse_evaluation_response(json.dumps(data))
