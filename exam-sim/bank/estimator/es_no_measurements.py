"""Question: es_no_measurements"""
from core.models import Question

QUESTION = Question(
    id='es_no_measurements',
    section='Estimator',
    question='What happens when a circuit CONTAINING measurement instructions is submitted to StatevectorEstimator?',
    options=[
        'It raises a QiskitError — estimator circuits must not contain measurements',
        'The measurements are silently discarded before estimation',
        'It works: the estimator uses the measured bits to compute the expectation value',
        'It works only if the observable is diagonal',
    ],
    correct_index=0,
    explanation="Estimators compute ⟨ψ|O|ψ⟩ from the un-collapsed quantum state and add measurement bases themselves as needed; a user-placed measure collapses the state and is rejected ('Cannot apply instruction with classical bits: measure'). This is the mirror image of the sampler, which REQUIRES measurements.",
    difficulty='medium',
)
