"""Card: hw_neutral_atom"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='hw_neutral_atom',
    category='Quantum Hardware',
    front='Neutral atom qubits: Rydberg blockade',
    back='Ground-state atoms in optical tweezers; qubit in hyperfine levels.  2-qubit gate via Rydberg excitation: blockade prevents double excitation within ~10 μm, implementing CZ.',
)
