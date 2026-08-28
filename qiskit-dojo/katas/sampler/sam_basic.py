"""Kata: sam_basic"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="sam_basic",
    section="Sampler",
    title="SamplerV2 basics: PUBs and BitArray",
    difficulty="beginner",
    prompt="""\
The V2 Sampler takes a list of PUBs (Primitive Unified Blocs) and returns
one result per PUB. Counts live on the result's DataBin, keyed by the
classical register name — measure_all() creates a register called "meas".

Build:
1. `qc` — Bell circuit with measure_all()
2. `sampler` — a StatevectorSampler
3. run [qc] with shots=2048
4. `counts` — result[0].data.meas.get_counts()

Expected: 2048 total shots, only '00'/'11' outcomes.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# TODO: build qc, create sampler, run with shots=2048, extract counts
""",
    test_code="""\
from qiskit.primitives import StatevectorSampler

assert isinstance(sampler, StatevectorSampler), "sampler must be a StatevectorSampler"
assert isinstance(counts, dict), "counts must come from .get_counts() on the BitArray"
assert sum(counts.values()) == 2048, (
    f"Expected 2048 shots total, got {sum(counts.values())}"
)
assert set(counts) <= {"00", "11"}, (
    f"Bell measurement gives only 00 and 11, got {sorted(counts)}"
)
assert len(counts) == 2, "Both 00 and 11 should appear at 2048 shots"
print(f"counts = {counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

sampler = StatevectorSampler()
job = sampler.run([qc], shots=2048)
result = job.result()
counts = result[0].data.meas.get_counts()
""",
    hints=[
        "sampler.run takes a LIST of pubs — a bare circuit is the simplest pub: run([qc], shots=2048).",
        "result[0] is the first pub's result; its .data has one attribute per classical register.",
        "measure_all() names its register 'meas', hence result[0].data.meas.get_counts().",
    ],
)
