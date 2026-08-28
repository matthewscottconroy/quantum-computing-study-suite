"""Card: qk_qsphere"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_qsphere',
    category='Qiskit API',
    front='On a plot_state_qsphere, what encodes amplitude and what encodes phase?',
    back='Each basis state is a node on the sphere; node SIZE encodes probability |amplitude|² and node COLOR encodes the relative PHASE (color wheel from 0 to 2π).  |0…0⟩ sits at the north pole, |1…1⟩ at the south pole.',
)
