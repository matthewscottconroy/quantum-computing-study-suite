"""
Entanglement detection problems.
Given a 2-qubit circuit, determine if the output is entangled or separable,
and identify the state.
Answer: MULTIPLE_CHOICE (auto-graded).
"""

from __future__ import annotations
import random
import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, entropy, DensityMatrix
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import render_circuit, format_statevector

BELL_STATES = [
    ("(1/√2)|00⟩ + (1/√2)|11⟩", "|Φ⁺⟩"),
    ("(1/√2)|00⟩ − (1/√2)|11⟩", "|Φ⁻⟩"),
    ("(1/√2)|01⟩ + (1/√2)|10⟩", "|Ψ⁺⟩"),
    ("(1/√2)|01⟩ − (1/√2)|10⟩", "|Ψ⁻⟩"),
]


def generate(difficulty: str) -> Problem:
    if difficulty == "beginner":
        return _basic_entanglement()
    elif difficulty == "intermediate":
        return _identify_bell_state()
    else:
        return _partial_entanglement()


def _basic_entanglement() -> Problem:
    # Randomly pick: entangled or separable
    entangled = random.choice([True, False])

    if entangled:
        qc = QuantumCircuit(2, name="Bell state circuit")
        qc.h(0)
        qc.cx(0, 1)
        sv = Statevector(qc)
        state_str = "(1/√2)|00⟩ + (1/√2)|11⟩"
        correct_idx = 0   # "Yes, entangled"
        steps = [
            "H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2",
            "CNOT(|+⟩⊗|0⟩) = (|00⟩+|11⟩)/√2",
            "This state CANNOT be written as |a⟩⊗|b⟩ → it is entangled.",
            "Entanglement entropy S = 1.0 bit (max for 2 qubits).",
        ]
    else:
        qc = QuantumCircuit(2, name="Separable circuit")
        qc.h(0)
        sv = Statevector(qc)
        state_str = "(1/√2)|00⟩ + (1/√2)|10⟩ = |+⟩⊗|0⟩"
        correct_idx = 1   # "No, separable"
        steps = [
            "H is applied to qubit 0 only. Qubit 1 stays in |0⟩.",
            "Output = |+⟩ ⊗ |0⟩ = (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2",
            "This factors as a tensor product → separable (not entangled).",
            "Entanglement entropy S = 0.",
        ]

    choices = ["Yes — the output is entangled", "No — the output is separable"]
    return Problem(
        category=ProblemCategory.ENTANGLEMENT,
        difficulty="beginner",
        question_text=(
            "Starting from |00⟩, is the output state of this circuit entangled?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Output: {state_str}",
        solution_steps=steps,
        key_concepts=["entanglement", "separability", "Bell states", "tensor product"],
    )


def _identify_bell_state() -> Problem:
    bell_idx = random.randint(0, 3)
    bell_circuits = [
        _make_bell(0), _make_bell(1), _make_bell(2), _make_bell(3)
    ]
    qc = bell_circuits[bell_idx]
    correct_label, correct_name = BELL_STATES[bell_idx]

    choices = [label for label, _ in BELL_STATES]
    correct_idx = bell_idx

    steps = [
        "Trace the circuit gate by gate.",
        f"Output: {correct_label} = {correct_name}",
        "The four Bell states differ by the initial X/Z gates before the H+CNOT.",
    ]

    return Problem(
        category=ProblemCategory.ENTANGLEMENT,
        difficulty="intermediate",
        question_text=(
            "Starting from |00⟩, which Bell state does this circuit produce?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Output: {correct_label}",
        solution_steps=steps,
        key_concepts=["Bell states", "Bell circuit", "entanglement"],
    )


def _partial_entanglement() -> Problem:
    alpha = round(random.choice([0.3, 0.6, 0.8]), 1)
    beta = round(math.sqrt(1 - alpha**2), 4)

    qc = QuantumCircuit(2, name="Partial entanglement")
    qc.ry(2 * math.acos(alpha), 0)
    qc.cx(0, 1)
    sv = Statevector(qc)

    dm = DensityMatrix(sv)
    rho_0 = partial_trace(dm, [1])
    ent = float(entropy(rho_0, base=2))
    ent_str = f"{ent:.4f} bits"

    correct_idx = 0  # answer: "Entangled (partial)"
    choices = [
        f"Entangled — S ≈ {ent:.3f} bits",
        "Separable — S = 0 bits",
        f"Maximally entangled — S = 1 bit",
        "Unknown without more information",
    ]

    steps = [
        f"RY({2*math.acos(alpha):.3f}) |0⟩ = {alpha:.2f}|0⟩ + {beta:.4f}|1⟩",
        f"CNOT produces: {alpha:.2f}|00⟩ + {beta:.4f}|11⟩",
        "Schmidt rank = 2 → entangled (partial, since coefficients are unequal).",
        f"Entanglement entropy S = {ent_str}",
    ]

    return Problem(
        category=ProblemCategory.ENTANGLEMENT,
        difficulty="advanced",
        question_text=(
            "Starting from |00⟩, classify the entanglement of the output state."
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer="0",
        choices=choices,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Output ≈ {alpha:.2f}|00⟩ + {beta:.4f}|11⟩, S = {ent_str}",
        solution_steps=steps,
        key_concepts=["Schmidt decomposition", "entanglement entropy", "partial trace"],
    )


def _make_bell(idx: int) -> QuantumCircuit:
    qc = QuantumCircuit(2, name=f"Bell {idx}")
    if idx in (1, 3):
        qc.x(0)
    if idx in (2, 3):
        qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    return qc
