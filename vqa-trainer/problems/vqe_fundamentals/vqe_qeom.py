"""Problem: vqe_qeom"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_qeom',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='What is the quantum equation of motion (qEOM) approach for excited states in VQE?',
    choices=[
        'Uses the VQE ground state to set up a linear-response eigenvalue problem that gives excitation energies from small extra quantum circuits',
        'Evolves the VQE state forward in imaginary time to access higher energy states',
        'Applies the Heisenberg equation of motion to compute real-time dynamics from a VQE initial state',
        'Solves the time-dependent Schrödinger equation variationally to extract excited-state frequencies',
    ],
    correct_index=0,
    explanation="qEOM (Ollitrault et al. 2020) builds on a converged VQE ground state |ψ₀⟩. It constructs matrix elements of commutators ⟨ψ₀|[Oₖ†, [H, Oₗ]]|ψ₀⟩ where {Oₖ} is an excitation operator set. These matrix elements define a generalised eigenvalue problem that yields excitation energies and transition amplitudes. The extra quantum cost is moderate — only expectation values of 2–4 body operators on the already-prepared ground state. qEOM combines VQE's hardware efficiency with equation-of-motion theory's ability to compute many excitations simultaneously.",
    hints=[
        'Think of it as linear response theory built on top of the VQE ground state.',
    ],
    grade_mode=GradeMode.MC,
)
