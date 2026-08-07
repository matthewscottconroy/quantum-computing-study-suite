"""Problem: noise_dynamical_decoupling"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='noise_dynamical_decoupling',
    category='Noise & Mitigation',
    difficulty='intermediate',
    question='Dynamical decoupling (DD) suppresses decoherence by:',
    choices=[
        'Applying periodic pulse sequences that average out low-frequency noise',
        'Increasing circuit depth to allow more time for decoherence',
        'Measuring the qubit frequently to collapse noise (quantum Zeno effect)',
        'Entangling idle qubits with ancillas to divert noise',
    ],
    correct_index=0,
    explanation='DD applies a sequence of pulses (e.g. XYXY) to idle qubits so that systematic errors from slow noise processes cancel over a cycle. The XY-4 sequence suppresses both Z and X errors from low-frequency noise. DD is hardware-level noise mitigation requiring no extra qubits.',
    hints=[
        'Think of it as a pulse sequence that averages the noise to zero.',
    ],
    grade_mode=GradeMode.MC,
)
