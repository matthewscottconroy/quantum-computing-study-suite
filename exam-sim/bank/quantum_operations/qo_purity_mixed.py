"""Question: qo_purity_mixed"""
from core.models import Question

QUESTION = Question(
    id='qo_purity_mixed',
    section='Quantum operations',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit.quantum_info import DensityMatrix, purity\n\nprint(purity(DensityMatrix(np.eye(2) / 2)))\n```',
    options=[
        '(0.5+0j) — purity is Tr(ρ²), which is 1/d = 0.5 for the maximally mixed qubit',
        '(1+0j) — every valid density matrix has purity 1',
        '(0+0j) — the maximally mixed state has zero purity',
        '(2+0j) — purity is the inverse of the participation ratio',
    ],
    correct_index=0,
    explanation='purity(ρ) = Tr(ρ²) ranges from 1 for a pure state down to 1/d for the maximally mixed state of dimension d; for one qubit d = 2, so ρ = I/2 gives exactly 0.5. The value is returned as a complex number with a negligible imaginary part, so compare `.real` (or use `round(purity(rho).real, 3)`) rather than testing against a float directly.',
    difficulty='medium',
)
