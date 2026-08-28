"""Question: ra_probabilities_dict"""
from core.models import Question

QUESTION = Question(
    id='ra_probabilities_dict',
    section='Results analysis',
    question="Without running any shots, which call gives the EXACT outcome probabilities of a circuit as a dictionary like {'00': 0.5, '11': 0.5}?",
    options=[
        'Statevector(qc).probabilities_dict()',
        'AerSimulator().run(qc, shots=0).result().get_counts()',
        'qc.probabilities()',
        'Statevector(qc).get_counts()',
    ],
    correct_index=0,
    explanation='Statevector(qc) computes the exact final state (for a measurement-free circuit) and probabilities_dict() squares the amplitudes into a bitstring-keyed dictionary. Zero-shot backend runs are invalid, and neither QuantumCircuit nor Statevector has the other listed methods.',
    difficulty='easy',
)
