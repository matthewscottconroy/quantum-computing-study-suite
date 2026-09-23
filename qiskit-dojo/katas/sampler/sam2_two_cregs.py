"""Kata: sam2_two_cregs"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="sam2_two_cregs",
    section="Sampler",
    title="Two classical registers, two BitArrays",
    difficulty="intermediate",
    prompt="""\
A SamplerV2 DataBin holds ONE BitArray per classical register, each named
after its register. With two registers you get two independent count
dicts — no manual bitstring slicing, no marginalisation.

Build a 3-qubit circuit `qc` with:
- QuantumRegister(3, "q")
- ClassicalRegister(2, "pair") and ClassicalRegister(1, "spare"), in that order
- a Bell pair on q[0], q[1] measured into `pair`
- q[2] left in |0> and measured into `spare`

Then run it on a StatevectorSampler with shots=600 and extract:
`pair_counts` (from data.pair) and `spare_counts` (from data.spare).
""",
    starter_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.primitives import StatevectorSampler

# TODO: registers q/pair/spare, Bell on q[0],q[1] -> pair, q[2] -> spare,
#       run with shots=600, then pair_counts and spare_counts
""",
    test_code="""\
_cregs = [r.name for r in qc.cregs]
assert _cregs == ["pair", "spare"], (
    f"Expected classical registers 'pair' then 'spare', got {_cregs}"
)
assert qc.num_qubits == 3 and qc.num_clbits == 3, (
    f"3 qubits and 2+1 classical bits expected, got {qc.num_qubits}/{qc.num_clbits}"
)

assert sum(pair_counts.values()) == 600, (
    f"pair_counts must total 600 shots, got {sum(pair_counts.values())}"
)
assert sum(spare_counts.values()) == 600, (
    f"spare_counts must total 600 shots, got {sum(spare_counts.values())}"
)
assert set(pair_counts) == {"00", "11"}, (
    f"The Bell pair gives 00 and 11 only (2-bit strings from the 'pair' register), "
    f"got {sorted(pair_counts)}"
)
assert spare_counts == {"0": 600}, (
    f"q[2] is never touched, so 'spare' is always '0'; got {spare_counts}. "
    "Each register has its OWN BitArray — data.spare is 1 bit wide."
)
print(f"pair={pair_counts}, spare={spare_counts}")
""",
    solution_code="""\
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.primitives import StatevectorSampler

q = QuantumRegister(3, "q")
pair = ClassicalRegister(2, "pair")
spare = ClassicalRegister(1, "spare")
qc = QuantumCircuit(q, pair, spare)

qc.h(q[0])
qc.cx(q[0], q[1])
qc.measure(q[0], pair[0])
qc.measure(q[1], pair[1])
qc.measure(q[2], spare[0])

result = StatevectorSampler(seed=23).run([qc], shots=600).result()
pair_counts = result[0].data.pair.get_counts()
spare_counts = result[0].data.spare.get_counts()
""",
    hints=[
        "QuantumCircuit(q, pair, spare) — the DataBin attribute names copy the register names.",
        "qc.measure(q[0], pair[0]) targets a specific classical bit; measure_all() would "
        "add a third register called 'meas' instead.",
        "result[0].data.pair and result[0].data.spare are separate BitArrays with "
        "num_bits 2 and 1.",
    ],
)
