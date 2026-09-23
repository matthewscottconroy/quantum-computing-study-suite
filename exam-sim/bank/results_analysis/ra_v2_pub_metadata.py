"""Question: ra_v2_pub_metadata"""
from core.models import Question

QUESTION = Question(
    id='ra_v2_pub_metadata',
    section='Results analysis',
    question='Where does the shot count of a V2 sampler job live in the result object?\n\n```python\nresult = StatevectorSampler().run([qc], shots=100).result()\n```',
    options=[
        "result[0].metadata['shots'] — each pub result carries its own execution metadata",
        "result.metadata['shots'] — the job-level metadata dict holds the shot count",
        'result[0].shots — PubResult exposes shots as a direct attribute',
        'result.results[0].shots — the V1 Result layout is still used under the hood',
    ],
    correct_index=0,
    explanation="A PrimitiveResult is a sequence of PubResults, and per-execution metadata belongs to the pub: result[0].metadata is {'shots': 100, 'circuit_metadata': {}}. The job-level result.metadata only reports {'version': 2}. There is no .shots attribute on a PubResult (the data-side equivalent is result[0].data.meas.num_shots), and the V1 `result.results[...]` layout is gone in V2.",
    difficulty='medium',
)
