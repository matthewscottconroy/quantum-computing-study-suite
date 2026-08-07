"""Problem: ansatz_physically_motivated_vs_hea"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ansatz_physically_motivated_vs_hea',
    category='Ansatz Design',
    difficulty='intermediate',
    question="What makes an ansatz 'physically motivated' vs 'hardware-efficient', and what are the trade-offs?",
    choices=[
        'Physically motivated: derived from problem symmetries/physics (UCCSD, HVA) — deeper but avoids irrelevant parameters; hardware-efficient: matches device connectivity — shallower but may miss problem structure',
        'Physically motivated: uses only classical gates; hardware-efficient: uses native quantum gates only',
        'Physically motivated: optimised by classical simulation; hardware-efficient: optimised on the quantum device',
        'They are equivalent — any hardware-efficient circuit can represent any physically motivated state given enough depth',
    ],
    correct_index=0,
    explanation="Physically motivated ansätze like UCCSD or Hamiltonian variational ansatz (HVA) are designed using knowledge of the problem's physical structure: symmetries, relevant excitation operators, or Trotter steps of H. They explore only the physically relevant region of Hilbert space, reducing barren plateau risk and improving convergence, but they may require deep circuits that exceed NISQ capabilities. Hardware-efficient ansätze (HEA) use the device's native gates and connectivity, minimising circuit depth and SWAP overhead, but their broad exploration of Hilbert space can cause barren plateaus and may include 'wasted' parameters with no physical interpretation.",
    hints=[
        'Physics motivation = fewer but more meaningful parameters; hardware efficiency = shallower circuits.',
    ],
    grade_mode=GradeMode.MC,
)
