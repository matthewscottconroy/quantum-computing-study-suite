"""Problem: ansatz_brick_layer_detail"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_brick_layer_detail',
    category='Ansatz Design',
    difficulty='intermediate',
    question="In a 'brick-layer' (alternating-layer) entangling pattern, how are CNOTs arranged across even and odd layers for n qubits on a linear chain?",
    choices=[
        'Even layers: CNOTs on pairs (0,1),(2,3),(4,5)...; odd layers: CNOTs on pairs (1,2),(3,4),(5,6)...; the two patterns tile like a brick wall',
        'Even layers: CNOT on all pairs; odd layers: no CNOTs',
        'Even layers: CNOTs from qubit 0 to all others; odd layers: CNOTs from qubit 1 to all others',
        "All layers use the same CNOT pattern — the 'brick' refers only to the shape of rotation blocks",
    ],
    correct_index=0,
    explanation='The brick-layer pattern staggers CNOTs to ensure all nearest-neighbour pairs interact across two adjacent layers. Layer 1 (even): (0,1),(2,3),(4,5),...; Layer 2 (odd): (1,2),(3,4),(5,6),.... After two layers, every neighbouring pair (i,i+1) has interacted at least once. This maximises connectivity on a linear chain while using only native nearest-neighbour gates, avoiding SWAP overhead. Deeper circuits repeat this 2-layer pattern, exponentially growing the entanglement reachable from the initial state.',
    hints=[
        'Picture a brick wall: each brick (CNOT) in one row sits between two bricks of the next row.',
    ],
    grade_mode=GradeMode.MC,
)
