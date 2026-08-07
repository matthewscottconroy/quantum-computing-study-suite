"""Problem: surf_color_code"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_color_code',
    category='Surface Code',
    difficulty='advanced',
    question='The color code is defined on a 3-colorable lattice. What is its key advantage over the surface code?',
    choices=[
        'The color code supports a transversal T gate (on 3D color codes), which the surface code lacks',
        'The color code has a higher fault-tolerant threshold than the surface code',
        'The color code requires fewer physical qubits per logical qubit',
        'The color code has only Z-type stabilizers, simplifying syndrome measurement',
    ],
    correct_index=0,
    explanation='3D color codes (e.g., on a tetrahedral lattice) support transversal T gates because the code is defined from a triply-even classical code. In contrast, the 2D surface code has no transversal non-Clifford gate, requiring magic state distillation for T. The trade-off: color codes have a lower fault-tolerant threshold (~0.1–0.5% for 3D vs ~1% for surface codes) and higher overhead per logical qubit. 2D color codes support transversal Clifford gates (H, S, CNOT) similar to CSS codes.',
    hints=[
        'The surface code needs magic state distillation for T; color codes can do better.',
    ],
    grade_mode=GradeMode.AUTO,
)
