"""Kata: est_hamiltonian_energy"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="est_hamiltonian_energy",
    section="Estimator",
    title="Energy of a state under a summed Hamiltonian",
    difficulty="intermediate",
    prompt="""\
A SparsePauliOp with several terms is ONE observable — the estimator
returns the full weighted sum in a single expectation value. That is how
VQE energies are evaluated.

Build:
1. `H` — SparsePauliOp for  -1.0 * ZZ  - 1.0 * XX   (use from_list)
2. `qc` — Bell circuit (no measurements)
3. run the pub (qc, H) on a StatevectorEstimator
4. `energy` — the resulting expectation value as a plain float

For the Bell state <ZZ> = <XX> = 1, so energy = -2.0 exactly.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

# TODO: H = ..., qc = ..., run, energy = float(...)
""",
    test_code="""\
from qiskit.quantum_info import SparsePauliOp

assert isinstance(H, SparsePauliOp), "H must be a SparsePauliOp"
assert len(H.paulis) == 2, (
    f"H must have exactly the two terms ZZ and XX, has {len(H.paulis)}"
)
assert isinstance(energy, float), (
    f"energy must be a plain float, got {type(energy).__name__} — wrap with float(...)"
)
assert abs(energy - (-2.0)) < 1e-9, (
    f"Expected energy -2.0 for the Bell state under -ZZ - XX, got {energy}"
)
print(f"energy = {energy}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

H = SparsePauliOp.from_list([("ZZ", -1.0), ("XX", -1.0)])

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

estimator = StatevectorEstimator()
result = estimator.run([(qc, H)]).result()
energy = float(result[0].data.evs)
""",
    hints=[
        "SparsePauliOp.from_list([(\"ZZ\", -1.0), (\"XX\", -1.0)]) builds the sum in one shot.",
        "One multi-term observable -> one number: no need to estimate terms separately.",
        "result[0].data.evs is a 0-d numpy array here; float(...) unwraps it.",
    ],
)
