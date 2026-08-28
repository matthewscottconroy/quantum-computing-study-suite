"""Card: qk_state_city"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_state_city',
    category='Qiskit API',
    front='What does plot_state_city display?',
    back="A 'cityscape': two 3D bar charts of the density matrix — real parts and imaginary parts of every element ρᵢⱼ.  Takes a Statevector or DensityMatrix.  A pure |+⟩⟨+| shows four equal 0.5 real bars.",
)
