"""Kata: dbg_wrong_basis"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg_wrong_basis",
    section="Debugging",
    title="Fix it: measuring <X> in the wrong basis",
    difficulty="advanced",
    prompt="""\
DEBUGGING KATA — the starter runs but the physics is wrong.

Goal: estimate <X> for the state |+> = H|0> from measurement counts.
The true value is exactly 1 (|+> is the +1 eigenstate of X).

But qubit measurements are Z-basis measurements. Measuring |+> directly
gives 50/50 outcomes and the code estimates <X> ~ 0 — the classic
"forgot the basis change" bug.

Fix: rotate the measurement basis with an H gate BEFORE the measure, so
counts of 0/1 become the +1/-1 eigenvalues of X. Keep the estimate in
`exp_x` computed from the counts.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(1, 1)
qc.h(0)                  # prepare |+>
qc.measure(0, 0)         # measures Z... but we want <X>

result = StatevectorSampler().run([qc], shots=4000).result()
counts = result[0].data.c.get_counts()

shots = sum(counts.values())
exp_x = (counts.get("0", 0) - counts.get("1", 0)) / shots
""",
    test_code="""\
assert abs(exp_x - 1.0) < 0.05, (
    f"<X> of |+> is 1.0 but you estimated {exp_x:.3f}. "
    "A bare measure is a Z measurement — apply H right before measuring "
    "to rotate the X basis onto Z."
)
print(f"exp_x = {exp_x}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(1, 1)
qc.h(0)                  # prepare |+>
qc.h(0)                  # basis change: X eigenbasis -> Z eigenbasis
qc.measure(0, 0)

result = StatevectorSampler().run([qc], shots=4000).result()
counts = result[0].data.c.get_counts()

shots = sum(counts.values())
exp_x = (counts.get("0", 0) - counts.get("1", 0)) / shots
""",
    hints=[
        "Run it: exp_x hovers near 0, not 1. The state is fine — the measurement basis isn't.",
        "To measure X, apply H just before the Z measurement (for Y it would be Sdg then H).",
        "Here H·H = I, so the circuit becomes measure |0> and every shot reads 0 -> exp_x = 1.",
    ],
)
