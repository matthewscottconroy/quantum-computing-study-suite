"""Question: es_precision_shots"""
from core.models import Question

QUESTION = Question(
    id='es_precision_shots',
    section='Estimator',
    question='What does this print?\n\n```python\nest = BackendEstimatorV2(backend=AerSimulator())\nqc = QuantumCircuit(1)\nqc.ry(np.pi / 3, 0)\n\nresult = est.run([(qc, "Z")], precision=0.01).result()\nprint(result[0].metadata["shots"])\n```',
    options=[
        '1024',
        '4096',
        '100',
        '10000',
    ],
    correct_index=3,
    explanation='A V2 estimator is asked for a target error, not a shot count: BackendEstimatorV2 converts it with shots = ceil(1 / precision**2), so precision=0.01 costs 10000 shots per circuit and tightening the target by 2x costs 4x the shots. 4096 is what its default precision of 0.015625 would have given.',
    difficulty='hard',
)
