"""Question: rc_no_measurements"""
from core.models import Question

QUESTION = Question(
    id='rc_no_measurements',
    section='Run circuits',
    question='What happens?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit_aer import AerSimulator\n\nqc = QuantumCircuit(2)          # no classical bits\nqc.h(0)\nqc.cx(0, 1)\nresult = AerSimulator().run(qc, shots=100).result()\ncounts = result.get_counts()\n```',
    options=[
        'get_counts() raises QiskitError — the circuit produced no counts because it has no measurements',
        "counts is {'00': 50, '11': 50} — the simulator measures automatically",
        "counts is {'00': 100} — unmeasured qubits read as 0",
        'run() raises an error immediately when given an unmeasured circuit',
    ],
    correct_index=0,
    explanation="AerSimulator happily runs a circuit with no measurements (you might only want saved simulator data), but the Result then holds no counts, so get_counts() raises QiskitError('No counts for experiment ...'). Add measure_all() to get a histogram.",
    difficulty='medium',
)
