"""Problem: vqe_classical_quantum_roles"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_classical_quantum_roles',
    category='VQE Fundamentals',
    difficulty='beginner',
    question='In VQE, who is responsible for optimising the circuit parameters — the quantum computer or the classical computer?',
    choices=[
        'The classical computer optimises; the quantum computer evaluates the energy',
        'The quantum computer optimises using quantum gradient descent',
        'Both computers share the optimisation equally',
        'Neither — parameters are fixed by physical symmetry',
    ],
    correct_index=0,
    explanation="VQE is a hybrid algorithm: the quantum computer prepares |ψ(θ)⟩ and measures ⟨H⟩(θ), but the parameter update θ → θ' is performed by a classical optimiser (e.g. gradient descent, COBYLA, SPSA). The loop repeats until ⟨H⟩ converges. This design allows VQE to run on NISQ devices that cannot yet perform fault-tolerant quantum computation.",
    hints=[
        "The 'V' in VQE involves a classical optimisation loop.",
    ],
    grade_mode=GradeMode.MC,
)
