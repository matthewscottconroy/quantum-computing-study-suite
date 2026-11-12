"""Problem: vqe_born_oppenheimer"""
from __future__ import annotations
from quantum_study.vqa_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_born_oppenheimer',
    category='VQE Fundamentals',
    difficulty='beginner',
    question='What is the Born-Oppenheimer approximation and why is it used in VQE for quantum chemistry?',
    choices=[
        'Nuclei are fixed classical points; only the electrons are treated quantum-mechanically',
        'Electrons are treated as classical particles; only nuclear motion is quantised',
        'Both electrons and nuclei are treated quantum-mechanically on an equal footing',
        'The wavefunction is factored into real and imaginary parts to reduce circuit depth',
    ],
    correct_index=0,
    explanation='The Born-Oppenheimer approximation separates nuclear and electronic motion because nuclei are ~1836x heavier than electrons and move much more slowly. Nuclei are treated as fixed classical charges generating an external potential; the electronic Hamiltonian H_el(R) is solved for each nuclear configuration R. This reduces VQE to solving a purely electronic problem, drastically simplifying the Hilbert space that must be represented on a quantum computer.',
    hints=[
        'Think about the mass difference between electrons and nuclei.',
    ],
    grade_mode=GradeMode.MC,
)
