"""Problem: vqe_uccsd"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_uccsd',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='UCCSD ansatz stands for:',
    choices=[
        'Unitary Coupled Cluster Singles and Doubles',
        'Universal Classical Circuit Simulation Device',
        'Unitary Clifford Circuit Single Depth',
        'Unrestricted Coupled Cluster Spin Decomposition',
    ],
    correct_index=0,
    explanation='UCCSD = Unitary Coupled Cluster Singles and Doubles. It applies e^{T - T†} to a reference state where T includes single (T₁) and double (T₂) excitation operators. UCCSD is chemically motivated but circuit depth scales poorly with system size.',
    hints=[
        "It's the quantum analogue of the CCSD method in quantum chemistry.",
    ],
    grade_mode=GradeMode.MC,
)
