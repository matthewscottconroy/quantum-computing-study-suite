"""Problem: ansatz_quantum_kernel"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_quantum_kernel',
    category='Ansatz Design',
    difficulty='advanced',
    question='What is a quantum kernel method as an ansatz-free alternative to VQAs?',
    choices=[
        "Uses a parameterised feature map circuit φ(x) to compute the kernel k(x,x') = |⟨φ(x)|φ(x')⟩|² and trains a classical SVM — no variational optimisation needed",
        'Replaces the variational ansatz with a fixed kernel circuit that computes inner products between classical data vectors',
        'A method where the quantum computer learns the kernel function by optimising circuit parameters',
        'A classical kernel SVM that uses quantum-inspired tensor network feature maps',
    ],
    correct_index=0,
    explanation="Quantum kernel methods (Havlíček et al. 2019) avoid variational optimisation entirely. A fixed (non-variational) feature map circuit φ(x)|0⟩ encodes classical data x into a quantum state. The kernel k(x,x') = |⟨0|φ†(x')φ(x)|0⟩|² is estimated by running the circuits and measuring the overlap. A classical SVM or kernel method is then trained on this kernel matrix. This sidesteps barren plateaus and VQA optimisation difficulties entirely, but the quantum advantage depends on the feature map being computationally hard to simulate classically.",
    hints=[
        'No variational loop needed — the circuit just computes inner products between data points.',
    ],
    grade_mode=GradeMode.MC,
)
