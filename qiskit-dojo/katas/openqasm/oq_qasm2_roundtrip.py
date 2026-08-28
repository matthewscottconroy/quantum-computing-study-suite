"""Kata: oq_qasm2_roundtrip"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="oq_qasm2_roundtrip",
    section="OpenQASM",
    title="OpenQASM 2 round-trip",
    difficulty="intermediate",
    prompt="""\
In Qiskit 2.x, OpenQASM 2 serialization lives in the `qiskit.qasm2`
module (the old qc.qasm() method is gone).

Build:
1. `qc` — Bell circuit with measure_all()
2. `qasm_str` — the OpenQASM 2 string of `qc` (qasm2.dumps)
3. `qc2` — a circuit parsed BACK from `qasm_str` (qasm2.loads)

The tests check the header, gate content, and that the round-trip
preserves the operation counts.
""",
    starter_code="""\
from qiskit import QuantumCircuit, qasm2

# TODO: qc, qasm_str = qasm2.dumps(qc), qc2 = qasm2.loads(qasm_str)
""",
    test_code="""\
from qiskit import QuantumCircuit

assert isinstance(qasm_str, str), "qasm_str must be a string (use qasm2.dumps)"
assert "OPENQASM 2.0" in qasm_str, "The program must carry the OPENQASM 2.0 header"
assert "h " in qasm_str and "cx " in qasm_str, "Expected h and cx statements in the QASM"
assert isinstance(qc2, QuantumCircuit), "qc2 must be parsed back with qasm2.loads"
assert dict(qc2.count_ops()) == dict(qc.count_ops()), (
    f"Round-trip changed the circuit: {dict(qc.count_ops())} -> {dict(qc2.count_ops())}"
)
print(qasm_str)
""",
    solution_code="""\
from qiskit import QuantumCircuit, qasm2

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

qasm_str = qasm2.dumps(qc)
qc2 = qasm2.loads(qasm_str)
""",
    hints=[
        "qasm2.dumps(qc) -> str, qasm2.loads(s) -> QuantumCircuit. (dump/load work with files.)",
        "You can import qasm2 straight from the top level: from qiskit import qasm2.",
    ],
)
