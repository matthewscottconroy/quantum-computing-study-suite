"""Problem: ansatz_projected_vs_unprojected"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_projected_vs_unprojected',
    category='Ansatz Design',
    difficulty='advanced',
    question="What distinguishes a 'projected' ansatz from an 'unprojected' one in VQE?",
    choices=[
        'Projected: applies a projector onto the physical symmetry sector (e.g. correct particle number) after each gate, enforcing hard constraints; unprojected: no such enforcement, may visit unphysical states',
        'Projected: reduces circuit depth by projecting long-range gates to nearest-neighbour; unprojected: uses full connectivity',
        'Projected: uses post-selection to keep only symmetry-correct measurement outcomes; unprojected: uses all outcomes',
        'Projected: initialises in the HF reference state (a projection of the full Fock space); unprojected: starts from |0⟩^n',
    ],
    correct_index=0,
    explanation='An unprojected ansatz like UCCSD starts from the HF reference and applies excitation operators, but hardware noise can scatter the state outside the physical symmetry sector (wrong particle number or spin). A projected ansatz explicitly enforces symmetry at each step, e.g. by using symmetry-preserving gates (Givens rotations, fSWAP) that commute with the particle-number operator, ensuring every intermediate state has the correct number of electrons. Projected ansätze are more robust to noise and reduce the effective parameter space to only physical excitations, improving both convergence and noise resilience.',
    hints=[
        'Projection enforces the constraint that the state stays in the physical subspace throughout.',
    ],
    grade_mode=GradeMode.MC,
)
