"""
Circuit equivalence problems.
Show two circuits side by side; determine if they are equivalent (same unitary up to global phase).
Answer: MULTIPLE_CHOICE (auto-graded via Operator comparison).
"""

from __future__ import annotations
import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from core.models import Problem, ProblemCategory, AnswerFormat
from problems._utils import render_circuit
from config import PHASE_TOLERANCE

def generate(difficulty: str) -> Problem:
    # Build pairs here so all builder functions are already defined
    all_pairs: list[tuple] = [
        # True equivalences
        ("HXH == Z",         _hxh,        _z_gate,       True,
         "HXH = Z is a fundamental identity: conjugation by H swaps X↔Z."),
        ("HZH == X",         _hzh,        _x_gate,       True,
         "HZH = X — the same conjugation identity in the other direction."),
        ("XX == I",          _xx,         _identity,     True,
         "X is self-inverse: X² = I."),
        ("HH == I",          _hh,         _identity,     True,
         "H is self-inverse: H² = I."),
        ("SS == Z",          _ss,         _z_gate,       True,
         "S² = Z because diag(1,i)² = diag(1,−1) = Z."),
        ("TT == S",          _tt,         _s_gate,       True,
         "T² = S because (e^(iπ/4))² = e^(iπ/2) = i."),
        ("CNOT·CNOT == I",   _cnot2,      _id2,          True,
         "CNOT is self-inverse: CNOT² = I."),
        ("SWAP = 3×CNOT",    _swap_3cnot, _swap_gate,    True,
         "SWAP = CNOT(0,1)·CNOT(1,0)·CNOT(0,1)."),
        # False equivalences
        ("H != X",           _h_gate,     _x_gate,       False,
         "H ≠ X: H maps |0⟩→|+⟩, X maps |0⟩→|1⟩."),
        ("S != T",           _s_gate,     _t_gate,       False,
         "S ≠ T: S applies phase i, T applies phase e^(iπ/4)."),
        ("HS != SH",         _hs,         _sh,           False,
         "H and S do not commute; HS ≠ SH."),
        ("CNOT(0,1) != CNOT(1,0)", _cnot_01, _cnot_10,  False,
         "CNOT direction matters: (0→1) ≠ (1→0) as operators."),
    ]
    beginner_labels = ("HXH == Z", "HZH == X", "XX == I", "HH == I")
    inter_labels    = ("SS == Z", "TT == S", "CNOT·CNOT == I", "H != X", "S != T")
    if difficulty == "beginner":
        pool = [p for p in all_pairs if p[0] in beginner_labels]
    elif difficulty == "intermediate":
        pool = [p for p in all_pairs if p[0] in inter_labels]
    else:
        pool = all_pairs

    label, build_a, build_b, equivalent, explanation = random.choice(pool)
    qc_a = build_a()
    qc_b = build_b()

    # Verify computationally
    n = max(qc_a.num_qubits, qc_b.num_qubits)
    qc_a_padded = _pad(qc_a, n)
    qc_b_padded = _pad(qc_b, n)
    op_a = np.array(Operator(qc_a_padded).data)
    op_b = np.array(Operator(qc_b_padded).data)
    phase = _global_phase(op_a, op_b)
    computed_equiv = phase is not None

    correct_idx = 0 if computed_equiv else 1
    choices = [
        "Yes — the circuits are equivalent (same unitary up to global phase)",
        "No — the circuits produce different unitaries",
    ]

    steps = [
        f"Compute the unitary of Circuit A: U_A",
        f"Compute the unitary of Circuit B: U_B",
        "Check if U_A = e^(iφ) · U_B for some real φ (global phase doesn't matter).",
        explanation,
        f"Answer: {'Equivalent' if computed_equiv else 'NOT equivalent'}",
    ]

    return Problem(
        category=ProblemCategory.CIRCUIT_EQUIVALENCE,
        difficulty=difficulty,
        question_text="Are these two circuits equivalent (same unitary up to global phase)?",
        answer_format=AnswerFormat.MULTIPLE_CHOICE,
        correct_answer=str(correct_idx),
        choices=choices,
        circuit_png=render_circuit(qc_a),
        aux_circuit_png=render_circuit(qc_b),
        matrix_str=None,
        state_str=f"Circuit A  vs  Circuit B — {'EQUIVALENT' if computed_equiv else 'NOT equivalent'}",
        solution_steps=steps,
        key_concepts=["circuit equivalence", "gate identities", "global phase", "unitary comparison"],
    )


