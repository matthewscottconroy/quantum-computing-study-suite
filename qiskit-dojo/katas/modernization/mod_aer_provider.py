"""Kata: mod_aer_provider"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod_aer_provider",
    section="Modernization",
    title="Modernize: from qiskit import Aer",
    difficulty="beginner",
    prompt="""\
MODERNIZATION KATA — `from qiskit import Aer` died when Aer moved to its
own package. In Qiskit 2.x the simulator comes from `qiskit_aer`
directly — no provider lookup, just instantiate the class.

Rewrite the starter keeping the contract:
- `backend` — the Aer simulator instance
- `counts` — Bell counts for shots=512
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x) — modernize me!
from qiskit import QuantumCircuit, transpile, Aer

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

backend = Aer.get_backend("aer_simulator")
tqc = transpile(qc, backend)
counts = backend.run(tqc, shots=512).result().get_counts()
""",
    test_code="""\
import qiskit
assert not hasattr(qiskit, "Aer"), "sanity: qiskit.Aer must not exist in 2.x"

from qiskit_aer import AerSimulator
assert isinstance(backend, AerSimulator), (
    f"backend must be a qiskit_aer.AerSimulator, got {type(backend).__name__}"
)
assert sum(counts.values()) == 512, f"Expected 512 shots, got {sum(counts.values())}"
assert set(counts) <= {"00", "11"}, f"Bell counts only, got {sorted(counts)}"
print(f"Modernized: counts = {counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

backend = AerSimulator()
tqc = transpile(qc, backend)
counts = backend.run(tqc, shots=512).result().get_counts()
""",
    hints=[
        "Aer lives in the qiskit-aer package now: from qiskit_aer import AerSimulator.",
        "No get_backend string lookup — AerSimulator() is the backend.",
    ],
)
