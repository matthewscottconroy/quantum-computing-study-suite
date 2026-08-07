"""Problem: surf_lattice_surgery_cnot"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_lattice_surgery_cnot',
    category='Surface Code',
    difficulty='advanced',
    question='How is a logical CNOT implemented between two surface code patches using lattice surgery?',
    choices=[
        'Merge the two patches along a shared boundary by measuring joint stabilizers, then split them — the merge/split sequence implements the CNOT',
        'Apply transversal CNOT qubit-by-qubit between corresponding qubits of the two patches',
        'Measure the logical Z of the control and classically control the logical X of the target',
        'Teleport one logical qubit to be adjacent to the other, then apply a transversal gate',
    ],
    correct_index=0,
    explanation='Lattice surgery CNOT: (1) Merge the two patches along a shared boundary by measuring the joint XX (or ZZ) stabilizers along the seam. (2) The measurement outcomes give a parity value. (3) Split the patches by removing the seam stabilizers. The sequence implements a logical joint parity measurement ⟨X̄_ctrl X̄_tgt⟩ or ⟨Z̄_ctrl Z̄_tgt⟩. Two such measurements (XX joint then ZZ joint) implement the full CNOT gate. This requires no transversal two-qubit gates between separate patches.',
    hints=[
        'Merge measures joint parity; split ends the entangling interaction — together they implement the gate.',
    ],
    grade_mode=GradeMode.AUTO,
)
