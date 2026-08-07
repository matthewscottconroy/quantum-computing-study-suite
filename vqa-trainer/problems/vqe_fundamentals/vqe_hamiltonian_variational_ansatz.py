"""Problem: vqe_hamiltonian_variational_ansatz"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_hamiltonian_variational_ansatz',
    category='VQE Fundamentals',
    difficulty='intermediate',
    question='What is the Hamiltonian variational ansatz (HVA) and what is its motivation?',
    choices=[
        'An ansatz whose layers are Trotterised evolution under each term of H, giving physically motivated parameterisation aligned with the problem structure',
        'An ansatz that directly parameterises the Hamiltonian coefficients rather than circuit angles',
        'A hardware-efficient ansatz built from the native Hamiltonian of the quantum processor',
        'A classical variational approach that varies the Hamiltonian itself to find the ground state',
    ],
    correct_index=0,
    explanation='The HVA (Wecker et al. 2015) constructs the ansatz as U(θ) = Πₗ Πₖ e^{-iθₗₖHₖ}, where {Hₖ} are the terms in the problem Hamiltonian. Each layer applies one parameterised rotation per Hamiltonian term, mirroring a Trotterised adiabatic evolution. This is physically motivated: if the problem Hamiltonian generates the ground state from a simple reference, the HVA provides a natural path. It also preserves symmetries of H automatically, and empirically requires fewer layers than generic ansätze.',
    hints=[
        'Each layer is built from the same terms that appear in H itself.',
    ],
    grade_mode=GradeMode.MC,
)
