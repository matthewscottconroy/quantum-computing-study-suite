"""
Multi-qubit circuit output problems (2–3 qubits).
Answer: MULTIPLE_CHOICE (auto-graded).
"""

from __future__ import annotations
import random
import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import render_circuit, format_statevector, make_distractors, statevector_for_circuit


def generate(difficulty: str) -> Problem:
    builders = {
        "beginner":     [_cnot_basic, _swap_basic, _cz_basic],
        "intermediate": [_ghz_circuit, _bell_with_phase, _cnot_chain],
        "advanced":     [_toffoli_circuit, _three_qubit_mix, _controlled_phase_circuit],
    }.get(difficulty, [_ghz_circuit, _bell_with_phase, _cnot_chain])
    return random.choice(builders)()


# ── Beginner builders ─────────────────────────────────────────────────────────

def _cnot_basic() -> Problem:
    input_name = random.choice(["|00⟩", "|01⟩", "|10⟩", "|11⟩"])
    input_sv = Statevector(
        {"00": [1,0,0,0], "01": [0,1,0,0], "10": [0,0,1,0], "11": [0,0,0,1]}
        [input_name[1:3]]
    )
    qc = QuantumCircuit(2, name="CNOT")
    qc.cx(0, 1)
    sv = statevector_for_circuit(qc, input_sv)
    correct = format_statevector(sv, 2)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        f"CNOT flips the target (qubit 1) when control (qubit 0) is |1⟩.",
        f"Input {input_name}:",
        "  If control=|0⟩ → target unchanged.",
        "  If control=|1⟩ → target flipped.",
        f"Output: {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, input_name, steps,
                 "What is the output of CNOT applied to the state below?",
                 "beginner", ["CNOT gate", "controlled operations"])


def _swap_basic() -> Problem:
    input_name = random.choice(["|01⟩", "|10⟩", "|00⟩", "|11⟩"])
    input_sv = Statevector(
        {"00": [1,0,0,0], "01": [0,1,0,0], "10": [0,0,1,0], "11": [0,0,0,1]}
        [input_name[1:3]]
    )
    qc = QuantumCircuit(2, name="SWAP")
    qc.swap(0, 1)
    sv = statevector_for_circuit(qc, input_sv)
    correct = format_statevector(sv, 2)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        "SWAP exchanges the states of the two qubits.",
        f"Input {input_name} → qubit 0 and qubit 1 are swapped.",
        f"Output: {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, input_name, steps,
                 "What is the output of SWAP applied to the state below?",
                 "beginner", ["SWAP gate"])


def _cz_basic() -> Problem:
    input_name = random.choice(["|+0⟩", "|11⟩", "|10⟩", "|++⟩"])
    sv_map = {
        "|+0⟩": Statevector([1,0,1,0]) / math.sqrt(2),
        "|11⟩": Statevector([0,0,0,1]),
        "|10⟩": Statevector([0,0,1,0]),
        "|++⟩": Statevector([1,1,1,1]) / 2,
    }
    input_sv = sv_map[input_name]
    qc = QuantumCircuit(2, name="CZ")
    qc.cz(0, 1)
    sv = statevector_for_circuit(qc, input_sv)
    correct = format_statevector(sv, 2)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        "CZ applies a phase of −1 to |11⟩ and leaves all other states unchanged.",
        f"Input: {input_name}",
        f"Output: {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, input_name, steps,
                 "What is the output of CZ applied to the state below?",
                 "beginner", ["CZ gate", "controlled-Z"])


# ── Intermediate builders ─────────────────────────────────────────────────────

def _ghz_circuit() -> Problem:
    n = random.choice([3, 3, 4])
    qc = QuantumCircuit(n, name=f"{n}-qubit GHZ")
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    sv = statevector_for_circuit(qc)
    correct = format_statevector(sv, n)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        f"H|0⟩ = (|0⟩+|1⟩)/√2 on qubit 0.",
        "CNOTs propagate the superposition to all qubits.",
        f"Output: (|{'0'*n}⟩ + |{'1'*n}⟩)/√2 — a {n}-qubit GHZ state.",
    ]
    return _make(qc, correct, correct_idx, choices, "|"+"0"*n+"⟩", steps,
                 f"Starting from |{'0'*n}⟩, what is the output of this {n}-qubit circuit?",
                 "intermediate", ["GHZ state", "multi-qubit entanglement", "CNOT chain"])


def _bell_with_phase() -> Problem:
    qc = QuantumCircuit(2, name="Bell + Z")
    qc.h(0)
    qc.cx(0, 1)
    qc.z(0)
    sv = statevector_for_circuit(qc)
    correct = format_statevector(sv, 2)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        "H+CNOT produces |Φ⁺⟩ = (|00⟩+|11⟩)/√2.",
        "Z on qubit 0: |0⟩→|0⟩, |1⟩→−|1⟩.",
        "Z⊗I on (|00⟩+|11⟩)/√2 = (|00⟩−|11⟩)/√2 = |Φ⁻⟩.",
        f"Output: {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, "|00⟩", steps,
                 "Starting from |00⟩, what is the output of this circuit?",
                 "intermediate", ["Bell states", "phase gates on entangled states"])


