"""Kata: qo2_partial_trace"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo2_partial_trace",
    section="Quantum operations",
    title="partial_trace, purity and fidelity",
    difficulty="intermediate",
    prompt="""\
Tracing out a qubit of a maximally entangled pair leaves the other qubit
maximally MIXED — the signature of entanglement.

Starting from the Bell state of the given circuit `bell`:
1. `sv` — the Statevector of `bell`
2. `rho0` — the reduced DensityMatrix of qubit 0 (trace out qubit 1)
3. `purity0` — the real part of rho0.purity()   (0.5 for a mixed qubit)
4. `fid` — state_fidelity(rho0, maximally mixed 1-qubit DensityMatrix)

Use `qiskit.quantum_info.partial_trace` and `state_fidelity`.
Remember partial_trace's second argument is the list of qubits to REMOVE.
""",
    starter_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import (Statevector, DensityMatrix,
                                 partial_trace, state_fidelity)

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)

# TODO: sv, rho0, purity0, fid
""",
    test_code="""\
import numpy as np
from qiskit.quantum_info import Statevector, DensityMatrix

assert isinstance(sv, Statevector), "sv must be a Statevector of the bell circuit"
assert isinstance(rho0, DensityMatrix), (
    "partial_trace returns a DensityMatrix — rho0 must be that reduced state"
)
assert rho0.dim == 2, (
    f"rho0 must be a single-qubit state (dim 2), got dim {rho0.dim} — "
    "partial_trace(sv, [1]) removes qubit 1 and KEEPS qubit 0"
)
assert np.allclose(rho0.data, np.eye(2) / 2), (
    f"Half of a Bell pair is the maximally mixed state I/2, got {np.round(rho0.data, 3)}"
)
assert abs(purity0 - 0.5) < 1e-9, (
    f"purity of I/2 is 0.5, got {purity0} (take .real — purity() returns a complex)"
)
assert abs(fid - 1.0) < 1e-9, (
    f"rho0 IS the maximally mixed state, so the fidelity is 1.0, got {fid}"
)
print(f"rho0 = {np.round(rho0.data, 3).tolist()}, purity = {purity0:.3f}, fidelity = {fid:.3f}")
""",
    solution_code="""\
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import (Statevector, DensityMatrix,
                                 partial_trace, state_fidelity)

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)

sv = Statevector.from_instruction(bell)
rho0 = partial_trace(sv, [1])
purity0 = rho0.purity().real
fid = state_fidelity(rho0, DensityMatrix(np.eye(2) / 2))
""",
    hints=[
        "Statevector.from_instruction(bell) evolves |00> through the circuit.",
        "partial_trace(state, qargs) traces OUT the listed qubits — pass [1] to keep qubit 0.",
        "DensityMatrix(np.eye(2) / 2) is the maximally mixed qubit; state_fidelity takes "
        "two states of the same dimension.",
    ],
)
