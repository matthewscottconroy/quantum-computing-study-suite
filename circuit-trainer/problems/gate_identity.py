"""
Gate/matrix identification problems.
Show a matrix or describe gate action; identify the gate.
Answer: MULTIPLE_CHOICE (auto-graded).
"""

from __future__ import annotations
import random
import numpy as np
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import GATE_MATRICES, render_matrix


GATE_DESCRIPTIONS: dict[str, list[str]] = {
    "X": [
        "Maps |0⟩→|1⟩ and |1⟩→|0⟩. It is the quantum NOT gate.",
        "Has eigenvalues +1 and −1 with eigenstates |+⟩ and |−⟩.",
        "Rotates the Bloch sphere by π around the X axis.",
    ],
    "Y": [
        "Maps |0⟩→i|1⟩ and |1⟩→−i|0⟩.",
        "Has matrix entries entirely imaginary off-diagonal.",
        "Rotates the Bloch sphere by π around the Y axis.",
    ],
    "Z": [
        "Maps |0⟩→|0⟩ and |1⟩→−|1⟩. It is the phase-flip gate.",
        "Is diagonal with entries 1 and −1.",
        "Rotates the Bloch sphere by π around the Z axis.",
    ],
    "H": [
        "Transforms |0⟩ to (|0⟩+|1⟩)/√2 and |1⟩ to (|0⟩−|1⟩)/√2.",
        "Is its own inverse: H² = I.",
        "Transforms the Z basis to the X basis and vice versa.",
    ],
    "S": [
        "Applies a phase of i to |1⟩ and leaves |0⟩ unchanged.",
        "Its square equals Z: S² = Z.",
        "Has matrix diag(1, i).",
    ],
    "T": [
        "Applies a phase of e^(iπ/4) to |1⟩ and leaves |0⟩ unchanged.",
        "Its square equals S: T² = S.",
        "Has matrix diag(1, e^(iπ/4)).",
    ],
    "Sdg": [
        "Is the inverse of S: S·S† = I.",
        "Applies a phase of −i to |1⟩.",
        "Has matrix diag(1, −i).",
    ],
    "Tdg": [
        "Is the inverse of T: T·T† = I.",
        "Applies a phase of e^(−iπ/4) to |1⟩.",
        "Has matrix diag(1, e^(−iπ/4)).",
    ],
}

ALL_NAMES = list(GATE_MATRICES.keys())


def generate(difficulty: str) -> Problem:
    if difficulty == "beginner":
        pool = ["X", "Z", "H"]
    elif difficulty == "intermediate":
        pool = ["X", "Y", "Z", "H", "S"]
    else:
        pool = ALL_NAMES

    correct_name = random.choice(pool)

    # Choose: matrix display or description
    use_matrix = random.choice([True, False]) if difficulty != "beginner" else True

    if use_matrix:
        return _matrix_problem(correct_name, pool, difficulty)
    else:
        return _description_problem(correct_name, pool, difficulty)


def _matrix_problem(correct_name: str, pool: list[str], difficulty: str) -> Problem:
    matrix = GATE_MATRICES[correct_name]
    matrix_str = render_matrix(matrix, label=f"Matrix M:")

    wrong_names = [n for n in ALL_NAMES if n != correct_name]
    random.shuffle(wrong_names)
    distractors = wrong_names[:3]
    choices_names = [correct_name] + distractors
    random.shuffle(choices_names)
    correct_idx = choices_names.index(correct_name)

    steps = [
        "Inspect the diagonal and off-diagonal entries.",
        _matrix_hint(correct_name),
        f"The gate is: {correct_name}",
    ]

    return Problem(
        category=ProblemCategory.GATE_IDENTITY,
        difficulty=difficulty,
        question_text="Which single-qubit gate has this matrix?",
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices_names,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=matrix_str,
        state_str=None,
        solution_steps=steps,
        key_concepts=["gate matrices", "Pauli gates", "phase gates"],
        problem_id=f"gi:matrix:{correct_name}",
    )


def _description_problem(correct_name: str, pool: list[str], difficulty: str) -> Problem:
    desc = random.choice(GATE_DESCRIPTIONS.get(correct_name, ["Applies a phase to |1⟩."]))

    wrong_names = [n for n in ALL_NAMES if n != correct_name]
    random.shuffle(wrong_names)
    distractors = wrong_names[:3]
    choices_names = [correct_name] + distractors
    random.shuffle(choices_names)
    correct_idx = choices_names.index(correct_name)

    steps = [
        f"The description says: '{desc}'",
        _matrix_hint(correct_name),
        f"Answer: {correct_name}",
    ]

    return Problem(
        category=ProblemCategory.GATE_IDENTITY,
        difficulty=difficulty,
        question_text=f"Which single-qubit gate is described by the following?\n\n\"{desc}\"",
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices_names,
        circuit_png=None,
        aux_circuit_png=None,
        matrix_str=render_matrix(GATE_MATRICES[correct_name], "Gate matrix:"),
        state_str=None,
        solution_steps=steps,
        key_concepts=["gate identification", "gate properties"],
        problem_id=f"gi:desc:{correct_name}",
    )


def _matrix_hint(name: str) -> str:
    hints = {
        "X":   "X is the Pauli-X (NOT) gate: [[0,1],[1,0]].",
        "Y":   "Y is the Pauli-Y gate: [[0,−i],[i,0]].",
        "Z":   "Z is the Pauli-Z gate: diag(1,−1).",
        "H":   "H has all entries ±1/√2.",
        "S":   "S = diag(1, i). Note i = e^(iπ/2).",
        "T":   "T = diag(1, e^(iπ/4)). The π/8 gate.",
        "Sdg": "S† = diag(1, −i) — the conjugate transpose of S.",
        "Tdg": "T† = diag(1, e^(−iπ/4)) — conjugate transpose of T.",
    }
    return hints.get(name, "")
