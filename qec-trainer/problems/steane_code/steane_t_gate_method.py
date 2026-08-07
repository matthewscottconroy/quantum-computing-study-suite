"""Problem: steane_t_gate_method"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_t_gate_method',
    category='Steane Code',
    difficulty='advanced',
    question='Since T is not transversal for the Steane code, how is it implemented fault-tolerantly?',
    choices=[
        'Magic state distillation and injection: prepare |T⟩ = T|+⟩ and consume it via gate teleportation',
        'Code switching to a code where T is transversal, then switching back',
        'Applying T directly to all 7 physical qubits simultaneously',
        'Decomposing T into a product of Clifford gates',
    ],
    correct_index=0,
    explanation='The standard approach is magic state distillation: prepare many noisy copies of |T⟩ = T|+⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2 using only Clifford operations and noisy T gates, then distill a high-fidelity |T⟩ using the 15-to-1 protocol (or similar). The purified magic state is then injected into the circuit via gate teleportation, with a Clifford correction conditioned on the measurement outcome.',
    hints=[
        "T|+⟩ is a 'magic state' that encodes the T gate action.",
    ],
    grade_mode=GradeMode.AUTO,
)
