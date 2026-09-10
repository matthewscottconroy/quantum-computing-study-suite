"""response_parser robustness: fences, embedded JSON, clamping, aliases, errors."""
import json

import pytest

from ai.response_parser import ParseError, parse_grade_response, parse_step_check_response
from core.models import GradeResult, StepCheck

GRADE = {"score": 7, "feedback": "Mostly right.", "missed_points": ["normalisation"]}


def test_parse_grade_plain_json_round_trip():
    result = parse_grade_response(json.dumps(GRADE))
    assert isinstance(result, GradeResult)
    assert (result.score, result.feedback, result.missed_points) == (
        7, "Mostly right.", ["normalisation"])


def test_parse_grade_tolerates_fences_and_prose():
    body = json.dumps(GRADE)
    for wrap in ("```json\n{body}\n```",
                 "```\n{body}\n```",
                 "Here is my grade:\n{body}\nHope that helps!"):
        assert parse_grade_response(wrap.format(body=body)).score == 7, wrap


def test_parse_grade_clamps_and_coerces_score():
    for raw, expected in ((12, 10), (-1, 0), (7.6, 8), ("9", 9)):
        assert parse_grade_response(json.dumps({"score": raw})).score == expected, raw


def test_parse_grade_normalises_missed_points():
    assert parse_grade_response(json.dumps(
        {"score": 5, "missed_points": "one thing"})).missed_points == ["one thing"]
    assert parse_grade_response(json.dumps(
        {"score": 5, "missed_points": ["", "  ", "x "]})).missed_points == ["x"]
    assert parse_grade_response(json.dumps({"score": 5})).missed_points == []


def test_parse_grade_rejects_bad_payloads():
    for raw in (json.dumps({"feedback": "no score"}),
                json.dumps({"score": "high"}),
                json.dumps([1, 2, 3]),
                "no json here at all",
                "{ this is: not json }"):
        with pytest.raises(ParseError):
            parse_grade_response(raw)


def test_parse_step_check_round_trip():
    check = parse_step_check_response(json.dumps({"verdict": "accept", "nudge": "Nice."}))
    assert isinstance(check, StepCheck)
    assert check.accepted and check.nudge == "Nice."
    check = parse_step_check_response(json.dumps({"verdict": "needs_work", "nudge": "Think about U."}))
    assert not check.accepted and check.verdict == "needs_work"


def test_parse_step_check_accepts_near_miss_labels():
    for label in ("Accepted", "CORRECT", "pass", "yes"):
        assert parse_step_check_response(json.dumps({"verdict": label})).verdict == "accept", label
    for label in ("needs-work", "Reject", "incorrect", "retry", "no"):
        assert parse_step_check_response(json.dumps({"verdict": label})).verdict == "needs_work", label


def test_parse_step_check_rejects_bad_payloads():
    for raw in (json.dumps({"nudge": "missing verdict"}),
                json.dumps({"verdict": "maybe"}),
                "```json\nnot json\n```"):
        with pytest.raises(ParseError):
            parse_step_check_response(raw)
