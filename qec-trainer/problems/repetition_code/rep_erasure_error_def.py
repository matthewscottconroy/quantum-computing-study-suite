"""Problem: rep_erasure_error_def"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_erasure_error_def',
    category='Repetition Code',
    difficulty='beginner',
    question='What is an erasure error, and how does it differ from a Pauli (depolarizing) error?',
    choices=[
        'An erasure is a loss event where the qubit location is known; a Pauli error is unknown in location',
        'An erasure replaces the qubit with |0⟩; a Pauli error replaces it with |1⟩',
        'An erasure destroys all quantum information; a Pauli error is always correctable',
        'Erasure errors only affect phase; Pauli errors only affect amplitude',
    ],
    correct_index=0,
    explanation='An erasure error means a qubit is lost or moved outside the codespace, but crucially, we know which qubit was erased (the location is flagged, e.g., a photon is lost from a specific channel). This extra information makes erasures easier to correct than Pauli errors: a code of distance d can correct up to d−1 erasures (vs. ⌊(d−1)/2⌋ Pauli errors). Pauli errors have unknown location, requiring syndrome measurement to locate them.',
    hints=[
        'The key difference is whether the error location is known or must be inferred.',
    ],
    grade_mode=GradeMode.AUTO,
)
