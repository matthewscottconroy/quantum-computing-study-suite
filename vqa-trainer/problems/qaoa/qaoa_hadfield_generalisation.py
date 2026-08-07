"""Problem: qaoa_hadfield_generalisation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_hadfield_generalisation',
    category='QAOA',
    difficulty='intermediate',
    question='How does the Quantum Alternating Operator Ansatz (Hadfield et al. 2019) generalise standard QAOA?',
    choices=[
        'It allows arbitrary mixer unitaries and initial states that preserve feasibility constraints, enabling direct encoding of constrained combinatorial problems',
        'It uses continuous-time evolution instead of discrete layers, removing the need to choose p',
        'It replaces the classical optimiser with a quantum subroutine for parameter updates',
        'It adds ancilla qubits to implement any desired mixer using unitary dilation',
    ],
    correct_index=0,
    explanation='Standard QAOA uses the X-mixer B = Σᵢ Xᵢ and initial state |+⟩^n, which put amplitude on infeasible states for constrained problems. The Quantum Alternating Operator Ansatz (QAOA+) allows any mixer U_B(β) that maps the feasible subspace to itself, and any feasible initial state. Examples: XY-mixers for MaxK-Colorable Subgraph that swap colors while preserving k-hot constraints, or ring-mixer for portfolio optimisation preserving the number of selected assets. This framework enables QAOA to handle hard constraints natively without penalty terms.',
    hints=[
        'The key extension is replacing the X-mixer with a feasibility-preserving mixer.',
    ],
    grade_mode=GradeMode.MC,
)
