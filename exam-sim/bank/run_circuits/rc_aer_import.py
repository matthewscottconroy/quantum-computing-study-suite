"""Question: rc_aer_import"""
from core.models import Question

QUESTION = Question(
    id='rc_aer_import',
    section='Run circuits',
    question='Which import gives you a local simulator backend in Qiskit 2.x?',
    options=[
        'from qiskit_aer import AerSimulator',
        'from qiskit import Aer',
        'from qiskit.providers.aer import QasmSimulator',
        'from qiskit import BasicSimulator',
    ],
    correct_index=0,
    explanation='Aer lives in the separate qiskit-aer package: from qiskit_aer import AerSimulator. The qiskit.Aer provider and qiskit.providers.aer path were removed years ago; BasicSimulator exists but under qiskit.providers.basic_provider, not as a top-level qiskit import.',
    difficulty='easy',
)
