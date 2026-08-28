"""Kata: mod_cx_cancellation"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod_cx_cancellation",
    section="Modernization",
    title="Modernize: CXCancellation pass",
    difficulty="advanced",
    prompt="""\
MODERNIZATION KATA — the `CXCancellation` transpiler pass was removed;
its job is now done by the more general `InverseCancellation` pass,
which cancels back-to-back pairs of any self-inverse gates you give it.

Rewrite the starter keeping the contract:
- `qc` — the wasteful circuit (cx, cx, x) from the starter
- `new_qc` — `qc` after a cancellation pass: ZERO cx gates remain,
  and the circuit is still equivalent to the original

Build InverseCancellation with [CXGate()] (from qiskit.circuit.library)
and remember a transpiler pass is directly callable on a circuit.
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x) — modernize me!
from qiskit import QuantumCircuit
from qiskit.transpiler.passes import CXCancellation

qc = QuantumCircuit(2)
qc.cx(0, 1)
qc.cx(0, 1)     # cancels the first cx
qc.x(0)

cancellation_pass = CXCancellation()
new_qc = cancellation_pass(qc)
""",
    test_code="""\
from qiskit.quantum_info import Operator

try:
    from qiskit.transpiler.passes import CXCancellation  # noqa: F401
    raise AssertionError("sanity: CXCancellation must not be importable in 2.x")
except ImportError:
    pass

assert new_qc.count_ops().get("cx", 0) == 0, (
    f"The back-to-back cx pair must cancel, {new_qc.count_ops().get('cx', 0)} left"
)
assert new_qc.count_ops().get("x", 0) == 1, "The x gate must survive"
assert Operator(new_qc).equiv(Operator(qc)), "new_qc must stay equivalent to qc"
print(f"Modernized: ops after cancellation = {dict(new_qc.count_ops())}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.circuit.library import CXGate
from qiskit.transpiler.passes import InverseCancellation

qc = QuantumCircuit(2)
qc.cx(0, 1)
qc.cx(0, 1)
qc.x(0)

cancellation_pass = InverseCancellation([CXGate()])
new_qc = cancellation_pass(qc)
""",
    hints=[
        "The successor pass is InverseCancellation, parameterized by the gates to cancel.",
        "InverseCancellation([CXGate()]) — CXGate comes from qiskit.circuit.library.",
        "Passes are callable: new_qc = cancellation_pass(qc). (A PassManager works too.)",
    ],
)
