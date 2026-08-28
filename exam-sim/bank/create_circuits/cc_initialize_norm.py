"""Question: cc_initialize_norm"""
from core.models import Question

QUESTION = Question(
    id='cc_initialize_norm',
    section='Create circuits',
    question='What happens when this runs?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nqc.initialize([0.5, 0.5], 0)\n```',
    options=[
        'It raises a QiskitError because the amplitude vector is not normalized',
        'It prepares the state (|0⟩ + |1⟩)/√2, normalizing automatically',
        'It prepares a state with 25% probability of measuring 0',
        'It raises a CircuitError because initialize needs 2ⁿ classical bits',
    ],
    correct_index=0,
    explanation='initialize() requires the amplitude vector to be normalized: |0.5|² + |0.5|² = 0.5 ≠ 1, so a QiskitError is raised. The correct equal-superposition amplitudes are [1/√2, 1/√2]. Qiskit does not silently renormalize.',
    difficulty='medium',
)
