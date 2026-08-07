"""
Circuit composition problems: identify what a composed circuit computes,
or select the circuit that achieves a given transformation.
Answer: MULTIPLE_CHOICE (auto-graded).
"""

from __future__ import annotations
import random
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import render_circuit, format_statevector, statevector_for_circuit, make_distractors

TASKS: list[dict] = [
    # ── Beginner ──────────────────────────────────────────────────────────────
    {
        "difficulty": "beginner",
        "description": "Flip a qubit from |0⟩ to |1⟩",
        "correct_gates": ["X"],
        "wrong_gates": [["H"], ["Z"], ["S"]],
        "concepts": ["X gate", "bit flip"],
    },
    {
        "difficulty": "beginner",
        "description": "Create a superposition (|0⟩+|1⟩)/√2 from |0⟩",
        "correct_gates": ["H"],
        "wrong_gates": [["X"], ["Z"], ["X", "H"]],
        "concepts": ["Hadamard", "superposition"],
    },
    {
        "difficulty": "beginner",
        "description": "Apply a phase of −1 to |1⟩ and leave |0⟩ unchanged",
        "correct_gates": ["Z"],
        "wrong_gates": [["X"], ["S"], ["H"]],
        "concepts": ["Z gate", "phase flip"],
    },
    # ── Intermediate ─────────────────────────────────────────────────────────
    {
        "difficulty": "intermediate",
        "description": "Prepare the Bell state |Φ⁺⟩ = (|00⟩+|11⟩)/√2 from |00⟩",
        "correct_gates": ["H(q0)", "CNOT(0→1)"],
        "wrong_gates": [["CNOT(0→1)", "H(q0)"], ["H(q0)", "H(q1)"], ["CNOT(0→1)"]],
        "concepts": ["Bell state", "H + CNOT", "entanglement creation"],
        "n_qubits": 2,
    },
    {
        "difficulty": "intermediate",
        "description": "Convert |+⟩ back to |0⟩",
        "correct_gates": ["H"],
        "wrong_gates": [["X"], ["Z"], ["T"]],
        "concepts": ["Hadamard is its own inverse", "H² = I"],
    },
    {
        "difficulty": "intermediate",
        "description": "Apply a phase of i to |1⟩ and leave |0⟩ unchanged",
        "correct_gates": ["S"],
        "wrong_gates": [["T"], ["Z"], ["Sdg"]],
        "concepts": ["S gate", "phase gate", "diag(1,i)"],
    },
    # ── Advanced ──────────────────────────────────────────────────────────────
    {
        "difficulty": "advanced",
        "description": "Transform Z into X: replace Z with X using only H and Z",
        "correct_gates": ["H", "Z", "H"],
        "wrong_gates": [["Z", "H", "Z"], ["H", "H"], ["Z", "Z", "H"]],
        "concepts": ["conjugation HZH = X", "Hadamard conjugation"],
    },
    {
        "difficulty": "advanced",
        "description": "Create the 3-qubit GHZ state from |000⟩",
        "correct_gates": ["H(q0)", "CNOT(0→1)", "CNOT(1→2)"],
        "wrong_gates": [
            ["H(q0)", "H(q1)", "H(q2)"],
            ["CNOT(0→1)", "H(q0)", "CNOT(1→2)"],
            ["H(q0)", "CNOT(0→2)", "CNOT(0→1)"],
        ],
        "concepts": ["GHZ state", "multi-qubit entanglement", "CNOT chain"],
        "n_qubits": 3,
    },
]


def generate(difficulty: str) -> Problem:
    pool = [t for t in TASKS if t["difficulty"] == difficulty]
    if not pool:
        pool = TASKS
    task = random.choice(pool)

    # Build correct circuit
    n = task.get("n_qubits", 1)
    correct_qc = _build_circuit(task["correct_gates"], n, "Correct")
    sv_correct = statevector_for_circuit(correct_qc)
    out_str = format_statevector(sv_correct, n)

    # Build wrong circuits
    wrong_qcs = [_build_circuit(g, n, f"Option {i+2}") for i, g in enumerate(task["wrong_gates"])]

    choices_qcs = [correct_qc] + wrong_qcs[:3]
    random.shuffle(choices_qcs)
    correct_idx = next(i for i, qc in enumerate(choices_qcs) if qc.name == "Correct")
    # Rename to generic labels after shuffle
    labels = ["Circuit A", "Circuit B", "Circuit C", "Circuit D"]
    for i, qc in enumerate(choices_qcs):
        qc.name = labels[i]

    choices_str = [qc.name for qc in choices_qcs]

    steps = [
        f"Goal: {task['description']}",
        f"Correct gate sequence: {' → '.join(task['correct_gates'])}",
        f"Output state: {out_str}",
        "The wrong options either produce a different state or wrong ordering.",
    ]

    # Render all 4 circuits (show them separately in the UI via matrix_str hack)
    import io, matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    circuit_renders = []
    for qc in choices_qcs:
        from problems._utils import render_circuit as _rc
        circuit_renders.append(_rc(qc))

    return Problem(
        category=ProblemCategory.CIRCUIT_COMPOSITION,
        difficulty=difficulty,
        question_text=(
            f"Which circuit correctly achieves the following?\n\n"
            f"  \"{task['description']}\""
        ),
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices_str,
        circuit_png=circuit_renders[0],          # Circuit A shown main
        aux_circuit_png=circuit_renders[1],       # Circuit B shown secondary
        matrix_str=None,
        state_str=f"Target output from |{'0'*n}⟩: {out_str}",
        solution_steps=steps,
        key_concepts=task["concepts"],
    )


def _build_circuit(gate_list: list[str], n: int, name: str) -> QuantumCircuit:
    """Build a QuantumCircuit from a human-readable gate list."""
    qc = QuantumCircuit(n, name=name)
    for g in gate_list:
        g = g.strip()
        if g == "H" or g == "H(q0)":   qc.h(0)
        elif g == "H(q1)":              qc.h(1)
        elif g == "H(q2)":              qc.h(2)
        elif g == "X":                  qc.x(0)
        elif g == "Y":                  qc.y(0)
        elif g == "Z":                  qc.z(0)
        elif g == "S":                  qc.s(0)
        elif g == "Sdg":                qc.sdg(0)
        elif g == "T":                  qc.t(0)
        elif g == "Tdg":                qc.tdg(0)
        elif g == "CNOT(0→1)":          qc.cx(0, 1) if n >= 2 else None
        elif g == "CNOT(1→0)":          qc.cx(1, 0) if n >= 2 else None
        elif g == "CNOT(0→2)":          qc.cx(0, 2) if n >= 3 else None
        elif g == "CNOT(1→2)":          qc.cx(1, 2) if n >= 3 else None
    return qc
