"""Problem: noise_gate_fidelity"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_gate_fidelity',
    category='Noise & Mitigation',
    difficulty='beginner',
    question='What is the standard metric for single-qubit gate fidelity?',
    choices=[
        'Average gate fidelity F = ∫ dψ ⟨ψ|U†E(|ψ⟩⟨ψ|)U|ψ⟩, often reported as (d·F_ent + 1)/(d+1) for d-dimensional systems',
        'F = Tr(U†U_actual)/d where U_actual is the implemented gate matrix',
        'F = 1 - error_rate, where error_rate is the probability of any Pauli error',
        'F = |⟨0|U†E(|0⟩⟨0|)U|0⟩|² measured on a single fixed state',
    ],
    correct_index=0,
    explanation='Average gate fidelity F_avg averages the state fidelity F(|ψ⟩, E(|ψ⟩⟨ψ|)) over the Haar measure of input states. It relates to the entanglement fidelity F_ent by F_avg = (d·F_ent + 1)/(d+1) for d-dimensional systems. For single qubits (d=2), F_avg = (2F_ent + 1)/3. Average gate fidelity is the standard figure of merit reported for hardware benchmarking because it is state-independent and efficiently estimated via randomized benchmarking without full process tomography.',
    hints=[
        "Average gate fidelity averages over all input states — it's state-independent.",
    ],
    grade_mode=GradeMode.MC,
)
