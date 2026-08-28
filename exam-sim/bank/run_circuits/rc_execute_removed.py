"""Question: rc_execute_removed"""
from core.models import Question

QUESTION = Question(
    id='rc_execute_removed',
    section='Run circuits',
    question='A tutorial written for an old Qiskit version contains:\n\n```python\nfrom qiskit import execute\n\njob = execute(qc, backend, shots=1024)\n```\n\nWhat happens in Qiskit 2.x?',
    options=[
        'ImportError — execute() was removed; transpile the circuit and call backend.run() (or use a primitive) instead',
        'It works but emits a DeprecationWarning',
        'It works only if the backend is a simulator',
        'ImportError — execute() moved to qiskit.tools.execute',
    ],
    correct_index=0,
    explanation='The top-level execute() helper was removed in Qiskit 1.0 and does not exist in 2.x. The modern flow is to transpile explicitly (e.g. with generate_preset_pass_manager) and then submit via backend.run() or, preferably, the Sampler/Estimator primitives.',
    difficulty='medium',
)
