"""Question: es_zne_enable"""
from core.models import Question

QUESTION = Question(
    id='es_zne_enable',
    section='Estimator',
    question='Which snippet explicitly enables zero-noise extrapolation with noise factors 1, 3 and 5 on a Runtime EstimatorV2?',
    options=[
        'estimator.options.resilience.zne_mitigation = True, then estimator.options.resilience.zne.noise_factors = (1, 3, 5)',
        'estimator.options.zne = True, then estimator.options.noise_factors = (1, 3, 5)',
        'estimator.options.error_mitigation = "zne", then estimator.options.factors = (1, 3, 5)',
        'estimator.run([(qc, obs)], zne=True, noise_factors=(1, 3, 5))',
    ],
    correct_index=0,
    explanation='Error mitigation is configured through the nested options tree: options.resilience.zne_mitigation turns the method on and options.resilience.zne holds its knobs (noise_factors, extrapolator, amplifier). run() accepts pubs and precision only, and there is no flat options.zne or error_mitigation string.',
    difficulty='medium',
)
