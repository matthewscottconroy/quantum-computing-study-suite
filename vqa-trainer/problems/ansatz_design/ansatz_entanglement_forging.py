"""Problem: ansatz_entanglement_forging"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_entanglement_forging',
    category='Ansatz Design',
    difficulty='advanced',
    question='What is the entanglement forging technique in VQA?',
    choices=[
        'Factoring an n-qubit simulation into two n/2-qubit circuits using classical post-processing with bootstrapping weights',
        'Replacing all CNOT gates with classically simulated entanglement maps',
        'Using ancilla qubits to entangle two separate quantum registers',
        'A method to forge (generate) maximally entangled states for use as ansatz inputs',
    ],
    correct_index=0,
    explanation='Entanglement forging (Eddins et al. 2022) decomposes an n-qubit state |ψ⟩ = Σₖ wₖ |bₖ⟩_A ⊗ |ψₖ⟩_B into a weighted sum over bitstrings bₖ on system A and quantum states on system B. Each term requires only n/2-qubit circuits, halving the qubit count. Expectation values are reconstructed classically by combining the n/2-qubit results with the bootstrapping weights wₖ. The classical overhead scales as 4^m for m forged qubits, so only modest forging (m=1–3) is practical, but this can extend the reach of current devices significantly.',
    hints=[
        'The n-qubit problem is split across two n/2-qubit circuits connected classically.',
    ],
    grade_mode=GradeMode.MC,
)
