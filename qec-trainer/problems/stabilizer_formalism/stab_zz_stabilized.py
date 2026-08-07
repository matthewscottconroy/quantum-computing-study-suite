"""Problem: stab_zz_stabilized"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_zz_stabilized',
    category='Stabilizer Formalism',
    difficulty='beginner',
    question='Which 2-qubit state is stabilized by +ZZ (and not by +ZI or +IZ alone)?',
    choices=[
        '(|00⟩ + |11⟩)/√2  and  (|00⟩ - |11⟩)/√2  (and any superposition)',
        '|00⟩ only',
        '|01⟩ and |10⟩',
        '|+⟩|+⟩',
    ],
    correct_index=0,
    explanation='ZZ|00⟩ = |00⟩ and ZZ|11⟩ = |11⟩, so any superposition α|00⟩ + β|11⟩ is stabilized by ZZ. Similarly ZZ|01⟩ = -|01⟩, so |01⟩ is not in the +1 eigenspace. The +ZZ codespace is the span {|00⟩, |11⟩}.',
    hints=[
        'Apply ZZ to each basis state and check the eigenvalue.',
    ],
    grade_mode=GradeMode.AUTO,
)
