"""Card: hw_T1_T2"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_T1_T2',
    category='Quantum Hardware',
    front='Typical T1 and T2 times for superconducting qubits',
    back='T1 (energy relaxation): 100–500 μs on state-of-the-art devices.  T2 (dephasing): similar or shorter.  T2 ≤ 2T1 always; T2 = 2T1 for pure T1 noise.',
)
