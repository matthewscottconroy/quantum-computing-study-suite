"""Question: rc_mode_type_error"""
from core.models import Question

QUESTION = Question(
    id='rc_mode_type_error',
    section='Run circuits',
    question='What happens here?\n\n```python\nfrom qiskit_ibm_runtime import SamplerV2\n\nsampler = SamplerV2(mode="ibm_torino")\n```',
    options=[
        'ValueError — mode must be a Backend, Session, Batch or None, not a backend name string',
        'It works: the string is resolved to a backend through the default saved account',
        'It works, but the first run() call raises because no service was supplied',
        'TypeError — the first positional parameter of SamplerV2 is backend, not mode',
    ],
    correct_index=0,
    explanation='SamplerV2(mode=...) accepts a BackendV2 (job mode), a Session, a Batch, or None (inherit the enclosing session/batch context). A string raises ValueError("mode must be of type Backend, Session, Batch or None"); resolve the name first with service.backend("ibm_torino"). mode *is* the first positional parameter — the V1-era backend= keyword is what no longer exists.',
    difficulty='medium',
)
