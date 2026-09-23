"""Question: cc_control_modifier_ccx"""
from core.models import Question

QUESTION = Question(
    id='cc_control_modifier_ccx',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit.circuit.library import XGate\n\ng = XGate().control(2)\nprint(g.name, g.num_qubits, g.num_ctrl_qubits)\n```',
    options=[
        'ccx 3 2',
        'cx 2 2',
        'ccx 2 2',
        'x 3 2',
    ],
    correct_index=0,
    explanation='Gate.control(n) returns a controlled version with n extra control qubits; for X with two controls Qiskit returns the standard CCXGate, so the name is "ccx", num_qubits is 2 controls + 1 target = 3 and num_ctrl_qubits is 2.',
    difficulty='easy',
)
