"""Card: qk_bloch_multivector"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_bloch_multivector',
    category='Qiskit API',
    front='What input does plot_bloch_multivector take and what does it show?',
    back="A Statevector or DensityMatrix (not counts, not a circuit).  It draws one Bloch sphere per qubit showing each qubit's reduced (partial-traced) state — entangled qubits appear as shortened vectors inside the sphere.",
)
