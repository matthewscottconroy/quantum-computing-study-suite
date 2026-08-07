"""Problem: vqe_open_bottlenecks"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='vqe_open_bottlenecks',
    category='VQE Fundamentals',
    difficulty='advanced',
    question='In 3–5 sentences, describe the main bottlenecks preventing VQE from achieving quantum advantage on current (NISQ) hardware.',
    choices=[],
    correct_index=-1,
    explanation='Key bottlenecks include: (1) Circuit depth — UCCSD and similar ansätze require deep circuits whose gate error rates exceed current hardware capabilities. (2) Measurement overhead — estimating all Pauli terms in H requires many circuit shots, especially for large molecules. (3) Classical optimisation — the energy landscape has many local minima and potentially barren plateaus, making convergence unreliable. (4) Noise-induced barren plateaus — hardware noise flattens the energy landscape for deep circuits, removing gradient signal. (5) Qubit count — classically intractable molecules require hundreds of logical qubits with error correction, far beyond NISQ scale.',
    hints=[
        'Consider circuit noise, measurement cost, optimisation landscape, and qubit overhead.',
    ],
    grade_mode=GradeMode.CLAUDE,
)
