"""Problem: ps_generator_assumption"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ps_generator_assumption',
    category='Parameter Shift',
    difficulty='beginner',
    question="What is the key property of a gate's generator that allows the parameter shift rule to give exact (not approximate) gradients?",
    choices=[
        'The generator has exactly two distinct eigenvalues (e.g. ±½ for Pauli generators)',
        'The generator is diagonal in the computational basis',
        'The generator commutes with all other gates in the circuit',
        'The generator is a real symmetric matrix',
    ],
    correct_index=0,
    explanation='The standard parameter shift rule ∂⟨H⟩/∂θ = [⟨H⟩(θ+π/2) - ⟨H⟩(θ-π/2)]/2 is derived from the fact that gates of the form e^{-iθG/2} with G having eigenvalues {±r} produce expectation values that are sinusoidal in θ with a single frequency. For Pauli generators (eigenvalues ±½), the shift is exactly π/2. If the generator has more than two distinct eigenvalues, the expectation value has multiple frequencies and a generalised multi-term shift rule is required.',
    hints=[
        "Pauli matrices have eigenvalues ±1 — what does that imply about the gate's spectrum?",
    ],
    grade_mode=GradeMode.MC,
)
