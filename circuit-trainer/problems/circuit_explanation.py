"""
FREE_FORM circuit explanation problems — graded asynchronously by Claude.
Student describes what a circuit does, why it works, or analyses a key property.
"""

from __future__ import annotations
import math
import random
from qiskit import QuantumCircuit
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import render_circuit


_PROBLEMS: list[dict] = [
    # ── Beginner ────────────────────────────────────────────────────────────────
    {
        "difficulty": "beginner",
        "build": lambda: _bell_circuit(),
        "question": (
            "Describe what this circuit computes starting from |00⟩. "
            "What is the output state, and what property makes it special?"
        ),
        "solution": [
            "H on qubit 0: |0⟩ → (|0⟩+|1⟩)/√2.",
            "CNOT(control=q0, target=q1): correlates qubits → (|00⟩+|11⟩)/√2.",
            "This is the Bell state |Φ⁺⟩ — a maximally entangled two-qubit state.",
            "Measuring either qubit collapses both: outcomes are perfectly correlated regardless of separation.",
            "The state cannot be written as any product |a⟩⊗|b⟩ — that is the definition of entanglement.",
        ],
        "concepts": ["Bell state", "entanglement", "H + CNOT", "superposition"],
        "hints": [
            "Apply H to q0 first; think about what superposition you get.",
            "CNOT flips q1 only when q0 = |1⟩ — trace both branches.",
        ],
    },
    {
        "difficulty": "beginner",
        "build": lambda: _x_then_h(),
        "question": (
            "Trace this circuit applied to |0⟩ step by step. "
            "What is the final state, and how does it differ from H|0⟩?"
        ),
        "solution": [
            "X|0⟩ = |1⟩ (bit flip).",
            "H|1⟩ = (|0⟩−|1⟩)/√2 = |−⟩.",
            "By contrast, H|0⟩ = (|0⟩+|1⟩)/√2 = |+⟩.",
            "The difference is the relative phase of the |1⟩ component: |+⟩ has +1, |−⟩ has −1.",
            "This phase difference is physically observable via interference (e.g., another H gate would yield |1⟩ vs |0⟩).",
        ],
        "concepts": ["X gate", "Hadamard", "relative phase", "|+⟩ vs |−⟩"],
        "hints": [
            "X gate is the quantum bit-flip: X|0⟩ = |1⟩.",
            "H applied to |1⟩ gives (|0⟩ - |1⟩)/√2, not (|0⟩ + |1⟩)/√2.",
        ],
    },
    {
        "difficulty": "beginner",
        "build": lambda: _hzh_circuit(),
        "question": (
            "What single-gate operation does this H–Z–H sequence implement? "
            "Verify your answer by computing its matrix."
        ),
        "solution": [
            "H = [[1,1],[1,-1]]/√2,  Z = [[1,0],[0,-1]].",
            "HZH = (1/2)·[[1,1],[1,-1]]·[[1,0],[0,-1]]·[[1,1],[1,-1]].",
            "Step 1: ZH = [[1,0],[0,-1]]·[[1,1],[1,-1]]/√2 = [[1,1],[-1,1]]/√2.",
            "Step 2: H·ZH = (1/2)·[[1,1],[1,-1]]·[[1,1],[-1,1]] = [[1,0],[0,-1]]... wait:",
            "Correct product: HZH = X (Pauli X gate).  This is because H diagonalises X.",
            "HXH = Z and HZH = X — Hadamard conjugates swap the X and Z Pauli operators.",
        ],
        "concepts": ["Hadamard", "Pauli X", "gate conjugation", "matrix product"],
        "hints": [
            "Compute the product matrix H·Z·H explicitly.",
            "H conjugation swaps X and Z: HZH = X.",
        ],
    },
    # ── Intermediate ────────────────────────────────────────────────────────────
    {
        "difficulty": "intermediate",
        "build": lambda: _phase_kickback(),
        "question": (
            "This circuit demonstrates phase kickback. "
            "Explain why the CNOT gate modifies the phase of the control qubit "
            "when the target is prepared in |−⟩."
        ),
        "solution": [
            "Initial state after H(q0), X(q1), H(q1): |+⟩⊗|−⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩−|1⟩)/√2.",
            "CNOT flips target when control=|1⟩. X|−⟩ = −|−⟩ (|−⟩ is an eigenstate of X with eigenvalue −1).",
            "Result: (|0⟩(X⁰|−⟩)+|1⟩(X¹|−⟩))/√2 = (|0⟩|−⟩ − |1⟩|−⟩)/√2 = |−⟩⊗|−⟩.",
            "The eigenvalue −1 'kicked back' as a relative phase onto the control qubit, changing |+⟩ to |−⟩.",
            "General rule: if target is in eigenstate |ψ⟩ with eigenvalue λ, control gets phase λ.",
        ],
        "concepts": ["phase kickback", "eigenstate", "CNOT", "quantum algorithms"],
        "hints": [
            "Write the target state as a CNOT eigenstate and think about what happens when control=|1⟩.",
            "|−⟩ is an eigenstate of X: X|−⟩ = −|−⟩.",
        ],
    },
    {
        "difficulty": "intermediate",
        "build": lambda: _ghz_3(),
        "question": (
            "Describe the output of this circuit from |000⟩. "
            "Is the state fully entangled? "
            "What happens probabilistically if only qubit 0 is measured?"
        ),
        "solution": [
            "H(q0): (|0⟩+|1⟩)/√2 ⊗ |00⟩.",
            "CNOT(0→1): (|00⟩+|11⟩)/√2 ⊗ |0⟩.",
            "CNOT(1→2): (|000⟩+|111⟩)/√2 — the 3-qubit GHZ state.",
            "Fully entangled: no bipartition is separable; the reduced state of any single qubit is maximally mixed.",
            "Measuring qubit 0: 50% → |0⟩ → whole state collapses to |000⟩; 50% → |1⟩ → collapses to |111⟩.",
        ],
        "concepts": ["GHZ state", "multi-qubit entanglement", "measurement collapse", "CNOT chain"],
        "hints": [
            "Trace the state through the H gate then each CNOT sequentially.",
            "The GHZ state is (|000⟩+|111⟩)/√2 — measuring any one qubit instantly fixes all others.",
        ],
    },
    {
        "difficulty": "intermediate",
        "build": lambda: _swap_circuit(),
        "question": (
            "Show that the SWAP gate can be decomposed into three CNOT gates. "
            "Explain what each CNOT step does to the computational basis states."
        ),
        "solution": [
            "SWAP decomposition: CNOT(0→1), CNOT(1→0), CNOT(0→1).",
            "Starting state |ab⟩ (a, b ∈ {0,1}):",
            "Step 1 CNOT(0→1): |a, a⊕b⟩.",
            "Step 2 CNOT(1→0): |a⊕(a⊕b), a⊕b⟩ = |b, a⊕b⟩.",
            "Step 3 CNOT(0→1): |b, b⊕(a⊕b)⟩ = |b, a⟩.",
            "The final state |ba⟩ confirms the SWAP operation for all basis states.",
        ],
        "concepts": ["SWAP gate", "CNOT decomposition", "gate synthesis", "XOR arithmetic"],
        "hints": [
            "Use the XOR property: a ⊕ a = 0.",
            "Track |ab⟩ through each CNOT: CNOT|a,b⟩ = |a, a⊕b⟩.",
        ],
    },
    # ── Advanced ────────────────────────────────────────────────────────────────
    {
        "difficulty": "advanced",
        "build": lambda: _qft_2(),
        "question": (
            "This is the 2-qubit Quantum Fourier Transform. "
            "Derive the output for input |01⟩ and explain the role of the controlled-phase gate."
        ),
        "solution": [
            "Order convention: qubit 1 is MSB, qubit 0 is LSB. Input |01⟩ encodes integer j=1.",
            "H(q1): (|0⟩+|1⟩)/√2 ⊗ |1⟩.",
            "CP(π/2) with q0 as control: |11⟩ component gains phase e^(iπ/2)=i → (|01⟩+i|11⟩)/√2.",
            "SWAP: (|10⟩+i|11⟩)/√2.",
            "H(q0): H|1⟩=(|0⟩−|1⟩)/√2, so final = (|00⟩−|01⟩+i|10⟩−i|11⟩)/2.",
            "CP introduces the twiddle factor ω^(jk) = e^(2πijk/N) that encodes the DFT phase relationships.",
        ],
        "concepts": ["QFT", "controlled-phase gate", "twiddle factor", "Hadamard", "DFT"],
        "hints": [
            "Track the state qubit-by-qubit: apply H to the most-significant qubit first.",
            "The controlled-phase gate CP(θ)|11⟩ = e^(iθ)|11⟩ only acts when both qubits are |1⟩.",
        ],
    },
    {
        "difficulty": "advanced",
        "build": lambda: _teleportation_bell_prep(),
        "question": (
            "This Bell pair is the shared entangled resource in quantum teleportation. "
            "Explain why two classical bits are sufficient to complete the teleportation protocol, "
            "and why this does not violate the no-faster-than-light constraint."
        ),
        "solution": [
            "Bell pair (|00⟩+|11⟩)/√2: Alice holds qubit 0, Bob holds qubit 1.",
            "Alice entangles her unknown state |ψ⟩ with her half of the pair, then measures two qubits → 2 bits.",
            "Bob applies one of {I, X, Z, XZ} conditioned on Alice's 2 bits to recover |ψ⟩.",
            "The 2 classical bits must be transmitted via a conventional channel (not instant) — no FTL.",
            "Bob's qubit is in a random mixed state until he receives the classical bits and applies his correction.",
            "Entanglement enables the transfer of quantum state information; classical communication enables decoding.",
        ],
        "concepts": ["quantum teleportation", "Bell pair", "classical communication", "no-signaling theorem"],
        "hints": [
            "Think about what Alice's measurement outcomes tell Bob about which correction to apply.",
            "Before receiving the classical bits, Bob has no information about |ψ⟩ — his qubit looks random.",
        ],
    },
    {
        "difficulty": "advanced",
        "build": lambda: _toffoli_circuit(),
        "question": (
            "The Toffoli (CCX) gate is universal for classical reversible computing. "
            "Explain why it is reversible, how it implements a classical AND gate, "
            "and what ancilla state is needed."
        ),
        "solution": [
            "Toffoli CCX: |a,b,c⟩ → |a,b,c⊕(a·b)⟩. It is its own inverse: applying twice returns the original state.",
            "Reversibility: all basis-state mappings are bijective — no information is erased.",
            "AND computation: set c=0. Then output qubit c = 0⊕(a·b) = a·b — this is the AND of a and b.",
            "The ancilla qubit c starts in |0⟩ (the 'workspace'); after the gate it holds the result.",
            "Unlike a classical AND gate (which discards inputs), the Toffoli keeps a and b intact (reversible).",
            "The Toffoli gate + CNOT + X generate all reversible Boolean circuits (Toffoli is universal for them).",
        ],
        "concepts": ["Toffoli gate", "reversible computing", "ancilla qubit", "universality", "AND gate"],
        "hints": [
            "Compute CCX|a,b,0⟩ for all 4 combinations of a,b ∈ {0,1}.",
            "The output register c = a·b when c starts as |0⟩ — that is the classical AND.",
        ],
    },
]


