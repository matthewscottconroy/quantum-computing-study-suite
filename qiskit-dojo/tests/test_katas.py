"""Kata bank loader: counts, ids, required fields, and set building."""
from pathlib import Path

import pytest

from core.models import DojoConfig, Kata
from katas import SECTION_ORDER, all_katas, all_sections, build_kata_set

EXPECTED_KATA_COUNT = 36
DIFFICULTIES = {"beginner", "intermediate", "advanced"}
TEXT_FIELDS = ("id", "section", "title", "difficulty", "prompt",
               "starter_code", "test_code", "solution_code")
KATAS_DIR = Path(__file__).resolve().parent.parent / "katas"


def test_bank_size_and_unique_ids(katas):
    assert len(katas) == EXPECTED_KATA_COUNT
    ids = [k.id for k in katas]
    assert len(set(ids)) == len(ids)


def test_ids_match_filenames(katas):
    stems = {p.stem for p in KATAS_DIR.glob("*/*.py") if p.stem != "__init__"}
    assert {k.id for k in katas} == stems


def test_every_kata_has_all_fields(katas):
    for k in katas:
        assert isinstance(k, Kata)
        for field in TEXT_FIELDS:
            value = getattr(k, field)
            assert isinstance(value, str) and value.strip(), (k.id, field)
        assert k.difficulty in DIFFICULTIES, k.id
        assert k.section in SECTION_ORDER, k.id
        assert isinstance(k.hints, list) and k.hints, k.id
        assert all(isinstance(h, str) and h.strip() for h in k.hints), k.id


@pytest.mark.parametrize("field", ["starter_code", "test_code", "solution_code"])
def test_kata_code_compiles(katas, field):
    for k in katas:
        compile(getattr(k, field), f"{k.id}:{field}", "exec")


def test_all_sections_follow_curriculum_order(katas):
    sections = all_sections()
    assert sections == [s for s in SECTION_ORDER if s in sections]
    assert set(sections) == {k.section for k in katas}
    assert set(SECTION_ORDER) <= set(sections)  # every curriculum area is populated


def test_build_kata_set_respects_count_and_sections(data_dir):
    cfg = DojoConfig(sections=["Sampler", "Estimator"], kata_count=4)
    for _ in range(5):
        chosen = build_kata_set(cfg)
        assert len(chosen) == 4
        assert len({k.id for k in chosen}) == 4
        assert all(k.section in cfg.sections for k in chosen)


def test_build_kata_set_caps_at_pool_size(data_dir):
    pool_ids = {k.id for k in all_katas() if k.section == "OpenQASM"}
    chosen = build_kata_set(DojoConfig(sections=["OpenQASM"], kata_count=50))
    assert {k.id for k in chosen} == pool_ids


def test_build_kata_set_curriculum_order_when_not_shuffled(data_dir):
    cfg = DojoConfig(sections=list(SECTION_ORDER), kata_count=12, shuffle=False)
    chosen = build_kata_set(cfg)
    rank = {s: i for i, s in enumerate(SECTION_ORDER)}
    keys = [(rank[k.section], k.id) for k in chosen]
    assert len(keys) == 12
    assert keys == sorted(keys)


def test_build_kata_set_empty_selection(data_dir):
    assert build_kata_set(DojoConfig(sections=[], kata_count=5)) == []
    assert build_kata_set(DojoConfig(sections=["No such section"], kata_count=5)) == []
