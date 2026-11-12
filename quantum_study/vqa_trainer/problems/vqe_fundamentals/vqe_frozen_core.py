"""Problem: vqe_frozen_core"""
from __future__ import annotations
from quantum_study.vqa_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_frozen_core',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='What is the frozen core approximation in VQE-based quantum chemistry?',
    choices=[
        'Core electrons are handled at mean-field level, outside the simulation',
        'The quantum circuit parameters are frozen after the first optimisation step',
        'Only the highest energy orbitals are excluded from the simulation',
        'The Hamiltonian is approximated by freezing off-diagonal elements',
    ],
    correct_index=0,
    explanation='Core electrons (e.g. 1s electrons in carbon) are tightly bound and contribute minimally to chemical bonding and correlation. The frozen core approximation excludes them from the quantum simulation entirely, treating them at the Hartree-Fock level. This reduces the active orbital count and thus the qubit count, at the cost of a small energy correction that can be added back classically.',
    hints=[
        "Core electrons don't participate much in bonding — can they be treated classically?",
    ],
    grade_mode=GradeMode.MC,
)
