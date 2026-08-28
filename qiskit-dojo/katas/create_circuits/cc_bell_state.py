"""Kata: cc_bell_state"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc_bell_state",
    section="Create circuits",
    title="Build a Bell state",
    difficulty="beginner",
    prompt="""\
Build a 2-qubit QuantumCircuit named `qc` that prepares the Bell state

    (|00> + |11>) / sqrt(2)

Do NOT add any measurements — the tests inspect the statevector directly.

Requirements:
- `qc` is a QuantumCircuit with exactly 2 qubits
- The state after running `qc` on |00> is the Bell state above
""",
    starter_code="""\
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
# TODO: add gates so qc prepares (|00> + |11>)/sqrt(2)
""",
    test_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

assert isinstance(qc, QuantumCircuit), "qc must be a QuantumCircuit"
assert qc.num_qubits == 2, f"qc must have 2 qubits, has {qc.num_qubits}"
assert qc.num_clbits == 0, "Do not add classical bits/measurements to qc"
assert "measure" not in qc.count_ops(), "Do not measure qc — tests use the statevector"

sv = Statevector.from_instruction(qc)
expected = Statevector(np.array([1, 0, 0, 1]) / np.sqrt(2))
assert sv.equiv(expected), (
    f"State is {np.round(sv.data, 3)}, expected (|00>+|11>)/sqrt(2). "
    "Remember: H on one qubit, then CX entangles the pair."
)
print("Bell state prepared correctly.")
""",
    solution_code="""\
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
""",
    hints=[
        "A Bell state is superposition + entanglement: one Hadamard, one CX.",
        "H on qubit 0 gives (|00>+|01>)/sqrt(2); a CX with control 0 copies that superposition onto qubit 1.",
    ],
)
