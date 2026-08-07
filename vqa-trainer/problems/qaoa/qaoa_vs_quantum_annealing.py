"""Problem: qaoa_vs_quantum_annealing"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='qaoa_vs_quantum_annealing',
    category='QAOA',
    difficulty='advanced',
    question='What are the key differences and similarities between QAOA and quantum annealing (QA)?',
    choices=[
        'Both implement adiabatic-inspired optimisation; QAOA is gate-based and classically optimises discrete parameters, while QA is analog and uses a physically continuous schedule',
        'QAOA and QA are identical algorithms — QA is just the continuous-time limit of QAOA',
        'QAOA is limited to MaxCut; QA can solve arbitrary optimisation problems including non-binary ones',
        'QA is provably better than QAOA for all problem sizes because it uses continuous time evolution',
    ],
    correct_index=0,
    explanation='Similarities: both use quantum superposition and interference to find low-energy states of a classical cost Hamiltonian; both can be analysed via the adiabatic theorem. Differences: QA is an analog device (D-Wave) with a fixed continuous-time schedule that cannot be classically optimised; QAOA is a digital gate-based algorithm with classically optimisable discrete parameters {γ,β}. QAOA allows arbitrary mixers, not just transverse-field B = ΣXᵢ, and operates on fault-tolerant or NISQ gate devices. Theoretical guarantees differ: QA has the adiabatic theorem; QAOA has formal approximation ratios.',
    hints=[
        'Analog vs digital is the key hardware distinction; parameter optimisation is the key algorithmic one.',
    ],
    grade_mode=GradeMode.MC,
)
