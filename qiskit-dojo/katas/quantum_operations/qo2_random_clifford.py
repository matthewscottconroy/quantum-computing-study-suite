"""Kata: qo2_random_clifford"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo2_random_clifford",
    section="Quantum operations",
    title="random_clifford round-trip",
    difficulty="advanced",
    prompt="""\
The Clifford group is the backbone of randomized benchmarking and
stabilizer simulation. `qiskit.quantum_info` can sample one, turn it into
a circuit, and read it back — a round-trip every Clifford workflow relies
on.

Build:
1. `cliff` — random_clifford(3, seed=2024)
2. `circ` — the circuit form of `cliff`
3. `back` — a Clifford rebuilt FROM `circ`
4. `same` — the truth value of `back == cliff`

The tests also check the unitary of `circ` matches cliff.to_operator()
up to global phase.
""",
    starter_code="""\
from qiskit.quantum_info import Clifford, Operator, random_clifford

# TODO: cliff, circ, back, same
""",
    test_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Operator, random_clifford

assert isinstance(cliff, Clifford), "cliff must come from random_clifford(...)"
assert cliff.num_qubits == 3, f"Sample a 3-qubit Clifford, got {cliff.num_qubits}"
assert cliff == random_clifford(3, seed=2024), (
    "Pass seed=2024 so the sample is reproducible"
)

assert isinstance(circ, QuantumCircuit), "circ must be a QuantumCircuit — use cliff.to_circuit()"
assert circ.num_qubits == 3, "circ must act on 3 qubits"
assert isinstance(back, Clifford), "back must be a Clifford rebuilt from circ — Clifford(circ)"

assert bool(same) is True, (
    f"The round-trip must be exact: Clifford(cliff.to_circuit()) == cliff. Got same={same!r}"
)
assert back == cliff, "back and cliff must be the same Clifford (tableaux compare equal)"
assert Operator(circ).equiv(cliff.to_operator()), (
    "The circuit's unitary must match cliff.to_operator() up to global phase"
)
print(f"Round-trip ok — circuit ops: {dict(circ.count_ops())}")
""",
    solution_code="""\
from qiskit.quantum_info import Clifford, Operator, random_clifford

cliff = random_clifford(3, seed=2024)
circ = cliff.to_circuit()
back = Clifford(circ)
same = back == cliff
""",
    hints=[
        "random_clifford(num_qubits, seed=...) returns a Clifford, not a circuit.",
        "cliff.to_circuit() synthesises a Clifford circuit; Clifford(circ) reads a circuit "
        "back into a tableau.",
        "Clifford equality compares stabilizer tableaux, so == is the right check here — "
        "use Operator.equiv only when comparing unitaries.",
    ],
)
