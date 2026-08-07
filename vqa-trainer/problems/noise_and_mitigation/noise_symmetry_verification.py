"""Problem: noise_symmetry_verification"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_symmetry_verification',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='What is symmetry verification (symmetry expansion) as an error mitigation technique?',
    choices=[
        'Discard (or post-select) measurement outcomes that violate known symmetries of the Hamiltonian, projecting to the physical subspace',
        'Add symmetry-breaking noise terms to the Hamiltonian and extrapolate to zero breaking',
        'Verify the symmetry of the ansatz circuit by comparing it to its transpose',
        'Use the symmetry group to reduce the Pauli decomposition of H before measurement',
    ],
    correct_index=0,
    explanation='Physical Hamiltonians have symmetries (e.g. particle number N̂, parity P̂). Hardware noise can scatter the quantum state outside the physical symmetry sector. Symmetry verification measures the symmetry operators after each circuit run; shots landing in the wrong symmetry sector are discarded (post-selection) or their contributions are down-weighted. This biases the estimate toward the physical subspace at the cost of reduced statistics. Symmetry expansion uses all shots but applies corrections to enforce the symmetry, giving an unbiased estimator within the physical sector.',
    hints=[
        'Physical states must satisfy symmetry constraints — use those constraints to filter noise.',
    ],
    grade_mode=GradeMode.MC,
)
