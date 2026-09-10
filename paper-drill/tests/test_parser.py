"""Response parsing round-trips: (optionally fenced) JSON -> typed models."""
import json

import pytest

from ai import generator, grader
from core.models import Evaluation, Question, Verdict

RAW_QUESTIONS = [
    {"index": 1, "text": "What is a qubit?", "type": "factual"},
    {"index": 2, "text": "Why does decoherence matter?", "type": "conceptual"},
    {"index": 3, "text": "Derive the Bell-state amplitudes.", "type": "derivation"},
]


def test_generate_questions_round_trip(fake_claude):
    fake_claude(json.dumps(RAW_QUESTIONS))
    qs = generator.generate_questions("paper", 3)

    assert all(isinstance(q, Question) for q in qs)
    assert [q.index for q in qs] == [1, 2, 3]
    assert [q.text for q in qs] == [d["text"] for d in RAW_QUESTIONS]
    assert [q.q_type for q in qs] == ["factual", "conceptual", "derivation"]


@pytest.mark.parametrize("wrap", [
    "```json\n{body}\n```",
    "```\n{body}\n```",
    "  {body}  \n",
])
def test_generate_questions_strips_fences(fake_claude, wrap):
    fake_claude(wrap.format(body=json.dumps(RAW_QUESTIONS[:1])))
    qs = generator.generate_questions("paper", 1)
    assert len(qs) == 1
    assert qs[0].text == "What is a qubit?"


def test_generate_questions_defaults_missing_type(fake_claude):
    fake_claude(json.dumps([{"index": 1, "text": "Q"}]))
    assert generator.generate_questions("p", 1)[0].q_type == "conceptual"


def test_generate_questions_rejects_malformed_json(fake_claude):
    fake_claude("Sure! Here are your questions: 1) ...")
    with pytest.raises(ValueError):  # json.JSONDecodeError is a ValueError
        generator.generate_questions("p", 1)


@pytest.mark.parametrize("raw", ["[]", "{}", '{"index": 1, "text": "Q"}'],
                         ids=["empty-array", "empty-object", "single-object"])
def test_generate_questions_rejects_empty_or_non_array(fake_claude, raw):
    fake_claude(raw)
    with pytest.raises(ValueError, match="no questions"):
        generator.generate_questions("p", 1)


@pytest.mark.parametrize("score,verdict", [
    (10, Verdict.CORRECT), (7, Verdict.CORRECT),
    (6, Verdict.PARTIAL), (4, Verdict.PARTIAL),
    (3, Verdict.INCORRECT), (0, Verdict.INCORRECT),
])
def test_grade_verdict_thresholds(fake_claude, score, verdict):
    fake_claude(json.dumps({"score": score, "feedback": "f", "model_answer": "m"}))
    ev = grader.grade_answer("p", "q", "a")
    assert ev.score == score
    assert ev.verdict is verdict


@pytest.mark.parametrize("raw,expected", [(15, 10), (-3, 0), ("8", 8)])
def test_grade_score_clamped_and_coerced(fake_claude, raw, expected):
    fake_claude(json.dumps({"score": raw, "feedback": "f"}))
    assert grader.grade_answer("p", "q", "a").score == expected


def test_grade_round_trip_fields_with_fence(fake_claude):
    payload = {"score": 9, "feedback": "Nice work.", "model_answer": "The ideal."}
    fake_claude("```json\n" + json.dumps(payload) + "\n```")
    ev = grader.grade_answer("p", "q", "a")
    assert isinstance(ev, Evaluation)
    assert (ev.score, ev.verdict, ev.feedback, ev.model_answer) == (
        9, Verdict.CORRECT, "Nice work.", "The ideal.")


def test_grade_missing_optional_fields_default_empty(fake_claude):
    fake_claude(json.dumps({"score": 5}))
    ev = grader.grade_answer("p", "q", "a")
    assert ev.verdict is Verdict.PARTIAL
    assert ev.feedback == "" and ev.model_answer == ""


def test_grade_missing_score_raises(fake_claude):
    fake_claude(json.dumps({"feedback": "no score here"}))
    with pytest.raises(KeyError):
        grader.grade_answer("p", "q", "a")
