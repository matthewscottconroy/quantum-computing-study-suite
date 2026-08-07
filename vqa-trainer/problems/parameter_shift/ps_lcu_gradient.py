"""Problem: ps_lcu_gradient"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_lcu_gradient',
    category='Parameter Shift',
    difficulty='advanced',
    question='What is the linear combination of unitaries (LCU) approach to gradient computation for VQAs?',
    choices=[
        'Expresses the gradient as a linear combination of quantum circuit expectation values via the Hadamard test, without requiring shifted circuits',
        'Decomposes the parameter shift formula into a sum of LCU-weighted unitary channels to reduce circuit depth',
        'Uses ancilla qubits and controlled gates to compute all gradients simultaneously in one circuit run',
        'Applies the LCU Hamiltonian simulation method to compute imaginary-time gradients',
    ],
    correct_index=0,
    explanation='The LCU approach computes ∂⟨ψ|O|ψ⟩/∂θ via the Hadamard test: for a gate G(θ) = e^{-iθH}, the gradient involves ⟨ψ|[H, O]|ψ⟩, which can be evaluated by a circuit with an ancilla qubit and a controlled-H operation. This avoids the 2 shifted forward circuits of the standard parameter shift rule, but introduces ancilla overhead and controlled operations. LCU-based gradient methods are particularly useful for generators that are not simple Paulis (where standard parameter shift requires multi-term formulas).',
    hints=[
        'LCU uses an ancilla qubit and a Hadamard test to evaluate the commutator gradient.',
    ],
    grade_mode=GradeMode.MC,
)
