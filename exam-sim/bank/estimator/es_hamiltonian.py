"""Question: es_hamiltonian"""
from core.models import Question

QUESTION = Question(
    id='es_hamiltonian',
    section='Estimator',
    question='What does this print (rounded)?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.primitives import StatevectorEstimator\nfrom qiskit.quantum_info import SparsePauliOp\n\nqc = QuantumCircuit(2)          # Bell state\nqc.h(0)\nqc.cx(0, 1)\nH = SparsePauliOp(["ZZ", "XX"], coeffs=[0.5, 0.5])\nev = StatevectorEstimator().run([(qc, H)]).result()[0].data.evs\nprint(round(float(ev), 6))\n```',
    options=[
        '1.0',
        '0.0',
        '0.5',
        '-1.0',
    ],
    correct_index=0,
    explanation='The Bell state (|00⟩+|11⟩)/√2 has perfectly correlated qubits in both the Z and X bases: ⟨ZZ⟩ = 1 and ⟨XX⟩ = 1. The weighted sum 0.5·1 + 0.5·1 = 1.0. The estimator evaluates the whole Pauli sum in one pub.',
    difficulty='hard',
)
