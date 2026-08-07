"""Problem: ft_code_switching"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_code_switching',
    category='Fault Tolerance',
    difficulty='advanced',
    question='What is code switching (code conversion) in fault-tolerant quantum computation?',
    choices=[
        'Transitioning a logical qubit from one code to another to access different transversal gate sets',
        'Switching between error correction and error detection codes at runtime',
        'Converting a physical qubit error into a syndrome measurement outcome',
        'Using different codes on different qubits in the same circuit',
    ],
    correct_index=0,
    explanation='Code switching: convert the encoding of a logical qubit from code A to code B, perform a gate that is transversal in B but not A, then switch back. For example, the [[15,1,3]] Reed-Muller code has a transversal T gate; one can switch from Steane code to Reed-Muller, apply T transversally, then switch back. This avoids magic state distillation at the cost of encoding overhead during the conversion.',
    hints=[
        'Different codes have different transversal gate sets; switching exploits this.',
    ],
    grade_mode=GradeMode.AUTO,
)
