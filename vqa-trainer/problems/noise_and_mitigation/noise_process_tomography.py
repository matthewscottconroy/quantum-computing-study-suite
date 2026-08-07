"""Problem: noise_process_tomography"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_process_tomography',
    category='Noise & Mitigation',
    difficulty='beginner',
    question='What is quantum process tomography (QPT) and what is its resource cost?',
    choices=[
        'Full characterisation of a quantum channel via 4ⁿ input states and 4ⁿ measurement settings; scales exponentially in qubit count',
        'Measuring the output of a single fixed input state to characterise the gate fidelity',
        'A classical simulation technique that reconstructs the quantum channel from process matrices',
        'Tomography of the quantum process using only Clifford circuits, scaling polynomially',
    ],
    correct_index=0,
    explanation='QPT reconstructs the full process matrix (χ-matrix or Choi state) of an n-qubit channel. It requires preparing all d² = 4ⁿ input states of a complete basis (e.g. {|0⟩,|1⟩,|+⟩,|+i⟩}^n) and measuring in all d² = 4ⁿ output bases. Total circuits: 4^n × 4^n = 16^n — exponential in qubit count. For a single qubit: 16 settings. For 2 qubits: 256. This exponential cost makes QPT impractical for more than ~3–4 qubits; efficient alternatives include randomized benchmarking and sparse QPT.',
    hints=[
        'For n qubits you need 4^n input states AND 4^n measurement bases — multiply them.',
    ],
    grade_mode=GradeMode.MC,
)
