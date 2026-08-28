"""Question: cc_measure_all_adds_reg"""
from core.models import Question

QUESTION = Question(
    id='cc_measure_all_adds_reg',
    section='Create circuits',
    question='A developer runs this code:\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.measure_all()\nprint(qc.num_clbits)\n```\n\nWhat is printed?',
    options=[
        '4',
        '2',
        '0',
        'It raises a CircuitError because the circuit already has classical bits',
    ],
    correct_index=0,
    explanation="By default measure_all() adds a brand-new ClassicalRegister named 'meas' sized to the qubit count, even if the circuit already has classical bits — giving 2 + 2 = 4 clbits. Use measure_all(add_bits=False) to measure into the existing bits instead.",
    difficulty='medium',
)
