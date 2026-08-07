"""Problem: stab_cluster_mbqc"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_cluster_mbqc',
    category='Stabilizer Formalism',
    difficulty='intermediate',
    question='What role does a cluster state (2D graph state) play in measurement-based quantum computation (MBQC)?',
    choices=[
        'It serves as a universal resource state: single-qubit measurements in adaptive bases implement any quantum circuit',
        'It provides a fault-tolerant code for storing logical qubits',
        'It allows classical simulation of all quantum circuits',
        'It implements CNOT gates via its entanglement structure without any measurements',
    ],
    correct_index=0,
    explanation='In MBQC, a 2D cluster state (lattice graph state) is the resource. Computation proceeds by measuring individual qubits in adaptively chosen bases (e.g., cos(θ)X + sin(θ)Y). The measurement outcomes drive Clifford corrections on remaining qubits. This implements any quantum circuit using only single-qubit measurements on an entangled resource — no two-qubit gates on the data are needed once the resource is prepared.',
    hints=[
        'MBQC separates entanglement generation (offline) from computation (adaptive measurements).',
    ],
    grade_mode=GradeMode.AUTO,
)
