"""Problem: bos_kerr_hamiltonian"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_kerr_hamiltonian',
    category='Bosonic Codes',
    difficulty='advanced',
    question='The Kerr Hamiltonian H = Kâ†²â² stabilizes cat states. How does this work?',
    choices=[
        'The Kerr interaction induces a photon-number-dependent phase rotation; eigenstates of â†²â² at eigenvalue n(n−1)K include the cat state superpositions, creating a two-fold degenerate ground manifold',
        'The Kerr term directly annihilates all photon loss errors',
        'Kerr interaction creates an energy gap that suppresses all errors exponentially',
        'The â†²â² operator has cat states as its zero-energy eigenstates in the rotating frame',
    ],
    correct_index=0,
    explanation='The Kerr Hamiltonian H = K â†²â² = K n̂(n̂−1)/1 (using n̂=â†â) introduces a photon-number-dependent energy shift. In a driven-dissipative system with two-photon drive H_drive = ε₂â†² + h.c., the combination stabilizes the cat manifold: the steady states are coherent superpositions |C±_α⟩ of |±α⟩. The two-photon dissipation κ₂â² pumps photon pairs to the vacuum, while the drive creates them — the balance fixes the amplitude |α|² = |ε₂|/κ₂. The resulting degenerate steady-state manifold spans the cat qubit code space, passively protecting against single-photon loss on timescales κ₁/κ₂ ≪ 1.',
    hints=[
        'Two-photon drive + two-photon dissipation creates a degenerate manifold = passive cat qubit stabilization.',
    ],
    grade_mode=GradeMode.AUTO,
)