def generate(difficulty: str) -> Problem:
    pool = [p for p in _PROBLEMS if p["difficulty"] == difficulty]
    if not pool:
        pool = _PROBLEMS
    entry = random.choice(pool)

    qc = entry["build"]()
    return Problem(
        category=ProblemCategory.CIRCUIT_EXPLANATION,
        difficulty=difficulty,
        question_text=entry["question"],
        answer_format=AnswerFormat.FREE_FORM,
        correct_answer="",
        choices=None,
        circuit_png=render_circuit(qc),
        aux_circuit_png=None,
        matrix_str=None,
        state_str=None,
        solution_steps=entry["solution"],
        key_concepts=entry["concepts"],
        hints=entry.get("hints", []),
    )


# ── Circuit builders ──────────────────────────────────────────────────────────

def _bell_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, name="Bell state")
    qc.h(0)
    qc.cx(0, 1)
    return qc


def _x_then_h() -> QuantumCircuit:
    qc = QuantumCircuit(1, name="X then H")
    qc.x(0)
    qc.h(0)
    return qc


def _hzh_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(1, name="H-Z-H")
    qc.h(0)
    qc.z(0)
    qc.h(0)
    return qc


def _phase_kickback() -> QuantumCircuit:
    qc = QuantumCircuit(2, name="Phase kickback")
    qc.h(0)    # control → |+⟩
    qc.x(1)    # target → |1⟩
    qc.h(1)    # target → |−⟩ (X eigenstate, eigenvalue −1)
    qc.cx(0, 1)
    return qc


def _ghz_3() -> QuantumCircuit:
    qc = QuantumCircuit(3, name="3-qubit GHZ")
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    return qc


def _swap_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, name="SWAP = 3 CNOTs")
    qc.cx(0, 1)
    qc.cx(1, 0)
    qc.cx(0, 1)
    return qc


def _qft_2() -> QuantumCircuit:
    qc = QuantumCircuit(2, name="2-qubit QFT")
    qc.h(1)
    qc.cp(math.pi / 2, 0, 1)
    qc.swap(0, 1)
    qc.h(0)
    return qc


def _teleportation_bell_prep() -> QuantumCircuit:
    qc = QuantumCircuit(2, name="Teleportation resource")
    qc.h(0)
    qc.cx(0, 1)
    return qc


def _toffoli_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3, name="Toffoli gate")
    qc.ccx(0, 1, 2)
    return qc
