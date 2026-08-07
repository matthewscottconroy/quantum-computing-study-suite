"""Problem: steane_cat_state_ancilla"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_cat_state_ancilla',
    category='Steane Code',
    difficulty='advanced',
    question='What is the cat state method for fault-tolerant ancilla preparation in Steane code syndrome measurement?',
    choices=[
        'Prepare (|0...0⟩ + |1...1⟩)/√2 as ancilla, verify it with a flag qubit, then use it for transversal stabilizer measurement',
        'Prepare individual |0⟩ ancillas and apply a CNOT chain',
        'Use cat states to distill magic states for the T gate',
        'Prepare the full encoded |0̄⟩ ancilla and verify it with another code block',
    ],
    correct_index=0,
    explanation="The cat state ancilla |cat⟩ = (|00...0⟩ + |11...1⟩)/√2 (n-qubit) can be used for fault-tolerant weight-n stabilizer measurement. Before use, the cat state is verified: a flag qubit is entangled and measured; if high-weight errors in cat state preparation leaked to the data, the flag fires. Shor's original fault-tolerant scheme uses cat states one-ancilla-per-stabilizer; Steane's method instead prepares full encoded ancilla blocks for parallel extraction.",
    hints=[
        'Cat states provide the weight-n ancilla needed to measure weight-n stabilizers fault-tolerantly.',
    ],
    grade_mode=GradeMode.AUTO,
)
