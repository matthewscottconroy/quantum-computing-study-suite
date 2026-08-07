"""Problem: ft_circuit_level_noise"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_circuit_level_noise',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='A circuit-level noise model for fault-tolerant analysis includes which error sources?',
    choices=[
        'Gate errors (1- and 2-qubit), state preparation errors, measurement errors, and idle (waiting) qubit errors',
        'Only two-qubit gate errors — single-qubit gates are assumed perfect',
        'Only measurement errors — gates are assumed unitary',
        'Gate errors and measurement errors, but not idle errors',
    ],
    correct_index=0,
    explanation='A realistic circuit-level noise model assigns an independent error probability to each operation: (1) two-qubit gates (e.g., depolarizing with probability p), (2) single-qubit gates (typically p/10), (3) state preparation (preparing |0⟩ or |+⟩ with probability p of bit flip or phase flip), (4) measurements (probability p of flipped outcome), and (5) idle qubits (during clock cycles where a qubit is not operated on). All five contribute to the circuit-level threshold (~0.5–1% for the surface code).',
    hints=[
        'Every physical operation in the circuit can fail — none are assumed perfect.',
    ],
    grade_mode=GradeMode.AUTO,
)
