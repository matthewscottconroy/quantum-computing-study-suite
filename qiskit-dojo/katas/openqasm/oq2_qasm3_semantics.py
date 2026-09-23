"""Kata: oq2_qasm3_semantics"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="oq2_qasm3_semantics",
    section="OpenQASM",
    title="A QASM 3 round-trip that preserves the unitary",
    difficulty="advanced",
    prompt="""\
Matching gate COUNTS after a round-trip is weak evidence: the same tally
can describe a different circuit. The strong check is semantic — rebuild
the operator and compare.

Build:
1. `qc`      — a 3-qubit circuit, no measurements:
               h(0), cx(0, 1), rz(pi/4, 1), cx(1, 2), sx(2)
2. `program` — qc serialized to OpenQASM 3 (qasm3.dumps)
3. `qc2`     — parsed back from `program` (qasm3.loads)
4. `same`    — a bool: do the two circuits implement the same unitary?
               Use Operator(qc2).equiv(Operator(qc))

`Operator.equiv` ignores a global phase, which is exactly the right
tolerance for a serialization round-trip.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit, qasm3
from qiskit.quantum_info import Operator

# TODO: qc, program = qasm3.dumps(qc), qc2 = qasm3.loads(program), same = ...
""",
    test_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

assert isinstance(program, str), "program must be a string (qasm3.dumps)"
assert "OPENQASM 3" in program, (
    "The program must carry the OpenQASM 3 header — qiskit.qasm3, not qiskit.qasm2"
)
assert 'include "stdgates.inc"' in program, (
    "The exporter pulls in the standard gate library; h/cx/rz/sx come from there"
)
assert isinstance(qc2, QuantumCircuit), "qc2 must come from qasm3.loads(program)"
assert qc.num_qubits == 3 and "measure" not in qc.count_ops(), (
    "qc is the 3-qubit unmeasured circuit from the prompt"
)
_ops = dict(qc.count_ops())
assert _ops == {"h": 1, "cx": 2, "rz": 1, "sx": 1}, (
    f"Expected h:1, cx:2, rz:1, sx:1 in qc, got {_ops}"
)
assert Operator(qc2).equiv(Operator(qc)), (
    "The reloaded circuit does not implement the same unitary — the round-trip lost "
    "something (check the rz angle and the cx qubit order)"
)
assert same is True, (
    f"same must be the bool from Operator(qc2).equiv(Operator(qc)), got {same!r}"
)
print(program)
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit, qasm3
from qiskit.quantum_info import Operator

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.rz(np.pi / 4, 1)
qc.cx(1, 2)
qc.sx(2)

program = qasm3.dumps(qc)
qc2 = qasm3.loads(program)
same = Operator(qc2).equiv(Operator(qc))
""",
    hints=[
        "qasm3.dumps(qc) -> str and qasm3.loads(s) -> QuantumCircuit, mirroring the qasm2 module.",
        "Operator(circuit) builds the dense unitary; .equiv() compares up to a global phase.",
        "Operator only works on unitary circuits — measurements would make it raise.",
    ],
)
