"""Question: cc_compose_inplace_returns"""
from core.models import Question

QUESTION = Question(
    id='cc_compose_inplace_returns',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\na = QuantumCircuit(1)\nb = QuantumCircuit(1)\nb.x(0)\nc = a.compose(b, inplace=True)\nprint(c, a.size())\n```',
    options=[
        'None 1 — with inplace=True, compose() mutates `a` and returns None',
        'The circuit drawing of the composed circuit, then 1 — compose() always returns a circuit',
        'None 0 — inplace=True discards the composed instructions',
        'It raises a TypeError: inplace and a return value are mutually exclusive',
    ],
    correct_index=0,
    explanation='compose(inplace=True) modifies the caller and returns None, so `c` is None while `a` now holds the single x gate. The default (inplace=False) is the opposite: `a` is untouched and the new circuit comes back as the return value.',
    difficulty='medium',
)
