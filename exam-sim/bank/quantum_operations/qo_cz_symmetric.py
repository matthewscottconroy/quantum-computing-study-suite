"""Question: qo_cz_symmetric"""
from core.models import Question

QUESTION = Question(
    id='qo_cz_symmetric',
    section='Quantum operations',
    question='Which statement about two-qubit gates in Qiskit is TRUE?',
    options=[
        'cz(0, 1) and cz(1, 0) implement exactly the same unitary',
        'cx(0, 1) and cx(1, 0) implement exactly the same unitary',
        'swap(0, 1) and cx(0, 1) implement the same unitary',
        'cz(0, 1) applies Z to both qubits unconditionally',
    ],
    correct_index=0,
    explanation='CZ applies a phase of −1 only to |11⟩, which is symmetric between the two qubits, so control and target are interchangeable. CX flips a specific target qubit, so swapping the arguments changes the unitary.',
    difficulty='medium',
)
