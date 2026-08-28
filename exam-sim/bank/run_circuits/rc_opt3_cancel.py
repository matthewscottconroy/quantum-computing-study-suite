"""Question: rc_opt3_cancel"""
from core.models import Question

QUESTION = Question(
    id='rc_opt3_cancel',
    section='Run circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit, transpile\n\nqc = QuantumCircuit(1)\nqc.h(0)\nqc.h(0)\nout = transpile(qc, basis_gates=["h", "cx"], optimization_level=3)\nprint(out.size())\n```',
    options=[
        '0 — two consecutive H gates cancel to the identity',
        '2 — transpile never removes user gates',
        '1 — the pair is merged into a single H',
        'It raises an error because the circuit has no measurements',
    ],
    correct_index=0,
    explanation='H is self-inverse, so H·H = I. At optimization_level 3 (and even lower levels) the transpiler cancels the adjacent pair, leaving an empty circuit. Transpilation freely rewrites and removes gates as long as the unitary is preserved, and measurements are never required.',
    difficulty='medium',
)
