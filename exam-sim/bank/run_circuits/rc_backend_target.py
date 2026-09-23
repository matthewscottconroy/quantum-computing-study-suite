"""Question: rc_backend_target"""
from core.models import Question

QUESTION = Question(
    id='rc_backend_target',
    section='Run circuits',
    question='For a BackendV2 object, which attribute describes the native instruction set, qubit connectivity and error/duration data that the transpiler compiles against?',
    options=[
        'backend.target',
        'backend.configuration()',
        'backend.properties()',
        'backend.defaults()',
    ],
    correct_index=0,
    explanation='BackendV2 unified everything the transpiler needs into a single Target object: supported operations, the qubit pairs each two-qubit gate is calibrated on, durations and errors. configuration(), properties() and defaults() are BackendV1 methods and are absent from a plain BackendV2 (accessing them raises AttributeError).',
    difficulty='easy',
)
