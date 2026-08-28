"""Kata: qo_statevector_evolve"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo_statevector_evolve",
    section="Quantum operations",
    title="Statevector evolution and probabilities",
    difficulty="intermediate",
    prompt="""\
Use `qiskit.quantum_info.Statevector` to simulate exactly, without any
sampler or backend.

Build:
1. `initial` — Statevector for |00> (try Statevector.from_label)
2. `qc` — a 2-qubit Bell circuit (H then CX, no measurements)
3. `final` — the result of evolving `initial` by `qc` (Statevector.evolve)
4. `probs` — final.probabilities_dict()

Expected: probs == {'00': 0.5, '11': 0.5}.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# TODO: initial = ..., qc = ..., final = ..., probs = ...
""",
    test_code="""\
import numpy as np
from qiskit.quantum_info import Statevector

assert isinstance(initial, Statevector), "initial must be a Statevector"
assert np.allclose(initial.data, [1, 0, 0, 0]), "initial must be |00>"
assert isinstance(final, Statevector), "final must be a Statevector (use initial.evolve(qc))"
assert set(probs) == {"00", "11"}, (
    f"probabilities_dict should have keys 00 and 11 only, got {sorted(probs)}"
)
assert abs(probs["00"] - 0.5) < 1e-9 and abs(probs["11"] - 0.5) < 1e-9, (
    f"Both outcomes should have probability 0.5, got {probs}"
)
print(f"probs = {probs}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

initial = Statevector.from_label("00")

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

final = initial.evolve(qc)
probs = final.probabilities_dict()
""",
    hints=[
        "Statevector.from_label(\"00\") builds the computational-basis state directly.",
        "initial.evolve(qc) returns the new Statevector — it does not mutate initial.",
        "probabilities_dict() drops (near-)zero entries automatically.",
    ],
)
