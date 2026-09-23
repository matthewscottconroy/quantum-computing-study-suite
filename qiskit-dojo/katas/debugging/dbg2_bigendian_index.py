"""Kata: dbg2_bigendian_index"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg2_bigendian_index",
    section="Debugging",
    title="Fix it: enumerate() reads a counts key big-endian",
    difficulty="intermediate",
    prompt="""\
DEBUGGING KATA — the starter RUNS and produces a plausible-looking
answer, which is the worst kind of bug. Run it as-is and read the
failure first.

The circuit flips qubits 0 and 1 of a 3-qubit register, so the only
outcome is the key '011' and the qubits that read 1 are [0, 1].

The author walks the key with `enumerate(key)` to recover those indices.
But enumerate numbers the CHARACTERS left to right, while a Qiskit
bitstring is printed highest-qubit-first: character j of an n-character
key is qubit (n - 1 - j). The reported list comes out shifted.

Fix the mapping so `ones` is [0, 1].
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(3)
qc.x(0)
qc.x(1)              # qubits 0 and 1 flipped; qubit 2 stays |0>
qc.measure_all()

result = StatevectorSampler(seed=11).run([qc], shots=400).result()
counts = result[0].data.meas.get_counts()
key = max(counts, key=counts.get)

# which qubits came out as 1?
ones = sorted(i for i, bit in enumerate(key) if bit == "1")
""",
    test_code="""\
assert key == "011", (
    f"Sanity: X on qubits 0 and 1 of |000> gives the single key '011', got {key!r}"
)
assert ones == [0, 1], (
    f"Qubits 0 and 1 were flipped, so ones must be [0, 1] — got {ones}. "
    "enumerate(key) numbered the characters left to right, but the LEFTMOST "
    "character is the HIGHEST qubit: character j is qubit (len(key) - 1 - j)."
)
print(f"key = {key} -> qubits reading 1: {ones}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(3)
qc.x(0)
qc.x(1)
qc.measure_all()

result = StatevectorSampler(seed=11).run([qc], shots=400).result()
counts = result[0].data.meas.get_counts()
key = max(counts, key=counts.get)

# walk the key from the right: character 0 of the reversed key is qubit 0
ones = sorted(i for i, bit in enumerate(reversed(key)) if bit == "1")
""",
    hints=[
        "Print key alongside ones: the key is '011' but the answer claims qubits 1 and 2.",
        "enumerate(reversed(key)) numbers the characters from qubit 0 upwards.",
        "Equivalently keep enumerate(key) and use index (len(key) - 1 - j).",
    ],
)
