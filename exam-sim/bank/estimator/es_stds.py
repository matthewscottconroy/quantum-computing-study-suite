"""Question: es_stds"""
from core.models import Question

QUESTION = Question(
    id='es_stds',
    section='Estimator',
    question='Every estimator PubResult carries `data.stds` next to `data.evs`. Which statement is TRUE?',
    options=[
        'stds holds the standard deviation of the observable eigenvalues, independent of shots',
        'stds repeats the target precision that was requested for the job',
        'stds is an array shaped like evs holding each value\'s standard error; StatevectorEstimator fills it with zeros',
        'stds is only present when resilience_level is 0',
    ],
    correct_index=2,
    explanation='evs and stds always come in pairs with matching shapes, which is what lets you put error bars on an energy curve. Shot-based estimators report the sampling standard error there; the exact reference StatevectorEstimator computes ⟨O⟩ analytically and reports zeros even when a nonzero precision was requested. The requested value is kept separately in the pub metadata as target_precision.',
    difficulty='medium',
)
