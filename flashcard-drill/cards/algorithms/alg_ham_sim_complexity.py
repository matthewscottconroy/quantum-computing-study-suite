"""Card: alg_ham_sim_complexity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='alg_ham_sim_complexity',
    category='Algorithms',
    front='Gate complexity for k-local Hamiltonian simulation',
    back='Trotter: O(poly(n)·t^{1+1/p}) for p-th order formula.  Qubitization/QSVT: O(t·‖H‖ + log(1/ε)) — near optimal.  Key benchmark for quantum advantage.',
)
