"""
Single-gate output problems.
Given one gate applied to a known input state, find the output state.
Answer format: MULTIPLE_CHOICE (auto-graded).
"""

from __future__ import annotations
import random
from qiskit import QuantumCircuit
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import (
    SINGLE_QUBIT_GATES, INPUT_STATES, render_circuit,
    format_statevector, statevector_for_circuit, make_distractors,
)


def generate(difficulty: str) -> Problem:
    if difficulty == "beginner":
        gate_name = random.choice(["X", "H", "Z"])
        input_name = random.choice(["|0⟩", "|1⟩"])
    elif difficulty == "intermediate":
        gate_name = random.choice(["X", "Y", "Z", "H", "S", "T", "Sdg", "Tdg",
                                    "Rx(π/2)", "Ry(π/2)", "Rz(π/2)"])
        input_name = random.choice(["|0⟩", "|1⟩", "|+⟩", "|−⟩"])
    else:
        gate_name = random.choice(["S", "T", "Sdg", "Tdg", "Y",
                                    "Rx(π/4)", "Rx(π/2)", "Ry(π/4)", "Ry(π/2)",
                                    "Rz(π/4)", "Rz(π/2)"])
        input_name = random.choice(list(INPUT_STATES.keys()))

    gate_label, gate_fn = SINGLE_QUBIT_GATES[gate_name]
    input_sv = INPUT_STATES[input_name]

    # Build circuit
    qc = QuantumCircuit(1, name=f"{gate_name} gate")
    gate_fn(qc, 0)

    # Compute output
    output_sv = statevector_for_circuit(qc, input_sv)
    correct_str = format_statevector(output_sv, 1)

    # Build choices
    distractors = make_distractors(correct_str, 3)
    choices = [correct_str] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct_str)

    # Solution steps
    steps = _solution_steps(gate_name, input_name, correct_str, difficulty)

    return Problem(
        category=ProblemCategory.SINGLE_GATE_OUTPUT,
        difficulty=difficulty,
        question_text=(
            f"The {gate_label} gate is applied to the state {input_name}.\n\n"
            f"What is the output state?"
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Input: {input_name}",
        solution_steps=steps,
        key_concepts=[f"{gate_name} gate action", "single-qubit state evolution"],
    )


def _solution_steps(gate: str, inp: str, out: str, difficulty: str) -> list[str]:
    steps_map: dict[str, dict[str, list[str]]] = {
        "X": {
            "|0⟩": ["X|0⟩ flips the bit.", "X|0⟩ = |1⟩"],
            "|1⟩": ["X|1⟩ flips the bit.", "X|1⟩ = |0⟩"],
            "|+⟩": ["X|+⟩: X maps |0⟩↔|1⟩, so the + superposition is unchanged.", "X|+⟩ = |+⟩"],
            "|−⟩": ["X swaps |0⟩ and |1⟩, which flips the sign of |−⟩.", "X|−⟩ = −|−⟩"],
        },
        "H": {
            "|0⟩": ["H|0⟩ = (|0⟩+|1⟩)/√2", "This is the |+⟩ state."],
            "|1⟩": ["H|1⟩ = (|0⟩−|1⟩)/√2", "This is the |−⟩ state."],
            "|+⟩": ["H is its own inverse: H|+⟩ = H·H|0⟩ = |0⟩"],
            "|−⟩": ["H·H|1⟩ = |1⟩, so H|−⟩ = |1⟩"],
        },
        "Z": {
            "|0⟩": ["Z|0⟩ = |0⟩ — the |0⟩ state is a Z eigenstate with eigenvalue +1."],
            "|1⟩": ["Z|1⟩ = −|1⟩ — the |1⟩ state is a Z eigenstate with eigenvalue −1."],
            "|+⟩": ["Z flips phase of |1⟩ component: (|0⟩+|1⟩)/√2 → (|0⟩−|1⟩)/√2 = |−⟩"],
            "|−⟩": ["Z flips phase of |1⟩: (|0⟩−|1⟩)/√2 → (|0⟩+|1⟩)/√2 = |+⟩"],
        },
        "Y": {
            "|0⟩": [
                "Y = [[0,−i],[i,0]]. Apply column 0: Y|0⟩ = [0, i]ᵀ = i|1⟩.",
                "The global phase i is unobservable; the state points to |1⟩ on the Bloch sphere.",
            ],
            "|1⟩": [
                "Y|1⟩: column 1 of Y gives [−i, 0]ᵀ = −i|0⟩.",
                "Result is −i|0⟩ — same measurement outcome as |0⟩.",
            ],
            "|+⟩": [
                "Y|+⟩ = (Y|0⟩ + Y|1⟩)/√2 = (i|1⟩ − i|0⟩)/√2 = i(|1⟩ − |0⟩)/√2.",
                "= −i(|0⟩ − |1⟩)/√2 = −i|−⟩.",
                "Up to global phase, Y maps |+⟩ to |−⟩.",
            ],
            "|−⟩": [
                "Y|−⟩ = (Y|0⟩ − Y|1⟩)/√2 = (i|1⟩ + i|0⟩)/√2 = i(|0⟩ + |1⟩)/√2 = i|+⟩.",
                "Up to global phase, Y maps |−⟩ to |+⟩.",
            ],
        },
        "S": {
            "|0⟩": [
                "S = [[1,0],[0,i]]. S|0⟩ = |0⟩.",
                "|0⟩ is the +1 eigenstate of S — it is unaffected.",
            ],
            "|1⟩": [
                "S|1⟩ = i|1⟩. S adds a phase of i = e^{iπ/2} to the |1⟩ component.",
                "|1⟩ is the i-eigenstate of S.",
            ],
            "|+⟩": [
                "S|+⟩ = (S|0⟩ + S|1⟩)/√2 = (|0⟩ + i|1⟩)/√2.",
                "This is the +Y eigenstate (|R⟩ on the Bloch sphere).",
                "S rotates |+⟩ by 90° around the Z-axis toward the +Y pole.",
            ],
            "|−⟩": [
                "S|−⟩ = (|0⟩ − i|1⟩)/√2.",
                "This is the −Y eigenstate (|L⟩ on the Bloch sphere).",
            ],
        },
        "Sdg": {
            "|0⟩": [
                "Sdg = S† = [[1,0],[0,−i]]. Sdg|0⟩ = |0⟩.",
            ],
            "|1⟩": [
                "Sdg|1⟩ = −i|1⟩. Sdg is the inverse of S: applies phase −i to |1⟩.",
            ],
            "|+⟩": [
                "Sdg|+⟩ = (|0⟩ − i|1⟩)/√2 = |L⟩ (−Y eigenstate).",
                "Sdg rotates |+⟩ by −90° around Z.",
            ],
            "|−⟩": [
                "Sdg|−⟩ = (|0⟩ + i|1⟩)/√2 = |R⟩ (+Y eigenstate).",
            ],
        },
        "T": {
            "|0⟩": [
                "T = [[1,0],[0,e^{iπ/4}]]. T|0⟩ = |0⟩.",
                "T is the π/8 gate: it adds a phase of e^{iπ/4} = (1+i)/√2 to the |1⟩ component only.",
            ],
            "|1⟩": [
                "T|1⟩ = e^{iπ/4}|1⟩ = [(1+i)/√2]|1⟩.",
                "e^{iπ/4} = cos(π/4) + i·sin(π/4) ≈ 0.707 + 0.707i.",
            ],
            "|+⟩": [
                "T|+⟩ = (T|0⟩ + T|1⟩)/√2 = (|0⟩ + e^{iπ/4}|1⟩)/√2.",
                "This state lies 45° between |+⟩ and |+Y⟩ on the Bloch sphere equator.",
            ],
            "|−⟩": [
                "T|−⟩ = (|0⟩ − e^{iπ/4}|1⟩)/√2.",
                "The |1⟩ component picks up the extra phase e^{iπ/4}.",
            ],
        },
        "Tdg": {
            "|0⟩": [
                "Tdg = T† = [[1,0],[0,e^{−iπ/4}]]. Tdg|0⟩ = |0⟩.",
            ],
            "|1⟩": [
                "Tdg|1⟩ = e^{−iπ/4}|1⟩ = [(1−i)/√2]|1⟩.",
                "Tdg is the inverse of T: applies phase e^{−iπ/4}.",
            ],
            "|+⟩": [
                "Tdg|+⟩ = (|0⟩ + e^{−iπ/4}|1⟩)/√2.",
                "e^{−iπ/4} = (1−i)/√2 — the |1⟩ component is rotated −45° in phase.",
            ],
            "|−⟩": [
                "Tdg|−⟩ = (|0⟩ − e^{−iπ/4}|1⟩)/√2.",
            ],
        },
        "Rx(π/2)": {
            "|0⟩": [
                "Rx(θ) = [[cos(θ/2), −i·sin(θ/2)], [−i·sin(θ/2), cos(θ/2)]].",
                "Rx(π/2)|0⟩ = cos(π/4)|0⟩ − i·sin(π/4)|1⟩ = (|0⟩ − i|1⟩)/√2.",
                "This is the −Y eigenstate on the Bloch sphere.",
            ],
            "|1⟩": [
                "Rx(π/2)|1⟩ = −i·sin(π/4)|0⟩ + cos(π/4)|1⟩ = (−i|0⟩ + |1⟩)/√2.",
            ],
            "|+⟩": [
                "Rx(π/2) rotates 90° around the X-axis.",
                "|+⟩ (equator, +X) is a fixed point of Rx — it only picks up a global phase.",
                "Rx(π/2)|+⟩ = e^{−iπ/4}|+⟩ (global phase).",
            ],
            "|−⟩": [
                "Rx(π/2) rotates 90° around X. |−⟩ is also an Rx eigenstate (with eigenvalue e^{iπ/4}).",
                "Rx(π/2)|−⟩ = e^{iπ/4}|−⟩.",
            ],
        },
        "Ry(π/2)": {
            "|0⟩": [
                "Ry(θ) = [[cos(θ/2), −sin(θ/2)], [sin(θ/2), cos(θ/2)]].",
                "Ry(π/2)|0⟩ = cos(π/4)|0⟩ + sin(π/4)|1⟩ = (|0⟩ + |1⟩)/√2 = |+⟩.",
                "Ry(π/2) rotates from the north pole to the +X equator — same output as H|0⟩!",
            ],
            "|1⟩": [
                "Ry(π/2)|1⟩ = −sin(π/4)|0⟩ + cos(π/4)|1⟩ = (−|0⟩ + |1⟩)/√2.",
                "This state is on the equator in the −X direction.",
            ],
            "|+⟩": [
                "Ry(π/2) rotates 90° around the Y-axis.",
                "|+⟩ (equator, +X) rotates toward the south pole (|1⟩).",
                "Ry(π/2)|+⟩ = (|0⟩ + |1⟩·cos − |0⟩·sin)/√2 ... result points toward |1⟩.",
            ],
            "|−⟩": [
                "Ry(π/2) rotates |−⟩ (−X equator) by 90° around Y toward the north pole.",
                "Result points toward |0⟩.",
            ],
        },
        "Rz(π/2)": {
            "|0⟩": [
                "Rz(θ) = [[e^{−iθ/2}, 0], [0, e^{iθ/2}]].",
                "Rz(π/2)|0⟩ = e^{−iπ/4}|0⟩ — only a global phase (unobservable).",
                "|0⟩ is on the Z-axis; Rz does not move it, only adds a global phase.",
            ],
            "|1⟩": [
                "Rz(π/2)|1⟩ = e^{iπ/4}|1⟩ — global phase on |1⟩ (unobservable in isolation).",
            ],
            "|+⟩": [
                "Rz(π/2)|+⟩ = (e^{−iπ/4}|0⟩ + e^{iπ/4}|1⟩)/√2.",
                "= e^{−iπ/4}(|0⟩ + e^{iπ/2}|1⟩)/√2 = e^{−iπ/4}(|0⟩ + i|1⟩)/√2.",
                "Up to global phase: (|0⟩ + i|1⟩)/√2 — the +Y eigenstate.",
                "Rz(π/2) rotates |+⟩ by 90° around Z to the +Y axis.",
            ],
            "|−⟩": [
                "Rz(π/2)|−⟩ = e^{−iπ/4}(|0⟩ − e^{iπ/2}|1⟩)/√2 = e^{−iπ/4}(|0⟩ − i|1⟩)/√2.",
                "Up to global phase: (|0⟩ − i|1⟩)/√2 — the −Y eigenstate.",
                "Rz(π/2) rotates |−⟩ by 90° around Z to the −Y axis.",
            ],
        },
        "Rx(π/4)": {
            "|0⟩": [
                "Rx(π/4)|0⟩ = cos(π/8)|0⟩ − i·sin(π/8)|1⟩.",
                "cos(π/8) ≈ 0.924, sin(π/8) ≈ 0.383 — a small tilt away from |0⟩.",
            ],
            "|1⟩": [
                "Rx(π/4)|1⟩ = −i·sin(π/8)|0⟩ + cos(π/8)|1⟩.",
                "cos(π/8) ≈ 0.924, sin(π/8) ≈ 0.383.",
            ],
        },
        "Ry(π/4)": {
            "|0⟩": [
                "Ry(π/4)|0⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩.",
                "cos(π/8) ≈ 0.924, sin(π/8) ≈ 0.383 — a small rotation toward |1⟩.",
            ],
            "|1⟩": [
                "Ry(π/4)|1⟩ = −sin(π/8)|0⟩ + cos(π/8)|1⟩.",
            ],
        },
        "Rz(π/4)": {
            "|0⟩": [
                "Rz(π/4)|0⟩ = e^{−iπ/8}|0⟩ (global phase — unobservable for |0⟩ alone).",
            ],
            "|1⟩": [
                "Rz(π/4)|1⟩ = e^{iπ/8}|1⟩ (global phase — unobservable for |1⟩ alone).",
            ],
            "|+⟩": [
                "Rz(π/4)|+⟩ = e^{−iπ/8}(|0⟩ + e^{iπ/4}|1⟩)/√2.",
                "A 45° Bloch rotation around Z — partway between |+⟩ and the +Y axis.",
            ],
            "|−⟩": [
                "Rz(π/4)|−⟩ = e^{−iπ/8}(|0⟩ − e^{iπ/4}|1⟩)/√2.",
                "A 45° rotation around Z from the −X equator point.",
            ],
        },
    }
    if gate in steps_map and inp in steps_map[gate]:
        return steps_map[gate][inp]
    # Fallback: matrix multiplication description
    return [
        f"Apply the {gate} gate matrix to the column vector for {inp}.",
        f"The result is: {out}",
        "Tip: memorise the action of each gate on the six cardinal Bloch-sphere states.",
    ]
