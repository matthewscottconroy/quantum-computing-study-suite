"""Question bank loader: 110 questions, documented section counts, valid fields."""
from collections import Counter

from bank import question_by_id, questions_by_section
from config import BANK_SIZE, SECTIONS
from core.models import Question

DOCUMENTED_SECTIONS = {
    "Create circuits": 20,
    "Quantum operations": 18,
    "Run circuits": 16,
    "Sampler": 13,
    "Estimator": 13,
    "Visualization": 12,
    "Results analysis": 11,
    "OpenQASM": 7,
}
DIFFICULTIES = {"easy", "medium", "hard"}


def test_config_sections_match_documented_counts():
    assert SECTIONS == DOCUMENTED_SECTIONS
    assert BANK_SIZE == 110


def test_bank_loads_110_questions_with_unique_ids(questions):
    assert len(questions) == 110
    ids = [q.id for q in questions]
    assert len(set(ids)) == len(ids)
    assert all(isinstance(q, Question) for q in questions)


def test_eight_sections_with_documented_counts(questions):
    assert Counter(q.section for q in questions) == DOCUMENTED_SECTIONS


def test_questions_by_section_keys_and_totals(questions):
    grouped = questions_by_section()
    assert set(grouped) == set(SECTIONS)
    assert {s: len(qs) for s, qs in grouped.items()} == DOCUMENTED_SECTIONS


def test_every_question_has_exactly_four_distinct_options(questions):
    for q in questions:
        assert len(q.options) == 4, q.id
        assert len(set(q.options)) == 4, q.id
        assert all(isinstance(o, str) and o.strip() for o in q.options), q.id


def test_correct_index_in_range(questions):
    for q in questions:
        assert isinstance(q.correct_index, int), q.id
        assert 0 <= q.correct_index < len(q.options), q.id


def test_required_text_fields_and_difficulty(questions):
    for q in questions:
        assert q.question.strip(), q.id
        assert q.explanation.strip(), q.id
        assert q.difficulty in DIFFICULTIES, q.id


def test_question_by_id_round_trip(questions):
    sample = questions[0]
    found = question_by_id(sample.id)
    assert found is not None
    assert (found.id, found.section, found.question) == (sample.id, sample.section, sample.question)
    assert question_by_id("definitely_not_a_question") is None
