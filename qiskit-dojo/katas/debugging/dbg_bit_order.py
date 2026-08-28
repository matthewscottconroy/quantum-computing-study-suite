"""Kata: dbg_bit_order"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg_bit_order",
    section="Debugging",
    title="Fix it: wrong bit order",
    difficulty="intermediate",
    prompt="""\
DEBUGGING KATA — the starter code RUNS but computes the wrong answer.
Find the bug and fix it (run it as-is first and read the failure).

The circuit applies X to qubit 0 only, so qubit 0 must measure 1 with
probability 1.0. The code samples the circuit and computes `p1_q0`, the
probability that qubit 0 measured 1 — but it reads the counts keys at
the wrong end.

Remember: counts bitstrings are little-endian — qubit 0 is the
RIGHTMOST character.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(2)
qc.x(0)              # flip qubit 0 -> it must always measure 1
qc.measure_all()

result = StatevectorSampler().run([qc], shots=1000).result()
counts = result[0].data.meas.get_counts()

# probability that qubit 0 measured 1
p1_q0 = sum(n for bits, n in counts.items() if bits[0] == "1") / 1000
""",
    test_code="""\
assert set(counts) == {"01"}, (
    f"Sanity: X on qubit 0 of |00> gives the key '01' (qubit 0 rightmost), got {sorted(counts)}"
)
assert abs(p1_q0 - 1.0) < 1e-9, (
    f"p1_q0 must be 1.0 — qubit 0 always reads 1 here — but got {p1_q0}. "
    "bits[0] is the HIGHEST qubit; qubit 0 is bits[-1]."
)
print(f"p1_q0 = {p1_q0} — bit order handled correctly.")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(2)
qc.x(0)
qc.measure_all()

result = StatevectorSampler().run([qc], shots=1000).result()
counts = result[0].data.meas.get_counts()

# qubit 0 is the RIGHTMOST character of each counts key
p1_q0 = sum(n for bits, n in counts.items() if bits[-1] == "1") / 1000
""",
    hints=[
        "Print the counts — you'll see the key '01', not '10'. Which qubit is which character?",
        "Qiskit bitstrings read qubit (n-1) ... qubit 0 from left to right.",
        "Change bits[0] to bits[-1].",
    ],
)
