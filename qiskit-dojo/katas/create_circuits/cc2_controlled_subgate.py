"""Kata: cc2_controlled_subgate"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="cc2_controlled_subgate",
    section="Create circuits",
    title="to_gate, control and append",
    difficulty="advanced",
    prompt="""\
Any circuit can be packaged as a reusable `Gate` with `to_gate()`, and any
gate can be promoted to a controlled version with `.control(n)`.

Build:
1. `sub` — a 2-qubit circuit NAMED "bell" preparing (|00>+|11>)/sqrt(2)
2. `bell_gate` — sub.to_gate()
3. `ctrl_bell` — the singly-controlled version of `bell_gate`
4. `qc` — a 3-qubit circuit that applies x to qubit 0, then appends
   `ctrl_bell` on qubits [0, 1, 2] (control first)

Because qubit 0 is |1>, the control fires and qubits 1,2 end up in a Bell
pair. Keep `qc` free of measurements.
""",
    starter_code="""\
from qiskit import QuantumCircuit

sub = QuantumCircuit(2, name="bell")
# TODO: make sub a Bell-state preparation

# TODO: bell_gate = ..., ctrl_bell = ..., qc = ...
""",
    test_code="""\
from qiskit import QuantumCircuit
from qiskit.circuit import Gate
from qiskit.quantum_info import Statevector

assert isinstance(bell_gate, Gate), "bell_gate must be a Gate — use sub.to_gate()"
assert bell_gate.name == "bell", (
    f"to_gate() takes its name from the circuit; name the circuit 'bell' "
    f"(got gate name {bell_gate.name!r})"
)
assert ctrl_bell.num_qubits == 3, (
    f"A 1-controlled 2-qubit gate spans 3 qubits, got {ctrl_bell.num_qubits}"
)
assert ctrl_bell.num_ctrl_qubits == 1, "ctrl_bell must have exactly one control qubit"

assert qc.num_qubits == 3, "qc must be a 3-qubit circuit"
_names = [i.operation.name for i in qc.data]
assert len(_names) == 2 and _names[0] == "x", (
    f"qc should be exactly x(0) then the controlled gate, got {_names}"
)

_ref = QuantumCircuit(3)
_ref.x(0)
_ref.h(1)
_ref.cx(1, 2)
_sv = Statevector.from_instruction(qc)
assert _sv.equiv(Statevector.from_instruction(_ref)), (
    "Expected |1> on qubit 0 and a Bell pair on qubits 1,2. Append order is "
    "[control, target0, target1]."
)
print(f"Controlled sub-gate applied: ops = {dict(qc.count_ops())}")
""",
    solution_code="""\
from qiskit import QuantumCircuit

sub = QuantumCircuit(2, name="bell")
sub.h(0)
sub.cx(0, 1)

bell_gate = sub.to_gate()
ctrl_bell = bell_gate.control(1)

qc = QuantumCircuit(3)
qc.x(0)
qc.append(ctrl_bell, [0, 1, 2])
""",
    hints=[
        "QuantumCircuit(2, name=\"bell\") — to_gate() inherits that name.",
        "gate.control(1) returns a ControlledGate whose qubit order is controls first, "
        "then the original gate's qubits.",
        "qc.append(ctrl_bell, [0, 1, 2]) maps control->0, sub qubit 0->1, sub qubit 1->2.",
    ],
)
