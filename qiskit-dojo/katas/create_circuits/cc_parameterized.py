"""Kata: cc_parameterized"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc_parameterized",
    section="Create circuits",
    title="Parameterized circuit + assign_parameters",
    difficulty="intermediate",
    prompt="""\
Parameterized circuits are the backbone of variational algorithms and of
the primitives' parameter sweeps.

Build:
1. `theta` — a qiskit.circuit.Parameter named "theta"
2. `qc` — a 1-qubit QuantumCircuit applying ry(theta) to qubit 0
3. `bound` — a NEW circuit obtained by assigning theta = pi/2
   (use `assign_parameters`; the original `qc` must stay parameterized)

After binding theta = pi/2, the state should be |+> = (|0>+|1>)/sqrt(2).
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

# TODO: define theta, build qc with ry(theta, 0), then bind pi/2 into `bound`.
""",
    test_code="""\
from qiskit.quantum_info import Statevector

assert qc.num_parameters == 1, (
    f"qc must keep exactly one free parameter, has {qc.num_parameters}"
)
assert next(iter(qc.parameters)).name == "theta", "The Parameter must be named 'theta'"
assert bound.num_parameters == 0, (
    "`bound` must have no free parameters — did you call assign_parameters?"
)
_sv = Statevector.from_instruction(bound)
assert _sv.equiv(Statevector.from_label("+")), (
    f"ry(pi/2)|0> should be |+>, got {_sv.data.round(3)}"
)
print("Parameter bound correctly: state is |+>.")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

theta = Parameter("theta")
qc = QuantumCircuit(1)
qc.ry(theta, 0)

bound = qc.assign_parameters({theta: np.pi / 2})
""",
    hints=[
        "Parameter(\"theta\") creates a symbolic parameter you can pass to any rotation gate.",
        "assign_parameters returns a new circuit — it does not modify qc in place.",
        "qc.assign_parameters({theta: np.pi / 2}) — a dict maps parameter to value.",
    ],
)
