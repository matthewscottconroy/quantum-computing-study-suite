"""
Measurement probability problems.
Given a circuit, find P(0) or P(1) on a specific qubit.
Answer: MULTIPLE_CHOICE (auto-graded).
"""

from __future__ import annotations
import random
import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import (
    render_circuit, statevector_for_circuit, make_prob_distractors,
    INPUT_STATES, SINGLE_QUBIT_GATES,
)


def generate(difficulty: str) -> Problem:
    if difficulty == "beginner":
        return _single_qubit_prob(difficulty)
    elif difficulty == "intermediate":
        return random.choice([_single_qubit_prob, _superposition_prob])(difficulty)
    else:
        return random.choice([_multi_qubit_prob, _superposition_prob])(difficulty)


def _single_qubit_prob(difficulty: str) -> Problem:
    gate_name = random.choice(["H", "X", "H", "Z", "S"])
    _, gate_fn = SINGLE_QUBIT_GATES[gate_name]
    input_name = random.choice(["|0⟩", "|1⟩"])
    input_sv = INPUT_STATES[input_name]

    qc = QuantumCircuit(1, name=f"{gate_name} gate")
    gate_fn(qc, 0)

    sv = statevector_for_circuit(qc, input_sv)
    probs = sv.probabilities()
    outcome = random.choice([0, 1])
    correct = round(float(probs[outcome]), 6)

    return _make_problem(
        qc=qc, sv=sv, qubit=0, qubit_label="the qubit",
        outcome=outcome, correct=correct,
        input_name=input_name, difficulty=difficulty,
        context=f"The {gate_name} gate is applied to {input_name}. "
                f"What is the probability of measuring |{outcome}⟩?",
    )


def _superposition_prob(difficulty: str) -> Problem:
    gate_name = random.choice(["H", "T", "S"])
    _, gate_fn = SINGLE_QUBIT_GATES[gate_name]
    input_name = "|+⟩" if difficulty != "beginner" else "|0⟩"
    input_sv = INPUT_STATES[input_name]

    qc = QuantumCircuit(1, name="Phase gate")
    gate_fn(qc, 0)

    sv = statevector_for_circuit(qc, input_sv)
    probs = sv.probabilities()
    outcome = random.choice([0, 1])
    correct = round(float(probs[outcome]), 6)

    return _make_problem(
        qc=qc, sv=sv, qubit=0, qubit_label="the qubit",
        outcome=outcome, correct=correct,
        input_name=input_name, difficulty=difficulty,
        context=f"Starting from {input_name}, the {gate_name} gate is applied. "
                f"What is P(|{outcome}⟩)?",
    )


def _multi_qubit_prob(difficulty: str) -> Problem:
    qc = QuantumCircuit(2, name="Two-qubit circuit")
    qc.h(0)
    qc.cx(0, 1)   # creates Bell state
    sv = statevector_for_circuit(qc)
    probs_q0 = sv.probabilities([0])
    outcome = random.choice([0, 1])
    correct = round(float(probs_q0[outcome]), 6)

    return _make_problem(
        qc=qc, sv=sv, qubit=0, qubit_label="qubit 0",
        outcome=outcome, correct=correct,
        input_name="|00⟩", difficulty=difficulty,
        context=(
            f"H is applied to qubit 0, then a CNOT with qubit 0 as control and qubit 1 as target, "
            f"starting from |00⟩. What is the probability of measuring |{outcome}⟩ on qubit 0?"
        ),
    )


def _make_problem(
    qc: QuantumCircuit, sv, qubit: int, qubit_label: str,
    outcome: int, correct: float, input_name: str,
    difficulty: str, context: str,
) -> Problem:
    distractors = [round(d, 6) for d in make_prob_distractors(correct, 3)]
    choices_f = [correct] + distractors
    random.shuffle(choices_f)
    choices = [f"{v:.4f}" if v not in (0.0, 0.25, 0.5, 0.75, 1.0)
               else {0.0:"0", 0.25:"1/4", 0.5:"1/2", 0.75:"3/4", 1.0:"1"}[v]
               for v in choices_f]
    correct_idx = next(i for i, v in enumerate(choices_f) if abs(v - correct) < 1e-9)

    steps = [
        f"1. Compute the output statevector starting from {input_name}.",
        f"2. The output state is: {_format_sv(sv)}",
        f"3. Probability of |{outcome}⟩ on {qubit_label} = sum of |amplitudes|² for basis states with qubit {qubit} = {outcome}.",
        f"4. P(|{outcome}⟩) = {correct:.4f}",
    ]

    return Problem(
        category=ProblemCategory.MEASUREMENT_PROBS,
        difficulty=difficulty,
        question_text=context,
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Input: {input_name}",
        solution_steps=steps,
        key_concepts=["Born rule", "measurement probability", "|amplitude|²"],
    )


def _format_sv(sv: Statevector) -> str:
    from problems._utils import format_statevector
    n = int(round(math.log2(len(sv))))
    return format_statevector(sv, n)
