"""Problem: ansatz_architecture_search"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_architecture_search',
    category='Ansatz Design',
    difficulty='intermediate',
    question="What is 'circuit architecture search' (CAS) for VQAs?",
    choices=[
        'Automatically optimising the circuit structure (gate types, connectivity, layer count) alongside parameters, using classical search algorithms',
        "Searching the parameter space using the circuit's architecture as a prior distribution",
        'Modifying the hardware device architecture to match a desired ansatz structure',
        'A technique to search for the shortest circuit depth that achieves a target fidelity',
    ],
    correct_index=0,
    explanation='CAS treats the circuit structure (which gates appear where) as a discrete hyperparameter to be optimised, not just the continuous gate angles. Approaches include: (1) evolutionary algorithms that mutate gate sequences; (2) differentiable architecture search (DAS) where gate type is a softmax mixture; (3) reinforcement learning that sequentially selects gates to add. CAS can discover compact problem-specific ansätze that outperform both generic hardware-efficient and manually designed problem-specific circuits, at the cost of a large outer optimisation loop.',
    hints=[
        'Architecture search optimises the circuit topology, not just the continuous parameters.',
    ],
    grade_mode=GradeMode.MC,
)
