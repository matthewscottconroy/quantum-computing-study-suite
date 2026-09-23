"""Question: es_pec_overhead"""
from core.models import Question

QUESTION = Question(
    id='es_pec_overhead',
    section='Estimator',
    question='A team switches from ZNE to probabilistic error cancellation (options.resilience.pec_mitigation = True). What is the main trade-off?',
    options=[
        'PEC gives an unbiased estimate, but its sampling overhead grows exponentially with circuit size and noise strength',
        'PEC is cheaper than ZNE but only works for diagonal (Z-only) observables',
        'PEC mitigates readout error only, so gate errors survive',
        'PEC needs no noise characterisation, unlike ZNE',
    ],
    correct_index=0,
    explanation='PEC samples from a quasi-probability decomposition of the inverted noise channel, so the estimator is unbiased — but the variance, and therefore the shot count, blows up exponentially, which is exactly why options.resilience.pec.max_overhead exists to cap it. PEC also requires a learned noise model, whereas plain ZNE does not.',
    difficulty='hard',
)
