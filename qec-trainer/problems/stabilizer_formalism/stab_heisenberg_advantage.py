"""Problem: stab_heisenberg_advantage"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_heisenberg_advantage',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='What is the computational advantage of the Heisenberg picture (stabilizer tableau) for simulating stabilizer circuits?',
    choices=[
        'Track O(n) Pauli generators instead of 2^n amplitudes, enabling efficient classical simulation',
        'It allows simulation of non-Clifford gates without overhead',
        'It reduces circuit depth by a factor of n',
        'It eliminates the need for ancilla qubits during syndrome extraction',
    ],
    correct_index=0,
    explanation='In the Schrödinger picture, an n-qubit state requires 2^n complex amplitudes. In the Heisenberg/stabilizer picture, a stabilizer state is fully described by its n stabilizer generators — each an n-bit Pauli string — requiring only O(n²) bits. Clifford operations update generators in O(n) time each, making stabilizer circuit simulation classically efficient (Gottesman-Knill theorem).',
    hints=[
        'How many bits describe n Pauli generators vs 2^n amplitudes?',
    ],
    grade_mode=GradeMode.AUTO,
)
