"""Question: es_ry_cos"""
from core.models import Question

QUESTION = Question(
    id='es_ry_cos',
    section='Estimator',
    question='What does this print (rounded)?\n\n```python\nqc = QuantumCircuit(1)\nqc.ry(np.pi / 3, 0)\nev = StatevectorEstimator().run([(qc, "Z")]).result()[0].data.evs\nprint(round(float(ev), 6))\n```',
    options=[
        '0.866025',
        '0.5',
        '-0.5',
        '0.0',
    ],
    correct_index=1,
    explanation='RY(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩, so ⟨Z⟩ = cos²(θ/2) − sin²(θ/2) = cos θ = cos(π/3) = 0.5. The half angle inside the gate and the full angle in the expectation value is the classic trap: 0.866025 is cos(π/6), the amplitude of |0⟩.',
    difficulty='medium',
)
