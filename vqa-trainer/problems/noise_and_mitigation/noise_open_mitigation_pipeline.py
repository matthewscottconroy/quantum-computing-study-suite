"""Problem: noise_open_mitigation_pipeline"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_open_mitigation_pipeline',
    category='Noise & Mitigation',
    difficulty='advanced',
    question='Design a practical noise mitigation pipeline for a 20-qubit VQE circuit on current hardware with ~0.1% two-qubit gate error. Describe in 3–5 sentences what techniques you would combine and why.',
    choices=[],
    correct_index=-1,
    explanation='A practical pipeline for 20-qubit VQE at 0.1% two-qubit gate error: (1) Pauli twirling on all two-qubit gates to convert coherent errors to Pauli channels, simplifying noise characterisation and making ZNE more accurate. (2) Dynamical decoupling on idle qubits to suppress low-frequency dephasing during measurement and multi-qubit gate phases. (3) ZNE with 2–3 noise factors (λ=1,2,3 via gate folding) with Richardson extrapolation — feasible overhead (~3× shots) at 0.1% error per gate (PEC overhead γ² would be unacceptable). (4) Symmetry verification to discard shots with wrong particle number — free and effective for chemistry VQE where particle number is conserved. (5) Readout error mitigation using tensor-product calibration for independent qubit correction. This layered approach addresses coherent, incoherent, and measurement errors in order of cost.',
    hints=[
        'Layer multiple complementary techniques: twirling, DD, ZNE, symmetry verification, readout mitigation.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
