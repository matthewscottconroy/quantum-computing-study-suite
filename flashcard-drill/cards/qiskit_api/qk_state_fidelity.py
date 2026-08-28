"""Card: qk_state_fidelity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qk_state_fidelity',
    category='Qiskit API',
    front='state_fidelity(a, b) in quantum_info — definition and example value?',
    back='For pure states it is |⟨a|b⟩|².  Accepts Statevector or DensityMatrix.  state_fidelity(|0⟩, |+⟩) = 0.5.  Returns 1.0 for identical states, 0.0 for orthogonal ones.',
)
