"""Question: cc_to_gate_with_clbits"""
from core.models import Question

QUESTION = Question(
    id='cc_to_gate_with_clbits',
    section='Create circuits',
    question='What happens on the last line?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.measure(0, 0)\ngate = qc.to_gate()\n```',
    options=[
        'A QiskitError is raised — a circuit containing classical bits cannot be converted to a Gate',
        'It succeeds and the measurement is silently dropped from the gate',
        'It succeeds and returns a Gate whose num_clbits is 1',
        'A TypeError — to_gate() is a module-level function, not a method',
    ],
    correct_index=0,
    explanation='A Gate must be unitary, so to_gate() refuses any circuit with classical bits: QiskitError("Circuit with classical bits cannot be converted to gate."). Use to_instruction() instead — an Instruction may carry classical bits and measurements.',
    difficulty='medium',
)
