"""Kata: cc2_w_state"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc2_w_state",
    section="Create circuits",
    title="Prepare a 3-qubit W state",
    difficulty="intermediate",
    prompt="""\
GHZ is not the only 3-qubit entangled state worth knowing. The W state

    |W> = (|001> + |010> + |100>) / sqrt(3)

spreads one excitation over three qubits, and unlike GHZ it stays
entangled when a qubit is lost.

Build `qc`: a 3-qubit QuantumCircuit, no classical bits and no
measurements, whose statevector is |W>.

Any construction is accepted — a hand-rolled ry/ch/cx ladder or a
`qc.initialize(...)` of the amplitude vector. The tests only look at the
resulting statevector (up to global phase).
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
# TODO: prepare (|001> + |010> + |100>) / sqrt(3)
""",
    test_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

assert isinstance(qc, QuantumCircuit), "qc must be a QuantumCircuit"
assert qc.num_qubits == 3, f"qc must have 3 qubits, has {qc.num_qubits}"
assert qc.num_clbits == 0, "Do not add classical bits — the tests read the statevector"
assert "measure" not in qc.count_ops(), "Do not measure qc"

_amps = np.zeros(8, dtype=complex)
for _label in ("001", "010", "100"):
    _amps[int(_label, 2)] = 1 / np.sqrt(3)
_expected = Statevector(_amps)

_sv = Statevector.from_instruction(qc)
assert _sv.equiv(_expected), (
    f"State is {np.round(_sv.data, 3)}, expected equal weight 1/sqrt(3) on "
    "|001>, |010> and |100> and zero everywhere else."
)
_probs = _sv.probabilities_dict()
assert set(_probs) == {"001", "010", "100"}, (
    f"Only the single-excitation basis states may appear, got {sorted(_probs)}"
)
print(f"W state prepared: {_sv.probabilities_dict()}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
qc.ry(2 * np.arccos(1 / np.sqrt(3)), 0)
qc.ch(0, 1)
qc.cx(1, 2)
qc.cx(0, 1)
qc.x(0)
""",
    hints=[
        "The quickest route: build the 8-amplitude numpy vector and call qc.initialize(vec, [0, 1, 2]).",
        "By hand: ry(2*arccos(1/sqrt(3))) on qubit 0 splits the weight 1/3 vs 2/3, then a "
        "controlled-H splits the remaining 2/3 evenly.",
        "Finish the ladder with cx(1, 2), cx(0, 1) and an x(0) so exactly one qubit is excited.",
    ],
)