def _cnot_chain() -> Problem:
    input_name = random.choice(["|100⟩", "|010⟩", "|110⟩"])
    sv_map = {
        "|100⟩": Statevector([0,0,0,0,1,0,0,0]),
        "|010⟩": Statevector([0,0,1,0,0,0,0,0]),
        "|110⟩": Statevector([0,0,0,0,0,0,1,0]),
    }
    input_sv = sv_map[input_name]
    qc = QuantumCircuit(3, name="CNOT chain")
    qc.cx(0, 1)
    qc.cx(1, 2)
    sv = statevector_for_circuit(qc, input_sv)
    correct = format_statevector(sv, 3)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        f"Input: {input_name}",
        "CNOT(0→1): flip qubit 1 if qubit 0 is |1⟩.",
        "CNOT(1→2): flip qubit 2 if (new) qubit 1 is |1⟩.",
        f"Output: {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, input_name, steps,
                 f"Starting from {input_name}, what is the output of this CNOT chain?",
                 "intermediate", ["CNOT", "classical reversible logic"])


# ── Advanced builders ─────────────────────────────────────────────────────────

def _toffoli_circuit() -> Problem:
    input_name = random.choice(["|110⟩", "|100⟩", "|010⟩", "|111⟩"])
    sv_map = {
        "|110⟩": Statevector([0]*6 + [1,0]),
        "|100⟩": Statevector([0]*4 + [1,0,0,0]),
        "|010⟩": Statevector([0,0,1,0,0,0,0,0]),
        "|111⟩": Statevector([0]*7 + [1]),
    }
    input_sv = sv_map[input_name]
    qc = QuantumCircuit(3, name="Toffoli (CCX)")
    qc.ccx(0, 1, 2)
    sv = statevector_for_circuit(qc, input_sv)
    correct = format_statevector(sv, 3)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        "Toffoli flips qubit 2 (target) only when BOTH qubits 0 and 1 are |1⟩.",
        f"Input {input_name}: control qubits = {input_name[1]},{input_name[2]}, target = {input_name[3]}.",
        f"Controls {'both 1 → flip target' if input_name[1:3] == '11' else 'not both 1 → target unchanged'}.",
        f"Output: {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, input_name, steps,
                 f"Starting from {input_name}, what is the output of the Toffoli gate?",
                 "advanced", ["Toffoli gate", "CCX", "classical computation"])


def _three_qubit_mix() -> Problem:
    qc = QuantumCircuit(3, name="H+CNOT+T mix")
    qc.h(0)
    qc.cx(0, 1)
    qc.t(2)
    qc.cx(1, 2)
    sv = statevector_for_circuit(qc)
    correct = format_statevector(sv, 3)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        "H(q0): (|0⟩+|1⟩)/√2 ⊗ |00⟩",
        "CNOT(0→1): entangles q0,q1 → (|00⟩+|11⟩)/√2 ⊗ |0⟩",
        "T(q2): |0⟩ unchanged (T|0⟩=|0⟩).",
        "CNOT(1→2): flips q2 conditioned on q1.",
        f"Output: {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, "|000⟩", steps,
                 "Starting from |000⟩, what is the output of this circuit?",
                 "advanced", ["multi-qubit circuits", "gate interaction"])


def _controlled_phase_circuit() -> Problem:
    qc = QuantumCircuit(2, name="H+CP circuit")
    qc.h(0)
    qc.h(1)
    qc.cp(math.pi / 2, 0, 1)  # CPhase(π/2) = CS gate
    sv = statevector_for_circuit(qc)
    correct = format_statevector(sv, 2)
    distractors = make_distractors(correct, 3)
    choices = [correct] + distractors
    random.shuffle(choices)
    correct_idx = choices.index(correct)
    steps = [
        "H⊗H|00⟩ = |++⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2",
        "CPhase(π/2) applies e^(iπ/2)=i to |11⟩ component only.",
        f"Output: (|00⟩+|01⟩+|10⟩+i|11⟩)/2 = {correct}",
    ]
    return _make(qc, correct, correct_idx, choices, "|00⟩", steps,
                 "Starting from |00⟩, what is the output of this H⊗H + CPhase(π/2) circuit?",
                 "advanced", ["controlled-phase", "CPhase gate", "QFT building block"])


# ── Helper ────────────────────────────────────────────────────────────────────

def _make(qc, correct, correct_idx, choices, input_name, steps, question, difficulty, concepts):
    return Problem(
        category=ProblemCategory.MULTI_QUBIT_OUTPUT,
        difficulty=difficulty,
        question_text=question,
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=f"Input: {input_name}",
        solution_steps=steps,
        key_concepts=concepts,
    )
