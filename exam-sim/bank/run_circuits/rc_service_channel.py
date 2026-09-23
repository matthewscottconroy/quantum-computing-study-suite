"""Question: rc_service_channel"""
from core.models import Question

QUESTION = Question(
    id='rc_service_channel',
    section='Run circuits',
    question='What happens here with qiskit-ibm-runtime 0.4x?\n\n```python\nfrom qiskit_ibm_runtime import QiskitRuntimeService\n\nservice = QiskitRuntimeService(channel="ibm_quantum", token=TOKEN)\n```',
    options=[
        'ValueError — "ibm_quantum" was retired; the valid channels are "ibm_quantum_platform" and "ibm_cloud"',
        'It works, but prints a DeprecationWarning',
        'It works: "ibm_quantum" is still the default channel',
        'ImportError — QiskitRuntimeService moved to qiskit_ibm_provider',
    ],
    correct_index=0,
    explanation='The legacy ibm_quantum channel was shut down with the move to the IBM Quantum Platform. The constructor validates the argument and raises ValueError ("\'channel\' can only be \'ibm_cloud\', or \'ibm_quantum_platform\'"). New code uses channel="ibm_quantum_platform" with an API key and a CRN/instance.',
    difficulty='medium',
)
