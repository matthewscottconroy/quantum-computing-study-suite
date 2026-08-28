"""Question: cc_ghz_completion"""
from core.models import Question

QUESTION = Question(
    id='cc_ghz_completion',
    section='Create circuits',
    question='Which line completes this circuit so it prepares the 3-qubit GHZ state (|000⟩ + |111⟩)/√2?\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.cx(0, 1)\n# --- which line goes here? ---\n```',
    options=[
        'qc.cx(1, 2)',
        'qc.cx(2, 0)',
        'qc.h(2)',
        'qc.x(2)',
    ],
    correct_index=0,
    explanation='After h(0); cx(0,1) the state is (|000⟩+|011⟩)/√2 (qubit 2 still |0⟩). A CX from either entangled qubit onto qubit 2 — cx(1,2) — extends the correlation to all three qubits. cx(2,0) uses qubit 2 (in |0⟩) as the control, so it does nothing; h(2) or x(2) give product states.',
    difficulty='easy',
)
