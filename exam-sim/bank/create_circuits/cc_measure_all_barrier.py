"""Question: cc_measure_all_barrier"""
from core.models import Question

QUESTION = Question(
    id='cc_measure_all_barrier',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.measure_all()\nprint(qc.size(), len(qc.data))\n```',
    options=[
        '3 4 — measure_all() also inserts a barrier, which len(qc.data) counts but size() does not',
        '4 4 — size() counts the barrier like any other instruction',
        '3 3 — measure_all() adds only the two measurements',
        '4 3 — the barrier replaces one of the measurements',
    ],
    correct_index=0,
    explanation='measure_all() adds a barrier across all qubits and then one measure per qubit. qc.data therefore holds 4 entries (h, barrier, measure, measure), but size() deliberately excludes barriers and other directives, so it reports 3. measure_all() always inserts that barrier (its only keyword arguments are inplace and add_bits); call qc.measure(range(n), range(n)) yourself if you need measurements with no barrier.',
    difficulty='hard',
)
