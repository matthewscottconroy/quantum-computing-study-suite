"""Every noise generator: 4 distinct choices, the key present exactly once, and
the worked-solution text says what the numbers say.

Regression for the p = 0.5 draws of _phase_flip_z_basis (3 choices with a
duplicated 0.25) and _bit_flip_on_plus (random fill duplicating the key)."""
from __future__ import annotations

import random

import pytest

from core.models import AnswerFormat, ProblemCategory
from problems import noise

GENERATORS = [
    noise._bit_flip_prob,
    noise._phase_flip_z_basis,
    noise._bit_flip_on_plus,
    noise._phase_flip_x_basis,
    noise._depolarizing_density_00,
    noise._depolarizing_on_bell,
    noise._two_qubit_depolarizing,
    noise._repeated_bit_flip,
    noise._amplitude_damping_00,
    noise._identify_kraus,
    noise._t1_excited_state,
    noise._amplitude_damping_superposition,
]
DRAWS = 200


@pytest.mark.parametrize("gen", GENERATORS, ids=lambda g: g.__name__)
def test_four_distinct_choices_and_key_appears_once(gen):
    random.seed(20260909)
    for _ in range(DRAWS):
        p = gen()
        assert p.category is ProblemCategory.NOISE_CHANNEL
        assert p.answer_format is AnswerFormat.MULTIPLE_CHOICE
        assert len(p.choices) == 4, p.choices
        assert len(set(p.choices)) == 4, p.choices
        key = p.choices[int(p.correct_answer)]
        assert p.choices.count(key) == 1, p.choices
        if gen is not noise._identify_kraus:
            assert 0.0 <= float(key) <= 1.0
            assert all(0.0 <= float(c) <= 1.0 for c in p.choices), p.choices


def test_phase_flip_z_basis_at_p_half_has_four_distinct_choices(monkeypatch):
    monkeypatch.setattr(noise.random, "choice", lambda seq: 0.5 if 0.5 in seq else seq[0])
    p = noise._phase_flip_z_basis()
    assert sorted(float(c) for c in p.choices) == sorted([0.5, 0.25, 0.75, 1.0])
    assert p.choices[int(p.correct_answer)] == "0.5"


def test_bit_flip_on_plus_at_p_half_has_four_distinct_choices(monkeypatch):
    monkeypatch.setattr(noise.random, "choice", lambda seq: 0.5 if 0.5 in seq else seq[0])
    p = noise._bit_flip_on_plus()
    assert sorted(float(c) for c in p.choices) == sorted([0.5, 0.75, 0.25, 0.0])
    assert p.choices[int(p.correct_answer)] == "0.5"


def test_distinct_distractors_helper():
    assert noise._distinct_distractors(0.5, [0.5, 0.5, 0.25, 0.25, 0.75, 1.0]) == [0.25, 0.75, 1.0]
    assert noise._distinct_distractors(0.1, [0.9, 0.1, 0.55], n=2) == [0.9, 0.55]
    assert noise._distinct_distractors(0.3, [0.3]) == []


def test_repeated_bit_flip_solution_states_the_inequality_correctly():
    random.seed(1)
    for _ in range(12):
        p = noise._repeated_bit_flip()
        text = " ".join(p.solution_steps)
        assert "p_eff < p" not in text
        assert "p_eff = 2p(1-p) > p" in text
        # and the numbers agree with the claim: p_eff > p for the p values used
        p_val = float(p.state_str.split("p = ")[1])
        assert float(p.choices[int(p.correct_answer)]) > p_val


def test_amplitude_damping_00_derivation_uses_the_right_kraus_entry():
    random.seed(2)
    for _ in range(6):
        p = noise._amplitude_damping_00()
        text = " ".join(p.solution_steps)
        assert "K₁[0,0]²" not in text
        assert "|K₁[0,1]|²·ρ[1,1]" in text


def test_identify_kraus_depolarizing_label_matches_module_convention():
    """Weights 0.7 / 0.1 are p = 0.4 in E(ρ) = (1-p)ρ + p·I/2, the convention
    every other depolarizing problem in noise.py uses."""
    random.seed(4)
    seen = set()
    for _ in range(40):
        p = noise._identify_kraus()
        seen.add(p.problem_id)
        depol = [c for c in p.choices if c.startswith("Depolarizing")]
        assert len(depol) == 1
        assert "p = 0.4" in depol[0] and "0.1" in depol[0]
        assert "p = 0.3" not in depol[0]
        assert p.problem_id.startswith("noise:kraus:")
    assert seen == {"noise:kraus:bitflip", "noise:kraus:phaseflip",
                    "noise:kraus:ampdamp", "noise:kraus:depol"}
