"""Problem: bos_cat_qubit_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_cat_qubit_def',
    category='Bosonic Codes',
    difficulty='beginner',
    question='A cat qubit encodes a logical qubit using which states of a harmonic oscillator?',
    choices=[
        'Superpositions of two coherent states |α⟩ and |−α⟩: |0̄⟩ ∝ |α⟩+|−α⟩ and |1̄⟩ ∝ |α⟩−|−α⟩',
        'The Fock states |0⟩ and |1⟩ of the oscillator',
        'Squeezed vacuum states displaced in opposite directions',
        'Two-mode entangled states of the oscillator with its environment',
    ],
    correct_index=0,
    explanation='A cat qubit encodes in the even and odd parity subspaces of a harmonic oscillator, spanned by the Schrödinger cat states: |C+_α⟩ ∝ |α⟩ + |−α⟩ (even parity superposition) and |C−_α⟩ ∝ |α⟩ − |−α⟩ (odd parity superposition). Here |±α⟩ are coherent states with amplitude ±α. Logical |0̄⟩ = |C+_α⟩ and |1̄⟩ = |C−_α⟩ (or vice versa depending on convention). For large |α|², the two coherent states are nearly orthogonal.',
    hints=[
        "Coherent states |α⟩ and |−α⟩ are the two 'pointer states' — their superpositions form the qubit.",
    ],
    grade_mode=GradeMode.AUTO,
)
