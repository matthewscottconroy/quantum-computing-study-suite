"""Problem: rep_5qubit_perfect"""
from __future__ import annotations
from quantum_study.qec_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_5qubit_perfect',
    category='Repetition Code',
    difficulty='advanced',
    question="The [[5,1,3]] code is called the 'perfect' single-error-correcting quantum code. Why?",
    choices=[
        'It saturates the quantum Hamming bound for d=3',
        'It can correct all errors perfectly with zero overhead',
        'It is a CSS code with perfect transversal gates',
        'It uses exactly 5 stabilizer generators',
    ],
    correct_index=0,
    explanation="The quantum Hamming bound requires n >= 5 to encode k=1 logical qubit with distance d=3. The [[5,1,3]] code achieves this minimum, making it 'perfect'. It has 4 stabilizer generators (n-k=4) and corrects any single-qubit Pauli error.",
    hints=[
        'Count the minimum qubits needed to distinguish all single-qubit error syndromes.',
    ],
    grade_mode=GradeMode.AUTO,
)
