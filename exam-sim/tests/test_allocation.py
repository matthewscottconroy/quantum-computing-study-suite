"""Exam-set allocation and sprint drawing (pure logic over the static bank).

Allocation is driven by the exam *weights* in ``config.SECTIONS``; the bank is
larger than those numbers, so the checks here compare draws against the real
per-section pool sizes rather than the weights.
"""
import random
from collections import Counter

import bank
from bank import (_proportional_allocation, all_questions, build_exam_set,
                  build_sprint_set, questions_by_section)
from config import EXAM_QUESTION_COUNT, SECTIONS, SPRINT_QUESTION_COUNT
from core.models import Question

# Largest-remainder result of 68 over the 20/18/16/13/13/12/11/7 weights.
EXPECTED_FULL_EXAM_ALLOCATION = {
    "Create circuits": 12, "Quantum operations": 11, "Run circuits": 10,
    "Sampler": 8, "Estimator": 8, "Visualization": 8,
    "Results analysis": 7, "OpenQASM": 4,
}


def _pool_sizes() -> dict[str, int]:
    return {s: len(v) for s, v in questions_by_section().items()}


def _fake(qid: str, section: str) -> Question:
    return Question(id=qid, section=section, question=f"{qid}?",
                    options=["a", "b", "c", "d"], correct_index=0,
                    explanation="x" * 40, difficulty="easy")


# ---- _proportional_allocation --------------------------------------------------

def test_allocation_68_matches_weights_and_fits_every_pool():
    alloc = _proportional_allocation(EXAM_QUESTION_COUNT)
    assert alloc == EXPECTED_FULL_EXAM_ALLOCATION
    assert sum(alloc.values()) == EXAM_QUESTION_COUNT
    pools = _pool_sizes()
    short = {s: (n, pools[s]) for s, n in alloc.items() if n > pools[s]}
    assert not short, f"full-exam allocation exceeds pool: {short}"
    assert all(n >= 1 for n in alloc.values())


def test_allocation_always_sums_to_requested_count():
    bank_size = len(all_questions())
    for count in (1, 10, 34, 68, 110, bank_size, bank_size + 50):
        alloc = _proportional_allocation(count)
        assert set(alloc) == set(SECTIONS)
        assert sum(alloc.values()) == count, count
        assert all(n >= 0 for n in alloc.values()), count


def test_allocation_never_rounds_a_section_by_more_than_one():
    total_weight = sum(SECTIONS.values())
    for count in (10, 34, 68, 100, 300):
        alloc = _proportional_allocation(count)
        for s, w in SECTIONS.items():
            assert abs(alloc[s] - count * w / total_weight) < 1, (count, s)


# ---- build_exam_set -------------------------------------------------------------

def test_full_exam_draws_68_unique_questions_with_exact_section_mix():
    for seed in range(5):
        random.seed(seed)
        chosen = build_exam_set(EXAM_QUESTION_COUNT)
        assert len(chosen) == EXAM_QUESTION_COUNT
        assert len({q.id for q in chosen}) == EXAM_QUESTION_COUNT, "duplicate question in exam set"
        # every pool is large enough, so no top-up: the mix is exactly the allocation
        assert Counter(q.section for q in chosen) == EXPECTED_FULL_EXAM_ALLOCATION


def test_full_exam_draws_differ_between_sessions():
    random.seed(1)
    first = [q.id for q in build_exam_set(EXAM_QUESTION_COUNT)]
    random.seed(2)
    second = [q.id for q in build_exam_set(EXAM_QUESTION_COUNT)]
    assert first != second
    assert set(first) != set(second), "same 68 questions in two sessions"


def test_full_exam_can_be_drawn_many_times_without_exhausting_any_section():
    """A student can sit several distinct mocks: 68 * 4 = 272 < 300."""
    pools = _pool_sizes()
    for s, n in EXPECTED_FULL_EXAM_ALLOCATION.items():
        assert pools[s] >= 2 * n, f"{s}: pool {pools[s]} < two exams' worth ({2 * n})"


def test_exam_set_of_whole_bank_returns_every_question():
    """Requesting the whole bank exercises the top-up path (some sections round
    up past their pool) and must still return each question exactly once."""
    everything = all_questions()
    chosen = build_exam_set(len(everything))
    assert len(chosen) == len(everything)
    assert {q.id for q in chosen} == {q.id for q in everything}


def test_exam_set_tops_up_from_other_sections_when_a_pool_runs_dry(monkeypatch):
    fake = ([_fake(f"cc{i}", "Create circuits") for i in range(2)]        # too few
            + [_fake(f"qo{i}", "Quantum operations") for i in range(40)]
            + [_fake(f"rc{i}", "Run circuits") for i in range(40)]
            + [_fake(f"sa{i}", "Sampler") for i in range(40)]
            + [_fake(f"es{i}", "Estimator") for i in range(40)]
            + [_fake(f"vz{i}", "Visualization") for i in range(40)]
            + [_fake(f"ra{i}", "Results analysis") for i in range(40)]
            + [_fake(f"oq{i}", "OpenQASM") for i in range(40)])
    monkeypatch.setattr(bank, "all_questions", lambda: list(fake))
    chosen = build_exam_set(EXAM_QUESTION_COUNT)
    assert len(chosen) == EXAM_QUESTION_COUNT
    assert len({q.id for q in chosen}) == EXAM_QUESTION_COUNT
    mix = Counter(q.section for q in chosen)
    assert mix["Create circuits"] == 2                    # whole (short) pool used
    assert sum(mix.values()) == EXAM_QUESTION_COUNT       # shortfall filled elsewhere


def test_exam_set_larger_than_bank_returns_whole_bank_once(monkeypatch):
    fake = [_fake(f"{p}{i}", s) for s, p in
            (("Create circuits", "cc"), ("OpenQASM", "oq")) for i in range(3)]
    monkeypatch.setattr(bank, "all_questions", lambda: list(fake))
    chosen = build_exam_set(50)
    assert sorted(q.id for q in chosen) == sorted(q.id for q in fake)


# ---- build_sprint_set -----------------------------------------------------------

def test_sprint_draws_ten_unique_from_every_section():
    for section in SECTIONS:
        for seed in range(3):
            random.seed(seed)
            chosen = build_sprint_set(section, SPRINT_QUESTION_COUNT)
            assert len(chosen) == SPRINT_QUESTION_COUNT, section
            assert len({q.id for q in chosen}) == SPRINT_QUESTION_COUNT, section
            assert {q.section for q in chosen} == {section}


def test_sprint_draws_differ_between_sessions():
    for section in SECTIONS:
        random.seed(1)
        first = [q.id for q in build_sprint_set(section, SPRINT_QUESTION_COUNT)]
        random.seed(2)
        second = [q.id for q in build_sprint_set(section, SPRINT_QUESTION_COUNT)]
        assert first != second, section


def test_sprint_on_small_section_returns_whole_pool(monkeypatch):
    fake = [_fake(f"oq{i}", "OpenQASM") for i in range(4)] + [_fake("cc0", "Create circuits")]
    monkeypatch.setattr(bank, "all_questions", lambda: list(fake))
    chosen = build_sprint_set("OpenQASM", SPRINT_QUESTION_COUNT)
    assert sorted(q.id for q in chosen) == ["oq0", "oq1", "oq2", "oq3"]
    assert {q.section for q in chosen} == {"OpenQASM"}


def test_sprint_unknown_section_is_empty():
    assert build_sprint_set("Not a section", SPRINT_QUESTION_COUNT) == []
