"""Question: rc_isa_counts_width"""
from core.models import Question

QUESTION = Question(
    id='rc_isa_counts_width',
    section='Run circuits',
    question='qc is a 2-qubit Bell circuit ending in measure_all(). It is transpiled for a 5-qubit backend, then run on AerSimulator. How wide are the bitstring keys?\n\n```python\nisa = pm.run(qc)              # pm built from the 5-qubit backend\ncounts = AerSimulator().run(isa, shots=200).result().get_counts()\nprint(set(map(len, counts)))\n```',
    options=[
        '{2} — key width follows the number of classical bits, which transpilation does not change',
        '{5} — the ISA circuit has 5 qubits, so every key has 5 characters',
        '{5} — three ancilla qubits are measured into extra classical bits set to 0',
        'It raises an error: the classical register is too small for a 5-qubit circuit',
    ],
    correct_index=0,
    explanation='Transpilation widens the *quantum* register to the backend width but leaves the classical register alone. measure_all() created a 2-bit register, so the histogram keys stay 2 characters wide ("00"/"11" for a Bell state). Ancillas are never measured.',
    difficulty='hard',
)
