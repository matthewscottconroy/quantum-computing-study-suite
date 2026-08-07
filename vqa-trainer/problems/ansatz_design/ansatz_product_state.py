"""Problem: ansatz_product_state"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_product_state',
    category='Ansatz Design',
    difficulty='beginner',
    question='What is a product-state (zero-entanglement) ansatz and when does it fail for VQE?',
    choices=[
        'A tensor product of independent single-qubit states; fails when the true ground state is entangled (strongly correlated systems)',
        'An ansatz with product-form gates (CNOT followed by single-qubit rotations) that still generates entanglement',
        'A classical shadow protocol that approximates quantum states as products',
        'Any ansatz with no parameterised gates — a fixed product state input',
    ],
    correct_index=0,
    explanation='A product ansatz |ψ(θ)⟩ = ⊗ᵢ|φᵢ(θᵢ)⟩ has no entanglement between qubits. It can only represent mean-field (Hartree-Fock-level) states. For weakly correlated molecules, the HF state is already >99% of the ground state, so a product ansatz suffices. For strongly correlated systems (transition metals, molecules near bond-breaking), the ground state has significant multi-reference character requiring entanglement between spin-orbitals — a product ansatz cannot capture this and gives a poor energy upper bound.',
    hints=[
        'Product state = no entanglement = mean-field. When does mean-field fail?',
    ],
    grade_mode=GradeMode.MC,
)
