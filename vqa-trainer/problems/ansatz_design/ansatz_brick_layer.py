"""Problem: ansatz_brick_layer"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_brick_layer',
    category='Ansatz Design',
    difficulty='intermediate',
    question='What is a brick-layer (alternating-layer) ansatz?',
    choices=[
        'Alternating layers of single-qubit rotations and nearest-neighbour entangling CNOT/CZ gates in a staggered pattern',
        'A circuit where each qubit has exactly two rotation gates and one CNOT',
        'A deep UCCSD circuit decomposed into repeated Trotter layers',
        'A circuit where brick-shaped blocks of 4 qubits are individually optimised',
    ],
    correct_index=0,
    explanation="A brick-layer ansatz interleaves two types of layers: (1) single-qubit rotation layers where each qubit gets Rz(θ)Ry(φ) (or similar) rotations, and (2) entangling layers with CNOT or CZ gates applied to neighbouring pairs in a staggered 'brick' pattern (e.g. odd pairs in even layers, even pairs in odd layers). This balances expressibility, hardware efficiency, and gradient trainability, and is widely used for both quantum chemistry and optimisation VQAs.",
    hints=[
        'Picture a brick wall: alternating rows of blocks offset by half a brick width.',
    ],
    grade_mode=GradeMode.MC,
)
