"""Problem: stab_teleportation_stabilizer"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_teleportation_stabilizer',
    category='Stabilizer Formalism',
    difficulty='advanced',
    question='In the stabilizer formalism, quantum teleportation works by:',
    choices=[
        'Bell measurement on (data, ebit) collapses stabilizers; Pauli correction restores the logical state on the remote qubit',
        'Transversal CNOT between source and destination code blocks',
        'Measuring stabilizers of the data qubit and classically transmitting them',
        'Entangling the data qubit with a magic state, then measuring in the Clifford basis',
    ],
    correct_index=0,
    explanation="In the stabilizer picture: Alice and Bob share an ebit (Bell pair) stabilized by XX and ZZ. Alice's data qubit has stabilizer generators {S} describing her state. A Bell measurement on (data, Alice's ebit) updates the stabilizer tableau: the data qubit stabilizers are transferred to Bob's qubit up to a Pauli correction determined by the measurement outcome (2 classical bits). After Bob applies the Pauli correction, his qubit has exactly Alice's original stabilizer generators.",
    hints=[
        'Track how stabilizer generators transform through the Bell measurement circuit.',
    ],
    grade_mode=GradeMode.AUTO,
)
