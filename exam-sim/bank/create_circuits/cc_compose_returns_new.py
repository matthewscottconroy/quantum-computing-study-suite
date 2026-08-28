"""Question: cc_compose_returns_new"""
from core.models import Question

QUESTION = Question(
    id='cc_compose_returns_new',
    section='Create circuits',
    question='After this code runs, how many instructions does circuit `a` contain?\n\n```python\nfrom qiskit import QuantumCircuit\n\na = QuantumCircuit(2)\na.h(0)\nb = QuantumCircuit(2)\nb.cx(0, 1)\nc = a.compose(b)\n```',
    options=[
        '1 — compose() returns a new circuit and leaves `a` unchanged',
        '2 — compose() appends `b` onto `a` in place',
        '0 — compose() moves the instructions of `a` into `c`',
        '3 — `c` is stored inside `a` as a sub-circuit',
    ],
    correct_index=0,
    explanation='compose() is not in-place by default: it returns a new circuit `c` containing h then cx, while `a` keeps only its single h gate. Pass inplace=True to modify `a` directly.',
    difficulty='medium',
)
