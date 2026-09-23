"""Question: rc_non_isa_error"""
from core.models import Question

QUESTION = Question(
    id='rc_non_isa_error',
    section='Run circuits',
    question='You build a circuit with h and cx, skip transpilation, and call SamplerV2(mode=ibm_backend).run([qc]). What happens?',
    options=[
        'An IBMInputValueError is raised client-side saying the instruction is not supported by the target',
        'The job is submitted and the service transpiles the circuit for you',
        'The job is submitted and fails on the server with a QiskitError after queueing',
        'It runs: h and cx are universal, so every backend accepts them',
    ],
    correct_index=0,
    explanation='The V2 primitives call validate_isa_circuits(pubs, backend.target) before submitting. A gate that is not in the target (h is not an IBM basis gate) or a two-qubit gate on an uncoupled pair raises IBMInputValueError locally — nothing is queued. Server-side auto-transpilation was removed in March 2024.',
    difficulty='hard',
)
