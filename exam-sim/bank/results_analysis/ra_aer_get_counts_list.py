"""Question: ra_aer_get_counts_list"""
from core.models import Question

QUESTION = Question(
    id='ra_aer_get_counts_list',
    section='Results analysis',
    question='What does this print?\n\n```python\nfrom qiskit_aer import AerSimulator\n\nresult = AerSimulator().run([qc_a, qc_b], shots=100).result()\nprint(type(result.get_counts()).__name__)\n```',
    options=[
        'list — one Counts object per submitted circuit; index it or call result.get_counts(0)',
        'Counts — the histograms of all circuits are merged into one dictionary',
        'dict — get_counts() always returns a plain dict of bitstrings to integers',
        'PrimitiveResult — Aer returns the V2 primitive container',
    ],
    correct_index=0,
    explanation="When a backend job contains several experiments, `Result.get_counts()` with no argument returns a LIST of Counts in submission order; pass an index (or the circuit object) to pick one. With a single circuit it returns a bare Counts, so code written against one circuit breaks the moment a second is added — always index explicitly. Aer's `run()` still uses the V1 Result API; the primitives return PrimitiveResult instead.",
    difficulty='medium',
)
