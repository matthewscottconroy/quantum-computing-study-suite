"""Question: sa_no_values_attr"""
from core.models import Question

QUESTION = Question(
    id='sa_no_values_attr',
    section='Sampler',
    question='Porting V1 code, you write `evs = job.result().values` after a SamplerV2 run. What happens?',
    options=[
        'AttributeError — .values is an Estimator V1 idiom; a sampler returns measurement samples, reached through result[0].data.<creg>',
        'It returns a numpy array of the sampled bit probabilities',
        'It returns the list of counts dictionaries, one per PUB',
        'It works, but only when every circuit uses measure_all()',
    ],
    correct_index=0,
    explanation='PrimitiveResult exposes no .values, .quasi_dists or .get_counts(): those belong to the removed V1 primitives. A sampler never produces expectation values at all — you index the result by PUB and read a BitArray per classical register. (Expectation values come from EstimatorV2 as result[0].data.evs.)',
    difficulty='medium',
)
