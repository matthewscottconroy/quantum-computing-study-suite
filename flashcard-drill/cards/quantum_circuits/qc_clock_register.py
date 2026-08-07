"""Card: qc_clock_register"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qc_clock_register',
    category='Quantum Circuits',
    front='Clock register in QMA verifier Hamiltonians',
    back='The clock register |t⟩ tracks the step in the computation.  Hamiltonian penalises states not in the computational history, with ground state encoding the correct computation path.',
)
