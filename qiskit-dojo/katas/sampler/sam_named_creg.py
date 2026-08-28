"""Kata: sam_named_creg"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="sam_named_creg",
    section="Sampler",
    title="Named registers in SamplerV2 results",
    difficulty="intermediate",
    prompt="""\
SamplerV2 results expose one BitArray PER classical register, as an
attribute of `result[i].data` named after the register. This kata makes
you use that access path deliberately.

Build:
1. `qc` — Bell circuit whose classical bits live in a
   ClassicalRegister of size 2 named "ans", measured explicitly
   (do NOT use measure_all — that would create a register named "meas")
2. run it on a StatevectorSampler with shots=1000
3. `bits` — the BitArray for the "ans" register (result[0].data.ans)
4. `counts` — bits.get_counts()
5. `nbits` — bits.num_bits
""",
    starter_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.primitives import StatevectorSampler

# TODO: registers (creg named "ans"), Bell + measure, sample,
#       then bits, counts, nbits from result[0].data.ans
""",
    test_code="""\
creg_names = [r.name for r in qc.cregs]
assert creg_names == ["ans"], (
    f"Circuit must have exactly one classical register named 'ans', got {creg_names}"
)
assert nbits == 2, f"bits.num_bits should be 2, got {nbits}"
assert bits.num_shots == 1000, f"Expected 1000 shots, got {bits.num_shots}"
assert sum(counts.values()) == 1000, "counts must total 1000 shots"
assert set(counts) <= {"00", "11"}, (
    f"Bell outcomes are only 00 and 11, got {sorted(counts)}"
)
print(f"counts from data.ans = {counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.primitives import StatevectorSampler

q = QuantumRegister(2, "q")
ans = ClassicalRegister(2, "ans")
qc = QuantumCircuit(q, ans)
qc.h(0)
qc.cx(0, 1)
qc.measure(q, ans)

sampler = StatevectorSampler()
result = sampler.run([qc], shots=1000).result()
bits = result[0].data.ans
counts = bits.get_counts()
nbits = bits.num_bits
""",
    hints=[
        "ClassicalRegister(2, \"ans\") then QuantumCircuit(qreg, creg).",
        "The DataBin attribute matches the register name exactly: result[0].data.ans.",
        "BitArray carries metadata too: num_bits, num_shots, get_bitstrings(), ...",
    ],
)
