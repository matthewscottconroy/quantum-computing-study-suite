"""Kata: cc2_ansatz_sweep"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc2_ansatz_sweep",
    section="Create circuits",
    title="ParameterVector ansatz and a bound sweep",
    difficulty="intermediate",
    prompt="""\
Variational workflows build ONE parameterized ansatz and then bind many
value sets into it. `ParameterVector` gives you an indexable block of
parameters in a single object.

Build:
1. `theta` — a ParameterVector named "theta" of length 2
2. `ansatz` — a 2-qubit circuit (no measurements) applying
   ry(theta[0], 0), ry(theta[1], 1), then cx(0, 1)
3. `sweep` — a list of 4 circuits, one per row of the given `values`,
   each produced with `assign_parameters`

`ansatz` itself must stay parameterized — assign_parameters returns a new
circuit.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

values = [[0.0, 0.0], [np.pi, 0.0], [0.0, np.pi], [np.pi, np.pi]]

# TODO: theta = ..., ansatz = ..., sweep = ...
""",
    test_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector

assert isinstance(theta, ParameterVector), "theta must be a ParameterVector"
assert theta.name == "theta", f"The ParameterVector must be named 'theta', got {theta.name!r}"
assert len(theta) == 2, f"theta must hold 2 parameters, holds {len(theta)}"

assert ansatz.num_qubits == 2, "ansatz must be a 2-qubit circuit"
assert ansatz.num_parameters == 2, (
    f"ansatz must keep both free parameters, has {ansatz.num_parameters} — "
    "assign_parameters returns a NEW circuit, it does not bind in place"
)
_names = [i.operation.name for i in ansatz.data]
assert _names == ["ry", "ry", "cx"], f"ansatz must be ry, ry, cx — got {_names}"

assert isinstance(sweep, list) and len(sweep) == 4, (
    f"sweep must be a list of 4 bound circuits, got {type(sweep).__name__} "
    f"of length {len(sweep) if hasattr(sweep, '__len__') else '?'}"
)
# ry(pi) on q0 -> |1>, then cx(0,1) flips q1.  Labels are little-endian q1q0.
_values = [[0.0, 0.0], [np.pi, 0.0], [0.0, np.pi], [np.pi, np.pi]]
_expected = ["00", "11", "10", "01"]
for _i, (_circ, _want) in enumerate(zip(sweep, _expected)):
    assert _circ.num_parameters == 0, (
        f"sweep[{_i}] still has {_circ.num_parameters} free parameter(s) — bind every value"
    )
    _p = Statevector.from_instruction(_circ).probabilities_dict()
    _got = max(_p, key=_p.get)
    assert _got == _want and _p[_got] > 0.99, (
        f"sweep[{_i}] with values {_values[_i]} should land on |{_want}>, got {_p}. "
        "Keep the rows in the order given."
    )
print("All 4 sweep points bound and verified.")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

values = [[0.0, 0.0], [np.pi, 0.0], [0.0, np.pi], [np.pi, np.pi]]

theta = ParameterVector("theta", 2)

ansatz = QuantumCircuit(2)
ansatz.ry(theta[0], 0)
ansatz.ry(theta[1], 1)
ansatz.cx(0, 1)

sweep = [ansatz.assign_parameters(v) for v in values]
""",
    hints=[
        "ParameterVector(\"theta\", 2) then index it: theta[0], theta[1].",
        "assign_parameters accepts a plain sequence in the circuit's parameter order, "
        "so ansatz.assign_parameters([0.0, np.pi]) works.",
        "Build sweep with a list comprehension over values — never bind in place, or the "
        "second iteration has nothing left to bind.",
    ],
)
