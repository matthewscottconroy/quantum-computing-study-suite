"""Kata: cc_registers_ghz"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc_registers_ghz",
    section="Create circuits",
    title="GHZ with explicit registers",
    difficulty="beginner",
    prompt="""\
Build a 3-qubit GHZ circuit using EXPLICIT registers:

- a QuantumRegister of size 3 named "q"
- a ClassicalRegister of size 3 named "c"
- a QuantumCircuit `qc` built from those two registers
- gates preparing (|000> + |111>) / sqrt(2)
- a measurement of every qubit into the matching classical bit

The tests will sample your circuit — only "000" and "111" may appear.
""",
    starter_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# TODO: create the registers, build qc from them, prepare GHZ, measure.
""",
    test_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

assert isinstance(qc, QuantumCircuit), "qc must be a QuantumCircuit"
qreg_names = [r.name for r in qc.qregs]
creg_names = [r.name for r in qc.cregs]
assert qreg_names == ["q"], f"Expected one QuantumRegister named 'q', got {qreg_names}"
assert creg_names == ["c"], f"Expected one ClassicalRegister named 'c', got {creg_names}"
assert qc.qregs[0].size == 3, "QuantumRegister must have size 3"
assert qc.cregs[0].size == 3, "ClassicalRegister must have size 3"
assert qc.count_ops().get("measure", 0) == 3, "Measure all 3 qubits into the classical register"

_result = StatevectorSampler(seed=42).run([qc], shots=1000).result()
_counts = _result[0].data.c.get_counts()
assert set(_counts) <= {"000", "111"}, (
    f"GHZ should only ever give 000 or 111, got {sorted(_counts)}"
)
assert len(_counts) == 2, f"Expected both 000 and 111 outcomes, got {sorted(_counts)}"
print(f"GHZ counts: {_counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

q = QuantumRegister(3, "q")
c = ClassicalRegister(3, "c")
qc = QuantumCircuit(q, c)
qc.h(q[0])
qc.cx(q[0], q[1])
qc.cx(q[1], q[2])
qc.measure(q, c)
""",
    hints=[
        "QuantumRegister(3, \"q\") and ClassicalRegister(3, \"c\"), then QuantumCircuit(q, c).",
        "GHZ = H on the first qubit, then a chain of CX gates spreading the superposition.",
        "qc.measure(q, c) measures the whole register in one call.",
    ],
)
