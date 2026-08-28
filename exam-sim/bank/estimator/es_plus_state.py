"""Question: es_plus_state"""
from core.models import Question

QUESTION = Question(
    id='es_plus_state',
    section='Estimator',
    question='For the state H|0⟩ = |+⟩, what are ⟨X⟩ and ⟨Z⟩ (in that order)?',
    options=[
        '⟨X⟩ = 1, ⟨Z⟩ = 0',
        '⟨X⟩ = 0, ⟨Z⟩ = 1',
        '⟨X⟩ = 0, ⟨Z⟩ = 0',
        '⟨X⟩ = 1, ⟨Z⟩ = 1',
    ],
    correct_index=0,
    explanation='|+⟩ is the +1 eigenstate of X, so ⟨X⟩ = 1. In the Z basis it is an equal superposition, so Z measurements average to 0. On the Bloch sphere the state points along +x, perpendicular to z.',
    difficulty='medium',
)
