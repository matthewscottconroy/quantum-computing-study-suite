"""Question: es_zne_concept"""
from core.models import Question

QUESTION = Question(
    id='es_zne_concept',
    section='Estimator',
    question='What does zero-noise extrapolation (ZNE) actually do?',
    options=[
        'It inverts the noise channel exactly, giving an unbiased estimate at exponential sampling cost',
        'It runs the circuit at several AMPLIFIED noise levels and extrapolates the results back to the zero-noise limit',
        'It discards any shot whose bitstring violates a known symmetry of the problem',
        'It randomises the measurement basis so that readout errors average out',
    ],
    correct_index=1,
    explanation='ZNE deliberately amplifies noise (by gate folding or pulse stretching), fits ⟨O⟩ as a function of the noise factor and evaluates that fit at zero. It reduces bias without guaranteeing to remove it, and it needs no noise model. Exact noise inversion at exponential cost is PEC, symmetry filtering is post-selection, and basis randomisation describes twirling.',
    difficulty='medium',
)
