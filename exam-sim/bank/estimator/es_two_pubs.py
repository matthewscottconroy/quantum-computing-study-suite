"""Question: es_two_pubs"""
from core.models import Question

QUESTION = Question(
    id='es_two_pubs',
    section='Estimator',
    question='What does this print?\n\n```python\na = QuantumCircuit(1)\na.x(0)\nb = QuantumCircuit(1)\nb.h(0)\n\nresult = StatevectorEstimator().run([(a, "Z"), (b, "X")]).result()\nprint(len(result), round(float(result[1].data.evs), 6))\n```',
    options=[
        '2 1.0',
        '1 1.0',
        '2 -1.0',
        '1 -1.0',
    ],
    correct_index=0,
    explanation='One PubResult comes back per pub, in submission order, so len(result) is 2: result[0] holds ⟨Z⟩ = −1 for |1⟩ and result[1] holds ⟨X⟩ = +1 for |+⟩. Batching independent pubs into one job is cheaper than separate jobs and nothing is averaged together.',
    difficulty='easy',
)
