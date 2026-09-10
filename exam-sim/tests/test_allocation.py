"""Exam-set allocation and sprint drawing (pure logic over the static bank)."""
import random
from collections import Counter

from bank import _proportional_allocation, all_questions, build_exam_set, build_sprint_set
from config import EXAM_QUESTION_COUNT, SECTIONS, SPRINT_QUESTION_COUNT


def test_allocation_68_sums_and_fits_pools():
    alloc = _proportional_allocation(EXAM_QUESTION_COUNT)
    assert set(alloc) == set(SECTIONS)
    assert sum(alloc.values()) == 68
    assert all(1 <= n <= SECTIONS[s] for s, n in alloc.items())
    # Largest-remainder result for the documented weights.
    assert alloc == {
        "Create circuits": 12, "Quantum operations": 11, "Run circuits": 10,
        "Sampler": 8, "Estimator": 8, "Visualization": 8,
        "Results analysis": 7, "OpenQASM": 4,
    }


def test_allocation_always_sums_to_requested_count():
    for count in (1, 10, 34, 68, 110):
        alloc = _proportional_allocation(count)
        assert sum(alloc.values()) == count, count
        assert all(n >= 0 for n in alloc.values()), count


def test_full_exam_draws_68_unique_questions_across_several_draws():
    alloc = _proportional_allocation(EXAM_QUESTION_COUNT)
    for seed in range(5):
        random.seed(seed)
        chosen = build_exam_set(EXAM_QUESTION_COUNT)
        assert len(chosen) == 68
        assert len({q.id for q in chosen}) == 68, "duplicate question in exam set"
        assert Counter(q.section for q in chosen) == alloc


def test_full_exam_draws_differ_between_sessions():
    random.seed(1)
    first = [q.id for q in build_exam_set(EXAM_QUESTION_COUNT)]
    random.seed(2)
    second = [q.id for q in build_exam_set(EXAM_QUESTION_COUNT)]
    assert first != second


def test_exam_set_of_whole_bank_returns_every_question():
    assert {q.id for q in build_exam_set(110)} == {q.id for q in all_questions()}


def test_sprint_draws_ten_from_one_section():
    big_sections = [s for s, n in SECTIONS.items() if n >= SPRINT_QUESTION_COUNT]
    assert big_sections
    for section in big_sections:
        chosen = build_sprint_set(section, SPRINT_QUESTION_COUNT)
        assert len(chosen) == 10, section
        assert len({q.id for q in chosen}) == 10, section
        assert {q.section for q in chosen} == {section}


def test_sprint_on_small_section_returns_whole_pool():
    chosen = build_sprint_set("OpenQASM", SPRINT_QUESTION_COUNT)
    assert len(chosen) == SECTIONS["OpenQASM"]
    assert {q.section for q in chosen} == {"OpenQASM"}


def test_sprint_unknown_section_is_empty():
    assert build_sprint_set("Not a section", SPRINT_QUESTION_COUNT) == []
