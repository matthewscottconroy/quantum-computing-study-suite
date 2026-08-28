"""Kata: dbg_measured_estimator"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="dbg_measured_estimator",
    section="Debugging",
    title="Fix it: measured circuit fed to the Estimator",
    difficulty="intermediate",
    prompt="""\
DEBUGGING KATA — the starter code CRASHES. Run it, read the traceback,
fix it.

The goal is <ZZ> of a Bell state via StatevectorEstimator. But the
author copy-pasted a Sampler workflow, measure_all() included — and the
Estimator computes <psi|O|psi> from the STATE, so it rejects circuits
containing measurements.

Fix the circuit so the estimator runs and `ev_zz` comes out as 1.0.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()        # left over from a Sampler workflow

estimator = StatevectorEstimator()
result = estimator.run([(qc, SparsePauliOp("ZZ"))]).result()
ev_zz = float(result[0].data.evs)
""",
    test_code="""\
assert "measure" not in qc.count_ops(), (
    "The circuit handed to an Estimator must contain no measurements"
)
assert abs(ev_zz - 1.0) < 1e-9, f"<ZZ> of the Bell state is exactly 1.0, got {ev_zz}"
print(f"ev_zz = {ev_zz}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
# no measure_all() — the Estimator works on the state, not on samples

estimator = StatevectorEstimator()
result = estimator.run([(qc, SparsePauliOp("ZZ"))]).result()
ev_zz = float(result[0].data.evs)
""",
    hints=[
        "Read the error: 'Cannot apply instruction with classical bits: measure'.",
        "Sampler pubs need measured circuits; Estimator pubs need UNmeasured circuits plus observables.",
        "Delete the measure_all() line (or call qc.remove_final_measurements()).",
    ],
)
