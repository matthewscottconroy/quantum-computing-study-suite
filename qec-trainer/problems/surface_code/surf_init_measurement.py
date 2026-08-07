"""Problem: surf_init_measurement"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_init_measurement',
    category='Surface Code',
    difficulty='intermediate',
    question='To initialize a surface code in the logical |0̄⟩ state, what is done?',
    choices=[
        'Initialize all data qubits in |0⟩, then measure Z-stabilizers (they are automatically +1); X-stabilizers are randomized and measured/corrected',
        'Apply the encoding circuit to a physical |0⟩ qubit',
        'Prepare a cat state and fan it out to all data qubits',
        'Perform a logical Z̄ measurement to project into |0̄⟩',
    ],
    correct_index=0,
    explanation="Initializing in |0̄⟩: set all d² data qubits to |0⟩. All Z-stabilizers are automatically satisfied (+1 eigenvalue), as Z|0⟩=+|0⟩. However, X-stabilizers are random (each qubit is in a Z eigenstate, not an X eigenstate). A single round of X-stabilizer measurement projects into the +1 X-eigenspace, completing the initialization. Any X-stabilizer that measured −1 indicates a local |1⟩ initialization error that can be tracked classically (it's equivalent to a known Z error, which is corrected by Pauli frame tracking).",
    hints=[
        'Physical |0⟩ satisfies Z-checks automatically; X-checks need one measurement round.',
    ],
    grade_mode=GradeMode.AUTO,
)
