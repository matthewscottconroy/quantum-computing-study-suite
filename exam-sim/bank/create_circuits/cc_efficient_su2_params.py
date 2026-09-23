"""Question: cc_efficient_su2_params"""
from core.models import Question

QUESTION = Question(
    id='cc_efficient_su2_params',
    section='Create circuits',
    question='What does this print?\n\n```python\nfrom qiskit.circuit.library import efficient_su2\n\nansatz = efficient_su2(3, reps=1)\nprint(ansatz.num_parameters)\n```',
    options=[
        '12',
        '6',
        '3',
        '24',
    ],
    correct_index=0,
    explanation='EfficientSU2 alternates rotation layers (RY then RZ on every qubit) with an entanglement layer, and adds one final rotation layer: (reps + 1) × 2 rotations × 3 qubits = 2 × 2 × 3 = 12. With the default reps=3 the same circuit would have 24 parameters. In Qiskit 2.x the function efficient_su2() is the supported builder; the EfficientSU2 class is deprecated since 2.1.',
    difficulty='medium',
)
