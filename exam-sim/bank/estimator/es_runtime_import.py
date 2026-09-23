"""Question: es_runtime_import"""
from core.models import Question

QUESTION = Question(
    id='es_runtime_import',
    section='Estimator',
    question='Which snippet is the Qiskit 2.x way to run an estimator job on a real IBM backend?',
    options=[
        'from qiskit_ibm_runtime import EstimatorV2; estimator = EstimatorV2(mode=backend); estimator.run([(isa_qc, isa_obs)])',
        'from qiskit.primitives import Estimator; estimator = Estimator(backend=backend); estimator.run([qc], [obs])',
        'from qiskit import execute; execute(qc, backend, observables=[obs])',
        'from qiskit_ibm_runtime import EstimatorV2; estimator = EstimatorV2(); estimator.run(qc, obs, backend=backend)',
    ],
    correct_index=0,
    explanation='A Runtime primitive takes its execution context first — mode= accepts a backend, a Session or a Batch — and run() takes a list of pubs built from already-transpiled (ISA) circuits and layout-mapped observables. qiskit.primitives.Estimator (V1) and execute() were both removed, and there is no backend= argument on run().',
    difficulty='medium',
)
