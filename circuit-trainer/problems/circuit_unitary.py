"""
Circuit unitary problems: compute the overall 2×2 or 4×4 unitary matrix.
Answer: MULTIPLE_CHOICE — choose the correct matrix.
"""

from __future__ import annotations
import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import (
    SINGLE_QUBIT_GATES, GATE_MATRICES, render_circuit, render_matrix,
)

KNOWN_COMPOSITES: list[tuple[list[str], str, np.ndarray]] = [
    (["H", "H"],    "I (identity)",  np.eye(2, dtype=complex)),
    (["X", "X"],    "I (identity)",  np.eye(2, dtype=complex)),
    (["Z", "Z"],    "I (identity)",  np.eye(2, dtype=complex)),
    (["S", "S"],    "Z",             GATE_MATRICES["Z"]),
    (["T", "T"],    "S",             GATE_MATRICES["S"]),
    (["H", "Z", "H"], "X",          GATE_MATRICES["X"]),
    (["H", "X", "H"], "Z",          GATE_MATRICES["Z"]),
    (["S", "S", "S", "S"], "I",     np.eye(2, dtype=complex)),
]


def generate(difficulty: str) -> Problem:
    if difficulty in ("beginner", "intermediate"):
        return _known_composite(difficulty)
    else:
        return _arbitrary_sequence(difficulty)


def _known_composite(difficulty: str) -> Problem:
    seq, name, correct_mat = random.choice(KNOWN_COMPOSITES)

    qc = QuantumCircuit(1, name=" ".join(seq))
    for g in seq:
        _, fn = SINGLE_QUBIT_GATES[g]
        fn(qc, 0)

    # Build 3 wrong matrices
    wrong_names = ["X", "Y", "Z", "H", "S", "T", "Sdg", "Tdg", "I (identity)"]
    wrong_names = [n for n in wrong_names if n != name]
    wrong_mats_names = random.sample(wrong_names, 3)
    wrong_mats = []
    for wn in wrong_mats_names:
        if wn == "I (identity)":
            wrong_mats.append(np.eye(2, dtype=complex))
        else:
            wrong_mats.append(GATE_MATRICES.get(wn, GATE_MATRICES["X"]))

    choices_data = [(correct_mat, name)] + [(m, n) for m, n in zip(wrong_mats, wrong_mats_names)]
    random.shuffle(choices_data)
    correct_idx = next(i for i, (_, n) in enumerate(choices_data) if n == name)

    choices_str = [n for _, n in choices_data]
    gate_str = " → ".join(seq)

    steps = [
        f"Multiply the gate matrices right-to-left: U = {' · '.join(reversed(seq))}",
        f"The composition {gate_str} equals the {name} matrix.",
        "Key identities to memorise:",
        "  H·H = I,   X·X = I,   S·S = Z,   T·T = S,   H·Z·H = X",
    ]

    return Problem(
        category=ProblemCategory.CIRCUIT_UNITARY,
        difficulty=difficulty,
        question_text=(
            f"What is the combined unitary matrix of the following gate sequence?\n\n"
            f"  {gate_str}"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices_str,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=render_matrix(correct_mat, f"Correct matrix ({name}):"),
        state_str=None,
        solution_steps=steps,
        key_concepts=["matrix multiplication", "gate identities", "unitary composition"],
    )


def _arbitrary_sequence(difficulty: str) -> Problem:
    n_gates = random.randint(2, 3)
    gate_names = random.choices(list(SINGLE_QUBIT_GATES.keys()), k=n_gates)

    qc = QuantumCircuit(1, name=" ".join(gate_names))
    for g in gate_names:
        _, fn = SINGLE_QUBIT_GATES[g]
        fn(qc, 0)

    correct_mat = np.array(Operator(qc).data)
    correct_str = render_matrix(correct_mat, "Correct:")

    # Build distractors by swapping one gate
    distractors = []
    for _ in range(3):
        alt_names = gate_names[:]
        alt_names[random.randrange(len(alt_names))] = random.choice(
            [g for g in SINGLE_QUBIT_GATES if g != alt_names[0]]
        )
        alt_qc = QuantumCircuit(1)
        for g in alt_names:
            _, fn = SINGLE_QUBIT_GATES[g]
            fn(alt_qc, 0)
        alt_mat = np.array(Operator(alt_qc).data)
        distractors.append(render_matrix(alt_mat, "Option:"))

    choices_data = [correct_str] + distractors
    random.shuffle(choices_data)
    correct_idx = choices_data.index(correct_str)

    steps = [
        f"Multiply matrices right-to-left: U = {'·'.join(reversed(gate_names))}",
        "Step-by-step:",
        *[f"  After {gate_names[:i+1]}: partial product computed" for i in range(n_gates)],
        f"Final unitary shown in the answer.",
    ]

    return Problem(
        category=ProblemCategory.CIRCUIT_UNITARY,
        difficulty=difficulty,
        question_text=(
            f"Compute the unitary matrix for the gate sequence:\n\n"
            f"  {' → '.join(gate_names)}\n\n"
            f"Which matrix is correct?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=[f"Matrix {i+1}" for i in range(4)],
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str="\n\n".join(choices_data),
        state_str=None,
        solution_steps=steps,
        key_concepts=["matrix multiplication", "gate unitary", "operator composition"],
    )
