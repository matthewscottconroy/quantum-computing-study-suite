"""Problem: ansatz_open_heisenberg"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_open_heisenberg',
    category='Ansatz Design',
    difficulty='advanced',
    question='For a 2D Heisenberg model H = J Σ_{⟨ij⟩} (XᵢXⱼ + YᵢYⱼ + ZᵢZⱼ) on a 4×4 grid with all-to-all hardware connectivity, what ansatz would you choose and why? Answer in 3–5 sentences.',
    choices=[],
    correct_index=-1,
    explanation='A symmetry-preserving brick-layer ansatz matching the 2D lattice connectivity is a strong choice. The Heisenberg model conserves total spin Sz = Σᵢ Zᵢ, so using particle-number-preserving gates (e.g. fSWAP, Givens rotations) constrains the search to the correct symmetry sector. With all-to-all hardware, one can apply CNOT gates between any pair of sites, but matching the 2D lattice structure (4-neighbour coupling) reduces unnecessary entanglement. ADAPT-VQE with an operator pool drawn from the Heisenberg interaction terms {XᵢXⱼ, YᵢYⱼ, ZᵢZⱼ} would build a compact, physically motivated circuit. Alternatively, a Hamiltonian variational ansatz using e^{-iθ(XᵢXⱼ+YᵢYⱼ+ZᵢZⱼ)} layers mirrors the Trotter structure and is known to capture the ground state well.',
    hints=[
        'Consider symmetry, the 2D lattice structure, and whether ADAPT or a fixed structure suits the problem.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
