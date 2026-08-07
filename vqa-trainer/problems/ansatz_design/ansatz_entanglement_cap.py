"""Problem: ansatz_entanglement_cap"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_entanglement_cap',
    category='Ansatz Design',
    difficulty='intermediate',
    question='Why is entanglement capacity an important property of a VQA ansatz for quantum chemistry?',
    choices=[
        'Molecular ground states are often strongly entangled; shallow product-state ansätze cannot represent them',
        'Entanglement reduces the number of Pauli terms in H',
        'NISQ devices can only prepare entangled states',
        'Entanglement reduces measurement overhead',
    ],
    correct_index=0,
    explanation='Strongly correlated molecules (e.g. transition metals) have ground states with high entanglement. Product-state ansätze (no entangling gates) miss this correlation. The ansatz must have sufficient entanglement capacity without creating barren plateaus.',
    hints=[
        "Think about what makes a molecule 'strongly correlated'.",
    ],
    grade_mode=GradeMode.MC,
)
