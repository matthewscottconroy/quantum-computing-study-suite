"""Problem: ansatz_open_2d_hubbard"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_open_2d_hubbard',
    category='Ansatz Design',
    difficulty='advanced',
    question='You are designing a VQE ansatz for a 2D Hubbard model on a 4×4 grid. What hardware connectivity do you need and what ansatz would you choose? Answer in 3–5 sentences.',
    choices=[],
    correct_index=-1,
    explanation='A 4×4 Hubbard model has 16 sites with spin-up and spin-down — 32 spin-orbitals, requiring 32 qubits with 2D grid (nearest-neighbour) connectivity. A symmetry-preserving ADAPT-VQE using pool operators drawn from the Hubbard interaction terms (hopping t_{ij} a†_i a_j and on-site U nᵢ↑nᵢ↓) would build a compact, physically motivated circuit tailored to the actual dominant correlations. The 2D grid connectivity matches the Hubbard lattice structure, minimising SWAP gates. For strongly correlated regimes (large U/t), a Hamiltonian variational ansatz with Trotter layers of the full Hubbard Hamiltonian would systematically improve with depth. Conserving total particle number and spin with symmetry-preserving gates reduces the search space and improves noise robustness.',
    hints=[
        'Match the circuit connectivity to the 2D lattice geometry. Consider ADAPT-VQE and HVA.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
