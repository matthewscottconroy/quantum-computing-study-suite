"""Kata: rc_transpile_opt"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc_transpile_opt",
    section="Run circuits",
    title="Optimization levels in transpile",
    difficulty="intermediate",
    prompt="""\
The transpiler doesn't just translate gates — at higher optimization
levels it cancels redundancy.

The starter builds a wasteful circuit: H·H and CX·CX pairs that are
pure identity, plus one real X gate. Your job:

1. `opt_qc` — transpile `qc` with optimization_level=3 and
   basis_gates=["rz", "sx", "x", "cx"]
2. `n_cx` — the number of cx gates left in `opt_qc`
   (count_ops().get("cx", 0))

Done right, every redundant pair cancels: zero CX gates remain and the
circuit is still equivalent to the original.
""",
    starter_code="""\
from qiskit import QuantumCircuit, transpile

qc = QuantumCircuit(2)
qc.h(0)
qc.h(0)        # cancels the first h
qc.cx(0, 1)
qc.cx(0, 1)    # cancels the first cx
qc.x(1)

# TODO: opt_qc = transpile(...), n_cx = ...
""",
    test_code="""\
from qiskit.quantum_info import Operator

_used = set(opt_qc.count_ops()) - {"barrier"}
assert _used <= {"rz", "sx", "x", "cx"}, (
    f"opt_qc must only use the requested basis gates, got {sorted(_used)}"
)
assert n_cx == 0, (
    f"optimization_level=3 cancels the back-to-back CX pair; n_cx is {n_cx}. "
    "Did you pass optimization_level=3?"
)
assert Operator(opt_qc).equiv(Operator(qc)), (
    "opt_qc must stay unitarily equivalent to the original circuit"
)
print(f"Optimized ops: {dict(opt_qc.count_ops())}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, transpile

qc = QuantumCircuit(2)
qc.h(0)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 1)
qc.x(1)

opt_qc = transpile(qc, optimization_level=3, basis_gates=["rz", "sx", "x", "cx"])
n_cx = opt_qc.count_ops().get("cx", 0)
""",
    hints=[
        "transpile accepts basis_gates and optimization_level directly — no backend needed.",
        "count_ops() returns a dict of gate name -> count; .get(\"cx\", 0) is safe when absent.",
        "Levels 0/1 mostly translate; levels 2/3 add resynthesis and cancellation.",
    ],
)
