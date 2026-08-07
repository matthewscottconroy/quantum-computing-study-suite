"""Problem: stab_clifford_conjugation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_clifford_conjugation',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='A stabilizer state |S⟩ is acted on by a Clifford unitary U. If g is a stabilizer generator of |S⟩, what stabilizes U|S⟩?',
    choices=[
        'UgU†',
        'U†gU',
        'g (unchanged)',
        'UgU†  only if g is Hermitian',
    ],
    correct_index=0,
    explanation='If g|S⟩ = |S⟩ then (UgU†)(U|S⟩) = Ug|S⟩ = U|S⟩. So UgU† stabilizes U|S⟩. Since U is Clifford, UgU† is also a Pauli operator, keeping the state in the stabilizer formalism. This is the Heisenberg picture update rule.',
    hints=[
        'Conjugate the stabilizer by U, just as in the Heisenberg picture.',
    ],
    grade_mode=GradeMode.AUTO,
)
