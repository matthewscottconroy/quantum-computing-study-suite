"""Question: qo_rx_pi"""
from core.models import Question

QUESTION = Question(
    id='qo_rx_pi',
    section='Quantum operations',
    question='A single qubit starts in |0⟩ and RX(π) is applied. If the qubit is then measured in the computational basis, what is the outcome?',
    options=[
        'Always 1 — RX(π) equals X up to a global phase of −i',
        'Always 0 — RX(π) is a full rotation back to |0⟩',
        '0 or 1 with 50% probability each',
        'Always 1, and the state is exactly |1⟩ with no phase factor',
    ],
    correct_index=0,
    explanation='RX(π)|0⟩ = −i|1⟩. The −i is a global phase, unobservable in any measurement, so the outcome is deterministically 1 — but the statevector is −i|1⟩, not exactly |1⟩, which is why the last option is wrong.',
    difficulty='medium',
)
