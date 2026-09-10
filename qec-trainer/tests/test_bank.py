"""Problem bank loader: counts, ids, categories, and checkable answers."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from core.models import GradeMode, Problem
from problems import all_categories, all_problems

EXPECTED_COUNT = 178
EXPECTED_CATEGORIES = {
    "Bosonic Codes", "Fault Tolerance", "Repetition Code",
    "Stabilizer Formalism", "Steane Code", "Surface Code",
}
DIFFICULTIES = {"beginner", "intermediate", "advanced"}


@pytest.fixture(scope="module")
def bank() -> list[Problem]:
    return all_problems()


def test_bank_loads_expected_number_of_problems(bank):
    assert len(bank) == EXPECTED_COUNT
    assert all(isinstance(p, Problem) for p in bank)


def test_every_problem_file_yields_a_problem(bank):
    """all_problems() swallows import errors; a broken file would silently vanish."""
    root = Path(all_problems.__code__.co_filename).parent
    files = [
        f for d in sorted(root.iterdir())
        if d.is_dir() and not d.name.startswith("_")
        for f in d.glob("*.py") if f.stem != "__init__"
    ]
    assert len(files) == len(bank)
    assert {f.stem for f in files} == {p.id for p in bank}


def test_ids_are_unique_and_well_formed(bank):
    ids = [p.id for p in bank]
    assert len(set(ids)) == len(ids)
    assert all(re.fullmatch(r"[A-Za-z0-9_]+", i) for i in ids)


def test_six_categories(bank):
    cats = all_categories()
    assert len(cats) == 6
    assert set(cats) == EXPECTED_CATEGORIES
    assert {p.category for p in bank} == EXPECTED_CATEGORIES
    for cat in EXPECTED_CATEGORIES:
        assert sum(p.category == cat for p in bank) >= 10


def test_required_fields_present(bank):
    for p in bank:
        assert p.difficulty in DIFFICULTIES, p.id
        assert p.question.strip(), p.id
        assert p.explanation.strip(), p.id
        assert isinstance(p.hints, list), p.id
        assert isinstance(p.grade_mode, GradeMode), p.id
    assert {p.difficulty for p in bank} == DIFFICULTIES


def test_auto_problems_are_checkable_and_claude_problems_are_open(bank):
    auto = [p for p in bank if p.grade_mode is GradeMode.AUTO]
    open_ = [p for p in bank if p.grade_mode is GradeMode.CLAUDE]
    assert len(auto) + len(open_) == len(bank)
    assert auto and open_
    for p in auto:
        assert len(p.choices) >= 2, p.id
        assert 0 <= p.correct_index < len(p.choices), p.id
        assert len(set(p.choices)) == len(p.choices), p.id
        assert all(c.strip() for c in p.choices), p.id
    for p in open_:
        assert p.choices == [] and p.correct_index == -1, p.id
