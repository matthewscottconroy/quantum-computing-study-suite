"""Kata: mod_execute"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod_execute",
    section="Modernization",
    title="Modernize: qiskit.execute",
    difficulty="intermediate",
    prompt="""\
MODERNIZATION KATA — the starter is pre-1.0 Qiskit and no longer runs
(`qiskit.execute` was removed). Run it, watch it fail, then rewrite it
for Qiskit 2.x while keeping the variable contract:

- `backend` — an AerSimulator
- `counts` — Bell-measurement counts for shots=1024

Modern replacement for execute(qc, backend, shots): transpile the
circuit for the backend, then call backend.run(tqc, shots=...) yourself.
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x) — modernize me!
from qiskit import QuantumCircuit, execute
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

backend = AerSimulator()
job = execute(qc, backend, shots=1024)
counts = job.result().get_counts()
""",
    test_code="""\
import sys
assert "qiskit" in sys.modules, "Keep this a Qiskit program"
_q = sys.modules["qiskit"]
assert not hasattr(_q, "execute"), "sanity: qiskit.execute must not exist in 2.x"

from qiskit_aer import AerSimulator
assert isinstance(backend, AerSimulator), "backend must stay an AerSimulator"
assert sum(counts.values()) == 1024, (
    f"Expected 1024 shots, got {sum(counts.values())}"
)
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
job = backend.run(tqc, shots=1024)
counts = job.result().get_counts()
""",
    hints=[
        "execute() bundled transpile + run; in 2.x you do the two steps explicitly.",
        "tqc = transpile(qc, backend); job = backend.run(tqc, shots=1024).",
        "For new code the primitives (SamplerV2) are preferred, but backend.run is the direct port.",
    ],
)
