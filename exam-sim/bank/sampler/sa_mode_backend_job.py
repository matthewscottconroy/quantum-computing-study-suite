"""Question: sa_mode_backend_job"""
from core.models import Question

QUESTION = Question(
    id='sa_mode_backend_job',
    section='Sampler',
    question='What execution mode does this use?\n\n```python\nfrom qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler\n\nbackend = QiskitRuntimeService().least_busy(operational=True, simulator=False)\nsampler = Sampler(mode=backend)\njob = sampler.run([isa_circuit], shots=4096)\n```',
    options=[
        'Job mode — passing a backend runs each call as an independent queued job, the only mode available on every plan',
        'Session mode — a session is opened implicitly around the backend',
        'Batch mode, because more than one shot batch is submitted',
        'Local testing mode, because no Session object was created',
    ],
    correct_index=0,
    explanation='mode=<BackendV2> is job mode: every run() is queued on its own. Sessions and batches exist only when you explicitly construct Session/Batch and pass it (or open it as a context manager). Job mode is the portable choice, since session and batch modes require a paid plan.',
    difficulty='medium',
)
