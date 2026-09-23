"""Question: qo_entropy_bell_subsystem"""
from core.models import Question

QUESTION = Question(
    id='qo_entropy_bell_subsystem',
    section='Quantum operations',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.quantum_info import Statevector, partial_trace, entropy\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nbell = Statevector(qc)\nprint(entropy(bell), entropy(partial_trace(bell, [0])))\n```',
    options=[
        '0 1.0 — the joint pure state has zero entropy, while each qubit alone has 1 bit',
        '1.0 1.0 — entanglement gives the whole state one bit of entropy too',
        '0 0 — entropy is zero for any state produced by a unitary circuit',
        '1.0 0.5 — the entropy of a subsystem is half the joint entropy',
    ],
    correct_index=0,
    explanation='A Bell state is pure, so its von Neumann entropy is 0. Tracing out one qubit leaves the maximally mixed single-qubit state, whose entropy is log₂2 = 1 (qiskit.quantum_info.entropy defaults to base 2; pass base=np.e for nats). A subsystem entropy larger than the joint entropy is precisely the signature of entanglement.',
    difficulty='hard',
)
