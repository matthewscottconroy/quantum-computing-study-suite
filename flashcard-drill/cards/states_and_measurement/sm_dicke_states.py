"""Card: sm_dicke_states"""
from __future__ import annotations
from core.models import Flashcard

CARD = Flashcard(
    id='sm_dicke_states',
    category='States & Measurement',
    front='Dicke states: definition',
    back='Symmetric superpositions of all n-qubit states with exactly k ones: |D_k^n⟩ = (1/√C(n,k))Σ_{|x|=k}|x⟩.  Relevant in superradiance and quantum optics.',
)
