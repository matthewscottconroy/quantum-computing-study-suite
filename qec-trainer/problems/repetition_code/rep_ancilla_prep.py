"""Problem: rep_ancilla_prep"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_ancilla_prep',
    category='Repetition Code',
    difficulty='intermediate',
    question='In the 3-qubit bit-flip code, ancilla qubits for syndrome measurement are prepared in which state?',
    choices=[
        '|0⟩ — the ancilla starts in |0⟩, a CNOT fan-in collects parity, then the ancilla is measured',
        '|+⟩ — the ancilla is in a superposition to measure X-type stabilizers',
        '|1⟩ — so a no-error result flips it back to |0⟩',
        '|Bell⟩ — an entangled pair for distributed syndrome extraction',
    ],
    correct_index=0,
    explanation='For measuring a Z-type stabilizer (Z₁Z₂ or Z₂Z₃), the ancilla is prepared in |0⟩. CNOT gates are applied with each data qubit in the stabilizer as control and the ancilla as target, fan-in the parity: ancilla becomes |parity(q₁⊕q₂)⟩. Measuring the ancilla in the Z basis gives 0 (even parity, +1 eigenvalue) or 1 (odd parity, −1 eigenvalue) without disturbing the logical superposition.',
    hints=[
        'Z-type stabilizers are measured using ancilla qubits in |0⟩ and CNOT gates.',
    ],
    grade_mode=GradeMode.AUTO,
)
