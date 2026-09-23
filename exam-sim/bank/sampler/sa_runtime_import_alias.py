"""Question: sa_runtime_import_alias"""
from core.models import Question

QUESTION = Question(
    id='sa_runtime_import_alias',
    section='Sampler',
    question='Which of these imports actually works in Qiskit 2.x and gives you the hardware sampler?',
    options=[
        'from qiskit_ibm_runtime import SamplerV2 as Sampler',
        'from qiskit.primitives import Sampler',
        'from qiskit_ibm_runtime.primitives import SamplerV2',
        'from qiskit import Sampler',
    ],
    correct_index=0,
    explanation='qiskit_ibm_runtime exports SamplerV2 at the top level, and the documented convention is to alias it to Sampler so call sites read naturally (the package also re-exports the same class under the plain name Sampler). The other three all fail: qiskit.primitives.Sampler was the V1 reference implementation, removed in Qiskit 1.x (its V2 replacement is StatevectorSampler); there is no qiskit_ibm_runtime.primitives module; and qiskit itself never exported a Sampler.',
    difficulty='easy',
)
