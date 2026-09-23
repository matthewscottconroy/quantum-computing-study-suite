"""Question: qo_fidelity_global_phase"""
from core.models import Question

QUESTION = Question(
    id='qo_fidelity_global_phase',
    section='Quantum operations',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit.quantum_info import Statevector, state_fidelity\n\na = Statevector([1 / np.sqrt(2), 1 / np.sqrt(2)])\nb = Statevector([1j / np.sqrt(2), 1j / np.sqrt(2)])\nprint(round(state_fidelity(a, b), 6), a == b)\n```',
    options=[
        '1.0 False — fidelity ignores global phase, but == compares amplitudes elementwise',
        '0.0 False — the two states are orthogonal because one is imaginary',
        '1.0 True — multiplying by i changes nothing that Statevector records',
        '0.5 False — the overlap |⟨a|b⟩| is 1/√2',
    ],
    correct_index=0,
    explanation="state_fidelity is |⟨a|b⟩|², and the modulus removes the global phase factor i, giving 1.0: the two vectors are the same physical state. `==` is exact elementwise array equality, so it reports False; `a.equiv(b)` is the comparison that tolerates a global phase. Mixing these three up is a classic source of 'my test fails but the physics is right'.",
    difficulty='medium',
)
