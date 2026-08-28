"""Kata: cc_compose"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc_compose",
    section="Create circuits",
    title="Compose circuits onto specific qubits",
    difficulty="intermediate",
    prompt="""\
`compose` stitches one circuit onto chosen qubits of another.

Build:
1. `bell_pair` — a 2-qubit circuit preparing (|00> + |11>)/sqrt(2)
2. `qc` — a 3-qubit circuit that:
   - applies X to qubit 0
   - composes `bell_pair` onto qubits [1, 2]

Final state: |1> on qubit 0, Bell pair on qubits 1 and 2.
Remember `compose` RETURNS a new circuit by default (or pass inplace=True).
""",
    starter_code="""\
from qiskit import QuantumCircuit

bell_pair = QuantumCircuit(2)
# TODO: make bell_pair a Bell state

qc = QuantumCircuit(3)
# TODO: x on qubit 0, then compose bell_pair onto qubits [1, 2]
""",
    test_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

assert bell_pair.num_qubits == 2, "bell_pair must be a 2-qubit circuit"
assert qc.num_qubits == 3, "qc must be a 3-qubit circuit"

_ref = QuantumCircuit(3)
_ref.x(0)
_ref.h(1)
_ref.cx(1, 2)
_expected = Statevector.from_instruction(_ref)
_sv = Statevector.from_instruction(qc)
assert _sv.equiv(_expected), (
    "State mismatch. Expected qubit 0 in |1> and a Bell pair on qubits 1,2. "
    "Common slip: compose() returns a NEW circuit — assign it back (qc = qc.compose(...)) "
    "or use inplace=True."
)
print("Composed state is correct.")
""",
    solution_code="""\
from qiskit import QuantumCircuit

bell_pair = QuantumCircuit(2)
bell_pair.h(0)
bell_pair.cx(0, 1)

qc = QuantumCircuit(3)
qc.x(0)
qc = qc.compose(bell_pair, qubits=[1, 2])
""",
    hints=[
        "qc.compose(other, qubits=[1, 2]) maps other's qubit 0 -> qc qubit 1, qubit 1 -> qc qubit 2.",
        "compose returns a new circuit unless you pass inplace=True — a very common trap.",
    ],
)
