"""Problem: bos_gkp_error_correction"""
from __future__ import annotations
from quantum_study.qec_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_gkp_error_correction',
    category='Bosonic Codes',
    difficulty='intermediate',
    question='How does the GKP code correct errors?',
    choices=[
        'Small shifts in q̂ and p̂ are measured (homodyne) and displaced back to the nearest lattice point',
        'Photon loss is directly reversed by applying the creation operator â†',
        'Errors are corrected by measuring the photon number and applying a rotation',
        'Phase-space displacements are undone by a second displacement in the opposite direction without measurement',
    ],
    correct_index=0,
    explanation='GKP error correction: (1) Measure the position modulo √π (i.e., measure the stabilizer S_q to get the fractional displacement in q̂). (2) Apply a corrective displacement to bring q̂ back to the nearest lattice point. (3) Repeat for p̂ using S_p measurement. This works because any small displacement error ε shifts the state off the lattice; if |ε| < √π/2, the nearest lattice point is unambiguous and the shift is correctable. The logical information is encoded in which lattice coset the state lies in — this is not disturbed by measurements of the modular position.',
    hints=[
        'GKP correction: measure fractional displacement (syndrome), then apply corrective displacement.',
    ],
    grade_mode=GradeMode.AUTO,
)
