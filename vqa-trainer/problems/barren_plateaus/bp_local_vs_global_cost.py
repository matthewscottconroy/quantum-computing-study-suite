"""Problem: bp_local_vs_global_cost"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bp_local_vs_global_cost',
    category='Barren Plateaus',
    difficulty='intermediate',
    question="Cerezo et al. (2021) showed that local cost functions avoid barren plateaus. What makes a cost function 'local' in this sense?",
    choices=[
        'The observable acts non-trivially on O(1) qubits (e.g. a single-qubit or two-qubit Pauli)',
        'The cost function is evaluated on a local (nearby) region of parameter space',
        'The circuit uses only nearest-neighbour gates',
        'The cost is computed from classical local post-processing, not quantum measurement',
    ],
    correct_index=0,
    explanation='A local cost function involves an observable that acts non-trivially on only O(1) qubits, e.g. C = Σᵢ (I - Zᵢ)/2 (sum of single-qubit terms). For local costs with L-layer circuits, Var[∂C/∂θ] ∝ 2^{-O(L)} rather than 2^{-n}, giving polynomial (not exponential) suppression in the system size. The intuition: local observables only probe O(1)-qubit reduced states, which are less affected by global scrambling than the full n-qubit state.',
    hints=[
        "'Local' refers to the number of qubits the observable acts on, not the circuit geometry.",
    ],
    grade_mode=GradeMode.MC,
)
