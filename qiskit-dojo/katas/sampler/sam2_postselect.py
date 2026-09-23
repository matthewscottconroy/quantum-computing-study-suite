"""Kata: sam2_postselect"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="sam2_postselect",
    section="Sampler",
    title="Post-select shots from a BitArray",
    difficulty="intermediate",
    prompt="""\
`BitArray.get_bitstrings()` hands back the raw per-shot outcomes, which is
what you need for post-selection, heralding and any conditional analysis
that counts dicts cannot express.

The starter builds a 2-qubit circuit with H on BOTH qubits, so all four
outcomes are equally likely. Run it on a StatevectorSampler with
shots=4000 and seed=99, then build:
1. `shots_list` — result[0].data.c.get_bitstrings()  (4000 strings)
2. `kept` — only the shots where QUBIT 0 measured 1
3. `frac` — len(kept) / len(shots_list)

THE TRAP: bitstrings are little-endian. Qubit 0 is the LAST character of
each string, so test `s[-1] == "1"`, not `s[0]`.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.h(1)
qc.measure([0, 1], [0, 1])

# TODO: run with shots=4000 and seed=99, then shots_list, kept, frac
""",
    test_code="""\
assert len(shots_list) == 4000, (
    f"get_bitstrings() returns one string per shot — expected 4000, got {len(shots_list)}"
)
assert all(len(s) == 2 for s in shots_list), (
    "Each bitstring covers the 2-bit register 'c'"
)

_expected = [s for s in shots_list if s[-1] == "1"]
assert len(kept) == len(_expected), (
    f"kept must hold the shots whose QUBIT 0 bit is 1. Qubit 0 is the LAST character "
    f"(little-endian), so s[-1] == '1'. Expected {len(_expected)} shots, got {len(kept)}. "
    f"Selecting on s[0] would have given {len([s for s in shots_list if s[0] == '1'])}."
)
assert all(s[-1] == "1" for s in kept), "Every kept shot must have qubit 0 == 1"
assert abs(frac - len(kept) / len(shots_list)) < 1e-12, (
    f"frac must be len(kept)/len(shots_list), got {frac}"
)
assert 0.45 < frac < 0.55, (
    f"Both qubits are in |+>, so about half the shots survive; got frac={frac}"
)
print(f"kept {len(kept)}/{len(shots_list)} shots (frac = {frac:.3f})")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.h(1)
qc.measure([0, 1], [0, 1])

result = StatevectorSampler(seed=99).run([qc], shots=4000).result()
shots_list = result[0].data.c.get_bitstrings()
kept = [s for s in shots_list if s[-1] == "1"]
frac = len(kept) / len(shots_list)
""",
    hints=[
        "StatevectorSampler(seed=99).run([qc], shots=4000).result() gives the PrimitiveResult.",
        "result[0].data.c.get_bitstrings() is a plain list of strings, one per shot — "
        "unlike get_counts(), it preserves shot order.",
        "Little-endian: in the string 'q1q0' the rightmost character is qubit 0, so filter "
        "on s[-1].",
    ],
)
