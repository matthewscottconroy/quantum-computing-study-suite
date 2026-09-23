"""Question: es_statevector_crosscheck"""
from core.models import Question

QUESTION = Question(
    id='es_statevector_crosscheck',
    section='Estimator',
    question='Which line reproduces the estimator value ⟨ψ|H|ψ⟩ exactly, without using any primitive?\n\n```python\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nH = SparsePauliOp(["ZZ", "XX"], coeffs=[0.5, 0.5])\n```',
    options=[
        'Statevector(qc).probabilities_dict()[H]',
        'Operator(qc).data.trace()',
        'np.real(Statevector(qc).expectation_value(H))',
        'sum(Statevector(qc).sample_counts(1024).values())',
    ],
    correct_index=2,
    explanation='Statevector.expectation_value(op) computes ⟨ψ|O|ψ⟩ analytically and matches StatevectorEstimator to floating-point precision (1.0 for this Bell state); np.real drops the negligible imaginary residue. Probability dictionaries are keyed by bitstrings, the trace of a unitary says nothing about ⟨H⟩, and summing counts just returns the shot total.',
    difficulty='easy',
)
