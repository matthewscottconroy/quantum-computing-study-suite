"""Prompt builders produce well-formed prompts carrying the JSON contract (no API calls)."""
from __future__ import annotations

from ai.prompt_builder import build_evaluation_prompt, build_generation_prompt
from core.models import Question
from core.topics import DIFFICULTY_LEVELS, QUESTION_TYPES, TOPICS

GENERATION_CONTRACT = ('Respond with ONLY valid JSON', '"question"', '"hints"')
EVALUATION_CONTRACT = (
    'Respond with ONLY valid JSON', '"score"', '"verdict"', '"feedback"',
    '"model_answer"', '"key_points_missed"', '"follow_up"',
)


def _question(**kw) -> Question:
    base = dict(
        subject="Number Theory",
        topic="the Euclidean algorithm and Bézout's identity",
        difficulty="intermediate",
        question_type="calculation",
        text="Compute gcd(252, 105) and express it as 252a + 105b.",
    )
    base.update(kw)
    return Question(**base)


def test_generation_prompt_carries_contract_and_inputs():
    p = build_generation_prompt(
        "Linear Algebra", "singular value decomposition (SVD)", "advanced",
        "proof sketch", [],
    )
    assert isinstance(p, str)
    for needle in GENERATION_CONTRACT:
        assert needle in p
    assert "Linear Algebra" in p and "singular value decomposition (SVD)" in p
    assert "advanced" in p and "proof sketch" in p
    assert "(none yet)" in p
    assert "{{" not in p and "}}" not in p     # f-string braces were resolved


def test_generation_prompt_lists_previous_questions():
    prev = ["What is a Hilbert space?", "Prove rank-nullity."]
    p = build_generation_prompt("Linear Algebra", "x", "beginner", "calculation", prev)
    for q in prev:
        assert f"  - {q}" in p
    assert "(none yet)" not in p


def test_generation_prompt_well_formed_for_every_subject_type_and_difficulty():
    for subject, topics in TOPICS.items():
        for qtype in QUESTION_TYPES:
            for difficulty in DIFFICULTY_LEVELS:
                p = build_generation_prompt(subject, topics[0], difficulty, qtype, [])
                assert subject in p and topics[0] in p
                assert all(n in p for n in GENERATION_CONTRACT), (subject, qtype)
                # every subject must have a real quantum-relevance note
                assert "Quantum computing relevance:\n  \n" not in p, subject


def test_subject_type_supplement_is_injected():
    plain = build_generation_prompt("Topology & Geometry", "t", "advanced", "proof sketch", [])
    calc = build_generation_prompt("Topology & Geometry", "t", "advanced", "calculation", [])
    assert "π₁" in calc and "π₁" not in plain


def test_evaluation_prompt_carries_contract_and_inputs():
    q = _question()
    p = build_evaluation_prompt(q, "gcd is 21 = 252*(-2) + 105*5")
    for needle in EVALUATION_CONTRACT:
        assert needle in p
    assert q.text in p and "gcd is 21 = 252*(-2) + 105*5" in p
    assert q.subject in p and q.topic in p and q.difficulty in p and q.question_type in p
    assert "{{" not in p and "}}" not in p


def test_evaluation_prompt_handles_empty_answer():
    p = build_evaluation_prompt(_question(), "")
    assert "Student's answer:" in p
    assert all(n in p for n in EVALUATION_CONTRACT)
