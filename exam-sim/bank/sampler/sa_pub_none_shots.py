"""Question: sa_pub_none_shots"""
from core.models import Question

QUESTION = Question(
    id='sa_pub_none_shots',
    section='Sampler',
    question='A circuit has no free parameters, but you want this one PUB to use 4096 shots while the others keep the run default. Which PUB is correct?',
    options=[
        '(qc, None, 4096)',
        '(qc, 4096)',
        '(qc, shots=4096)',
        '(qc, [], 4096)',
    ],
    correct_index=0,
    explanation='PUB elements are positional, so to reach the third slot you must fill the second with None (meaning "no parameter values"). (qc, 4096) would be read as parameter values and fails because the circuit has no parameters, and a tuple cannot carry a keyword argument.',
    difficulty='medium',
)
