"""Question: qo_random_statevector_dims"""
from core.models import Question

QUESTION = Question(
    id='qo_random_statevector_dims',
    section='Quantum operations',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit.quantum_info import random_statevector\n\nrs = random_statevector(4, seed=0)\nprint(type(rs).__name__, rs.num_qubits, round(float(np.linalg.norm(rs.data)), 6))\n```',
    options=[
        'Statevector 2 1.0 — the argument is the Hilbert-space DIMENSION, so 4 means 2 qubits',
        'Statevector 4 1.0 — the argument is the number of qubits',
        'ndarray 2 1.0 — random_statevector returns a raw NumPy vector',
        'Statevector 2 4.0 — the vector is scaled by the dimension, not normalized',
    ],
    correct_index=0,
    explanation='random_statevector(dims, seed=...) takes the DIMENSION (or a tuple of subsystem dimensions), so 4 = 2² produces a 2-qubit Statevector; use random_statevector(2**n) for n qubits. The sample is Haar-random and always normalized, and the seed makes it reproducible. random_clifford and random_unitary take a qubit count and a dimension respectively — another easy mix-up.',
    difficulty='medium',
)
