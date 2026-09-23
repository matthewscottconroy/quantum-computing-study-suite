"""Kata: cc2_dynamic_if"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc2_dynamic_if",
    section="Create circuits",
    title="Dynamic circuit with if_test",
    difficulty="advanced",
    prompt="""\
Dynamic circuits branch on a mid-circuit measurement. In Qiskit 2.x the
construction is the `if_test` context manager — the old
`instruction.c_if(...)` was removed.

Build `qc` with, IN THIS ORDER:
- QuantumRegister(2, "q"), ClassicalRegister(1, "flag"), ClassicalRegister(1, "out")
- h on q[0]
- measure q[0] into flag[0]
- `with qc.if_test((flag, 1)):` apply x to q[1]
- measure q[1] into out[0]

The result: the two classical bits always agree, 50/50 across shots —
a measurement-conditioned copy. Note StatevectorSampler cannot execute
control flow; the tests use AerSimulator.
""",
    starter_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# TODO: registers q/flag/out, h + mid-circuit measure, if_test branch, final measure
""",
    test_code="""\
from qiskit import transpile
from qiskit_aer import AerSimulator

_qregs = [r.name for r in qc.qregs]
_cregs = [r.name for r in qc.cregs]
assert _qregs == ["q"], f"Expected one QuantumRegister named 'q', got {_qregs}"
assert _cregs == ["flag", "out"], (
    f"Expected classical registers 'flag' then 'out', got {_cregs}"
)
assert "if_else" in qc.count_ops(), (
    f"qc must contain a control-flow branch built with `with qc.if_test(...)`. "
    f"Ops found: {dict(qc.count_ops())}"
)
assert qc.count_ops().get("measure", 0) == 2, "Measure q[0] into flag and q[1] into out"

_sim = AerSimulator()
_counts = _sim.run(transpile(qc, _sim), shots=800, seed_simulator=7).result().get_counts()
for _key, _n in _counts.items():
    _bits = _key.replace(" ", "")
    assert _bits[0] == _bits[1], (
        f"Outcome {_key!r} has disagreeing bits — q[1] must be flipped exactly when "
        "flag == 1, so both classical bits always match."
    )
assert len(_counts) == 2, (
    f"At 800 shots both 0/0 and 1/1 should appear, got {sorted(_counts)}"
)
print(f"Dynamic circuit counts: {_counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

q = QuantumRegister(2, "q")
flag = ClassicalRegister(1, "flag")
out = ClassicalRegister(1, "out")
qc = QuantumCircuit(q, flag, out)

qc.h(q[0])
qc.measure(q[0], flag[0])
with qc.if_test((flag, 1)):
    qc.x(q[1])
qc.measure(q[1], out[0])
""",
    hints=[
        "QuantumCircuit(q, flag, out) — register order matters for how results are labelled.",
        "`with qc.if_test((flag, 1)):` opens the branch; gates applied inside the block are "
        "the body. The condition can be (register, int) or (clbit, bool).",
        "c_if was removed in Qiskit 2.0 — if_test is the only supported form.",
    ],
)
