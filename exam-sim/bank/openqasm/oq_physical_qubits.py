"""Question: oq_physical_qubits"""
from core.models import Question

QUESTION = Question(
    id='oq_physical_qubits',
    section='OpenQASM',
    question='What does this print?\n\n```python\nprog = """\nOPENQASM 3.0;\ninclude "stdgates.inc";\nh $0;\ncx $0, $1;\n"""\nqc = qasm3.loads(prog)\nprint(qc.num_qubits, len(qc.qregs))\n```',
    options=[
        '2 0',
        '2 1',
        '0 0',
        'QASM3ImporterError — every qubit must be declared before use',
    ],
    correct_index=0,
    explanation='The $n syntax names PHYSICAL (hardware) qubits and needs no declaration, so the importer builds a circuit of two loose qubits with no QuantumRegister at all — which is what already-transpiled, hardware-ready programs look like. Pass num_qubits= to qasm3.loads if the circuit should be widened to the full device size.',
    difficulty='hard',
)
