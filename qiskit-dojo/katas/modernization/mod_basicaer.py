"""Kata: mod_basicaer"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod_basicaer",
    section="Modernization",
    title="Modernize: BasicAer",
    difficulty="intermediate",
    prompt="""\
MODERNIZATION KATA — `BasicAer` (the old pure-Python provider) was
removed. Its successor is the `BasicSimulator` class in
`qiskit.providers.basic_provider` — still pure Python, still in Qiskit
itself, no qiskit-aer needed.

Rewrite the starter keeping the contract:
- `backend` — a BasicSimulator instance (NOT AerSimulator — the point
  here is knowing where BasicAer went)
- `counts` — Bell counts for shots=256
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x) — modernize me!
from qiskit import QuantumCircuit, transpile, BasicAer

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

backend = BasicAer.get_backend("qasm_simulator")
tqc = transpile(qc, backend)
counts = backend.run(tqc, shots=256).result().get_counts()
""",
    test_code="""\
import qiskit
assert not hasattr(qiskit, "BasicAer"), "sanity: qiskit.BasicAer must not exist in 2.x"

from qiskit.providers.basic_provider import BasicSimulator
assert isinstance(backend, BasicSimulator), (
    f"backend must be qiskit.providers.basic_provider.BasicSimulator, "
    f"got {type(backend).__name__}"
)
assert sum(counts.values()) == 256, f"Expected 256 shots, got {sum(counts.values())}"
assert set(counts) <= {"00", "11"}, f"Bell counts only, got {sorted(counts)}"
print(f"Modernized: counts = {counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit.providers.basic_provider import BasicSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

backend = BasicSimulator()
tqc = transpile(qc, backend)
counts = backend.run(tqc, shots=256).result().get_counts()
""",
    hints=[
        "BasicAer's replacement stayed inside Qiskit: qiskit.providers.basic_provider.",
        "BasicSimulator() replaces BasicAer.get_backend(\"qasm_simulator\").",
    ],
)
