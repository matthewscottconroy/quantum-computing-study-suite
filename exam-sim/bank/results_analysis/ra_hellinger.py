"""Question: ra_hellinger"""
from core.models import Question

QUESTION = Question(
    id='ra_hellinger',
    section='Results analysis',
    question='Which qiskit.quantum_info function quantifies how similar two COUNTS distributions are, returning 1.0 for identical distributions?',
    options=[
        'hellinger_fidelity(counts_a, counts_b)',
        'state_fidelity(counts_a, counts_b)',
        'process_fidelity(counts_a, counts_b)',
        'counts_a.compare(counts_b)',
    ],
    correct_index=0,
    explanation='hellinger_fidelity works directly on counts dictionaries — 1.0 means identical distributions, 0.0 means disjoint support. state_fidelity and process_fidelity compare quantum states and channels respectively, not measurement histograms.',
    difficulty='medium',
)
