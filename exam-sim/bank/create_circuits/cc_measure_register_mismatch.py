"""Question: cc_measure_register_mismatch"""
from core.models import Question

QUESTION = Question(
    id='cc_measure_register_mismatch',
    section='Create circuits',
    question='What happens when this runs?\n\n```python\nfrom qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\n\nqr = QuantumRegister(3, "q")\ncr = ClassicalRegister(2, "c")\nqc = QuantumCircuit(qr, cr)\nqc.measure(qr, cr)\n```',
    options=[
        'A CircuitError ("register size error") — measuring a whole register into a whole register requires equal sizes',
        'Qubits 0 and 1 are measured into c[0] and c[1]; qubit 2 is silently skipped',
        'It wraps around: qubit 2 is measured into c[0], overwriting the first result',
        'A third classical bit is appended to cr so the shapes match',
    ],
    correct_index=0,
    explanation='measure() broadcasts a register onto a register only when both have the same length. QuantumRegister(3) into ClassicalRegister(2) raises CircuitError("register size error"). To measure a subset, pass explicit lists, e.g. qc.measure([0, 1], [0, 1]).',
    difficulty='medium',
)
