"""Kata: rc2_opt_level_depth"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="rc2_opt_level_depth",
    section="Run circuits",
    title="Compare depth across preset optimization levels",
    difficulty="intermediate",
    prompt="""\
Choosing an optimization level is a real decision on hardware: level 0
barely touches the circuit, levels 1-3 spend classical time to shorten it.
Measure the difference instead of guessing.

The starter builds a redundancy-heavy circuit `qc` and a fake `backend`.
Build:
1. `depths` — a dict {level: depth} for levels 0, 1, 2, 3, where each
   depth comes from running `qc` through
   generate_preset_pass_manager(optimization_level=level,
                                backend=backend, seed_transpiler=1234)
2. `best_level` — the level with the smallest depth (ties: the lowest
   level number)

Every H·H and CX·CX pair cancels, so the higher levels collapse the
circuit almost entirely.
""",
    starter_code="""\
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import generate_preset_pass_manager

backend = GenericBackendV2(num_qubits=5, seed=99)

qc = QuantumCircuit(4)
for _ in range(4):
    for i in range(4):
        qc.h(i)
        qc.h(i)          # cancels
    for i in range(3):
        qc.cx(i, i + 1)
        qc.cx(i, i + 1)  # cancels
qc.x(0)
qc.measure_all()

# TODO: depths = {...}, best_level = ...
""",
    test_code="""\
assert isinstance(depths, dict), "depths must be a dict {level: depth}"
assert sorted(depths) == [0, 1, 2, 3], (
    f"depths must have one entry per optimization level 0-3, got {sorted(depths)}"
)
assert all(isinstance(v, int) and v > 0 for v in depths.values()), (
    f"Every value must be a positive int from circuit.depth(), got {depths}"
)

assert depths[0] > depths[3], (
    f"Level 3 must be shallower than level 0 on this redundant circuit, got {depths}. "
    "Are you transpiling the SAME qc each time, and reading .depth() of the result?"
)
assert depths[3] <= depths[0] // 2, (
    f"The cancelling pairs should collapse almost everything at level 3, got {depths}"
)
assert best_level == min(depths, key=lambda lvl: (depths[lvl], lvl)), (
    f"best_level must be the shallowest level (lowest level number on a tie); "
    f"got {best_level} for depths {depths}"
)
print(f"depths = {depths}, best_level = {best_level}")
""",
    solution_code="""\
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import generate_preset_pass_manager

backend = GenericBackendV2(num_qubits=5, seed=99)

qc = QuantumCircuit(4)
for _ in range(4):
    for i in range(4):
        qc.h(i)
        qc.h(i)
    for i in range(3):
        qc.cx(i, i + 1)
        qc.cx(i, i + 1)
qc.x(0)
qc.measure_all()

depths = {}
for level in range(4):
    pm = generate_preset_pass_manager(
        optimization_level=level, backend=backend, seed_transpiler=1234
    )
    depths[level] = pm.run(qc).depth()

best_level = min(depths, key=lambda lvl: (depths[lvl], lvl))
""",
    hints=[
        "Loop over range(4), build a pass manager per level and call pm.run(qc).depth().",
        "pm.run never mutates qc, so the same circuit can feed all four levels.",
        "min(depths, key=lambda lvl: (depths[lvl], lvl)) breaks ties toward the lower level.",
    ],
)