# ── Circuit builders ──────────────────────────────────────────────────────────

def _hxh():
    qc = QuantumCircuit(1, name="H·X·H"); qc.h(0); qc.x(0); qc.h(0); return qc
def _hzh():
    qc = QuantumCircuit(1, name="H·Z·H"); qc.h(0); qc.z(0); qc.h(0); return qc
def _xx():
    qc = QuantumCircuit(1, name="X·X"); qc.x(0); qc.x(0); return qc
def _hh():
    qc = QuantumCircuit(1, name="H·H"); qc.h(0); qc.h(0); return qc
def _ss():
    qc = QuantumCircuit(1, name="S·S"); qc.s(0); qc.s(0); return qc
def _tt():
    qc = QuantumCircuit(1, name="T·T"); qc.t(0); qc.t(0); return qc
def _z_gate():
    qc = QuantumCircuit(1, name="Z"); qc.z(0); return qc
def _x_gate():
    qc = QuantumCircuit(1, name="X"); qc.x(0); return qc
def _h_gate():
    qc = QuantumCircuit(1, name="H"); qc.h(0); return qc
def _s_gate():
    qc = QuantumCircuit(1, name="S"); qc.s(0); return qc
def _t_gate():
    qc = QuantumCircuit(1, name="T"); qc.t(0); return qc
def _identity():
    qc = QuantumCircuit(1, name="I (identity)"); return qc
def _hs():
    qc = QuantumCircuit(1, name="H·S"); qc.h(0); qc.s(0); return qc
def _sh():
    qc = QuantumCircuit(1, name="S·H"); qc.s(0); qc.h(0); return qc
def _cnot2():
    qc = QuantumCircuit(2, name="CNOT·CNOT"); qc.cx(0,1); qc.cx(0,1); return qc
def _id2():
    return QuantumCircuit(2, name="Identity (2-qubit)")
def _swap_gate():
    qc = QuantumCircuit(2, name="SWAP"); qc.swap(0,1); return qc
def _swap_3cnot():
    qc = QuantumCircuit(2, name="3×CNOT")
    qc.cx(0,1); qc.cx(1,0); qc.cx(0,1); return qc
def _cnot_01():
    qc = QuantumCircuit(2, name="CNOT(0→1)"); qc.cx(0,1); return qc
def _cnot_10():
    qc = QuantumCircuit(2, name="CNOT(1→0)"); qc.cx(1,0); return qc


# ── Utilities ─────────────────────────────────────────────────────────────────

def _pad(qc: QuantumCircuit, n: int) -> QuantumCircuit:
    if qc.num_qubits == n:
        return qc
    padded = QuantumCircuit(n)
    padded.compose(qc, qubits=list(range(qc.num_qubits)), inplace=True)
    return padded


def _global_phase(a: np.ndarray, b: np.ndarray) -> float | None:
    """Return the global phase φ if a = e^(iφ)·b, else None."""
    flat_a = a.flatten()
    flat_b = b.flatten()
    idx = np.argmax(np.abs(flat_b))
    if abs(flat_b[idx]) < 1e-9:
        return None
    ratio = flat_a[idx] / flat_b[idx]
    if abs(abs(ratio) - 1.0) > PHASE_TOLERANCE:
        return None
    if np.allclose(a, ratio * b, atol=PHASE_TOLERANCE):
        return float(np.angle(ratio))
    return None
