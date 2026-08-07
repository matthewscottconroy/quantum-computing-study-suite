"""Problem: stab_bell_stabilizers"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_bell_stabilizers',
    category='Stabilizer Formalism',
    difficulty='beginner',
    question='The Bell state |Φ+⟩ = (|00⟩+|11⟩)/√2 is stabilized by which pair?',
    choices=[
        'XX and ZZ',
        'XX and ZI',
        'IZ and ZI',
        'YY and XX',
    ],
    correct_index=0,
    explanation='XX|Φ+⟩ = (|11⟩+|00⟩)/√2 = |Φ+⟩  ✓\nZZ|Φ+⟩ = (|00⟩+|11⟩)/√2 = |Φ+⟩  ✓\nThese two independent stabilizers uniquely fix the Bell state.',
    hints=[
        'Apply XX and ZZ explicitly to (|00⟩+|11⟩)/√2.',
    ],
    grade_mode=GradeMode.AUTO,
)
