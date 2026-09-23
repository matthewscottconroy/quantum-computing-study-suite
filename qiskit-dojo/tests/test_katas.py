"""Kata bank loader: counts, ids, required fields, conventions, set building.

The bank was rebalanced toward the C1000-179 exam blueprint in Sep 2026
(36 -> 72 katas).  Counts are asserted as FLOORS so that adding katas never
breaks the suite, while silently losing one (an import error is swallowed
by the loader) does.
"""
from __future__ import annotations

import importlib
from collections import Counter
from pathlib import Path

import pytest

from core.models import DojoConfig, Kata
from katas import SECTION_ORDER, all_katas, all_sections, build_kata_set

# Minimum katas per section (the exam-blueprint targets). Adding more is fine.
SECTION_TARGETS = {
    "Create circuits": 10,
    "Quantum operations": 9,
    "Run circuits": 8,
    "Sampler": 7,
    "Estimator": 7,
    "Visualization": 6,
    "Results analysis": 6,
    "OpenQASM": 3,
    "Debugging": 8,
    "Modernization": 8,
}
MIN_KATA_COUNT = 72
assert sum(SECTION_TARGETS.values()) == MIN_KATA_COUNT  # keep the constants honest

DIFFICULTIES = {"beginner", "intermediate", "advanced"}
TEXT_FIELDS = ("id", "section", "title", "difficulty", "prompt",
               "starter_code", "test_code", "solution_code")
MIN_HINTS, MAX_HINTS = 2, 3
# Sections whose starter is deliberately broken; their titles announce it.
FIX_IT_TITLE_PREFIX = {"Debugging": "Fix it:", "Modernization": "Modernize:"}
KATAS_DIR = Path(__file__).resolve().parent.parent / "katas"


def _kata_files() -> list[Path]:
    return sorted(p for p in KATAS_DIR.glob("*/*.py") if p.stem != "__init__")


def _section_dir_name(section: str) -> str:
    """'Results analysis' -> 'results_analysis' (the katas/ layout convention)."""
    return section.lower().replace(" ", "_")


# --------------------------------------------------------------------------- #
# Bank size and identity
# --------------------------------------------------------------------------- #

def test_bank_size_and_unique_ids(katas):
    assert len(katas) >= MIN_KATA_COUNT, (
        f"bank shrank to {len(katas)} katas (expected at least {MIN_KATA_COUNT})")
    ids = [k.id for k in katas]
    dupes = sorted(i for i, n in Counter(ids).items() if n > 1)
    assert not dupes, f"duplicate kata ids: {dupes}"


def test_section_targets_cover_every_curriculum_section():
    assert set(SECTION_TARGETS) == set(SECTION_ORDER), (
        "SECTION_TARGETS and katas.SECTION_ORDER disagree - update one of them")


@pytest.mark.parametrize("section", list(SECTION_ORDER))
def test_section_meets_blueprint_target(katas, section):
    have = [k.id for k in katas if k.section == section]
    want = SECTION_TARGETS[section]
    assert len(have) >= want, (
        f"{section!r} has {len(have)} katas, blueprint target is {want}: {have}")


def test_every_kata_file_loads(katas):
    """The loader swallows import errors, so a kata with a typo simply vanishes.
    Catch that here and surface the real exception."""
    loaded = {k.id for k in katas}
    problems = []
    for path in _kata_files():
        if path.stem in loaded:
            continue
        mod_name = f"katas.{path.parent.name}.{path.stem}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:  # noqa: BLE001 - we want the message
            problems.append(f"{path.relative_to(KATAS_DIR)}: {type(exc).__name__}: {exc}")
        else:
            if not hasattr(mod, "KATA"):
                problems.append(f"{path.relative_to(KATAS_DIR)}: no KATA object")
            else:
                problems.append(f"{path.relative_to(KATAS_DIR)}: KATA.id "
                                f"{mod.KATA.id!r} != filename stem {path.stem!r}")
    assert not problems, "kata files that did not make it into the bank:\n" + "\n".join(problems)


def test_ids_match_filenames(katas):
    stems = {p.stem for p in _kata_files()}
    assert {k.id for k in katas} == stems


def test_kata_lives_in_its_section_directory(katas):
    """katas/<section_dir>/<id>.py - a kata filed under the wrong directory
    would still load, but the README's layout promise would be broken."""
    dir_of = {p.stem: p.parent.name for p in _kata_files()}
    misfiled = [(k.id, dir_of[k.id], k.section) for k in katas
                if dir_of[k.id] != _section_dir_name(k.section)]
    assert not misfiled, f"(id, directory, section) mismatches: {misfiled}"


# --------------------------------------------------------------------------- #
# Per-kata content
# --------------------------------------------------------------------------- #

def test_every_kata_has_all_fields(katas):
    for k in katas:
        assert isinstance(k, Kata)
        for field in TEXT_FIELDS:
            value = getattr(k, field)
            assert isinstance(value, str) and value.strip(), (k.id, field)
        assert k.difficulty in DIFFICULTIES, (k.id, k.difficulty)
        assert k.section in SECTION_ORDER, (k.id, k.section)


def test_every_kata_has_two_to_three_distinct_hints(katas):
    bad = []
    for k in katas:
        hints = k.hints
        ok = (isinstance(hints, list)
              and MIN_HINTS <= len(hints) <= MAX_HINTS
              and all(isinstance(h, str) and h.strip() for h in hints)
              and len({h.strip() for h in hints}) == len(hints))
        if not ok:
            bad.append((k.id, hints))
    assert not bad, f"katas with missing/duplicate/out-of-range hints: {bad}"


def test_titles_are_unique(katas):
    titles = Counter(k.title.strip() for k in katas)
    dupes = sorted(t for t, n in titles.items() if n > 1)
    assert not dupes, f"duplicate kata titles: {dupes}"


def test_fix_it_sections_announce_themselves_in_the_title(katas):
    wrong = [(k.id, k.title) for k in katas
             if k.section in FIX_IT_TITLE_PREFIX
             and not k.title.startswith(FIX_IT_TITLE_PREFIX[k.section])]
    assert not wrong, f"Debugging/Modernization titles must start with 'Fix it:'/'Modernize:': {wrong}"


def test_test_code_contains_assertions(katas):
    missing = [k.id for k in katas if "assert" not in k.test_code]
    assert not missing, f"test_code with no assert cannot fail: {missing}"


def test_solution_differs_from_starter(katas):
    same = [k.id for k in katas if k.solution_code.strip() == k.starter_code.strip()]
    assert not same, f"solution identical to starter (nothing to learn): {same}"


@pytest.mark.parametrize("field", ["starter_code", "test_code", "solution_code"])
def test_kata_code_compiles(katas, field):
    for k in katas:
        compile(getattr(k, field), f"{k.id}:{field}", "exec")


def test_bank_spans_all_difficulties(katas):
    present = {k.difficulty for k in katas}
    assert present == DIFFICULTIES, f"difficulty levels missing from the bank: {DIFFICULTIES - present}"


# --------------------------------------------------------------------------- #
# Section listing and set building
# --------------------------------------------------------------------------- #

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


def test_build_kata_set_can_serve_the_whole_bank(data_dir, katas):
    """Asking for more katas than exist returns every kata exactly once."""
    cfg = DojoConfig(sections=list(SECTION_ORDER), kata_count=len(katas) + 10)
    chosen = build_kata_set(cfg)
    assert sorted(k.id for k in chosen) == sorted(k.id for k in katas)


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
