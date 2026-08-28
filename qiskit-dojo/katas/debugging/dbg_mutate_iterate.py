"""Kata: dbg_mutate_iterate"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg_mutate_iterate",
    section="Debugging",
    title="Fix it: mutating circuit data while iterating",
    difficulty="advanced",
    prompt="""\
DEBUGGING KATA — the starter runs without error but silently does only
HALF the job.

Goal: strip ALL measurement instructions from a measured GHZ circuit
(to reuse it with an Estimator). The starter loops over `qc.data` and
removes measures as it goes — but deleting from a list WHILE iterating
it skips elements, so one measure survives.

Fix the removal so no measure operations remain (the h and both cx
gates must survive). The cleanest fix is Qiskit's own
`remove_final_measurements()`; iterating over a COPY of the list also
works.
""",
    starter_code="""\
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

# strip the measurements  (BUG: mutates qc.data during iteration)
for instruction in qc.data:
    if instruction.operation.name == "measure":
        qc.data.remove(instruction)
""",
    test_code="""\
_ops = qc.count_ops()
assert _ops.get("measure", 0) == 0, (
    f"{_ops.get('measure', 0)} measure instruction(s) survived! Removing items from "
    "a list while iterating it skips the element after each removal. "
    "Iterate over a copy, or use qc.remove_final_measurements()."
)
assert _ops.get("h", 0) == 1 and _ops.get("cx", 0) == 2, (
    f"The h and both cx gates must survive, got {dict(_ops)}"
)
print(f"Ops after stripping: {dict(_ops)}")
""",
    solution_code="""\
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure_all()

# the built-in does exactly this job (also drops the now-idle classical register)
qc.remove_final_measurements()

# equivalent manual fix: iterate over a snapshot
# for instruction in list(qc.data):
#     if instruction.operation.name == "measure":
#         qc.data.remove(instruction)
""",
    hints=[
        "Print qc.count_ops() after the loop — a measure is still there. Why only some?",
        "list.remove during a for-loop shifts indices: the iterator then skips the next element.",
        "qc.remove_final_measurements() or `for ins in list(qc.data): ...` both fix it.",
    ],
)
