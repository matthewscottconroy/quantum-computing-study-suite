"""Kata: qo2_expectation_value"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo2_expectation_value",
    section="Quantum operations",
    title="Exact expectation values from a Statevector",
    difficulty="beginner",
    prompt="""\
You do not need an Estimator to get an expectation value when you can
simulate exactly: `Statevector.expectation_value(observable)` does it in
one call.

For the Bell state (|00>+|11>)/sqrt(2) compute, as plain floats (take
`.real`):
1. `sv`  — the Statevector of the given `bell` circuit
2. `zz`  — <ZZ>   (expect +1)
3. `xx`  — <XX>   (expect +1)
4. `zi`  — <Z on qubit 1, I on qubit 0>, i.e. label "ZI"  (expect 0)

Build each observable with `SparsePauliOp(label)`. Remember Pauli labels
are little-endian: the rightmost character acts on qubit 0.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)

# TODO: sv, zz, xx, zi
""",
    test_code="""\
from qiskit.quantum_info import Statevector

assert isinstance(sv, Statevector), "sv must be a Statevector"
for _name, _val, _want in (("zz", zz, 1.0), ("xx", xx, 1.0), ("zi", zi, 0.0)):
    assert isinstance(_val, float), (
        f"{_name} must be a float — expectation_value returns a complex, take .real "
        f"(got {type(_val).__name__})"
    )
    assert abs(_val - _want) < 1e-9, (
        f"<{_name.upper()}> for the Bell state should be {_want}, got {_val}"
    )
print(f"<ZZ>={zz:.3f}  <XX>={xx:.3f}  <ZI>={zi:.3f}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)

sv = Statevector.from_instruction(bell)
zz = sv.expectation_value(SparsePauliOp("ZZ")).real
xx = sv.expectation_value(SparsePauliOp("XX")).real
zi = sv.expectation_value(SparsePauliOp("ZI")).real
""",
    hints=[
        "Statevector.from_instruction(bell) gives the state; .expectation_value(obs) the value.",
        "SparsePauliOp(\"ZZ\") builds a single-term observable directly from a label.",
        "The return type is complex even for Hermitian observables — append .real.",
    ],
)
