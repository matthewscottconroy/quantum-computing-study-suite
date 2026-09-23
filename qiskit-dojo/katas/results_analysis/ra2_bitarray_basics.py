"""Kata: ra2_bitarray_basics"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="ra2_bitarray_basics",
    section="Results analysis",
    title="BitArray: per-shot samples, counts on demand",
    difficulty="intermediate",
    prompt="""\
SamplerV2 does not hand back a histogram — it hands back a BitArray, the
raw per-shot register readings. Counts are something you ASK it for. Know
its three headline members and the V2 result plumbing stops being
mysterious.

Build:
1. `qc`     — 3-qubit GHZ with measure_all()
2. `bits`   — the BitArray for the 'meas' register after a 512-shot
              StatevectorSampler run
3. `counts` — bits.get_counts()
4. `shots`  — bits.num_shots
5. `first`  — the bitstring of the very first shot
              (bits.get_bitstrings()[0])
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# TODO: qc, run 512 shots, bits, counts, shots, first
""",
    test_code="""\
from qiskit.primitives.containers import BitArray

assert isinstance(bits, BitArray), (
    f"bits must be the BitArray at result[0].data.meas, got {type(bits).__name__}"
)
assert shots == 512, f"num_shots should be 512, got {shots}"
assert bits.num_bits == 3, (
    f"measure_all() on 3 qubits gives a 3-bit register, num_bits is {bits.num_bits}"
)
assert sum(counts.values()) == 512, (
    f"The counts must account for all 512 shots, got {sum(counts.values())}"
)
assert set(counts) <= {"000", "111"}, (
    f"A noiseless GHZ only ever yields 000 or 111, got {sorted(counts)}"
)
assert len(counts) == 2, "Both GHZ outcomes should appear at 512 shots"
assert len(bits.get_bitstrings()) == 512, (
    "get_bitstrings() returns one string PER SHOT — 512 of them, not one per outcome"
)
assert first in {"000", "111"}, f"The first shot must be 000 or 111, got {first!r}"
print(f"{shots} shots, {bits.num_bits} bits, counts {counts}, first shot {first}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

result = StatevectorSampler().run([qc], shots=512).result()
bits = result[0].data.meas

counts = bits.get_counts()
shots = bits.num_shots
first = bits.get_bitstrings()[0]
""",
    hints=[
        "measure_all() creates a register called 'meas', so the BitArray is result[0].data.meas.",
        "BitArray exposes num_shots, num_bits and .array (shape (shots, packed bytes)).",
        "get_counts() aggregates; get_bitstrings() keeps every individual shot.",
    ],
)
