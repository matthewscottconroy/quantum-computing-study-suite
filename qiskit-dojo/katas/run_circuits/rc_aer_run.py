"""Kata: rc_aer_run"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc_aer_run",
    section="Run circuits",
    title="Run on AerSimulator",
    difficulty="beginner",
    prompt="""\
Run a circuit end-to-end on the local Aer simulator.

Build:
1. `qc` — 2-qubit Bell circuit WITH measure_all()
2. `backend` — an AerSimulator instance (import from qiskit_aer)
3. transpile `qc` for the backend
4. run the transpiled circuit with shots=1024 and store the counts dict
   in `counts` (job.result().get_counts())

Expected: counts sums to 1024 with only '00' and '11' outcomes.
""",
    starter_code="""\
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# TODO: build qc, create backend, transpile, run with shots=1024, get counts
""",
    test_code="""\
from qiskit_aer import AerSimulator

assert isinstance(backend, AerSimulator), "backend must be an AerSimulator instance"
assert isinstance(counts, dict), "counts must be the dict from result.get_counts()"
assert sum(counts.values()) == 1024, (
    f"Total shots must be 1024, got {sum(counts.values())} — pass shots=1024 to run()"
)
assert set(counts) <= {"00", "11"}, (
    f"A Bell measurement gives only 00 and 11, got {sorted(counts)}"
)
assert len(counts) == 2, f"Expected both 00 and 11 to appear, got {sorted(counts)}"
print(f"counts = {counts}")
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
        "In Qiskit 2.x there is no qiskit.execute — the pattern is transpile(qc, backend) then backend.run.",
        "measure_all() adds a barrier plus one measurement per qubit into a fresh 'meas' register.",
        "backend.run(tqc, shots=1024).result().get_counts() chains straight through.",
    ],
)
