"""Problem: ft_gate_teleportation_T"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_gate_teleportation_T',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='How is gate teleportation used to implement a T gate fault-tolerantly?',
    choices=[
        'Prepare the magic state |T⟩ = T|+⟩, then consume it via Bell measurement + Clifford correction to apply T to the data qubit',
        'Teleport the data qubit to a location where T is transversal, apply T, then teleport back',
        'Measure the data qubit in the T-basis and apply a correction based on the outcome',
        'Use two CNOT gates and an ancilla to synthesize T from Clifford gates',
    ],
    correct_index=0,
    explanation='Gate teleportation for T: (1) prepare resource state |T⟩ = T|+⟩ = (|0⟩ + e^{iπ/4}|1⟩)/√2. (2) Perform a Bell-basis measurement between the data qubit and |T⟩. (3) Apply a Clifford correction (from {I, X, SX, SXS†} depending on the 2-bit outcome). The T gate is effectively applied to the data qubit through the magic state, so only Clifford operations need to be applied to the actual data.',
    hints=[
        "The T gate is 'encoded' in the resource state; standard teleportation transfers it.",
    ],
    grade_mode=GradeMode.AUTO,
)
