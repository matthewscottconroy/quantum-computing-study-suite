"""Question: vz_bloch_entangled"""
from core.models import Question

QUESTION = Question(
    id='vz_bloch_entangled',
    section='Visualization',
    question='plot_bloch_multivector is applied to the Bell state (|00⟩ + |11⟩)/√2. What do the two Bloch spheres show?',
    options=[
        "Both vectors have length zero (points at the sphere's center) — each qubit alone is maximally mixed",
        "Both vectors point to +z, since '00' is the most likely outcome",
        'One vector points +z and the other −z, showing the correlation',
        'The function raises an error for entangled states',
    ],
    correct_index=0,
    explanation="Each qubit's reduced density matrix is I/2 — the maximally mixed state — whose Bloch vector is (0,0,0). Per-qubit Bloch spheres cannot display entanglement; the correlations live in the joint state, which is why the arrows vanish rather than point anywhere.",
    difficulty='hard',
)
