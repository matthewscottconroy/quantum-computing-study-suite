"""Question: cc_inverse_order"""
from core.models import Question

QUESTION = Question(
    id='cc_inverse_order',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(1)\nqc.h(0)\nqc.t(0)\ninv = qc.inverse()\nprint([instr.operation.name for instr in inv.data])\n```',
    options=[
        "['tdg', 'h']",
        "['h', 'tdg']",
        "['h', 't']",
        "['tdg', 'hdg']",
    ],
    correct_index=0,
    explanation='inverse() reverses the instruction order and replaces each gate with its adjoint: (H·T)† = T†·H†. H is Hermitian so H† = H (there is no "hdg" gate), while T† is tdg. The reversal is the part most often missed.',
    difficulty='easy',
)
