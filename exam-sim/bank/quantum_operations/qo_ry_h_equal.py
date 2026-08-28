"""Question: qo_ry_h_equal"""
from core.models import Question

QUESTION = Question(
    id='qo_ry_h_equal',
    section='Quantum operations',
    question='Which rotation gate, applied to |0⟩, produces exactly the same state as H|0⟩ = (|0⟩ + |1⟩)/√2?',
    options=[
        'RY(π/2)',
        'RX(π/2)',
        'RZ(π/2)',
        'RY(π)',
    ],
    correct_index=0,
    explanation='RY(π/2)|0⟩ = cos(π/4)|0⟩ + sin(π/4)|1⟩ = (|0⟩+|1⟩)/√2 with real amplitudes — identical to H|0⟩. RX(π/2) gives a complex relative phase (−i on |1⟩), RZ leaves |0⟩ unchanged up to phase, and RY(π) gives |1⟩.',
    difficulty='medium',
)
