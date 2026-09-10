"""Curriculum data shape."""
from __future__ import annotations

from core.topics import DIFFICULTY_LEVELS, QUESTION_TYPES, TOPICS

EXPECTED_SUBJECT_COUNT = 13


def test_thirteen_subjects():
    assert len(TOPICS) == EXPECTED_SUBJECT_COUNT
    assert all(isinstance(s, str) and s.strip() for s in TOPICS)


def test_every_subject_has_non_empty_unique_topics():
    for subject, topics in TOPICS.items():
        assert isinstance(topics, list) and topics, subject
        assert all(isinstance(t, str) and t.strip() for t in topics), subject
        assert len(set(topics)) == len(topics), f"duplicate topic in {subject}"


def test_difficulty_levels():
    assert DIFFICULTY_LEVELS == ["beginner", "intermediate", "advanced", "expert"]


def test_question_types():
    assert len(set(QUESTION_TYPES)) == len(QUESTION_TYPES) >= 4
    assert {"calculation", "proof sketch", "conceptual explanation"} <= set(QUESTION_TYPES)
