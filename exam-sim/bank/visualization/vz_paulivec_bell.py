"""Question: vz_paulivec_bell"""
from core.models import Question

QUESTION = Question(
    id='vz_paulivec_bell',
    section='Visualization',
    question='plot_state_paulivec is applied to the Bell state (|00⟩ + |11⟩)/√2. Which bars are nonzero?',
    options=[
        'Only ZZ, at height 1',
        'II, XX, YY and ZZ, all at +1',
        'II = 1, XX = 1, ZZ = 1 and YY = −1; every other Pauli is 0',
        'All sixteen two-qubit Paulis, each at height 1/4',
    ],
    correct_index=2,
    explanation='The paulivec bars are the expectation values ⟨P⟩ of each Pauli string. For this Bell state the stabilisers XX and ZZ give +1 and II is always 1, while YY = −1 because Y⊗Y contributes the product of two imaginary units. Every single-qubit term (XI, IZ, …) vanishes, since each qubit on its own is maximally mixed.',
    difficulty='hard',
)
