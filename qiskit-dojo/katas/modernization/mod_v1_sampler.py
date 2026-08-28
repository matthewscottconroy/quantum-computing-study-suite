"""Kata: mod_v1_sampler"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="mod_v1_sampler",
    section="Modernization",
    title="Modernize: V1 Sampler and quasi_dists",
    difficulty="intermediate",
    prompt="""\
MODERNIZATION KATA — the V1 primitives were removed in Qiskit 2.0:
`from qiskit.primitives import Sampler` no longer imports, and the
`quasi_dists` result format is gone with it.

Rewrite for the V2 world:
- use StatevectorSampler
- run [qc] with shots=1000
- V2 returns raw samples per register, so the contract becomes:
  `counts` — result[0].data.meas.get_counts()

(quasi-probability dicts -> BitArray counts is THE V1->V2 mindset shift:
V2 gives you shots, you derive statistics.)
""",
    starter_code="""\
# LEGACY CODE (Qiskit 0.x/1.x) — modernize me!
from qiskit import QuantumCircuit
from qiskit.primitives import Sampler

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

sampler = Sampler()
job = sampler.run(qc, shots=1000)
quasi_dist = job.result().quasi_dists[0]
counts = {format(k, "02b"): int(v * 1000) for k, v in quasi_dist.items()}
""",
    test_code="""\
from qiskit.primitives import StatevectorSampler

try:
    from qiskit.primitives import Sampler  # noqa: F401
    raise AssertionError("sanity: the V1 Sampler must not be importable in 2.x")
except ImportError:
    pass

assert isinstance(sampler, StatevectorSampler), (
    f"sampler must be a StatevectorSampler, got {type(sampler).__name__}"
)
assert sum(counts.values()) == 1000, f"Expected 1000 shots, got {sum(counts.values())}"
assert set(counts) <= {"00", "11"}, f"Bell counts only, got {sorted(counts)}"
assert len(counts) == 2, "Both outcomes should appear at 1000 shots"
print(f"Modernized: counts = {counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

sampler = StatevectorSampler()
job = sampler.run([qc], shots=1000)
counts = job.result()[0].data.meas.get_counts()
""",
    hints=[
        "The V2 reference sampler is StatevectorSampler; run() takes a LIST of pubs.",
        "No quasi_dists in V2 — counts come from result[0].data.<register>.get_counts().",
        "measure_all() names the register 'meas'.",
    ],
)
