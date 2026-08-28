"""Question: oq_dumps3"""
from core.models import Question

QUESTION = Question(
    id='oq_dumps3',
    section='OpenQASM',
    question='Which call converts a QuantumCircuit into an OpenQASM 3 program string?',
    options=[
        'from qiskit import qasm3; program = qasm3.dumps(qc)',
        'program = qc.qasm(version=3)',
        'from qiskit import qasm3; program = qasm3.dump(qc)',
        'program = str(qc)',
    ],
    correct_index=0,
    explanation='qasm3.dumps(qc) returns the program as a string; qasm3.dump(qc, file) writes to a file object (like json.dump/dumps). The QuantumCircuit.qasm() method was removed in Qiskit 1.0, and str(qc) gives the text drawing, not QASM.',
    difficulty='easy',
)
