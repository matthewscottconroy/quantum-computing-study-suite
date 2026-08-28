"""Question: qo_ccx"""
from core.models import Question

QUESTION = Question(
    id='qo_ccx',
    section='Quantum operations',
    question='What is the final state?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.x(0)\nqc.x(1)\nqc.ccx(0, 1, 2)\n```',
    options=[
        '|111⟩ — both controls are set, so the target flips',
        '|011⟩ — the Toffoli target is qubit 0',
        '|110⟩ — CCX requires the target to start in |1⟩',
        '|100⟩ — only the last control matters',
    ],
    correct_index=0,
    explanation='ccx(0, 1, 2) uses qubits 0 and 1 as controls and qubit 2 as the target. With both controls in |1⟩, the target flips from |0⟩ to |1⟩, giving |111⟩ (all three qubits set).',
    difficulty='easy',
)
