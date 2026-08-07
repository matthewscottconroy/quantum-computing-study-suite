"""Problem: readout_mitigation"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='readout_mitigation',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='Readout error mitigation using a calibration matrix A works by:',
    choices=[
        'Measuring A (noisy→ideal mapping) on all 2ⁿ basis states and inverting it',
        'Applying a unitary before measurement to cancel readout errors',
        'Repeating each measurement 3 times and taking the majority',
        'Using ancilla qubits to non-destructively measure the state',
    ],
    correct_index=0,
    explanation='Build calibration matrix Aᵢⱼ = P(measure i | prepared j) for all j. Then invert: p_ideal = A⁻¹ p_noisy. Full n-qubit calibration scales as 2ⁿ circuits — tensor product (independent qubit) approximation scales as n circuits.',
    hints=[
        'Prepare each basis state, measure the confusion, then invert.',
    ],
    grade_mode=GradeMode.MC,
)
