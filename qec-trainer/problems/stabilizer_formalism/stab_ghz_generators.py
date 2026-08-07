"""Problem: stab_ghz_generators"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='stab_ghz_generators',
    category='Stabilizer Formalism',
    difficulty='beginner',
    question='The 3-qubit GHZ state |GHZ⟩ = (|000⟩ + |111⟩)/√2. Which set of operators generates its stabilizer group?',
    choices=[
        'XXX, ZZI, IZZ',
        'ZZZ, XXI, IXX',
        'XXX, ZZZ, III',
        'ZXZ, XZX, ZZZ',
    ],
    correct_index=0,
    explanation='XXX|GHZ⟩ = (|111⟩+|000⟩)/√2 = |GHZ⟩ ✓. ZZI|GHZ⟩ = (|000⟩+|111⟩·(−1)·(−1))/√2 = |GHZ⟩ ✓ (ZZ on first two qubits gives +1 for both |00⟩ and |11⟩). IZZ similarly gives +1. These three generators (only two are independent since XXX is the product) fully characterize the GHZ stabilizer state.',
    hints=[
        'Verify each candidate by acting it on (|000⟩ + |111⟩)/√2 and checking for +1 eigenvalue.',
    ],
    grade_mode=GradeMode.AUTO,
)
