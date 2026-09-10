"""Problem and derivation bank loaders: counts, ids, required fields."""
from pathlib import Path

from core.models import Derivation, Problem
from derivations import all_derivations
from problems import all_problems, all_topics, problems_by_topic

APP_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PROBLEMS = 16
EXPECTED_DERIVATIONS = 7


def test_problem_bank_size_and_unique_ids(problems):
    assert len(problems) == EXPECTED_PROBLEMS
    ids = [p.id for p in problems]
    assert len(set(ids)) == len(ids)
    assert all(isinstance(p, Problem) for p in problems)


def test_derivation_bank_size_and_unique_ids(derivations):
    assert len(derivations) == EXPECTED_DERIVATIONS
    ids = [d.id for d in derivations]
    assert len(set(ids)) == len(ids)
    assert all(isinstance(d, Derivation) for d in derivations)
    assert all(d.id.startswith("deriv_") for d in derivations)


def test_ids_unique_across_both_banks_and_match_filenames(problems, derivations):
    prob_ids = {p.id for p in problems}
    deriv_ids = {d.id for d in derivations}
    assert not (prob_ids & deriv_ids)
    prob_stems = {f.stem for f in (APP_ROOT / "problems").glob("*/*.py") if f.stem != "__init__"}
    deriv_stems = {f.stem for f in (APP_ROOT / "derivations").glob("*.py") if f.stem != "__init__"}
    assert prob_ids == prob_stems
    assert deriv_ids == deriv_stems


def test_every_part_has_rubric_and_model_solution(problems):
    for p in problems:
        assert p.title.strip() and p.statement.strip() and p.topic.strip(), p.id
        assert p.parts, p.id
        part_ids = [pt.part_id for pt in p.parts]
        assert len(set(part_ids)) == len(part_ids), p.id
        for pt in p.parts:
            where = (p.id, pt.part_id)
            assert pt.prompt.strip(), where
            assert isinstance(pt.points, int) and pt.points > 0, where
            assert isinstance(pt.rubric, list) and pt.rubric, where
            assert all(isinstance(r, str) and r.strip() for r in pt.rubric), where
            assert isinstance(pt.model_solution, str) and pt.model_solution.strip(), where
        assert p.total_points == sum(pt.points for pt in p.parts) > 0


def test_every_step_has_prompt_expected_hint_model_step(derivations):
    for d in derivations:
        assert d.title.strip() and d.goal.strip(), d.id
        assert d.steps, d.id
        step_ids = [s.step_id for s in d.steps]
        assert len(set(step_ids)) == len(step_ids), d.id
        for s in d.steps:
            for field in ("prompt", "expected", "hint", "model_step"):
                value = getattr(s, field)
                assert isinstance(value, str) and value.strip(), (d.id, s.step_id, field)


def test_topics_and_topic_filter(problems):
    topics = all_topics()
    assert topics and len(set(topics)) == len(topics)
    assert set(topics) == {p.topic for p in problems}
    for topic in topics:
        subset = problems_by_topic([topic])
        assert subset and all(p.topic == topic for p in subset)
    assert {p.id for p in problems_by_topic(topics)} == {p.id for p in problems}
    assert problems_by_topic([]) == []
