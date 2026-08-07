"""Problem: bos_what_is_bosonic"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_what_is_bosonic',
    category='Bosonic Codes',
    difficulty='beginner',
    question='What is a bosonic code?',
    choices=[
        'An encoding of a logical qubit into the quantum states of a single harmonic oscillator (infinite-dimensional bosonic mode)',
        'A code that uses bosons (photons) instead of qubits as physical carriers, but still encodes one bit per particle',
        'A topological code where errors are modeled as bosonic anyons',
        'A code that uses boson sampling to perform error correction',
    ],
    correct_index=0,
    explanation='A bosonic code encodes one (or more) logical qubits into the Hilbert space of a single quantum harmonic oscillator mode — an infinite-dimensional bosonic system described by creation/annihilation operators â†, â and Fock states |n⟩. Rather than distributing a logical qubit across many two-level qubits (qubit codes), bosonic codes exploit the large Hilbert space of one oscillator. Examples include cat codes, GKP codes, and binomial codes. They are natural for photonic and microwave cavity platforms.',
    hints=[
        'A harmonic oscillator has infinitely many energy levels — much more Hilbert space than a qubit.',
    ],
    grade_mode=GradeMode.AUTO,
)
