"""Question: qo_group_commuting"""
from core.models import Question

QUESTION = Question(
    id='qo_group_commuting',
    section='Quantum operations',
    question='What does this print, and why is the method useful?\n\n```python\nfrom qiskit.quantum_info import SparsePauliOp\n\nH = SparsePauliOp(["XX", "YY", "ZZ", "IZ"])\nprint(len(H.group_commuting()))\n```',
    options=[
        '2 — the terms split into {IZ, ZZ} and {XX, YY}, each group shareable in one measurement basis',
        '4 — every term must be measured on its own',
        '1 — all four terms commute with each other',
        '3 — only the two Z-type terms can be grouped',
    ],
    correct_index=0,
    explanation='group_commuting() partitions the terms into mutually commuting sets, returning a list of SparsePauliOps. ZZ and IZ are both diagonal; XX and YY commute with each other but not with the Z-type terms, so two groups result. Each group can be estimated from ONE basis-rotated circuit, which is how Estimator implementations cut the circuit count (pass qubit_wise=True for the stricter qubit-wise grouping).',
    difficulty='hard',
)
