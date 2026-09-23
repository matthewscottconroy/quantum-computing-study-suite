"""Kata: cc2_multi_register"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc2_multi_register",
    section="Create circuits",
    title="Two quantum registers and a cross-register Toffoli",
    difficulty="beginner",
    prompt="""\
A circuit can hold several registers; qubit indices run through them in
the order the registers were added.

Build a 2-bit AND gate:
1. `a` — QuantumRegister(2, "a")     (the two inputs)
2. `b` — QuantumRegister(1, "b")     (the output qubit)
3. `res` — ClassicalRegister(1, "res")
4. `qc` — QuantumCircuit(a, b, res) that sets BOTH input qubits to |1>,
   applies a Toffoli (ccx) with controls a[0], a[1] and target b[0],
   then measures b[0] into res[0]

With both inputs 1 the AND is 1, so every shot must read "1".
""",
    starter_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# TODO: registers a (2), b (1), res (1); build qc; x both inputs;
#       ccx into b[0]; measure b[0] -> res[0]
""",
    test_code="""\
from qiskit.primitives import StatevectorSampler

assert [r.name for r in qc.qregs] == ["a", "b"], (
    f"Expected quantum registers 'a' then 'b', got {[r.name for r in qc.qregs]}"
)
assert [r.name for r in qc.cregs] == ["res"], (
    f"Expected one classical register named 'res', got {[r.name for r in qc.cregs]}"
)
assert qc.num_qubits == 3, f"a(2) + b(1) = 3 qubits, got {qc.num_qubits}"
assert qc.find_bit(b[0]).index == 2, (
    "b[0] should be qubit index 2 — registers are laid out in the order given to "
    "QuantumCircuit(a, b, res)"
)
assert "ccx" in qc.count_ops(), (
    f"Use a Toffoli (qc.ccx) for the AND; ops are {dict(qc.count_ops())}"
)

_counts = StatevectorSampler(seed=11).run([qc], shots=400).result()[0].data.res.get_counts()
assert _counts == {"1": 400}, (
    f"1 AND 1 = 1, so every shot must read '1'; got {_counts}. "
    "Did you X both input qubits before the Toffoli?"
)
print(f"AND(1,1) measured as {_counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

a = QuantumRegister(2, "a")
b = QuantumRegister(1, "b")
res = ClassicalRegister(1, "res")
qc = QuantumCircuit(a, b, res)

qc.x(a[0])
qc.x(a[1])
qc.ccx(a[0], a[1], b[0])
qc.measure(b[0], res[0])
""",
    hints=[
        "QuantumCircuit(a, b, res) concatenates the registers: a[0]=0, a[1]=1, b[0]=2.",
        "qc.ccx(control1, control2, target) is the Toffoli; you can pass Qubit objects "
        "straight from the registers instead of integers.",
        "qc.find_bit(bit).index tells you the global index of any bit.",
    ],
)
