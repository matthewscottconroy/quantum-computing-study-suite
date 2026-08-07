"""
Gate sequence problems: apply 2–4 gates in succession, find the output.
Answer: MULTIPLE_CHOICE (auto-graded).
"""

from __future__ import annotations
import random
from qiskit import QuantumCircuit
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import (
    SINGLE_QUBIT_GATES, INPUT_STATES, render_circuit,
    format_statevector, statevector_for_circuit, make_distractors,
)

# Interesting gate sequences with known identities
SEQUENCES = {
    "beginner": [
        ["H", "X", "H"],   # HXH = Z
        ["X", "X"],         # XX = I
        ["Z", "Z"],         # ZZ = I
        ["H", "H"],         # HH = I
        ["H", "Z", "H"],   # HZH = X
    ],
    "intermediate": [
        ["H", "S", "H"],
        ["S", "S"],         # SS = Z
        ["T", "T"],         # TT = S
        ["H", "T", "H"],
        ["X", "H", "X"],
        ["H", "S", "S", "H"],
    ],
    "advanced": [
        ["T", "T", "T", "T"],  # TTTT = Z
        ["H", "T", "H", "T", "H"],
        ["S", "H", "S"],
        ["T", "S", "T"],
        ["H", "S", "H", "S", "H"],
    ],
}


def generate(difficulty: str) -> Problem:
    seq = random.choice(SEQUENCES.get(difficulty, SEQUENCES["intermediate"]))
    input_name = random.choice(["|0⟩", "|1⟩"] if difficulty == "beginner"
                               else list(INPUT_STATES.keys())[:4])
    input_sv = INPUT_STATES[input_name]

    # Build circuit
    qc = QuantumCircuit(1, name="Gate sequence")
    for gate_name in seq:
        _, fn = SINGLE_QUBIT_GATES[gate_name]
        fn(qc, 0)

    output_sv = statevector_for_circuit(qc, input_sv)
    correct_str = format_statevector(output_sv, 1)

    distractors = make_distractors(correct_str, 3)
    choices = [correct_str] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct_str)

    gate_str = " → ".join(seq)

    steps = [
        f"Apply gates left to right: {gate_str}",
        f"Start with {input_name}.",
    ]
    for i, g in enumerate(seq):
        partial_qc = QuantumCircuit(1)
        for g2 in seq[:i+1]:
            _, fn = SINGLE_QUBIT_GATES[g2]
            fn(partial_qc, 0)
        sv = statevector_for_circuit(partial_qc, input_sv)
        steps.append(f"After {g}: {format_statevector(sv, 1)}")
    steps.append(f"Final output: {correct_str}")

    return Problem(
        category=ProblemCategory.GATE_SEQUENCE,
        difficulty=difficulty,
        question_text=(
            f"The following gates are applied in sequence to the state {input_name}:\n\n"
            f"  {gate_str}\n\n"
            f"What is the final output state?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Input: {input_name}",
        solution_steps=steps,
        key_concepts=["gate composition", "sequential application", "gate identities"],
    )
