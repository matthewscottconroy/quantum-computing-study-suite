"""Question: qo_dm_purity_subsystem"""
from core.models import Question

QUESTION = Question(
    id='qo_dm_purity_subsystem',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import DensityMatrix, partial_trace\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\ndm = DensityMatrix(qc)\nprint(round(dm.purity().real, 3), round(partial_trace(dm, [1]).purity().real, 3))\n```',
    options=[
        '1.0 0.5 — the joint state is pure, but each half of a Bell pair is maximally mixed',
        '1.0 1.0 — tracing out a qubit of a pure state leaves another pure state',
        '0.5 0.5 — a density matrix built from a circuit is never pure',
        '1.0 0.25 — the subsystem purity is 1/d² for a two-qubit state',
    ],
    correct_index=0,
    explanation='DensityMatrix(qc) of a unitary circuit is the pure projector |ψ⟩⟨ψ| with purity 1. Tracing out either qubit of a maximally entangled pair leaves I/2, whose purity is 1/d = 0.5. This 1.0-versus-0.5 pair is the standard numerical fingerprint of maximal two-qubit entanglement, and it is what the reduced-state entropy of 1 bit measures in information terms.',
    difficulty='hard',
)
