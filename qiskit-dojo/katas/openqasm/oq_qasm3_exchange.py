"""Kata: oq_qasm3_exchange"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="oq_qasm3_exchange",
    section="OpenQASM",
    title="OpenQASM 3: loads and dumps",
    difficulty="intermediate",
    prompt="""\
OpenQASM 3 support lives in `qiskit.qasm3`. The starter gives you an
OpenQASM 3 program as a string.

Build:
1. `qc` — the QuantumCircuit parsed from `program` (qasm3.loads)
2. `n_cx` — how many cx gates `qc` contains
3. `dumped` — `qc` serialized back to an OpenQASM 3 string (qasm3.dumps)

The tests verify the parsed gate counts and that `dumped` carries an
OPENQASM 3 header (not 2.0!).
""",
    starter_code='''\
from qiskit import qasm3

program = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] c;
h q[0];
cx q[0], q[1];
cx q[1], q[2];
c = measure q;
"""

# TODO: qc = ..., n_cx = ..., dumped = ...
''',
    test_code="""\
from qiskit import QuantumCircuit

assert isinstance(qc, QuantumCircuit), "qc must come from qasm3.loads(program)"
assert qc.num_qubits == 3, f"The program declares 3 qubits, qc has {qc.num_qubits}"
_ops = qc.count_ops()
assert _ops.get("h", 0) == 1 and _ops.get("measure", 0) == 3, (
    f"Expected 1 h and 3 measures from the program, got {dict(_ops)}"
)
assert n_cx == 2, f"The program has 2 cx gates, you reported {n_cx}"
assert isinstance(dumped, str) and "OPENQASM 3" in dumped, (
    "dumped must be an OpenQASM 3 string (qasm3.dumps) with its version header"
)
assert "OPENQASM 2.0" not in dumped, "That's the qasm2 serializer — use qiskit.qasm3"
print(dumped)
""",
    solution_code='''\
from qiskit import qasm3

program = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] c;
h q[0];
cx q[0], q[1];
cx q[1], q[2];
c = measure q;
"""

qc = qasm3.loads(program)
n_cx = qc.count_ops().get("cx", 0)
dumped = qasm3.dumps(qc)
''',
    hints=[
        "qasm3.loads(program) parses the string into a QuantumCircuit.",
        "count_ops().get(\"cx\", 0) reads the gate tally.",
        "qasm3.dumps(qc) emits OpenQASM 3 — same verbs as qasm2, different module.",
    ],
)
