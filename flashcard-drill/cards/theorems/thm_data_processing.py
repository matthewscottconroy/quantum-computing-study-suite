"""Card: thm_data_processing"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='thm_data_processing',
    category='Theorems',
    front='Quantum data processing inequality',
    back='Applying a quantum channel (local operation) on B cannot increase correlations: S(A|B) ≤ S(A|C) if ρ_AC → ρ_AB by a channel on C.  Equivalent to monotonicity of relative entropy.',
)
