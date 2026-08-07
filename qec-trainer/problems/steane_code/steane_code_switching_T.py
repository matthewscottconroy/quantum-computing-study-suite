"""Problem: steane_code_switching_T"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_code_switching_T',
    category='Steane Code',
    difficulty='advanced',
    question='Code switching between [[7,1,3]] and [[15,1,3]] allows implementation of which gate?',
    choices=[
        'T gate — the [[15,1,3]] Reed-Muller code has a transversal T, while [[7,1,3]] does not',
        'CNOT — neither code has transversal CNOT so switching is needed',
        'H gate — [[15,1,3]] has transversal H but [[7,1,3]] does not',
        'S gate — code switching provides a more efficient S implementation',
    ],
    correct_index=0,
    explanation='The [[15,1,3]] Reed-Muller code is a CSS code derived from RM(1,4), which is triply even (all codeword weights divisible by 8). This property enables a transversal T gate. The approach: (1) switch from [[7,1,3]] Steane to [[15,1,3]] Reed-Muller by encoding each of the 7 Steane qubits into the Reed-Muller code; (2) apply T transversally; (3) switch back. This avoids the large overhead of magic state distillation at the cost of temporarily using 15×7 = 105 physical qubits.',
    hints=[
        'The Reed-Muller code has a transversal T because of its triply-even codeword weight structure.',
    ],
    grade_mode=GradeMode.AUTO,
)
