"""Problem: ansatz_mera"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_mera',
    category='Ansatz Design',
    difficulty='intermediate',
    question='What is the multiscale entanglement renormalisation ansatz (MERA)?',
    choices=[
        'A tensor network ansatz with alternating disentangler and isometry tensors at each scale, capturing long-range entanglement at O(log n) depth',
        'An ansatz that uses multiple energy scales in the Hamiltonian to design separate layers',
        'A renormalisation group-inspired classical algorithm that generates initial parameters for VQE',
        'A 1D ansatz equivalent to MPS but extended to 2D by adding renormalisation layers',
    ],
    correct_index=0,
    explanation="MERA (Vidal 2007) represents quantum states via a hierarchical tensor network: at each length scale, pairs of 'disentangler' unitaries remove short-range entanglement, then 'isometry' tensors coarse-grain the system, halving the qubit count. This multi-scale structure efficiently captures critical (gapless) systems with logarithmic entanglement — beyond what MPS can represent. On a quantum computer, MERA translates to a circuit of depth O(log² n) with spatially structured gates, making it attractive for 1D and 2D critical systems beyond the MPS regime.",
    hints=[
        'MERA uses a renormalisation hierarchy: coarse-grain and remove entanglement at each level.',
    ],
    grade_mode=GradeMode.MC,
)
