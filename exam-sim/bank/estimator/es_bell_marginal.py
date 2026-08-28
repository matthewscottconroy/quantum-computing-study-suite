"""Question: es_bell_marginal"""
from core.models import Question

QUESTION = Question(
    id='es_bell_marginal',
    section='Estimator',
    question='For the Bell state (|00⟩ + |11⟩)/√2, which set of expectation values is correct?',
    options=[
        '⟨ZZ⟩ = 1 while ⟨ZI⟩ = 0 and ⟨IZ⟩ = 0',
        '⟨ZZ⟩ = 1 and ⟨ZI⟩ = 1 and ⟨IZ⟩ = 1',
        '⟨ZZ⟩ = 0 because the state is entangled',
        "⟨ZZ⟩ = 0.5, matching the probability of '00'",
    ],
    correct_index=0,
    explanation='Each qubit alone is maximally mixed, so single-qubit ⟨Z⟩ values vanish — but the outcomes are perfectly correlated, so the product ZZ is always +1. This correlation-without-marginals pattern is the signature of entanglement.',
    difficulty='hard',
)
