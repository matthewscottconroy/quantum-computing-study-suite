"""Problem: qoc_gate_vs_pulse"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qoc_gate_vs_pulse',
    category='Optimal Control',
    difficulty='beginner',
    question='What is the key difference between gate-level and pulse-level control in quantum computing?',
    choices=[
        'Gate-level: discrete unitaries (CNOT, Ry) as primitives; pulse-level: continuous microwave/laser waveforms that physically implement those gates — pulse level has more freedom but more complexity',
        'Gate-level uses classical bits for control; pulse-level uses quantum bits for feedback',
        'Gate-level circuits are executed on digital computers; pulse-level requires analog hardware',
        'Pulse-level is slower but more accurate; gate-level is faster but noisier',
    ],
    correct_index=0,
    explanation='Gate-level programming assembles circuits from discrete, fixed-fidelity primitives (e.g. CNOT, single-qubit rotations) and passes them to the quantum computer, which compiles them to pulses internally. Pulse-level programming directly specifies the microwave amplitudes and phases over time, giving more freedom: one can implement non-standard gates, faster two-qubit operations, native multi-qubit gates, and error-robust shaped pulses. Tools like Qiskit Pulse and OpenPulse provide pulse-level access; optimal control packages (QuTiP-QOC, qopt) automate pulse design.',
    hints=[
        'Gates are the high-level API; pulses are the low-level physics.',
    ],
    grade_mode=GradeMode.MC,
)
