"""Question: sa_v1_removed"""
from core.models import Question

QUESTION = Question(
    id='sa_v1_removed',
    section='Sampler',
    question='What does this do in Qiskit 2.x?\n\n```python\nfrom qiskit.primitives import Sampler\n```',
    options=[
        'ImportError — the V1 Sampler was removed in Qiskit 2.0; use StatevectorSampler (or BackendSamplerV2)',
        'It imports an alias of StatevectorSampler',
        'It works but every call emits a PendingDeprecationWarning',
        'It imports the abstract base class shared by all samplers',
    ],
    correct_index=0,
    explanation='Qiskit 2.0 removed the V1 primitive implementations (Sampler/Estimator and their Base*V1 interfaces). The reference V2 implementations are StatevectorSampler and StatevectorEstimator; BackendSamplerV2 wraps any backend. The abstract interface is BaseSamplerV2, not Sampler.',
    difficulty='medium',
)
