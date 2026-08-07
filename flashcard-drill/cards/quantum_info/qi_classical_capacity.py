"""Card: qi_classical_capacity"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_classical_capacity',
    category='Quantum Info',
    front='Classical capacity C of a quantum channel',
    back='C = max_{pᵢ,ρᵢ} [S(Σpᵢε(ρᵢ)) − Σpᵢ S(ε(ρᵢ))] (Holevo capacity per use).  Additivity for entangled inputs proven for some channels.',
)
