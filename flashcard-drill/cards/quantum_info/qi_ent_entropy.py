"""Card: qi_ent_entropy"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='qi_ent_entropy',
    category='Quantum Info',
    front='Entanglement entropy of a bipartite pure state',
    back='E(|ψ⟩_AB) = S(ρ_A) = S(ρ_B)   where ρ_A = Tr_B(|ψ⟩⟨ψ|).  Equals 1 ebit for Bell states.',
)
