"""Problem: steane_transversal_cnot"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_transversal_cnot',
    category='Steane Code',
    difficulty='intermediate',
    question='For any CSS code (including Steane), the CNOT gate can be implemented:',
    choices=[
        'Transversally — apply CNOT qubit-by-qubit between two code blocks',
        'Only via magic state injection',
        'Only after decoding and re-encoding',
        'By measuring in the Bell basis',
    ],
    correct_index=0,
    explanation='For CSS codes, transversal CNOT between two code blocks implements the logical CNOT. This works because CNOT maps X_ctrl X_tgt -> X_ctrl (and X I -> X X), which is compatible with the X and Z stabilizer structure of CSS codes.',
    hints=[
        'CSS codes have separate X-type and Z-type stabilizer groups — CNOT preserves both.',
    ],
    grade_mode=GradeMode.AUTO,
)
