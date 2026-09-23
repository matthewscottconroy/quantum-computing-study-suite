"""Kata: qo2_global_phase"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo2_global_phase",
    section="Quantum operations",
    title="Operator equality vs equivalence up to global phase",
    difficulty="intermediate",
    prompt="""\
`rz(pi)` and the `Z` gate do the same physics, but they are NOT the same
matrix: rz(theta) = diag(e^{-i theta/2}, e^{+i theta/2}), so

    rz(pi) = -i * Z

Operator `==` compares matrices entry by entry and says "different".
`Operator.equiv` ignores a global phase and says "same".

Build:
1. `rz_circ` — 1-qubit circuit with rz(pi) on qubit 0
2. `z_circ`  — 1-qubit circuit with z on qubit 0
3. `exact_equal` — bool: Operator(rz_circ) == Operator(z_circ)   (False)
4. `up_to_phase` — bool: Operator(rz_circ).equiv(Operator(z_circ)) (True)
5. `fixed` — a copy of `rz_circ` with a global_phase added so that it is
   now EXACTLY equal to `z_circ`
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

# TODO: rz_circ, z_circ, exact_equal, up_to_phase, fixed
""",
    test_code="""\
import numpy as np
from qiskit.quantum_info import Operator

assert [i.operation.name for i in rz_circ.data] == ["rz"], "rz_circ must be a single rz gate"
assert [i.operation.name for i in z_circ.data] == ["z"], "z_circ must be a single z gate"

assert exact_equal is False, (
    "Operator(rz_circ) == Operator(z_circ) is False — rz(pi) carries a -i global phase, "
    f"got exact_equal={exact_equal!r}"
)
assert up_to_phase is True, (
    "Operator.equiv ignores global phase, so this one is True, "
    f"got up_to_phase={up_to_phase!r}"
)

assert Operator(fixed) == Operator(z_circ), (
    "fixed must be EXACTLY equal to z_circ. rz(pi) = -i*Z, so adding a global phase of "
    f"+pi/2 cancels the -i. Got matrix {np.round(Operator(fixed).data, 3)}"
)
assert [i.operation.name for i in fixed.data] == ["rz"], (
    "fixed should still be the rz circuit, just with global_phase set — not a rebuilt z gate"
)
print(f"rz(pi) matrix = {np.round(Operator(rz_circ).data, 3).tolist()}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

rz_circ = QuantumCircuit(1)
rz_circ.rz(np.pi, 0)

z_circ = QuantumCircuit(1)
z_circ.z(0)

exact_equal = Operator(rz_circ) == Operator(z_circ)
up_to_phase = Operator(rz_circ).equiv(Operator(z_circ))

fixed = rz_circ.copy()
fixed.global_phase += np.pi / 2
""",
    hints=[
        "Operator(circ) builds the unitary; == is exact, .equiv() quotients out a global phase.",
        "QuantumCircuit has a `global_phase` attribute in radians — set or increment it.",
        "rz(pi) = -i*Z = e^{-i pi/2} * Z, so you need to add +pi/2 to the global phase.",
    ],
)
