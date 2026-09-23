"""Question: es_pauli_label_order"""
from core.models import Question

QUESTION = Question(
    id='es_pauli_label_order',
    section='Estimator',
    question='What does this print?\n\n```python\nqc = QuantumCircuit(2)\nqc.x(0)\nev = StatevectorEstimator().run([(qc, "IZ")]).result()[0].data.evs\nprint(float(ev))\n```',
    options=[
        '1.0',
        '-1.0',
        '0.0',
        'It raises an error — a plain string is not a valid observable',
    ],
    correct_index=1,
    explanation='Pauli labels are little-endian: the RIGHTMOST character is qubit 0. "IZ" therefore measures Z on qubit 0, which X has flipped to |1⟩, so the value is −1; "ZI" would give +1. Plain label strings are perfectly valid observables — they are coerced to Pauli terms for you.',
    difficulty='medium',
)
