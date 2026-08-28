"""Question: sa_backend_sampler"""
from core.models import Question

QUESTION = Question(
    id='sa_backend_sampler',
    section='Sampler',
    question='You want the V2 sampler interface but with shots executed on a specific backend object (e.g. an AerSimulator with a noise model). Which class do you use?',
    options=[
        'BackendSamplerV2(backend=backend)',
        'StatevectorSampler(backend=backend)',
        'Sampler.from_backend(backend)',
        'backend.sampler()',
    ],
    correct_index=0,
    explanation='BackendSamplerV2 wraps any BackendV2 (including Aer with noise) behind the V2 sampler interface. StatevectorSampler takes no backend — it always simulates the ideal statevector locally — and the other two APIs do not exist.',
    difficulty='medium',
)
