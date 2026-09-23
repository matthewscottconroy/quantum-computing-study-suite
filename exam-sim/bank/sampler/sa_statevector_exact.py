"""Question: sa_statevector_exact"""
from core.models import Question

QUESTION = Question(
    id='sa_statevector_exact',
    section='Sampler',
    question='Which statement about StatevectorSampler is correct?',
    options=[
        'It simulates the exact statevector and samples it, so circuits need no transpilation and results carry no hardware noise',
        'It returns exact probabilities rather than shot counts, so the shots argument is ignored',
        'It requires ISA circuits, just like the Runtime SamplerV2',
        'It is a drop-in for the removed V1 Sampler and returns quasi_dists',
    ],
    correct_index=0,
    explanation='StatevectorSampler is a reference implementation in qiskit.primitives: it builds the full statevector, so any gate set and any connectivity are fine and there is no noise. It still honours shots — it draws that many samples from the exact distribution — and its results use the V2 shape (result[0].data.<creg>), never quasi_dists.',
    difficulty='easy',
)
