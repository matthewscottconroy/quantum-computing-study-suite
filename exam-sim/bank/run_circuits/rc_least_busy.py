"""Question: rc_least_busy"""
from core.models import Question

QUESTION = Question(
    id='rc_least_busy',
    section='Run circuits',
    question='Which call returns the operational IBM QPU with the shortest queue that has at least 127 qubits?',
    options=[
        'service.least_busy(operational=True, simulator=False, min_num_qubits=127)',
        'service.backends(least_busy=True, min_num_qubits=127)',
        'service.backend("least_busy", min_num_qubits=127)',
        'QiskitRuntimeService.least_busy(127)',
    ],
    correct_index=0,
    explanation='least_busy() is an instance method; min_num_qubits is a named parameter and extra filters such as operational=True and simulator=False are forwarded as backend-attribute keyword filters. It returns a single IBMBackend, whereas backends() returns a filtered list and has no least_busy flag.',
    difficulty='medium',
)
