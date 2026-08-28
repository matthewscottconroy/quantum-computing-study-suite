"""Kata: mod_qasm_method"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod_qasm_method",
    section="Modernization",
    title="Modernize: qc.qasm()",
    difficulty="beginner",
    prompt="""\
MODERNIZATION KATA — the `QuantumCircuit.qasm()` method was removed in
Qiskit 1.0. OpenQASM 2 export now lives in the `qiskit.qasm2` module:
`qasm2.dumps(qc)` for a string, `qasm2.dump(qc, file)` for files.

Rewrite the starter keeping the contract:
- `qasm_str` — the OpenQASM 2.0 serialization of the Bell circuit
- `qc2` — the circuit parsed back from `qasm_str`
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x) — modernize me!
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

qasm_str = qc.qasm()

from qiskit.qasm2 import loads
qc2 = loads(qasm_str)
""",
    test_code="""\
from qiskit import QuantumCircuit

assert not hasattr(QuantumCircuit, "qasm"), "sanity: qc.qasm() must not exist in 2.x"
assert isinstance(qasm_str, str) and "OPENQASM 2.0" in qasm_str, (
    "qasm_str must be an OpenQASM 2.0 program string (qasm2.dumps)"
)
assert "h " in qasm_str and "cx " in qasm_str, "Expected h and cx statements"
assert isinstance(qc2, QuantumCircuit), "qc2 must be parsed back from the string"
assert dict(qc2.count_ops()) == dict(qc.count_ops()), (
    f"Round-trip mismatch: {dict(qc.count_ops())} vs {dict(qc2.count_ops())}"
)
print(f"Modernized: round-trip ok, ops = {dict(qc2.count_ops())}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, qasm2

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

qasm_str = qasm2.dumps(qc)
qc2 = qasm2.loads(qasm_str)
""",
    hints=[
        "The method became a module: qiskit.qasm2 with dumps/dump/loads/load.",
        "qasm2.dumps(qc) returns the string the old qc.qasm() used to give you.",
    ],
)
