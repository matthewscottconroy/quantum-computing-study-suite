"""Problem: bos_two_mode_cat"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_two_mode_cat',
    category='Bosonic Codes',
    difficulty='advanced',
    question='A two-mode cat code uses two oscillator modes. What is the key advantage over a single-mode cat code?',
    choices=[
        'The two-mode code can correct both photon loss AND dephasing errors, while a single-mode cat code only exponentially suppresses one type',
        'Two modes double the encoding rate — two logical qubits in two oscillators',
        'Two-mode codes require fewer ancilla qubits for syndrome measurement',
        'The two-mode code has a higher threshold under depolarizing noise',
    ],
    correct_index=0,
    explanation='A single-mode cat qubit exponentially suppresses phase flips (Z errors from photon loss changing the cat parity), but bit flips (X errors) are only polynomially suppressed. A two-mode cat code can encode the logical qubit in a subspace of two oscillators in a way that provides protection against both loss and gain errors in both modes. For example, the two-mode code |0̄⟩ ∝ |α,−α⟩+|−α,α⟩ protects against simultaneous single-photon events in each mode. More modes give more redundancy, similar to going from a 3-qubit to a 5-qubit qubit code.',
    hints=[
        'One mode protects against one type of error; two modes can be arranged to protect against more.',
    ],
    grade_mode=GradeMode.AUTO,
)
